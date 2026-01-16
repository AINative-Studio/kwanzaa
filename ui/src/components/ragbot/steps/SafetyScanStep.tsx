/**
 * Safety Scan Step Component
 *
 * Runs PII detection and content moderation on uploaded documents.
 * CRITICAL: Required by Issue #38 - Safety Integration
 */

import React, { useState, useEffect } from 'react';
import PIIDetector, { PIIMatch } from '../../../lib/aikit/safety/PIIDetector';
import ContentModerator, { ModerationResult } from '../../../lib/aikit/safety/ContentModerator';
import StreamingIndicator from '../../../lib/aikit/react/StreamingIndicator';
import ToolResult from '../../../lib/aikit/react/ToolResult';
import { DocumentMetadata, SafetyScanResult } from '../RAGBotUploadWorkflow';

interface SafetyScanStepProps {
  documentId: string;
  metadata: DocumentMetadata;
  onScanComplete: (result: SafetyScanResult) => void;
  onBack: () => void;
}

export const SafetyScanStep: React.FC<SafetyScanStepProps> = ({
  documentId,
  metadata,
  onScanComplete,
  onBack,
}) => {
  const [scanning, setScanning] = useState(true);
  const [documentText, setDocumentText] = useState('');
  const [piiMatches, setPiiMatches] = useState<PIIMatch[]>([]);
  const [moderationResults, setModerationResults] = useState<ModerationResult[]>([]);
  const [autoRedact, setAutoRedact] = useState(false);
  const [curatorDecision, setCuratorDecision] = useState<'proceed' | 'cancel' | 'redact' | null>(
    null
  );

  useEffect(() => {
    performSafetyScan();
  }, [documentId]);

  const performSafetyScan = async () => {
    try {
      setScanning(true);

      // Fetch document text for scanning
      const response = await fetch(`/api/v1/ragbot/document/${documentId}/text`);
      if (!response.ok) {
        throw new Error('Failed to fetch document text');
      }

      const { text } = await response.json();
      setDocumentText(text);

      // Run safety scan
      const scanResponse = await fetch(`/api/v1/ragbot/scan-safety`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_id: documentId,
          text,
          metadata,
        }),
      });

      if (!scanResponse.ok) {
        throw new Error('Safety scan failed');
      }

      const scanResult = await scanResponse.json();
      setPiiMatches(scanResult.pii_matches || []);
      setModerationResults(scanResult.moderation_results || []);

      setScanning(false);
    } catch (error) {
      console.error('Safety scan error:', error);
      setScanning(false);
    }
  };

  const handleProceed = () => {
    const result: SafetyScanResult = {
      pii_matches: piiMatches.length,
      moderation_flags: moderationResults.filter((r) => r.detected).length,
      passed: true,
      report: {
        pii_matches: piiMatches,
        moderation_results: moderationResults,
        curator_decision: 'proceed',
        auto_redact: autoRedact,
      },
    };
    onScanComplete(result);
  };

  const handleCancel = () => {
    onBack();
  };

  const handleRedact = async () => {
    // Implement redaction logic
    setAutoRedact(true);
    setCuratorDecision('redact');
  };

  const hasPII = piiMatches.length > 0;
  const hasModerationFlags = moderationResults.some((r) => r.detected && r.confidence >= 0.5);
  const hasBlockingIssues = moderationResults.some(
    (r) => r.detected && r.severity === 'critical'
  );

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Safety Scan</h2>
        <p className="text-gray-600">
          Automated PII detection and content moderation analysis
        </p>
      </div>

      {scanning ? (
        <div className="flex flex-col items-center justify-center py-12 space-y-4">
          <StreamingIndicator variant="spinner" size="lg" color="primary" />
          <p className="text-lg font-medium text-gray-900">Scanning document...</p>
          <p className="text-sm text-gray-600">Running PII detection and content moderation</p>
        </div>
      ) : (
        <>
          {/* Safety Status Summary */}
          <div
            className={`border-2 rounded-lg p-4 ${
              hasBlockingIssues
                ? 'border-red-500 bg-red-50'
                : hasPII || hasModerationFlags
                ? 'border-yellow-500 bg-yellow-50'
                : 'border-green-500 bg-green-50'
            }`}
          >
            <div className="flex items-start space-x-3">
              <span className="text-2xl">
                {hasBlockingIssues ? '🚫' : hasPII || hasModerationFlags ? '⚠️' : '✓'}
              </span>
              <div className="flex-1">
                <h3 className="font-bold text-lg mb-1">
                  {hasBlockingIssues
                    ? 'Critical Issues Detected'
                    : hasPII || hasModerationFlags
                    ? 'Safety Warnings Found'
                    : 'Safety Scan Passed'}
                </h3>
                <div className="text-sm space-y-1">
                  <div>
                    PII Instances: <strong>{piiMatches.length}</strong>
                  </div>
                  <div>
                    Content Moderation Flags:{' '}
                    <strong>{moderationResults.filter((r) => r.detected).length}</strong>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* PII Detection Results */}
          {documentText && (
            <div>
              <h3 className="text-lg font-semibold mb-3">PII Detection</h3>
              <PIIDetector
                text={documentText.substring(0, 5000)} // Show first 5000 chars
                autoDetect
                showMatches
                onDetected={setPiiMatches}
              />
              {documentText.length > 5000 && (
                <p className="text-sm text-gray-600 mt-2">
                  Showing first 5,000 characters. Full document scanned.
                </p>
              )}
            </div>
          )}

          {/* Content Moderation Results */}
          <div>
            <h3 className="text-lg font-semibold mb-3">Content Moderation</h3>
            <ContentModerator
              text={documentText}
              autoModerate
              threshold={0.5}
              showRecommendations
              onResults={setModerationResults}
            />
          </div>

          {/* Safety Event Log */}
          <ToolResult
            toolName="Safety Scan Report"
            status="success"
            result={{
              document_id: documentId,
              scan_timestamp: new Date().toISOString(),
              pii_instances: piiMatches.length,
              moderation_flags: moderationResults.filter((r) => r.detected).length,
              severity: hasBlockingIssues ? 'critical' : hasPII || hasModerationFlags ? 'warning' : 'pass',
            }}
            collapsible
            defaultExpanded={false}
          />

          {/* Curator Decision Panel */}
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h3 className="font-semibold text-gray-900 mb-3">Curator Decision</h3>

            {hasPII && (
              <div className="mb-3">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={autoRedact}
                    onChange={(e) => setAutoRedact(e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700">
                    Auto-redact PII before publication
                  </span>
                </label>
              </div>
            )}

            <div className="space-y-2 text-sm text-gray-700">
              {hasBlockingIssues && (
                <div className="bg-red-100 border border-red-300 rounded p-2 text-red-900">
                  <strong>⚠️ Critical Content Detected:</strong> This document contains content
                  that violates publication policies. Manual review required before proceeding.
                </div>
              )}

              {hasPII && (
                <div className="bg-yellow-100 border border-yellow-300 rounded p-2 text-yellow-900">
                  <strong>PII Detected:</strong> Personal information found. Consider redaction
                  or verify that publication is appropriate.
                </div>
              )}

              {!hasBlockingIssues && !hasPII && !hasModerationFlags && (
                <div className="bg-green-100 border border-green-300 rounded p-2 text-green-900">
                  <strong>✓ No Issues:</strong> Document passed all safety checks.
                </div>
              )}
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center justify-between pt-4 border-t">
            <button
              onClick={onBack}
              className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Back
            </button>

            <div className="flex items-center space-x-3">
              <button
                onClick={handleCancel}
                className="px-6 py-2 border border-red-300 text-red-700 rounded-lg hover:bg-red-50 transition-colors"
              >
                Cancel Upload
              </button>

              {hasBlockingIssues ? (
                <button
                  disabled
                  className="px-6 py-2 bg-gray-400 text-white font-medium rounded-lg cursor-not-allowed"
                  title="Cannot proceed with critical content violations"
                >
                  Cannot Proceed
                </button>
              ) : (
                <button
                  onClick={handleProceed}
                  className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
                >
                  {hasPII || hasModerationFlags
                    ? 'Proceed with Warnings'
                    : 'Continue to Preview'}
                </button>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default SafetyScanStep;
