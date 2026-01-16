/**
 * AnswerJsonRenderer Component
 *
 * Complete renderer for Kwanzaa answer_json format using AIKit components.
 * Displays answer, sources, retrieval summary, and unknowns with RLHF feedback.
 */

import React from 'react';
import { clsx } from 'clsx';
import type { AnswerJsonContract, RLHFeedback } from '../../types/answer-json';
import { AgentResponse } from '../aikit/AgentResponse';
import { ToolResult } from '../aikit/ToolResult';
import { SourcesList } from './SourcesList';
import { UnknownsSection } from './UnknownsSection';
import { FeedbackButtons } from '../rlhf/FeedbackButtons';

export interface AnswerJsonRendererProps {
  data: AnswerJsonContract;
  messageId: string;
  onFeedback: (feedback: RLHFeedback) => void;
  className?: string;
}

export const AnswerJsonRenderer: React.FC<AnswerJsonRendererProps> = ({
  data,
  messageId,
  onFeedback,
  className,
}) => {
  return (
    <div className={clsx('answer-json-renderer space-y-6', className)}>
      {/* Main Answer with AIKit AgentResponse */}
      <AgentResponse data={data} />

      {/* Sources */}
      {data.sources.length > 0 && (
        <SourcesList sources={data.sources} />
      )}

      {/* Retrieval Summary (Collapsible) */}
      {data.retrieval_summary.results.length > 0 && (
        <ToolResult
          title="Show Your Work - Retrieval Details"
          results={data.retrieval_summary.results}
          defaultExpanded={false}
        />
      )}

      {/* Unknowns */}
      <UnknownsSection unknowns={data.unknowns} />

      {/* Provenance metadata (small, subtle) */}
      {data.provenance && (
        <div className="text-xs text-gray-500 pt-4 border-t border-gray-200">
          <p>Generated at: {new Date(data.provenance.generated_at).toLocaleString()}</p>
          {data.provenance.retrieval_run_id && (
            <p>Retrieval ID: {data.provenance.retrieval_run_id}</p>
          )}
          {data.provenance.model_version && (
            <p>Model: {data.provenance.model_version}</p>
          )}
        </div>
      )}

      {/* RLHF Feedback Buttons */}
      <div className="pt-4 border-t border-gray-200">
        <FeedbackButtons messageId={messageId} onFeedback={onFeedback} />
      </div>
    </div>
  );
};
