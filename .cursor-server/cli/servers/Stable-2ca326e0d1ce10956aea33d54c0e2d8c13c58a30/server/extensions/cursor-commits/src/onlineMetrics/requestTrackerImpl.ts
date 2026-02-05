import * as vscode from 'vscode';
import * as path from 'path';
import * as fs from 'fs';
import { ReportAgentSnapshotRequest, RequestTrackingFileGitInfo, RequestTrackingFileSnapshot, RequestTrackingFileSnapshot_DiffChange, RequestTrackingFileSnapshot_Kind, StoredRequestTrackingMetadata, StoredRequestTrackingMetadata_File } from 'proto/aiserver/v1/online_metrics_pb.js';
import { ConfigServiceActions, START_TRACKING_REQUEST_ACTION_ID, StartTrackingRequestArgs } from '@cursor/types';
import { CursorDebugLogger } from '../utils/logger.js';
import { PlainMessage } from '@bufbuild/protobuf';
import { generateUuid } from '../utils/uuid.js';
import { DiffService } from '../diffService.js';
import { ComputeLinesDiffResponse } from '../worker/worker.api.js';
import { GetServerConfigResponse } from 'proto/aiserver/v1/server_config_pb.js';
import { OnlineMetricsConfig } from 'proto/aiserver/v1/online_metrics_pb.js';
import { BackendClientService } from '../backendClient.js';
import { gitInfoFromGitRootToHead, IRequestTracker, ISpecificRequestTracker, ProcessSnapshotArgs } from './requestTracker.js';
import { CommitTracker } from './commitTracker.js';
import { getTracingHeaders } from '../utils/requests.js';
import { TimeTracker } from './timeTracker.js';
import { API } from '../../../git/src/api/git.js';

function getLines(s: string | null): string[] {
	if (s === null) {
		return [];
	}
	return s.split('\n').map(line => line.endsWith('\r') ? line.slice(0, -1) : line);
}

export class RequestTracker implements vscode.Disposable, IRequestTracker {

	readonly requestTrackingCache = new Map<string, StoredRequestTrackingMetadata>();
	readonly specificRequestTrackers: ISpecificRequestTracker[] = [];

	private readonly onDidFinishProcessingQueueEmitter = new vscode.EventEmitter<void>();
	readonly onDidFinishProcessingQueue = this.onDidFinishProcessingQueueEmitter.event;

	private readonly disposables: vscode.Disposable[] = [];

	constructor(
		private readonly context: vscode.ExtensionContext,
		private readonly diffService: DiffService,
		private readonly backendClientService: BackendClientService,
		private readonly gitAPI: API | undefined,
	) {
		this.disposables.push(vscode.commands.registerCommand(START_TRACKING_REQUEST_ACTION_ID, (args: StartTrackingRequestArgs) => {
			void this.startTrackingRequest(args).catch(e => {
				CursorDebugLogger.error('Failed to start tracking request', e);
			});
		}));

		// track based on git commits!
		this.specificRequestTrackers.push(new CommitTracker(this.context, this, this.gitAPI));
		// rl-5 generalized
		this.specificRequestTrackers.push(new TimeTracker(this.context, this));

		this.loadCache().catch(e => {
			CursorDebugLogger.error('Failed to load cache', e);
		});
	}

	private async loadCache() {
		const config = await this.getConfig();
		const storagePath = this.globalStoragePath();
		if (await fs.promises.stat(storagePath).then(s => s.isDirectory()).catch(e => false)) {
			const metadatas: StoredRequestTrackingMetadata[] = [];
			const files = await fs.promises.readdir(storagePath, { withFileTypes: true });
			for (const file of files) {
				if (file.isDirectory()) {
					try {
						const metadataFile = path.join(storagePath, file.name, 'metadata.json');
						const metadataJson = await fs.promises.readFile(metadataFile, 'utf8');
						const metadata = StoredRequestTrackingMetadata.fromJsonString(metadataJson);
						metadatas.push(metadata);
					} catch (e) {
						// if we can't read it, purge it
						await fs.promises.rm(path.join(storagePath, file.name), { recursive: true, force: true });
					}
				}
			}
			// delete globally
			const toDelete = await this.getRequestIdsToPurge(metadatas);
			// also delete any requests that don't have a workspace id (we can get into weird things with no workspace id since the request may be in multiple windows caches)
			toDelete.push(...metadatas.filter(m => m.workspaceId.length === 0).map(m => m.agentRequestId));
			for (const requestId of toDelete) {
				await this.deleteRequest(requestId);
			}
			// then, load in all metadatas for this workspace
			for (const metadata of metadatas) {
				if (metadata.workspaceId === vscode.cursor.workspaceId()) {
					this.requestTrackingCache.set(metadata.agentRequestId, metadata);
				}
			}
		}
		// now, for each metadata, we should track
		for (const metadata of this.requestTrackingCache.values()) {
			for (const tracker of this.specificRequestTrackers) {
				tracker.track(metadata, config);
			}
		}
	}

	private async computeDiff(originalLines: string[], modifiedLines: string[], tokenizedLines: Map<string, number>): Promise<{
		timedOut: boolean;
		changes: PlainMessage<RequestTrackingFileSnapshot_DiffChange>[];
	}> {
		const result = await this.diffService.computeLinesDiff({
			original: originalLines,
			modified: modifiedLines,
			ignoreTrimWhitespace: true,
			// we use max computation time 500 milliseconds here since we are in a worker thread
			maxComputationTimeMs: 500,
			// we skip diff refinement since we don't really need it (we only care about line-level diffs)
			// this will save cpu time
			skipDiffRefinement: true,
		});

		// we add 1M here just to make things easier to view.
		let currentToken = Math.max(0, ...tokenizedLines.values()) + 1000000;

		return {
			timedOut: result.timedOut,
			changes: result.changes.map(c => ({
				originalEndLineNumberExclusiveOneIndexed: c.originalRange.endLineNumberExclusiveOneIndexed,
				originalStartLineNumberOneIndexed: c.originalRange.startLineNumberOneIndexed,
				modifiedEndLineNumberExclusiveOneIndexed: c.modifiedRange.endLineNumberExclusiveOneIndexed,
				modifiedStartLineNumberOneIndexed: c.modifiedRange.startLineNumberOneIndexed,
				addedLines: modifiedLines.slice(c.modifiedRange.startLineNumberOneIndexed - 1, c.modifiedRange.endLineNumberExclusiveOneIndexed - 1),
				tokenizedAddedLines: (() => {
					const result: number[] = [];
					for (let i = c.modifiedRange.startLineNumberOneIndexed - 1; i < c.modifiedRange.endLineNumberExclusiveOneIndexed - 1; i++) {
						const line = modifiedLines[i];
						const token = tokenizedLines.get(line);
						if (token !== undefined) {
							result.push(token);
						} else {
							tokenizedLines.set(line, currentToken);
							result.push(currentToken);
							currentToken++;
						}
					}
					return result;
				})()
			})),
		}

	}

	globalStoragePath() {
		return path.join(this.context.globalStoragePath, 'checkpoints');
	}
	storagePath(requestId: string) {
		return path.join(this.globalStoragePath(), requestId);
	}


	private configCache: { value: OnlineMetricsConfig; expiresAt: number } | undefined;

	async getConfig(): Promise<OnlineMetricsConfig> {
		// we cache the config to reduce exthost ipc calls
		const now: number = Date.now();
		const cacheDurationMs: number = 5 * 60 * 1000; // 5 minutes

		if (this.configCache !== undefined && this.configCache.expiresAt > now) {
			return this.configCache.value;
		}

		const config: GetServerConfigResponse | undefined = await vscode.commands.executeCommand(
			ConfigServiceActions.GetCachedServerConfig
		);
		const onlineMetricsConfig: OnlineMetricsConfig = config?.onlineMetricsConfig ?? new OnlineMetricsConfig({});
		this.configCache = {
			value: onlineMetricsConfig,
			expiresAt: now + cacheDurationMs,
		};
		return onlineMetricsConfig;
	}

	async getGitInfos(fsPaths: string[]): Promise<Map<string, PlainMessage<RequestTrackingFileGitInfo>>> {
		const fsPathAndGitRoot: {
			fsPath: string;
			gitRoot: string | null;
		}[] = [];
		const gitRoots = new Set<string>();
		for (const fsPath of fsPaths) {
			const gitRoot = this.gitAPI?.getRepository(vscode.Uri.file(fsPath))?.rootUri.fsPath ?? null;
			fsPathAndGitRoot.push({
				fsPath: fsPath,
				gitRoot: gitRoot,
			});
			if (gitRoot !== null) {
				gitRoots.add(gitRoot);
			}
		}

		const gitRootToHead = new Map<string, {
			branch: string;
			commitHash: string;
		}>();
		for (const gitRoot of gitRoots) {
			try {
				const head = this.gitAPI?.getRepository(vscode.Uri.file(gitRoot))?.state.HEAD;
				if (head?.name && head.commit) {
					gitRootToHead.set(gitRoot, {
						branch: head.name,
						commitHash: head.commit,
					});
				}
			} catch (e) {
				CursorDebugLogger.warn(`Failed to get head for git root ${gitRoot}`, e);
			}
		}

		const result = new Map<string, PlainMessage<RequestTrackingFileGitInfo>>();
		for (const { fsPath, gitRoot } of fsPathAndGitRoot) {
			result.set(fsPath, gitInfoFromGitRootToHead({
				gitRoot: gitRoot,
				gitRootToHead: gitRootToHead,
			}));
		}

		return result;
	}


	async startTrackingRequest(args: StartTrackingRequestArgs): Promise<void> {
		// if privacy mode is enabled, we should not track anything!
		if (vscode.cursor.getPrivacyMode() !== false) {
			return;
		}

		// for question-only requests, we don't need to track anything for now
		if (args.files.length === 0) {
			return;
		}

		const snapshotDate = Date.now();

		const config = await this.getConfig();

		await this.maybeCleanStorage();

		// we immediately get the git info for the files
		const gitInfos = await this.getGitInfos(args.files.map(f => f.fsPath));

		const storagePath = this.storagePath(args.requestId);
		// just use fs stuff
		await fs.promises.mkdir(storagePath, { recursive: true });

		const filesStoragePath = path.join(storagePath, 'files');
		await fs.promises.mkdir(filesStoragePath, { recursive: true });

		const diffsStoragePath = path.join(storagePath, 'diffs');
		await fs.promises.mkdir(diffsStoragePath, { recursive: true });

		const requestFiles: PlainMessage<StoredRequestTrackingMetadata_File>[] = [];

		let fileSizeBytes = 0;

		for (const file of args.files) {
			const fileUuid = generateUuid();

			if (file.tooBig) {
				requestFiles.push({
					fsPath: file.fsPath,
					fileUuid: fileUuid,
					gitInfo: gitInfos.get(file.fsPath),
					tooBig: true,
				})
				continue;
			}

			const fileUri = path.join(filesStoragePath, fileUuid);
			if (file.startContents !== null) {
				await fs.promises.writeFile(fileUri, file.startContents);
				fileSizeBytes += file.startContents?.length ?? 0;
			}

			const oldLines = getLines(file.startContents);
			const tokenizedLines: Map<string, number> = new Map();
			let token = 1;
			for (let i = 0; i < oldLines.length; i++) {
				const line = oldLines[i];
				if (!tokenizedLines.has(line)) {
					tokenizedLines.set(line, token);
					token++;
				}
			}
			const newLines = getLines(file.endContents);
			const diff = await this.computeDiff(oldLines, newLines, tokenizedLines);
			const newSnapshot: PlainMessage<RequestTrackingFileSnapshot> = {
				fsPath: file.fsPath,
				fileUuid: fileUuid,
				fileSizeBytes: file.endContents?.length ?? 0,
				numLines: newLines.length,
				kind: file.startContents === null ? RequestTrackingFileSnapshot_Kind.ADDED : file.endContents === null ? RequestTrackingFileSnapshot_Kind.DELETED : RequestTrackingFileSnapshot_Kind.MODIFIED,
				diffTimedOut: diff.timedOut,
				diffChanges: diff.changes,
				gitInfo: gitInfos.get(file.fsPath),
			}

			const diffUri = path.join(diffsStoragePath, fileUuid);
			const diffJson = new RequestTrackingFileSnapshot(newSnapshot).toJsonString();
			await fs.promises.writeFile(diffUri, diffJson);
			fileSizeBytes += diffJson.length;

			requestFiles.push({
				fsPath: file.fsPath,
				fileUuid: fileUuid,
				gitInfo: gitInfos.get(file.fsPath),
				tooBig: false,
			})
		}

		const deduplicatedGitInfos: Map<string, PlainMessage<RequestTrackingFileGitInfo>> = new Map();
		for (const gitInfo of gitInfos.values()) {
			if (gitInfo.info?.case === 'gitInfo') {
				deduplicatedGitInfos.set(gitInfo.info.value.gitRoot, gitInfo);
			}
		}

		const metadataRaw: PlainMessage<StoredRequestTrackingMetadata> = {
			agentRequestId: args.requestId,
			requestFiles: requestFiles,
			deduplicatedGitInfos: Array.from(deduplicatedGitInfos.values()),
			numCommitsTracked: 0,
			startTrackingDateUnixMilliseconds: snapshotDate,
			fileSizeBytes: fileSizeBytes,
			workspaceId: vscode.cursor.workspaceId() ?? '',
		}
		const metadata = new StoredRequestTrackingMetadata(metadataRaw);

		// store the metadata
		await fs.promises.writeFile(path.join(storagePath, 'metadata.json'), metadata.toJsonString());

		// insert into the cache
		this.requestTrackingCache.set(args.requestId, metadata);

		// send initial snapshot
		await this.queueSnapshot({
			requestId: args.requestId,
			name: 'initial',
			readFile: async (fsPath: string) => {
				// for the initial snapshot, we just use the end contents!
				const file = args.files.find(f => f.fsPath === fsPath);
				if (!file) {
					// this shouldn't really happen.... since we should only try to send files in the metadata
					// we log an error and return null
					CursorDebugLogger.error(`File ${fsPath} not found in args.files. Should not happen!`);
					return { case: 'contents', contents: null };
				}
				return { case: 'contents', contents: file.endContents };
			},
			gitInfos: gitInfos,
			snapshotDateUnixMilliseconds: snapshotDate,
		});

		// now, we should subscribe to git roots
		for (const tracker of this.specificRequestTrackers) {
			tracker.track(metadata, config);
		}
	}

	private async deleteRequest(requestId: string) {
		try {
			const storagePath = this.storagePath(requestId);
			await fs.promises.rm(storagePath, { recursive: true, force: true });
			this.requestTrackingCache.delete(requestId);
		} catch (e) {
			CursorDebugLogger.error(`Failed to delete request ${requestId}`, e);
		}
	}

	private async getRequestIdsToPurge(metadatas: StoredRequestTrackingMetadata[]): Promise<string[]> {
		const config = await this.getConfig();
		const toDelete: string[] = [];

		let totalSizeBytes = 0;

		const requestIdsSorted: {
			requestId: string;
			date: number;
			sizeBytes: number;
		}[] = [];

		for (const metadata of metadatas) {
			if (Date.now() - metadata.startTrackingDateUnixMilliseconds > config.maxRequestRetentionSeconds * 1000) {
				// this request is too old!
				toDelete.push(metadata.agentRequestId);
				continue;
			}
			if (this.specificRequestTrackers.every(t => t.isDoneTracking(metadata, config))) {
				// this request is done tracking!
				// let's delete it
				toDelete.push(metadata.agentRequestId);
				continue;
			}
			totalSizeBytes += metadata.fileSizeBytes;
			requestIdsSorted.push({
				requestId: metadata.agentRequestId,
				date: metadata.startTrackingDateUnixMilliseconds,
				sizeBytes: metadata.fileSizeBytes,
			});
		}

		if (requestIdsSorted.length > config.maxRequestsTracked || totalSizeBytes > config.maxRequestsTrackedMb * 1024 * 1024) {
			// we should sort by date
			requestIdsSorted.sort((a, b) => a.date - b.date);
			// now, we should delete the oldest requests until we are in a good place
			for (let i = 0; i < requestIdsSorted.length - config.maxRequestsTracked; i++) {
				toDelete.push(requestIdsSorted[i].requestId);
				totalSizeBytes -= requestIdsSorted[i].sizeBytes;
			}
			while (totalSizeBytes > config.maxRequestsTrackedMb * 1024 * 1024) {
				const r = requestIdsSorted.shift();
				if (r === undefined) {
					break;
				}
				totalSizeBytes -= r.sizeBytes;
				toDelete.push(r.requestId);
			}
		}
		return toDelete;
	}

	private async maybeCleanStorage() {
		const toDelete = await this.getRequestIdsToPurge(Array.from(this.requestTrackingCache.values()));
		for (const requestId of toDelete) {
			await this.deleteRequest(requestId);
		}
	}

	private readonly queue: ProcessSnapshotArgs[] = [];
	async queueSnapshot(args: ProcessSnapshotArgs): Promise<void> {
		// we put all snapshot requests on a global queue to prevent overloading
		// we allow at most 2000 on the queue; otherwise we start dropping
		this.queue.push(args);
		while (this.queue.length > 2000) {
			// we drop the oldest request
			this.queue.shift();
		}
		// make sure we process the next one
		this.processQueue();
	}

	private isQueueProcessing = false;
	private processQueue() {
		if (this.isQueueProcessing) {
			return;
		}
		(async () => {
			if (this.queue.length === 0) {
				this.onDidFinishProcessingQueueEmitter.fire();
				return;
			}
			this.isQueueProcessing = true;
			const requestId = generateUuid();
			try {
				const args = this.queue.shift();
				if (args === undefined) {
					return;
				}
				await this.sendSnapshot(args, requestId);
			} catch (e) {
				CursorDebugLogger.error(`Failed to process queue element ${requestId}, continuing`, e);
			} finally {
				this.isQueueProcessing = false;
				// keep processing the queue!
				this.processQueue();
			}
		})().catch(e => {
			CursorDebugLogger.error('Failed to process queue', e);
		});
	}

	async persistRequestMetadata(requestId: string): Promise<void> {
		const metadata = this.requestTrackingCache.get(requestId);
		if (metadata === undefined) {
			return;
		}
		const storagePath = this.storagePath(requestId);
		// only persist if the path still exists
		if (await fs.promises.stat(storagePath).then(s => s.isDirectory()).catch(e => false)) {
			await fs.promises.writeFile(path.join(storagePath, 'metadata.json'), metadata.toJsonString());
		}
	}

	private async sendSnapshot(args: ProcessSnapshotArgs, requestId: string) {
		const config = await this.getConfig();
		if (vscode.cursor.getPrivacyMode() !== false) {
			return;
		}
		if (!config.enabled) {
			return;
		}
		CursorDebugLogger.debug("Processing request", {
			requestId: args.requestId,
			name: args.name,
		});

		const metadata = await this.getRequestMetadata(args.requestId);

		const newFiles: {
			fsPath: string;
			contents: string | null;
			sizeBytes: number;
		}[] = [];

		const tooBigFiles: Set<string> = new Set();
		for (const file of metadata.requestFiles) {
			if (file.tooBig) {
				tooBigFiles.add(file.fsPath);
			}
		}

		// we read the files first so we get them as fresh as possible
		for (const file of metadata.requestFiles) {
			if (tooBigFiles.has(file.fsPath)) {
				continue;
			}
			const contents = await args.readFile(file.fsPath);
			if (contents.case === 'tooBig') {
				tooBigFiles.add(file.fsPath);
				continue;
			}
			newFiles.push({
				fsPath: file.fsPath,
				contents: contents.contents,
				// for now we estimate bytes as length of string
				sizeBytes: contents.contents ? contents.contents.length : 0,
			});
		}

		// now we compute the diffs
		const fileSnapshots: PlainMessage<RequestTrackingFileSnapshot>[] = [];
		const initialFileSnapshots: PlainMessage<RequestTrackingFileSnapshot>[] = [];

		for (const file of metadata.requestFiles) {
			if (tooBigFiles.has(file.fsPath)) {
				continue;
			}
			// important that oldSnapshot is a new object and not shared!
			// if it were shared, the mutation that we're doing later would cause problems
			const oldSnapshot = await (async () => {
				const fileUri = path.join(this.storagePath(args.requestId), 'diffs', file.fileUuid);
				const contents = await fs.promises.readFile(fileUri, 'utf8');
				return RequestTrackingFileSnapshot.fromJsonString(contents);
			})();

			const oldFile = await (async () => {
				if (oldSnapshot.kind === RequestTrackingFileSnapshot_Kind.ADDED) {
					return null;
				}
				const fileUri = path.join(this.storagePath(args.requestId), 'files', file.fileUuid);
				const contents = await fs.promises.readFile(fileUri, 'utf8');
				return contents;
			})();

			const newFile = newFiles.find(f => f.fsPath === file.fsPath);
			if (newFile === undefined) {
				// this should never happen!
				CursorDebugLogger.error(`File ${file.fsPath} not found in newFiles. Should not happen!`);
				continue;
			}

			const newLines = getLines(newFile.contents);
			const oldLines = getLines(oldFile);


			const tokenizedLines: Map<string, number> = new Map();
			let token = 1;
			for (let i = 0; i < oldLines.length; i++) {
				const line = oldLines[i];
				if (!tokenizedLines.has(line)) {
					tokenizedLines.set(line, token);
					token++;
				}
			}
			for (const change of oldSnapshot.diffChanges) {
				for (let i = 0; i < change.tokenizedAddedLines.length; i++) {
					const token = change.tokenizedAddedLines.at(i);
					const line = change.addedLines.at(i);
					if (line !== undefined && token !== undefined) {
						tokenizedLines.set(line, token);
					}
				}
			}

			const newDiff = await this.computeDiff(oldLines, newLines, tokenizedLines);

			const newSnapshot: PlainMessage<RequestTrackingFileSnapshot> = {
				fsPath: file.fsPath,
				fileUuid: file.fileUuid,
				fileSizeBytes: newFile.sizeBytes,
				numLines: newLines.length,
				diffTimedOut: newDiff.timedOut,
				diffChanges: newDiff.changes,
				kind: newLines.length === 0 ? RequestTrackingFileSnapshot_Kind.DELETED : oldLines.length === 0 ? RequestTrackingFileSnapshot_Kind.ADDED : RequestTrackingFileSnapshot_Kind.MODIFIED,
				gitInfo: args.gitInfos.get(file.fsPath),
			}

			if (!config.sendFullAddedLinesInDiffChanges) {
				// clean out the full added lines from both!
				for (const change of newSnapshot.diffChanges) {
					change.addedLines = [];
				}
				for (const change of oldSnapshot.diffChanges) {
					change.addedLines = [];
				}
			}
			if (config.sendOriginalFileContentsForInitialSnapshot && args.name === "initial") {
				oldSnapshot.originalFileContents = oldFile ?? undefined;
			}

			fileSnapshots.push(newSnapshot);
			initialFileSnapshots.push(oldSnapshot);

		}

		const requestSnapshotRaw: PlainMessage<ReportAgentSnapshotRequest> = {
			agentRequestId: metadata.agentRequestId,
			fileSnapshots: fileSnapshots,
			initialFileSnapshots: initialFileSnapshots,
			name: args.name,
			snapshotDateUnixMilliseconds: args.snapshotDateUnixMilliseconds,
			tooBigFiles: Array.from(tooBigFiles),
		}

		const requestSnapshot = new ReportAgentSnapshotRequest(requestSnapshotRaw);

		const client = await this.backendClientService.getOnlineMetricsClient();

		// check privacy mode again, just in case
		if (vscode.cursor.getPrivacyMode() !== false) {
			return;
		}

		await client.reportAgentSnapshot(requestSnapshot, {
			headers: getTracingHeaders(requestId),
		});
	}

	// NOTE: this may throw!!!
	private async getRequestMetadata(requestId: string): Promise<StoredRequestTrackingMetadata> {
		// first try to get from the cache
		const metadata = this.requestTrackingCache.get(requestId);
		if (metadata) {
			return metadata;
		}

		// then try to get from the file
		const metadataFile = path.join(this.storagePath(requestId), 'metadata.json');
		const metadataJson = await fs.promises.readFile(metadataFile, 'utf8');
		const metadataPure = StoredRequestTrackingMetadata.fromJsonString(metadataJson);
		this.requestTrackingCache.set(requestId, metadataPure);
		return metadataPure;
	}

	dispose() {
		this.requestTrackingCache.clear();
		for (const disposable of this.disposables) {
			disposable.dispose();
		}
		for (const disposable of this.specificRequestTrackers) {
			disposable.dispose();
		}
	}
}


