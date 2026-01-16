/**
 * RAGBot Upload Workflow Component
 *
 * Complete document upload and curation workflow with safety scanning and observability.
 * Implements Epic 7 - Issue #38 requirements.
 */

import React, { useState } from 'react';
import { UploadStep } from './steps/UploadStep';
import { MetadataStep } from './steps/MetadataStep';
import { SafetyScanStep } from './steps/SafetyScanStep';
import { ChunkPreviewStep } from './steps/ChunkPreviewStep';
import { ReviewStep } from './steps/ReviewStep';
import { PublishStep } from './steps/PublishStep';
import { getMetrics } from '../../lib/aikit/observability/MetricsTracker';

export interface DocumentMetadata {
  source_org: string;
  canonical_url: string;
  license: string;
  year: number;
  content_type: string;
  author?: string;
  title?: string;
  tags?: string[];
}

export interface SafetyScanResult {
  pii_matches: number;
  moderation_flags: number;
  passed: boolean;
  report: any;
}

export interface ChunkData {
  chunk_id: string;
  text: string;
  chunk_index: number;
  embedding_preview?: number[];
  metadata: Record<string, any>;
}

export interface WorkflowState {
  step: 1 | 2 | 3 | 4 | 5 | 6;
  file?: File;
  documentId?: string;
  metadata?: DocumentMetadata;
  safetyScan?: SafetyScanResult;
  chunks?: ChunkData[];
  namespace?: string;
}

export const RAGBotUploadWorkflow: React.FC = () => {
  const [state, setState] = useState<WorkflowState>({ step: 1 });
  const metrics = getMetrics();

  const handleFileUploaded = (file: File, documentId: string) => {
    metrics.trackUpload(file.size, file.type, 0);
    setState((prev) => ({
      ...prev,
      step: 2,
      file,
      documentId,
    }));
  };

  const handleMetadataSubmitted = (metadata: DocumentMetadata) => {
    setState((prev) => ({
      ...prev,
      step: 3,
      metadata,
    }));
  };

  const handleSafetyScanComplete = (safetyScan: SafetyScanResult) => {
    if (state.documentId) {
      metrics.trackSafetyScan(
        state.documentId,
        safetyScan.pii_matches,
        safetyScan.moderation_flags
      );
    }

    setState((prev) => ({
      ...prev,
      step: safetyScan.passed ? 4 : 3,
      safetyScan,
    }));
  };

  const handleChunksGenerated = (chunks: ChunkData[]) => {
    if (state.documentId) {
      metrics.trackChunkGeneration(chunks.length, state.documentId, 0);
    }

    setState((prev) => ({
      ...prev,
      step: 5,
      chunks,
    }));
  };

  const handleReviewComplete = (namespace: string) => {
    setState((prev) => ({
      ...prev,
      step: 6,
      namespace,
    }));
  };

  const handlePublish = () => {
    if (state.documentId) {
      metrics.trackCuratorAction('publish', state.documentId);
    }
    // Reset workflow
    setState({ step: 1 });
  };

  const handleReject = () => {
    if (state.documentId) {
      metrics.trackCuratorAction('reject', state.documentId);
    }
    // Reset workflow
    setState({ step: 1 });
  };

  const handleBack = () => {
    setState((prev) => ({
      ...prev,
      step: Math.max(1, prev.step - 1) as WorkflowState['step'],
    }));
  };

  const stepTitles = {
    1: 'Upload Document',
    2: 'Enter Metadata',
    3: 'Safety Scan',
    4: 'Preview Chunks',
    5: 'Review & Validate',
    6: 'Publish',
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Progress Indicator */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-2">
          <h1 className="text-3xl font-bold text-gray-900">RAGBot Document Curation</h1>
          <span className="text-sm text-gray-600">
            Step {state.step} of 6: {stepTitles[state.step]}
          </span>
        </div>

        <div className="flex items-center space-x-2">
          {[1, 2, 3, 4, 5, 6].map((step) => (
            <React.Fragment key={step}>
              <div
                className={`flex-1 h-2 rounded-full transition-colors ${
                  step < state.step
                    ? 'bg-green-500'
                    : step === state.step
                    ? 'bg-blue-500'
                    : 'bg-gray-200'
                }`}
              />
              {step < 6 && <div className="w-2" />}
            </React.Fragment>
          ))}
        </div>

        <div className="flex justify-between mt-2 text-xs text-gray-600">
          {Object.entries(stepTitles).map(([stepNum, title]) => (
            <span
              key={stepNum}
              className={`${
                Number(stepNum) === state.step ? 'font-semibold text-blue-600' : ''
              }`}
            >
              {title}
            </span>
          ))}
        </div>
      </div>

      {/* Step Content */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        {state.step === 1 && <UploadStep onFileUploaded={handleFileUploaded} />}

        {state.step === 2 && state.file && (
          <MetadataStep
            file={state.file}
            onSubmit={handleMetadataSubmitted}
            onBack={handleBack}
          />
        )}

        {state.step === 3 && state.documentId && state.metadata && (
          <SafetyScanStep
            documentId={state.documentId}
            metadata={state.metadata}
            onScanComplete={handleSafetyScanComplete}
            onBack={handleBack}
          />
        )}

        {state.step === 4 && state.documentId && state.safetyScan && (
          <ChunkPreviewStep
            documentId={state.documentId}
            safetyScan={state.safetyScan}
            onChunksGenerated={handleChunksGenerated}
            onBack={handleBack}
          />
        )}

        {state.step === 5 && state.chunks && state.metadata && state.safetyScan && (
          <ReviewStep
            chunks={state.chunks}
            metadata={state.metadata}
            safetyScan={state.safetyScan}
            onReviewComplete={handleReviewComplete}
            onBack={handleBack}
          />
        )}

        {state.step === 6 && state.documentId && state.namespace && state.chunks && (
          <PublishStep
            documentId={state.documentId}
            namespace={state.namespace}
            chunks={state.chunks}
            metadata={state.metadata!}
            onPublish={handlePublish}
            onReject={handleReject}
            onBack={handleBack}
          />
        )}
      </div>
    </div>
  );
};

export default RAGBotUploadWorkflow;
