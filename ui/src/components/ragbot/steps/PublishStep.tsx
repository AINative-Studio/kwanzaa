/**
 * Publish Step - Final confirmation and ZeroDB publication
 */
import React, { useState } from 'react';
import ProgressBar from '../../../lib/aikit/react/ProgressBar';
import ToolResult from '../../../lib/aikit/react/ToolResult';
import { ChunkData, DocumentMetadata } from '../RAGBotUploadWorkflow';
import { getZeroDB } from '../../../lib/aikit/zerodb/ZeroDBClient';

interface PublishStepProps {
  documentId: string;
  namespace: string;
  chunks: ChunkData[];
  metadata: DocumentMetadata;
  onPublish: () => void;
  onReject: () => void;
  onBack: () => void;
}

export const PublishStep: React.FC<PublishStepProps> = ({
  documentId,
  namespace,
  chunks,
  metadata,
  onPublish,
  onReject,
  onBack,
}) => {
  const [publishing, setPublishing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handlePublish = async () => {
    setPublishing(true);
    setProgress(0);

    try {
      const response = await fetch('/api/v1/ragbot/publish', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_id: documentId,
          namespace,
          chunks,
          metadata,
        }),
      });

      if (!response.ok) throw new Error('Publication failed');

      const data = await response.json();
      setResult(data);
      setProgress(100);

      setTimeout(() => {
        onPublish();
      }, 2000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Publication failed');
      setPublishing(false);
    }
  };

  const handleReject = async () => {
    try {
      await fetch('/api/v1/ragbot/reject', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ document_id: documentId }),
      });
      onReject();
    } catch (err) {
      console.error('Reject failed:', err);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Publish to Vector Database</h2>

      {!publishing && !result && (
        <>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-semibold text-blue-900 mb-2">Publication Summary</h3>
            <div className="space-y-1 text-sm text-blue-800">
              <div>Document ID: {documentId}</div>
              <div>Namespace: {namespace}</div>
              <div>Chunks to publish: {chunks.length}</div>
              <div>Source: {metadata.source_org}</div>
              <div>License: {metadata.license}</div>
            </div>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm">
            <strong>⚠️ Final Confirmation:</strong> This action will make the document searchable
            in the RAG system. Ensure all information is correct before proceeding.
          </div>

          <div className="flex justify-between pt-4 border-t">
            <div className="space-x-3">
              <button onClick={onBack} className="px-6 py-2 border rounded-lg">
                Back
              </button>
              <button
                onClick={handleReject}
                className="px-6 py-2 border border-red-300 text-red-700 rounded-lg hover:bg-red-50"
              >
                Reject Document
              </button>
            </div>
            <button
              onClick={handlePublish}
              className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg"
            >
              Publish to ZeroDB
            </button>
          </div>
        </>
      )}

      {publishing && (
        <div className="space-y-4">
          <ProgressBar
            value={progress}
            label="Publishing to ZeroDB..."
            color="primary"
            showPercentage
            animated
          />
        </div>
      )}

      {result && (
        <ToolResult
          toolName="Publication Result"
          status="success"
          result={result}
          metadata={{ duration: result.duration_ms }}
        />
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
          <strong>Error:</strong> {error}
        </div>
      )}
    </div>
  );
};

export default PublishStep;
