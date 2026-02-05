import { compressionGzip, createConnectTransport } from '@connectrpc/connect-node';
import * as vscode from 'vscode';
import { CursorDebugLogger } from './utils/logger';
import { Interceptor, PromiseClient, Transport, createPromiseClient } from '@connectrpc/connect';
import { AiService } from 'proto/aiserver/v1/aiserver_connectweb.js';
import { randomUUID } from 'crypto';
import { OnlineMetricsService } from 'proto/aiserver/v1/online_metrics_connectweb.js';

export class BackendClientService implements vscode.Disposable {
	private disposables: vscode.Disposable[] = [];

	private accessToken?: string;
	private cursorCreds?: vscode.cursor.CursorCreds;

	constructor(private readonly context: vscode.ExtensionContext) {
		this.disposables.push(vscode.cursor.onDidChangeCursorAuthToken((
			(e: vscode.cursor.CursorAuthToken) => {
				this.accessToken = e;
			}
		)));

		this.disposables.push(vscode.cursor.onDidChangeCursorCreds((
			(e: vscode.cursor.CursorCreds) => {
				this.cursorCreds = e;
				this.aiClient = undefined;
				this.onlineMetricsClient = undefined;
			}
		)));

		const getInitialValues = async () => {
			while (this.cursorCreds === undefined) {
				try {
					this.accessToken = vscode.cursor.getCursorAuthToken();
					this.cursorCreds = vscode.cursor.getCursorCreds();
				} catch (e) {
					CursorDebugLogger.error('Failed to get initial values', e);
				}
				await new Promise(resolve => setTimeout(resolve, 200));
			}
		}

		getInitialValues().then(() => {}).catch();
	}

	private aiClient: PromiseClient<typeof AiService> | undefined = undefined;
	async getAIClient(): Promise<PromiseClient<typeof AiService>> {
		if (this.aiClient === undefined) {
			while (this.cursorCreds === undefined) {
				// wait for a little bit
				await new Promise(resolve => setTimeout(resolve, 200));
			}
			const transport = this.createTransport({
				baseUrl: this.cursorCreds.backendUrl,
			});
			this.aiClient = createPromiseClient(AiService, transport);
		}
		return this.aiClient;
	}
	private onlineMetricsClient: PromiseClient<typeof OnlineMetricsService> | undefined = undefined;
	async getOnlineMetricsClient(): Promise<PromiseClient<typeof OnlineMetricsService>> {
		if (this.onlineMetricsClient === undefined) {
			while (this.cursorCreds === undefined) {
				// wait for a little bit
				await new Promise(resolve => setTimeout(resolve, 200));
			}
			const transport = this.createTransport({
				baseUrl: this.cursorCreds.backendUrl,
			});
			this.onlineMetricsClient = createPromiseClient(OnlineMetricsService, transport);
		}
		return this.onlineMetricsClient;
	}

	private createTransport(args: {
		baseUrl: string;
	}): Transport {
		const bearerTokenInterceptor: Interceptor = (next) => async (req) => {
			req.header.set("Authorization", `Bearer ${this.accessToken}`);

			return await next(req);
		};

		const addHeaders: Interceptor = (next: any) => async (req: any) => {
			vscode.cursor.getAllRequestHeadersExceptAccessToken({ req: req, backupRequestId: randomUUID() })

			return await next(req);
		};

		const isLocal = (
			args.baseUrl.match(/(?:[^\/]+\.)?lclhst\.build(?::\d+)?(?:\/|$)/) !== null
			|| args.baseUrl.match(/(?:[^\/]+\.)?localhost(?::\d+)?(?:\/|$)/) !== null
		);

		const nodeInDevOptions = (this.context.isDevelopment && isLocal) ? {
			rejectUnauthorized: false,
			ALPNProtocols: ['http/1.1']
		} : {};

		const transport = createConnectTransport({
			// we only support http1 for now...
			// in the future, we should make the ai connect transport a package, and then we can import it both in cursor-retrieval and cursor-always-local
			httpVersion: '1.1',
			baseUrl: args.baseUrl,
			useBinaryFormat: true,
			interceptors: [
				bearerTokenInterceptor,
				addHeaders,
			],
			sendCompression: compressionGzip,
			acceptCompression: [compressionGzip],
			nodeOptions: {
				...nodeInDevOptions,
			}
		});
		return transport;
	}


	dispose() {
		this.disposables.forEach((disposable) => disposable.dispose());
	}
}

