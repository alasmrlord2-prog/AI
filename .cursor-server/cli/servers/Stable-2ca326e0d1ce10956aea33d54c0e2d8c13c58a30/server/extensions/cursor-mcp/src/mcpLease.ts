import * as vscode from 'vscode';
import type {
	Disposable,
	McpClient,
	ObservableMcpLease,
	McpToolResult,
	NamedMcpToolDefinition,
} from '@anysphere/agent-exec';
import type { Context } from '@anysphere/context';
import { ExecutableMcpTool, ExecutableMcpToolSet, McpManager, type McpElicitationProviderFactory } from '@anysphere/local-exec';
import type { JsonValue } from '@bufbuild/protobuf';
import type { McpProvider } from '@cursor/types';
import { getMcpManager } from './commands/mcpCommands.js';
import { z } from 'zod';
import { McpFileSystemOptions, McpInstructions } from '@anysphere/proto/agent/v1/mcp_pb.js';

// Schema for JSON Schema property definition
const JsonSchemaPropertySchema = z.object({
	description: z.string().optional(),
}).passthrough();

// Schema for JSON Schema parameters object
const JsonSchemaParametersSchema = z.object({
	properties: z.record(z.string(), JsonSchemaPropertySchema).optional(),
	required: z.array(z.string()).optional(),
}).passthrough();

/**
 * @deprecated VscodeMcpLease is getting phased out in favor of WorkbenchVscodeMcpLease.
 * It will be deleted when the rollout of cursor extension isolation is complete.
 */
export class VscodeMcpLease implements ObservableMcpLease {
	private readonly mcpManager: McpManager;
	private readonly changeListeners: Set<() => void> = new Set();

	constructor(
		private readonly context: vscode.ExtensionContext,
	) {
		this.mcpManager = getMcpManager();

		// Listen to mcpManager changes (e.g., from mcpCommands.ts when servers connect/disconnect)
		// This ensures we propagate all client additions/removals, not just those from vscode.cursor events
		const disposeManagerListener = this.mcpManager.onDidChange(() => {
			this.fireDidChange();
		});
		// Register disposal with the extension context
		this.context.subscriptions.push({ dispose: disposeManagerListener });

		this.initializeMcpProviders();

		this.context.subscriptions.push(
			vscode.cursor.onDidRegisterMcpProvider((provider) => {
				// Note: registerMcpProvider calls mcpManager.setClient, which will trigger
				// mcpManager.onDidChange and fireDidChange() via the listener above
				this.registerMcpProvider(provider);
			})
		);

		// If main thread broadcasts an unregistration event for a remote mcp provider, delete the client from the local manager
		this.context.subscriptions.push(
			vscode.cursor.onDidUnregisterMcpProvider((id) => {
				// Note: deleteClient will trigger mcpManager.onDidChange and fireDidChange() via the listener above
				this.mcpManager.deleteClient(id);
			})
		);
	}

	onDidChange(listener: () => void): Disposable {
		this.changeListeners.add(listener);
		return {
			dispose: async () => {
				this.changeListeners.delete(listener);
			}
		};
	}

	private fireDidChange(): void {
		for (const listener of this.changeListeners) {
			try {
				listener();
			} catch (e) {
				console.error('Error in MCP change listener:', e);
			}
		}
	}

	async getClients(): Promise<Record<string, McpClient>> {
		return this.mcpManager.getClients();
	}

	async getClient(name: string): Promise<McpClient | undefined> {
		return this.mcpManager.getClient(name);
	}

	async getInstructions(ctx: Context): Promise<McpInstructions[]> {
		return this.mcpManager.getInstructions(ctx);
	}

	private async initializeMcpProviders(): Promise<void> {
		try {
			const providers = await vscode.cursor.getAllMcpProviders();

			for (const provider of providers) {
				await this.registerMcpProviderToManager(this.mcpManager, provider);
			}
		} catch (error) {
			console.error('Failed to initialize MCP providers:', error);
		}
	}

	private async registerMcpProvider(provider: McpProvider): Promise<void> {
		try {
			await this.registerMcpProviderToManager(this.mcpManager, provider);
		} catch (error) {
			console.error(`Failed to register MCP provider ${provider.id}:`, error);
		}
	}

	private async registerMcpProviderToManager(
		mcpManager: McpManager,
		provider: McpProvider
	): Promise<void> {
		const clientWrapper: McpClient = {
			getState: async (_ctx: Context) => ({ kind: 'ready' as const }),
			getTools: async (_ctx: Context) => {
				const offerings = await provider.listOfferings();
				if (!offerings?.tools) {
					return [];
				}
				return offerings.tools.map((tool) => ({
					name: tool.name,
					description: tool.description,
					inputSchema: JSON.parse(tool.parameters),
				}));
			},
			callTool: async (
				_ctx: Context,
				toolName: string,
				args: Record<string, unknown>,
				_toolCallId?: string,
				_elicitationProvider?: any
			) => {
				return provider.callTool(toolName, args) as ReturnType<
					McpClient['callTool']
				>;
			},
			getInstructions: async (_ctx: Context) => {
				return provider.instructions;
			},
			listResources: async (_ctx: Context) => {
				const offerings = await provider.listOfferings();
				if (!offerings?.resources) {
					return { resources: [] };
				}
				return { resources: offerings.resources };
			},
			readResource: async (_ctx: Context, _args: { uri: string }) => {
				return { contents: [] };
			},
			listPrompts: async (_ctx: Context) => {
				const offerings = await provider.listOfferings();
				if (!offerings?.prompts) {
					return [];
				}
				return offerings.prompts.map((prompt) => {
					let argumentsList: Array<{ name: string; description?: string; required: boolean }> = [];

					if (prompt.parameters) {
						const parsed = JSON.parse(prompt.parameters);
						const result = JsonSchemaParametersSchema.safeParse(parsed);

						if (result.success && result.data.properties) {
							const requiredSet = new Set(result.data.required ?? []);
							argumentsList = Object.entries(result.data.properties).map(([name, prop]) => ({
								name,
								description: prop.description,
								required: requiredSet.has(name),
							}));
						}
					}

					return {
						name: prompt.name,
						description: prompt.description,
						arguments: argumentsList,
					};
				});
			},
			getPrompt: async (_ctx: Context, _name: string, _args?: Record<string, string>) => {
				return { messages: [] };
			},
			serverName: provider.name ?? provider.id,
			// Config is not available for extension-based MCP providers
			// It will be available for config-based MCP clients (stdio/http)
			config: undefined,
		};

		mcpManager.setClient(provider.id, clientWrapper);
	}

	async getToolSet(ctx: Context): Promise<ExecutableMcpToolSet> {
		const enabledToolsByServer = await vscode.cursor.getEnabledMcpTools();

		const allClients = await this.getClients();


		// Filter to only clients that have enabled tools
		const enabledClients = Object.fromEntries(
			Object.entries(allClients).filter(([key, client]) =>
				enabledToolsByServer[key] !== undefined
			)
		);

		const clientTools = await Promise.all(
			Object.entries(enabledClients).map(([key, client]) =>
				client
					.getTools(ctx)
					.then((tools) =>
						tools.map((tool) => ({
							...tool,
							// Use key (identifier) for filtering, serverName for display/providerIdentifier
							clientKey: key,
							clientName: client.serverName,
							client: client,
						}))
					)
					.catch(() => [])
			)
		);

		// Filter to only include enabled tools using the same mechanism as mcpService
		// enabledToolsByServer maps server identifier (key) -> list of enabled tool names
		const tools = clientTools.flat().filter((tool) => {
			const enabledToolsForServer = enabledToolsByServer[tool.clientKey];
			if (!enabledToolsForServer) {
				return false; // No enabled tools list means server not enabled or not found
			}
			return enabledToolsForServer.includes(tool.name);
		});

		const toolsMap: Record<string, ExecutableMcpTool> = {};
		for (const tool of tools) {
			// Use clientKey (identifier) for the map key, clientName (display name) for providerIdentifier
			toolsMap[`${tool.clientKey}-${tool.name}`] = {
				definition: {
					...tool,
					clientKey: tool.clientKey,
					providerIdentifier: tool.clientName,
					toolName: tool.name,
				},
				execute: async (
					args: Record<string, JsonValue>,
					toolCallId?: string,
					elicitationFactory?: McpElicitationProviderFactory
				) => {
					const elicitationProvider = elicitationFactory?.createProvider(
						tool.clientName,
						tool.name,
						toolCallId
					);

					const result = await tool.client.callTool(
						ctx,
						tool.name,
						args,
						toolCallId,
						elicitationProvider
					);
					return result;
				},
			};
		}

		// Build a simple MCP file system options callback that doesn't require context.
		// This callback is only used for error messages when a tool is not found,
		// so we only need to check if the feature is enabled and get the project dir.
		// We avoid using the request-scoped ctx here since the toolset may be cached
		// and the original context could be stale/aborted when this callback runs.
		const getMcpFileSystemOptions = async (): Promise<McpFileSystemOptions> => {
			if (!vscode.cursor.getMcpFileSystemEnabled()) {
				return new McpFileSystemOptions({ enabled: false });
			}
			const projectDir = vscode.cursor.getWorkspaceProjectDir();
			if (!projectDir) {
				return new McpFileSystemOptions({ enabled: false });
			}
			// For error messages, we only need enabled + projectDir, not full server descriptors
			return new McpFileSystemOptions({
				enabled: true,
				workspaceProjectDir: projectDir,
				mcpDescriptors: [],
			});
		};

		return new ExecutableMcpToolSet(toolsMap, getMcpFileSystemOptions);
	}

	async getTools(ctx: Context): Promise<NamedMcpToolDefinition[]> {
		const toolSet = await this.getToolSet(ctx);
		return toolSet.getTools();
	}
}
