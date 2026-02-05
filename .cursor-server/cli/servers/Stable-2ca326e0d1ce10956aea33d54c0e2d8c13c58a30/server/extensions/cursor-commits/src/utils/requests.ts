export function getTracingHeaders(
	generationUUID: string,
) {
	const headers: Record<string, string> = {
		'X-Request-ID': generationUUID,
		'X-Amzn-Trace-Id': `Root=${generationUUID}`,
	};

	return headers;
}