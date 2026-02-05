import { LogOutputChannel } from 'vscode';
import * as vscode from 'vscode';

export class CursorBugbotLogger {
	private static output: LogOutputChannel | undefined;

	public static init(): void {
		CursorBugbotLogger.output = vscode.window.createOutputChannel('Cursor Agent Review', { log: true });
	}

	public static isTrace(): boolean {
		return CursorBugbotLogger.output?.logLevel === vscode.LogLevel.Trace;
	}
	public static error(msg: string, ...args: any[]): void {
		CursorBugbotLogger.output?.error(msg, ...args);
	}
	public static warn(msg: string, ...args: any[]): void {
		CursorBugbotLogger.output?.warn(msg, ...args);
	}
	public static info(msg: string, ...args: any[]): void {
		CursorBugbotLogger.output?.info(msg, ...args);
	}
	public static debug(msg: string, ...args: any[]): void {
		CursorBugbotLogger.output?.debug(msg, ...args);
	}
	public static trace(msg: string, ...args: any[]): void {
		CursorBugbotLogger.output?.trace(msg, ...args);
	}
}

export class CursorDebugLogger {
	private static output: LogOutputChannel | undefined;

	public static init(): void {
		CursorDebugLogger.output = vscode.window.createOutputChannel('Cursor-commits debug logs', { log: true });
	}

	public static error(msg: string, ...args: any[]): void {
		CursorDebugLogger.output?.error(msg, ...args);
	}
	public static warn(msg: string, ...args: any[]): void {
		CursorDebugLogger.output?.warn(msg, ...args);
	}
	public static info(msg: string, ...args: any[]): void {
		CursorDebugLogger.output?.info(msg, ...args);
	}
	public static debug(msg: string, ...args: any[]): void {
		CursorDebugLogger.output?.debug(msg, ...args);
	}
	public static trace(msg: string, ...args: any[]): void {
		CursorDebugLogger.output?.trace(msg, ...args);
	}
}