import { ComputeLinesDiffRequest, ComputeLinesDiffResponse } from './worker/worker.api.js';
import { WorkerManagerImpl } from './worker/workerManager.js';
import * as vscode from 'vscode';


let diffService: DiffService | undefined;

export class DiffService implements vscode.Disposable {

	private workerManager: WorkerManagerImpl;

	constructor(
		private readonly context: vscode.ExtensionContext,
	) {
		// we enforce singleton here
		if (diffService) {
			throw new Error('DiffService already initialized');
		}
		diffService = this;

		this.workerManager = new WorkerManagerImpl(context, {
			timeoutAfterNoRequestsForMinutes: 5,
		});
	}

	async computeLinesDiff(request: ComputeLinesDiffRequest): Promise<ComputeLinesDiffResponse> {
		const response = await this.workerManager.call({ kind: 'computeLinesDiff', request });
		if (response.kind !== 'computeLinesDiff') {
			throw new Error('Unexpected response kind');
		}
		return response.response;
	}

	dispose() {
		this.workerManager.dispose();
		diffService = undefined;
	}

}