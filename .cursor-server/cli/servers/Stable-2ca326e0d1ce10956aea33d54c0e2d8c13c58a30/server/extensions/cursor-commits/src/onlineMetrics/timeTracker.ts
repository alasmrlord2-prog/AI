import * as vscode from 'vscode';
import { IRequestTracker, ISpecificRequestTracker } from './requestTracker.js';
import { CursorDebugLogger } from '../utils/logger.js';
import { StoredRequestTrackingMetadata } from 'proto/aiserver/v1/online_metrics_pb.js';
import { OnlineMetricsConfig } from 'proto/aiserver/v1/online_metrics_pb.js';
import * as fs from 'node:fs';

export class TimeTracker implements vscode.Disposable, ISpecificRequestTracker {

	private readonly disposables: vscode.Disposable[] = [];

	track(metadata: StoredRequestTrackingMetadata, config: OnlineMetricsConfig): void {
		for (const intervalMinutes of config.timeIntervalsTrackedMinutes) {
			const remainingTimeMs = 1000 * 60 * intervalMinutes - (Date.now() - metadata.startTrackingDateUnixMilliseconds);
			if (remainingTimeMs > 0) {
				setTimeout(async () => {
					try {
						this.requestTracker.queueSnapshot({
							requestId: metadata.agentRequestId,
							name: `time-${intervalMinutes}`,
							readFile: async (fsPath) => {
								// read the file
								try {
									// stat first to get file size
									const stat = await fs.promises.stat(fsPath);
									if (stat.size > config.tooBigFileSizeBytes) {
										return { case: 'tooBig' };
									}
									const contents = await fs.promises.readFile(fsPath, 'utf8');
									return { case: 'contents', contents: contents };
								} catch (e) {
									// probably file doesn't exist
									return { case: 'contents', contents: null };
								}
							},
							gitInfos: await this.requestTracker.getGitInfos(metadata.requestFiles.map(f => f.fsPath)),
							snapshotDateUnixMilliseconds: Date.now(),
						});
					} catch (e) {
						CursorDebugLogger.error('Failed to queue rl-5 snapshot', e);
					}
				}, remainingTimeMs);
			}
		}
	}

	isDoneTracking(metadata: StoredRequestTrackingMetadata, config: OnlineMetricsConfig): boolean {
		const maxTime = Math.max(...config.timeIntervalsTrackedMinutes);
		const timeSinceStart = (Date.now() - metadata.startTrackingDateUnixMilliseconds);
		return timeSinceStart >= maxTime * 1000 * 60;
	}

	constructor(
		private readonly context: vscode.ExtensionContext,
		private readonly requestTracker: IRequestTracker,
	) {
	}

	dispose() {
		for (const disposable of this.disposables) {
			disposable.dispose();
		}
	}
}