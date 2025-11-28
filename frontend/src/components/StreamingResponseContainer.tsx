import { useStreaming } from '../hooks/useStreaming';

const endpoint = 'http://localhost:5000'

// --- Component Using the Hook --------------------------------------
export default function StreamingComponent({ requestBody = {}, headers = {} }) {
  const { chunks, isLoading, error } = useStreaming(endpoint, requestBody, headers);

  return (
    <div className="p-6 max-w-xl mx-auto space-y-4">
      <h1 className="text-xl font-bold">Streaming Response</h1>

      {isLoading && <p className="opacity-60">Loading...</p>}
      {error && <p className="text-red-500">Error: {error}</p>}

      <pre className="whitespace-pre-wrap p-4 border rounded-xl bg-gray-50">
        {chunks}
      </pre>
    </div>
  );
}