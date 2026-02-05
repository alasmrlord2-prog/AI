export type ComputeLinesDiffRequest = {
	original: string[];
	modified: string[];
	ignoreTrimWhitespace: boolean;
	maxComputationTimeMs: number;
	skipDiffRefinement?: boolean;
}

export type WorkerError = {
	message: string;
	code?: string;
	stack?: string;
}

export type ComputeLinesDiffResponse = {
	changes: {
		originalRange: {
			startLineNumberOneIndexed: number;
			endLineNumberExclusiveOneIndexed: number;
		}
		modifiedRange: {
			startLineNumberOneIndexed: number;
			endLineNumberExclusiveOneIndexed: number;
		}
	}[];
	timedOut: boolean;
}


export type WorkerRequest = {
	kind: 'computeLinesDiff';
	request: ComputeLinesDiffRequest;
}
export type WorkerResponse = {
	kind: 'computeLinesDiff';
	response: ComputeLinesDiffResponse;
}

export type WorkerRequestMessage = {
	id: string;
	request: WorkerRequest;
}

export type WorkerResponseMessage = {
	id: string;
	response?: WorkerResponse;
	error?: WorkerError;
}