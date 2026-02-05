import * as vscode from 'vscode';
import { generateUuid } from '../utils/uuid.js';
import { WorkerRequest, WorkerResponse, WorkerResponseMessage } from './worker.api.js';
import { CursorDebugLogger } from '../utils/logger.js';

export class WorkerManagerImpl implements vscode.Disposable {
	private worker: import('node:worker_threads').Worker | undefined;
	private readonly pending = new Map<string, { resolve: (d: WorkerResponse) => void; reject: (e: any) => void }>();
	private disposeTimer: NodeJS.Timeout | undefined;

	constructor(
		private readonly context: vscode.ExtensionContext,
		private readonly config: {
			timeoutAfterNoRequestsForMinutes: number;
		}
	) {}

	private async ensureWorker(): Promise<import('node:worker_threads').Worker> {
		if (this.worker) {
			return this.worker;
		}
		if (!this.context) {
			throw new Error('DiffWorkerManager not initialized');
		}
		const { Worker } = await import('node:worker_threads');
		const clientMain = vscode.extensions.getExtension('anysphere.cursor-commits')?.packageJSON?.main || '';
		const workerJs = vscode.Uri.joinPath(this.context.extensionUri, 'worker', clientMain.indexOf('/dist/') !== -1 ? 'dist' : 'out', 'main.js').fsPath;
		this.worker = new Worker(workerJs, {});
		this.worker.on('message', (msg: WorkerResponseMessage) => {
			const pending = this.pending.get(msg.id);
			if (!pending) {
				return;
			}
			this.pending.delete(msg.id);
			if (msg.error) {
				pending.reject(Object.assign(new Error(msg.error.message), { code: msg.error.code, stack: msg.error.stack }));
				return;
			}
			if (msg.response) {
				pending.resolve(msg.response);
				return;
			}
			pending.reject(new Error('Worker sent empty message'));
		});
		const fatal = (err: any) => {
			try {
				for (const [, pending] of this.pending) {
					pending.reject(err instanceof Error ? err : new Error(String(err)));
				}
			} finally {
				this.pending.clear();
				try {
					void this.worker?.terminate();
				} catch (e) {
					CursorDebugLogger.error('Failed to terminate worker after fatal', e);
				}
				this.worker = undefined;
			}
		};
		this.worker.on('error', fatal);
		// messageerror fired if structured clone fails
		this.worker.on('messageerror', fatal as any);
		this.worker.on('exit', (code) => {
			if (code !== 0) {
				fatal(new Error(`Worker exited with code ${code}`));
			} else {
				this.worker = undefined;
			}
		});
		return this.worker;
	}

	private armDisposeTimer() {
		if (this.disposeTimer) {
			clearTimeout(this.disposeTimer);
		}
		// Dispose after idle for a while
		this.disposeTimer = setTimeout(() => {
			try {
				void this.worker?.terminate();
			} catch (e) {
				CursorDebugLogger.error('Failed to terminate worker', e);
			}
			this.worker = undefined;
		}, this.config.timeoutAfterNoRequestsForMinutes * 60 * 1000);
	}

	async call(request: WorkerRequest): Promise<WorkerResponse> {
		const worker = await this.ensureWorker();
		this.armDisposeTimer();
		const id = generateUuid();
		return new Promise<WorkerResponse>((resolve, reject) => {
			this.pending.set(id, { resolve, reject });
			try {
				worker.postMessage({ id, request });
			} catch (err) {
				this.pending.delete(id);
				reject(err);
			}
		});
	}

	dispose(): void {
		if (this.disposeTimer) {
			clearTimeout(this.disposeTimer);
			this.disposeTimer = undefined;
		}
		try {
			void this.worker?.terminate();
		} catch (e) {
			CursorDebugLogger.error('Failed to terminate worker', e);
		}
		this.worker = undefined;
		this.pending.clear();
	}
}

