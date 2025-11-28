import { useEffect, useState } from "react";

// --- Reusable Hook --------------------------------------------------
// useStreaming(endpoint, requestBody, headers)
// Returns: { chunks, isLoading, error }
export function useStreaming(endpoint: string, requestBody = {}, headers = {}) {
  const [chunks, setChunks] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    let reader;
    let cancelled = false;

    async function fetchStream() {
      setIsLoading(true);
      setError(null);
      setChunks("");

      try {
        const response = await fetch(endpoint, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...headers,
          },
          body: JSON.stringify(requestBody),
        });

        if (!response.ok || !response.body) {
          throw new Error(`Request failed: ${response.status}`);
        }

        reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
          const { value, done } = await reader.read();
          if (done || cancelled) break;

          const text = decoder.decode(value, { stream: true });
          setChunks(prev => prev + text);
        }
      } catch (err) {
        if (!cancelled) setError(err.message);
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    fetchStream();

    return () => {
      cancelled = true;
      if (reader) reader.cancel();
    };
  }, [endpoint, JSON.stringify(requestBody), JSON.stringify(headers)]);

  return { chunks, isLoading, error };
}

