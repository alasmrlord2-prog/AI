import { PlainMessage } from '@bufbuild/protobuf';
import { RequestTrackingFileGitInfo, StoredRequestTrackingMetadata } from 'proto/aiserver/v1/online_metrics_pb.js';
import * as vscode from 'vscode';
import { OnlineMetricsConfig } from 'proto/aiserver/v1/online_metrics_pb.js';


export interface IRequestTracker {
	readonly requestTrackingCache: Map<string, StoredRequestTrackingMetadata>;
	getConfig(): Promise<OnlineMetricsConfig>;
	persistRequestMetadata(requestId: string): Promise<void>;
	getGitInfos(fsPaths: string[]): Promise<Map<string, PlainMessage<RequestTrackingFileGitInfo>>>;

	// queues up a snapshot to be sent
	// the snapshot may not be sent immediately, but will be sent eventually
	queueSnapshot(args: ProcessSnapshotArgs): Promise<void>;

	onDidFinishProcessingQueue: vscode.Event<void>;
}

export type ProcessSnapshotArgs = {
	requestId: string;
	name: string;
	readFile: (fsPath: string) => Promise<{ case: 'contents', contents: string | null } | { case: 'tooBig' }>;
	gitInfos: Map<string, PlainMessage<RequestTrackingFileGitInfo>>
	snapshotDateUnixMilliseconds: number;
}

export interface ISpecificRequestTracker extends vscode.Disposable {
	track(metadata: StoredRequestTrackingMetadata, config: OnlineMetricsConfig): void;
	isDoneTracking(metadata: StoredRequestTrackingMetadata, config: OnlineMetricsConfig): boolean;
}



export function gitInfoFromGitRootToHead({
	gitRoot,
	gitRootToHead,
}: {
	gitRoot: string | null;
	gitRootToHead: Map<string, {
		branch: string;
		commitHash: string;
	}>;
}): PlainMessage<RequestTrackingFileGitInfo> {
	if (gitRoot === null) {
		return {
			info: {
				case: 'noRepoFound',
				value: true,
			}
		};
	} else {
		return {
			info: {
				case: 'gitInfo',
				value: {
					gitRoot: gitRoot,
					branch: gitRootToHead.get(gitRoot)?.branch ?? '',
					commitHash: gitRootToHead.get(gitRoot)?.commitHash ?? '',
				}
			}
		};
	}
}