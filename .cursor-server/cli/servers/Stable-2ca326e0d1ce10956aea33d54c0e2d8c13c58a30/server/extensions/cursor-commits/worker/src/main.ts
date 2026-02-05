import { parentPort } from 'node:worker_threads';
import { computeLinesDiff } from './diff.js';
import { WorkerRequestMessage, WorkerResponseMessage } from '../../src/worker/worker.api.js';

// Throw an error if parent port is not defined
if (!parentPort) {
	throw new Error('Parent port is not defined. This worker must be run in a worker thread context.');
}

parentPort.on('message', async (msg: WorkerRequestMessage) => {
	try {
		const response: WorkerResponseMessage = await (async () => {
			const request = msg.request as WorkerRequestMessage['request'];
			switch (request.kind) {
				case 'computeLinesDiff': {
					const response = await computeLinesDiff(request.request);
					return {
						id: msg.id,
						response: {
							kind: 'computeLinesDiff',
							response,
						}
					}
				}
				default: {
					const _x: never = request.kind;
					throw new Error(`Unknown request kind: ${_x}`);
				}
			}
		})();
		parentPort?.postMessage(response);
	} catch (err: any) {
		const errorMsg: WorkerResponseMessage = {
			id: msg.id,
			error: {
				message: err?.message ?? String(err),
				code: err?.code,
				stack: err?.stack,
			}
		};
		try {
			parentPort?.postMessage(errorMsg);
		} catch {
			// ignore
		}
	}
});

