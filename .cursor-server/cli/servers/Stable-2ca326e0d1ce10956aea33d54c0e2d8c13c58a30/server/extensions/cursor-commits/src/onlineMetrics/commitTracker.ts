import * as vscode from 'vscode';
import { gitInfoFromGitRootToHead, IRequestTracker, ISpecificRequestTracker } from './requestTracker.js';
import { StoredRequestTrackingMetadata } from 'proto/aiserver/v1/online_metrics_pb.js';
import { LRUCache } from 'lru-cache';
import { OnlineMetricsConfig } from 'proto/aiserver/v1/online_metrics_pb.js';
import { API, Repository } from '../../../git/src/api/git.js';
import * as path from 'path';
import * as fs from 'fs';
import { CursorDebugLogger } from '../utils/logger.js';
import { PlainMessage } from '@bufbuild/protobuf';
import { RequestTrackingFileGitInfo } from 'proto/aiserver/v1/online_metrics_pb.js';

type FileContentCacheValue = { case: 'null' } | { case: 'string', value: string } | { case: 'tooBig' };
function cacheValueToReturnValue(cached: FileContentCacheValue): { case: 'contents', contents: string | null } | { case: 'tooBig' } {
	switch (cached.case) {
		case 'string':
			return { case: 'contents', contents: cached.value };
		case 'null':
			return { case: 'contents', contents: null };
		case 'tooBig':
			return { case: 'tooBig' };
		default: {
			const _x: never = cached;
			throw new Error(`Invalid cache value: ${_x}`);
		}
	}
}

export class CommitTracker implements vscode.Disposable, ISpecificRequestTracker {

	private readonly disposables: vscode.Disposable[] = [];
	private repositories: Repository[] = [];

	private readonly fileContentCache = new LRUCache<string, FileContentCacheValue>({
		maxSize: 100 * 1024 * 1024, // 100MB
		sizeCalculation: (value) => {
			// lru cache forces this to be >= 1
			if (value.case === 'string') {
				return value.value.length + 1;
			} else {
				return 1;
			}
		},
	})

	track(metadata: StoredRequestTrackingMetadata): void {
		// Git repositories are automatically tracked via the Git extension API
		// in initializeGitExtension(), so no additional subscription is needed here
	}

	isDoneTracking(metadata: StoredRequestTrackingMetadata, config: OnlineMetricsConfig): boolean {
		return metadata.numCommitsTracked >= config.numCommitsTracked;
	}

	constructor(
		private readonly context: vscode.ExtensionContext,
		private readonly requestTracker: IRequestTracker,
		gitAPI: API | undefined,
	) {
		this.disposables.push(this.requestTracker.onDidFinishProcessingQueue(e => {
			// when the queue has finished processing, we can safely clear the cache!
			// that way, the 100mb extra memory is always just temporary
			this.fileContentCache.clear();
		}));

		if (gitAPI) {

			// Initialize Git extension
			// Shallow copy
			this.repositories = [...gitAPI.repositories];
			for (const repo of this.repositories) {
				this.subscribeToRepository(repo);
			}

			// Subscribe to repository changes
			this.disposables.push(gitAPI.onDidOpenRepository(repo => {
				if (this.repositories.some(r => r.rootUri.fsPath === repo.rootUri.fsPath)) {
					return;
				}
				this.repositories.push(repo);
				this.subscribeToRepository(repo);
			}));

			this.disposables.push(gitAPI.onDidCloseRepository(repo => {
				this.repositories = this.repositories.filter(r => r.rootUri.fsPath !== repo.rootUri.fsPath);
			}));

		}
	}

	private subscribeToRepository(repo: Repository) {
		// Subscribe to commit events
		this.disposables.push(repo.onDidCommit(() => {
			this.handleCommit(repo).catch(
				e => CursorDebugLogger.error('Failed to process commit', e)
			);
		}));
	}

	private async handleCommit(repo: Repository) {
		const commitDate = Date.now();
		const gitRoot = repo.rootUri.fsPath;
		const branch = repo.state.HEAD?.name || '';

		const gitRootToHead = new Map<string, {
			branch: string;
			commitHash: string;
		}>();

		const config = await this.requestTracker.getConfig();

		for (const [requestId, metadata] of this.requestTracker.requestTrackingCache) {
			if (this.isDoneTracking(metadata, config)) {
				continue;
			}

			let shouldSendSnapshot = false;
			for (const gitInfo of metadata.deduplicatedGitInfos) {
				if (gitInfo.info?.case === 'gitInfo' && gitInfo.info.value && typeof gitInfo.info.value === 'object' && 'gitRoot' in gitInfo.info.value && 'branch' in gitInfo.info.value) {
					if (gitInfo.info.value.gitRoot === gitRoot && gitInfo.info.value.branch === branch) {
						// let's send a snapshot for this request!
						shouldSendSnapshot = true;
						break;
					}
				}
			}
			if (!shouldSendSnapshot) {
				continue;
			}
			// get the head for each git root
			for (const gitInfo of metadata.deduplicatedGitInfos) {
				if (gitInfo.info?.case === 'gitInfo' && gitInfo.info.value && typeof gitInfo.info.value === 'object' && 'gitRoot' in gitInfo.info.value) {
					const gitRootPath = gitInfo.info.value.gitRoot as string;
					if (gitRootToHead.has(gitRootPath)) {
						continue;
					}
					// Use repository info from VSCode Git API
					const matchingRepo = this.repositories.find(r => r.rootUri.fsPath === gitRootPath);
					if (matchingRepo && matchingRepo.state.HEAD) {
						gitRootToHead.set(gitRootPath, {
							branch: matchingRepo.state.HEAD.name || '',
							commitHash: matchingRepo.state.HEAD.commit || ''
						});
					}
				}
			}

			// let's increment num commits tracked
			// note: there is not a race condition here, since we increment the metadata synchronously
			const thisCommit = metadata.numCommitsTracked + 1;
			metadata.numCommitsTracked = thisCommit;
			await this.requestTracker.persistRequestMetadata(requestId);
			// let's send a snapshot for this request!

			const gitInfos = new Map<string, PlainMessage<RequestTrackingFileGitInfo>>();
			for (const file of metadata.requestFiles) {
				gitInfos.set(file.fsPath, gitInfoFromGitRootToHead({
					gitRoot: file.gitInfo?.info?.case === 'gitInfo' ? file.gitInfo.info.value.gitRoot : null,
					gitRootToHead: gitRootToHead,
				}));
			}

			await this.requestTracker.queueSnapshot({
				requestId: requestId,
				name: `commit-${thisCommit}`,
				readFile: async (fsPath: string) => {
					const gitInfo = gitInfos.get(fsPath);
					if (gitInfo?.info?.case === 'gitInfo') {
						const commit = gitInfo.info.value.commitHash;
						const gitRoot = gitInfo.info.value.gitRoot;

						const relativePath = path.relative(gitRoot, fsPath);
						const cacheKey = `${gitRoot}-${relativePath}-${commit}`;
						const cached = this.fileContentCache.get(cacheKey);
						if (cached) {
							return cacheValueToReturnValue(cached);
						}
						// stat the file currently. if it is too big, we return too too big
						try {
							const stat = await fs.promises.stat(fsPath);
							if (stat.size > config.tooBigFileSizeBytes) {
								this.fileContentCache.set(cacheKey, { case: 'tooBig' });
								return { case: 'tooBig' };
							}
						} catch (e) {
							// ignore, maybe was deleted? it might still exist in git, so we don't return an error here
							CursorDebugLogger.error('Failed to stat file', e);
						}

						// get the contents!
						const value: FileContentCacheValue = await (async () => {
							try {
								// Use repository API to get file content at specific commit
								const matchingRepo = this.repositories.find(r => r.rootUri.fsPath === gitRoot);
								if (!matchingRepo) {
									return { case: 'null' };
								}
								const contents = await matchingRepo.show(commit, relativePath);
								if (contents === null || contents === undefined) {
									return { case: 'null' };
								}

								if (contents.length > config.tooBigFileSizeBytes) {
									return { case: 'tooBig' };
								}

								return { case: 'string', value: contents };
							} catch (e) {
								// if it fails, it most likely means the file is gitignore or something
								// we return null
								// note that this may mask actual problems such as `git` executable not existing
								// but for now this is fine
								return { case: 'null' };
							}
						})();
						this.fileContentCache.set(cacheKey, value);
						return cacheValueToReturnValue(value);
					}
					// file is not in git, then we return null
					return { case: 'contents', contents: null };
				},
				gitInfos: gitInfos,
				snapshotDateUnixMilliseconds: commitDate,
			});
		}
	}

	dispose() {
		for (const disposable of this.disposables) {
			disposable.dispose();
		}
	}
}