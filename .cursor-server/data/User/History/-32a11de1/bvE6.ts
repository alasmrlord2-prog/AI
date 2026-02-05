"use client";

import { useState, useCallback } from "react";
import { apiRequest, APIError, NetworkError, TimeoutError } from "@/lib/api";

interface UseApiOptions {
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
}

export function useApi() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [data, setData] = useState<any>(null);

  const execute = useCallback(
    async (
      endpoint: string,
      options: RequestInit = {},
      apiOptions?: UseApiOptions
    ) => {
      setLoading(true);
      setError(null);

      try {
        const result = await apiRequest(endpoint, options);
        setData(result);
        apiOptions?.onSuccess?.(result);
        return result;
      } catch (err) {
        const error = err instanceof Error ? err : new Error("Unknown error");
        setError(error);
        apiOptions?.onError?.(error);
        throw error;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const reset = useCallback(() => {
    setError(null);
    setData(null);
    setLoading(false);
  }, []);

  return {
    execute,
    loading,
    error,
    data,
    reset,
    isError: error !== null,
    isSuccess: error === null && data !== null,
  };
}

