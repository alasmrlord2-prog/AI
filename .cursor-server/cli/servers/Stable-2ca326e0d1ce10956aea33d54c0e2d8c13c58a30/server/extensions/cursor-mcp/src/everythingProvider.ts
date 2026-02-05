import { EverythingProvider, EverythingProviderArgs, ExtractArgs, ExtractReturn, TreeSitterActions } from '@cursor/types';
import * as vscode from 'vscode';
import { getCommandFromRegistry } from './commands/registryAll';
import { ACTION_REGISTRY } from './commands/registry';

export class EverythingProviderCreator implements vscode.Disposable {
	private disposables: vscode.Disposable[] = [];

	constructor(context: vscode.ExtensionContext) {
		const supportedCommands = Object.keys(ACTION_REGISTRY).filter(
			(cmd): cmd is EverythingProviderArgs['name'] => true
		);

		const everythingProvider: EverythingProvider = {
			supportedCommands,
			// @ts-ignore (Needed for gulpfile building only)
			runCommand: <K extends EverythingProviderArgs['name']>(commandName: K, args: ExtractArgs<K>): ExtractReturn<K> | Promise<undefined> => {
				const command = getCommandFromRegistry(commandName);
				if (command !== undefined) {
					// Also seemingly needed ts-ignore
					// @ts-ignore
					return command(args, { context: context });
				}

				return Promise.resolve(undefined);
			}
		}

		context.subscriptions.push(vscode.cursor.registerEverythingProvider(everythingProvider));
	}

	dispose() {
		this.disposables.forEach((disposable) => disposable.dispose());
	}
}

