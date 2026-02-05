import { ComputeLinesDiffRequest, ComputeLinesDiffResponse } from '../../src/worker/worker.api.js';
import { linesDiffComputers } from './vs/editor/common/diff/linesDiffComputers.js';



export async function computeLinesDiff(request: ComputeLinesDiffRequest): Promise<ComputeLinesDiffResponse> {
	const diff = linesDiffComputers.getDefault().computeDiff(request.original, request.modified, {
		ignoreTrimWhitespace: request.ignoreTrimWhitespace,
		computeMoves: false,
		maxComputationTimeMs: request.maxComputationTimeMs,
		shouldGracefullyFallBackOnTimeout: true,
		skipDiffRefinement: request.skipDiffRefinement,
	});

	return {
		changes: diff.changes.map(c => ({
			originalRange: {
				startLineNumberOneIndexed: c.original.startLineNumber,
				endLineNumberExclusiveOneIndexed: c.original.endLineNumberExclusive,
			},
			modifiedRange: {
				startLineNumberOneIndexed: c.modified.startLineNumber,
				endLineNumberExclusiveOneIndexed: c.modified.endLineNumberExclusive,
			},
		})),
		timedOut: diff.hitTimeout,
	};
}