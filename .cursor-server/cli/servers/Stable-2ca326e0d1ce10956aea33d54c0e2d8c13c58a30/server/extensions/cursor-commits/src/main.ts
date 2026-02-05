import * as vscode from 'vscode';
import { CursorBugbotLogger, CursorDebugLogger } from './utils/logger.js';
import { DiffService } from './diffService.js';
import { BackendClientService } from './backendClient.js';
import { RequestTracker } from './onlineMetrics/requestTrackerImpl.js';
import { EverythingProvider, EverythingProviderArgs, ExtractArgs, ExtractReturn, GitActions } from '@cursor/types';
import { API, Branch, Commit, GitExtension, Repository } from '../../git/src/api/git.js';

type GitActionHandler = (args: ExtractArgs<GitActions.GetCurrentIndexAndRecentCommits>) => ExtractReturn<GitActions.GetCurrentIndexAndRecentCommits>;

const ACTION_REGISTRY: Partial<Record<GitActions, GitActionHandler>> = {};

function registerAction(name: GitActions, action: GitActionHandler): void {
	if (name in ACTION_REGISTRY) {
		throw new Error(`Action ${name} already registered`);
	}
	ACTION_REGISTRY[name] = action;
}

function getCommandFromRegistry(name: GitActions): GitActionHandler | undefined {
	return ACTION_REGISTRY[name];
}

type UriComponents = {
	scheme: string;
	authority?: string;
	path?: string;
	query?: string;
	fragment?: string;
};

async function getGitAPI(): Promise<API | undefined> {
	const gitExtensionWrapper = vscode.extensions.getExtension<GitExtension>('vscode.git');
	if (!gitExtensionWrapper) {
		CursorDebugLogger.warn('Git extension not found');
		return;
	}
	const gitExtension = gitExtensionWrapper.isActive ? gitExtensionWrapper.exports : await gitExtensionWrapper.activate();

	if (!gitExtension || !gitExtension.enabled) {
		CursorDebugLogger.warn('Git extension is not enabled');
		return undefined;
	}

	return gitExtension.getAPI(1);
}

async function registerGitIgnoreProvider(gitAPI: API, context: vscode.ExtensionContext): Promise<void> {
	const disposable = vscode.scm.registerGitIgnoreProvider({
		areIgnored: async (uris: (vscode.Uri | UriComponents)[]): Promise<boolean[]> => {
			if (uris.length === 0) {
				return [];
			}

			// Convert all URIs to vscode.Uri
			const vscodeUris: vscode.Uri[] = uris.map((uri) => {
				if (!(uri instanceof vscode.Uri)) {
					return vscode.Uri.from(uri);
				}
				return uri;
			});

			// Group URIs by repository
			// Repository type is from the git extension API
			type RepositoryInfo = { repo: Repository; uris: vscode.Uri[]; indices: number[] };
			const repoMap: Map<string, RepositoryInfo> = new Map<string, RepositoryInfo>();

			for (let i = 0; i < vscodeUris.length; i++) {
				const uri: vscode.Uri = vscodeUris[i];
				const repo = await gitAPI.openRepository(uri);
				if (!repo) {
					// Will be handled as not ignored
					continue;
				}

				const repoKey: string = repo.rootUri.toString();
				const existing = repoMap.get(repoKey);
				if (!existing) {
					repoMap.set(repoKey, { repo, uris: [uri], indices: [i] });
				} else {
					existing.uris.push(uri);
					existing.indices.push(i);
				}
			}

			// Initialize all results to false (not ignored)
			const results: boolean[] = new Array<boolean>(uris.length).fill(false);

			// Check each repository's files in batch
			const checkPromises = Array.from(repoMap.values()).map(async ({ repo, uris: repoUris, indices }) => {
				// checkIgnore requires file system paths (strings), not URI objects
				const filePaths: string[] = repoUris.map((uri) => uri.fsPath);
				const ignoredSet: Set<string> = await repo.checkIgnore(filePaths);

				// Update results for this repository's files
				for (let i = 0; i < repoUris.length; i++) {
					const filePath: string = filePaths[i];
					const originalIndex: number = indices[i];
					results[originalIndex] = ignoredSet.has(filePath);
				}
			});

			await Promise.all(checkPromises);
			return results;
		}
	});

	context.subscriptions.push(disposable);
}

async function shouldRunBugbot(gitAPI: API, repo: Repository, lastHead: Branch, lastRebaseAt: number | undefined): Promise<boolean> {
	const head = repo.state.HEAD;
	CursorBugbotLogger.debug(`shouldRunBugbot: head = ${head?.name}, lastHead = ${lastHead?.name}, lastRebaseAt = ${lastRebaseAt}`);

	if (head === undefined) {
		// no head state; we're probably detached
		CursorBugbotLogger.debug('shouldRunBugbot: no head state');
		return false;
	}

	if (head.name !== lastHead.name) {
		// checkout changed; this is not a user's commit
		CursorBugbotLogger.debug('shouldRunBugbot: checkout changed');
		return false;
	}

	if (head.commit === undefined || head.commit === lastHead.commit) {
		// commit is the same
		CursorBugbotLogger.debug('shouldRunBugbot: commit is the same');
		return false;
	}

	if (lastRebaseAt !== undefined && Math.abs(Date.now() - lastRebaseAt) < 10_000) {
		// if we've just finished rebasing the repository, we don't want to trigger a local bugbot run
		CursorBugbotLogger.debug('shouldRunBugbot: just finished rebasing');
		return false;
	}

	let commit: Commit;
	try {
		commit = await repo.getCommit(head.commit);
	} catch {
		CursorBugbotLogger.debug('shouldRunBugbot: failed to get commit');
		return false;
	}

	if (commit.parents.length > 1) {
		CursorBugbotLogger.debug('shouldRunBugbot: merge commit');
		return false;
	}

	let authoredByMeRecently = false;
	try {
		const committerIdentOutput = await gitAPI.rawGit.exec(repo.rootUri.fsPath, ['var', 'GIT_COMMITTER_IDENT']);
		const committerIdent = committerIdentOutput.stdout.trim();
		const mailmapOutput = await gitAPI.rawGit.exec(repo.rootUri.fsPath, ['check-mailmap', committerIdent]);
		const mailmap = mailmapOutput.stdout.trim();

		const expectedCommitterEmail = `${commit.authorName} <${commit.authorEmail}>`;

		CursorBugbotLogger.trace(`shouldRunBugbot: committer_ident = '${committerIdent}'`);
		CursorBugbotLogger.trace(`shouldRunBugbot: mailmap = '${mailmap}'`);
		CursorBugbotLogger.trace(`shouldRunBugbot: expected_committer_email = '${expectedCommitterEmail}'`);

		if (mailmap === expectedCommitterEmail && commit.commitDate !== undefined) {
			authoredByMeRecently = Math.abs(Date.now() - commit.commitDate.getTime()) < 30_000;
		}
	} catch (e) {
	}

	// if this is not our commit, we don't want to review it
	if (!authoredByMeRecently) {
		CursorBugbotLogger.debug('shouldRunBugBot: not authored by me recently');
		return false;
	}

	// Check if this commit exists in the origin;
	// anything that has already been pushed by the user should not trigger a local bugbot run
	try {
		const mergeBaseOutput = await gitAPI.rawGit.exec(repo.rootUri.fsPath, ['merge-base', '--is-ancestor', 'HEAD', '@{u}']);
		if (mergeBaseOutput.exitCode === 0) {
			CursorBugbotLogger.debug('shouldRun: commit has been pushed');
			return false;
		}
	} catch {
		// This is OK; it means the commit has not been pushed yet
	}

	CursorBugbotLogger.info('shouldRun: OK! Running local Agent Review on commit...');
	return true;
}

function setupBugbotAutoRun(gitAPI: API, context: vscode.ExtensionContext): void {
	const afterCommitDebounceDelay = 5 * 1000; // 5 seconds
	const repoSubscriptions = new Map<Repository, vscode.Disposable>();
	const subscribe = (repo: Repository) => {
		let lastHead: Branch | undefined = repo.state.HEAD;
		let pending: NodeJS.Timeout | undefined = undefined;
		let lastRebaseAt: number | undefined = undefined;

		const existing = repoSubscriptions.get(repo);
		if (existing) {
			existing.dispose();
		}

		const dispState = repo.state.onDidChange(() => {
			if (pending !== undefined) {
				clearTimeout(pending);
				pending = undefined;
			}

			if (repo.state.rebaseCommit !== undefined) {
				lastRebaseAt = Date.now();
			}

			pending = setTimeout(async () => {
				pending = undefined;

				if (lastHead !== undefined) {
					if (await shouldRunBugbot(gitAPI, repo, lastHead, lastRebaseAt)) {
						void vscode.commands.executeCommand('cursor.runEditorBugbot', repo.rootUri, repo.state.HEAD?.commit);
					}
				}

				// Trigger commit scoring when a new commit is detected (not when switching branches)
				const currentHead = repo.state.HEAD;
				// Only trigger if commit hash changed AND branch name is the same (indicating a new commit, not a branch switch)
				// Explicitly check that both branch names are defined to avoid triggering in detached HEAD state
				if (currentHead?.commit &&
					lastHead?.commit !== currentHead.commit &&
					currentHead.name !== undefined &&
					lastHead?.name !== undefined &&
					currentHead.name === lastHead.name) {
					const commandPromise = vscode.commands.executeCommand('developer.aiCodeTracking.scoreCommitInternal', currentHead.commit, repo.rootUri.fsPath, { report: true });
					// Handle Thenable properly
					if (commandPromise && typeof (commandPromise as Promise<void>).then === 'function') {
						(commandPromise as Promise<void>).then(
							() => {},
							(error) => {
								CursorDebugLogger.error('Failed to trigger commit scoring', error);
							}
						);
					}
				}

				lastHead = repo.state.HEAD;
			}, afterCommitDebounceDelay);
		});

		repoSubscriptions.set(repo, dispState);
	};

	for (const repo of gitAPI.repositories) {
		subscribe(repo);
	}
	context.subscriptions.push(
		gitAPI.onDidOpenRepository((repo) => {
			subscribe(repo);
		}),
		gitAPI.onDidCloseRepository((repo) => {
			const disp = repoSubscriptions.get(repo);
			if (disp) {
				disp.dispose();
				repoSubscriptions.delete(repo);
			}
		}),
		{ dispose: () => repoSubscriptions.forEach(d => d.dispose()) }
	);
}

let _cursorExtensionsIsolationEnabled: Promise<boolean> | undefined;
function getCursorExtensionsIsolationEnabled(): Promise<boolean> {
	if (_cursorExtensionsIsolationEnabled === undefined) {
		_cursorExtensionsIsolationEnabled = Promise.resolve(vscode.cursor.getCursorExtensionsIsolationEnabled()).catch(() => false);
	}
	return _cursorExtensionsIsolationEnabled;
}

export async function activate(context: vscode.ExtensionContext): Promise<void> {
	const extensionIsolationEnabled = await getCursorExtensionsIsolationEnabled();
	if (!extensionIsolationEnabled) {
		// This is not necessary. The activate() function will never be called if extension isolation is enabled.
		// But to make bugbot and agents happy we add this check.
		return;
	}

	let gitAPI: API | undefined;
	try {
		gitAPI = await getGitAPI();
	} catch (e) {
		CursorDebugLogger.error('Failed to get Git API', e);
	}

	CursorBugbotLogger.init();
	if (context.isDevelopment) {
		CursorDebugLogger.init();
	}

	const supportedCommands = Object.keys(ACTION_REGISTRY).filter(
		(cmd): cmd is EverythingProviderArgs['name'] => true
	);

	const everythingProvider: EverythingProvider = {
		supportedCommands,
		// @ts-ignore (Needed for gulpfile building only)
		runCommand: <K extends EverythingProviderArgs['name']>(commandName: K, args: ExtractArgs<K>): ExtractReturn<K> | Promise<undefined> => {
			if (commandName === GitActions.GetCurrentIndexAndRecentCommits) {
				const command = getCommandFromRegistry(GitActions.GetCurrentIndexAndRecentCommits);
				if (command !== undefined) {
					// @ts-ignore
					return command(args as ExtractArgs<GitActions.GetCurrentIndexAndRecentCommits>) as ExtractReturn<K>;
				}
			}
			return Promise.resolve(undefined);
		}
	};
	context.subscriptions.push(vscode.cursor.registerEverythingProvider(everythingProvider));

	if (gitAPI) {
		try {
			await registerGitIgnoreProvider(gitAPI, context);
		} catch (e) {
			CursorDebugLogger.error('Failed to register git ignore provider', e);
		}
	}

	const diffService = new DiffService(context);
	context.subscriptions.push(diffService);

	const backendClientService = new BackendClientService(context);
	context.subscriptions.push(backendClientService);

	const requestTracker = new RequestTracker(context, diffService, backendClientService, gitAPI);
	context.subscriptions.push(requestTracker);

	if (gitAPI) {
		setupBugbotAutoRun(gitAPI, context);
	}
}

export function deactivate(): void {
}

registerAction(GitActions.GetCurrentIndexAndRecentCommits, async ({ rootPath, rawUris }) => {
	// Git doesn't care about paths being "/" vs "\", so we just use .path instead of .fsPath
	const gitExtension = vscode.extensions.getExtension<GitExtension>('vscode.git');
	if (gitExtension === undefined) {
		throw new Error('Git extension not found');
	}
	const extension = await gitExtension.activate();
	const api = extension.getAPI(1);

	const repos = api.repositories
	const desiredRepo = repos.find(repo => repo.rootUri.path === rootPath);
	if (!desiredRepo) {
		throw new Error('No repository found');
	}

	if (!rootPath.endsWith('/')) {
		rootPath += '/';
	}

	const hasHead = await desiredRepo.getCommit('HEAD').then(commit => true).catch(() => false);
	const relativePaths = rawUris.map(rawUri => vscode.Uri.parse(rawUri).path.substring(rootPath.length));

	const empty = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"; // This is the empty tree SHA // pragma: allowlist secret
	const diffs = hasHead ? (await Promise.all(relativePaths.map(path => desiredRepo.diffWith('HEAD', path)))) : (await Promise.all(relativePaths.map(path => desiredRepo.diffWith(empty, path))));

	const previousCommitMessages = hasHead ? (await desiredRepo.log({ maxEntries: 10 })) : [];

	return { diffs, previousCommitMessages: previousCommitMessages.map(commit => commit.message) };
});

