/**
 * Chunk Preview Step - Shows document chunks with MarkdownRenderer
 */
import React, { useState, useEffect } from 'react';
import MarkdownRenderer from '../../../lib/aikit/react/MarkdownRenderer';
import CodeBlock from '../../../lib/aikit/react/CodeBlock';
import StreamingToolResult from '../../../lib/aikit/react/StreamingToolResult';
import { ChunkData, SafetyScanResult } from '../RAGBotUploadWorkflow';

interface ChunkPreviewStepProps {
  documentId: string;
  safetyScan: SafetyScanResult;
  onChunksGenerated: (chunks: ChunkData[]) => void;
  onBack: () => void;
}

export const ChunkPreviewStep: React.FC<ChunkPreviewStepProps> = ({
  documentId,
  safetyScan,
  onChunksGenerated,
  onBack,
}) => {
  const [loading, setLoading] = useState(true);
  const [chunks, setChunks] = useState<ChunkData[]>([]);
  const [selectedChunk, setSelectedChunk] = useState<number>(0);

  useEffect(() => {
    generateChunks();
  }, [documentId]);

  const generateChunks = async () => {
    try {
      const response = await fetch('/api/v1/ragbot/chunk-preview', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ document_id: documentId }),
      });

      const data = await response.json();
      setChunks(data.chunks || []);
      setLoading(false);
    } catch (error) {
      console.error('Chunk generation failed:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <h2 className="text-2xl font-bold">Generating Chunks...</h2>
        <StreamingToolResult
          toolName="Document Chunking"
          chunks={['Processing document...', 'Generating embeddings...']}
          isStreaming={true}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between">
        <h2 className="text-2xl font-bold">Chunk Preview ({chunks.length} chunks)</h2>
        <div className="text-sm text-gray-600">
          Chunk {selectedChunk + 1} of {chunks.length}
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="col-span-1 space-y-2 max-h-96 overflow-y-auto">
          {chunks.map((chunk, idx) => (
            <button
              key={idx}
              onClick={() => setSelectedChunk(idx)}
              className={`w-full text-left p-2 rounded border ${
                idx === selectedChunk ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
              }`}
            >
              <div className="font-medium text-sm">Chunk {idx + 1}</div>
              <div className="text-xs text-gray-600 truncate">{chunk.text.substring(0, 50)}...</div>
            </button>
          ))}
        </div>

        <div className="col-span-3 space-y-4">
          <MarkdownRenderer content={chunks[selectedChunk]?.text || ''} />

          <details>
            <summary className="cursor-pointer font-medium text-sm">Show Metadata</summary>
            <CodeBlock
              code={JSON.stringify(chunks[selectedChunk]?.metadata || {}, null, 2)}
              language="json"
              copyable
            />
          </details>
        </div>
      </div>

      <div className="flex justify-between pt-4 border-t">
        <button onClick={onBack} className="px-6 py-2 border rounded-lg">
          Back
        </button>
        <button
          onClick={() => onChunksGenerated(chunks)}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg"
        >
          Continue to Review
        </button>
      </div>
    </div>
  );
};

export default ChunkPreviewStep;
