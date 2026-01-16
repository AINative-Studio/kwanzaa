/**
 * Review Step - Final validation before publishing
 */
import React, { useState } from 'react';
import { ChunkData, DocumentMetadata, SafetyScanResult } from '../RAGBotUploadWorkflow';

interface ReviewStepProps {
  chunks: ChunkData[];
  metadata: DocumentMetadata;
  safetyScan: SafetyScanResult;
  onReviewComplete: (namespace: string) => void;
  onBack: () => void;
}

export const ReviewStep: React.FC<ReviewStepProps> = ({
  chunks,
  metadata,
  safetyScan,
  onReviewComplete,
  onBack,
}) => {
  const [checklist, setChecklist] = useState({
    provenanceVerified: false,
    licenseConfirmed: false,
    contentReviewed: false,
    safetyApproved: false,
  });
  const [namespace, setNamespace] = useState('kwanzaa_primary_sources');

  const allChecked = Object.values(checklist).every((v) => v);

  const namespaces = [
    'kwanzaa_primary_sources',
    'kwanzaa_black_press',
    'kwanzaa_speeches_letters',
    'kwanzaa_black_stem',
    'kwanzaa_teaching_kits',
  ];

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Review & Validation</h2>

      {/* Provenance Summary */}
      <div className="border rounded-lg p-4 space-y-2">
        <h3 className="font-semibold">Provenance Information</h3>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div><strong>Source:</strong> {metadata.source_org}</div>
          <div><strong>License:</strong> {metadata.license}</div>
          <div><strong>Year:</strong> {metadata.year}</div>
          <div><strong>Type:</strong> {metadata.content_type}</div>
        </div>
      </div>

      {/* Safety Summary */}
      <div className={`border rounded-lg p-4 ${safetyScan.passed ? 'bg-green-50 border-green-200' : 'bg-yellow-50 border-yellow-200'}`}>
        <h3 className="font-semibold mb-2">Safety Scan Summary</h3>
        <div className="text-sm space-y-1">
          <div>PII Instances: {safetyScan.pii_matches}</div>
          <div>Moderation Flags: {safetyScan.moderation_flags}</div>
          <div>Status: {safetyScan.passed ? '✓ Passed' : '⚠️ Warnings'}</div>
        </div>
      </div>

      {/* Content Summary */}
      <div className="border rounded-lg p-4">
        <h3 className="font-semibold mb-2">Content Summary</h3>
        <div className="text-sm space-y-1">
          <div>Total Chunks: {chunks.length}</div>
          <div>Average Chunk Size: {Math.round(chunks.reduce((sum, c) => sum + c.text.length, 0) / chunks.length)} chars</div>
        </div>
      </div>

      {/* Namespace Selection */}
      <div>
        <label className="block font-medium mb-2">Target Namespace</label>
        <select
          value={namespace}
          onChange={(e) => setNamespace(e.target.value)}
          className="w-full px-3 py-2 border rounded-lg"
        >
          {namespaces.map((ns) => (
            <option key={ns} value={ns}>{ns}</option>
          ))}
        </select>
      </div>

      {/* Validation Checklist */}
      <div className="border rounded-lg p-4 space-y-3">
        <h3 className="font-semibold">Validation Checklist</h3>
        {Object.entries({
          provenanceVerified: 'Provenance information verified and accurate',
          licenseConfirmed: 'License allows publication and attribution is correct',
          contentReviewed: 'Content reviewed and appropriate for publication',
          safetyApproved: 'Safety scan results reviewed and acceptable',
        }).map(([key, label]) => (
          <label key={key} className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={checklist[key as keyof typeof checklist]}
              onChange={(e) =>
                setChecklist((prev) => ({ ...prev, [key]: e.target.checked }))
              }
              className="rounded border-gray-300 text-blue-600"
            />
            <span className="text-sm">{label}</span>
          </label>
        ))}
      </div>

      <div className="flex justify-between pt-4 border-t">
        <button onClick={onBack} className="px-6 py-2 border rounded-lg">
          Back
        </button>
        <button
          onClick={() => onReviewComplete(namespace)}
          disabled={!allChecked}
          className={`px-6 py-2 rounded-lg font-medium ${
            allChecked
              ? 'bg-blue-600 hover:bg-blue-700 text-white'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          Continue to Publish
        </button>
      </div>
    </div>
  );
};

export default ReviewStep;
