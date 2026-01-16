/**
 * AgentResponse Component
 *
 * Renders structured AI agent responses with citations, metadata, and provenance.
 * Designed specifically for answer_json format rendering.
 * Part of @ainative/ai-kit-react component library.
 */

import React from 'react';
import { clsx } from 'clsx';
import type { AnswerJsonContract } from '../../types/answer-json';
import { MarkdownRenderer } from './MarkdownRenderer';
import { Badge } from './Badge';
import { AlertCircle, CheckCircle2 } from 'lucide-react';

export interface AgentResponseProps {
  data: AnswerJsonContract;
  className?: string;
}

export const AgentResponse: React.FC<AgentResponseProps> = ({ data, className }) => {
  const { answer, integrity, persona, model_mode } = data;

  return (
    <div className={clsx('agent-response space-y-4', className)}>
      {/* Header with metadata */}
      <div className="flex items-center gap-2 flex-wrap">
        {persona && (
          <Badge variant="blue" size="sm">
            {persona.charAt(0).toUpperCase() + persona.slice(1)}
          </Badge>
        )}
        {model_mode && (
          <Badge variant="gray" size="sm">
            {model_mode}
          </Badge>
        )}
        {answer.completeness && (
          <Badge
            variant={answer.completeness === 'complete' ? 'green' : 'yellow'}
            size="sm"
          >
            {answer.completeness}
          </Badge>
        )}
        {answer.confidence !== undefined && (
          <Badge variant="purple" size="sm">
            Confidence: {(answer.confidence * 100).toFixed(0)}%
          </Badge>
        )}
      </div>

      {/* Main answer text */}
      <div className="agent-response-content">
        <MarkdownRenderer content={answer.text} />
      </div>

      {/* Integrity indicators */}
      {integrity && (
        <div className="flex items-center gap-4 text-sm">
          {integrity.citations_provided !== undefined && (
            <div className="flex items-center gap-1">
              {integrity.citations_provided ? (
                <CheckCircle2 size={16} className="text-green-600" />
              ) : (
                <AlertCircle size={16} className="text-amber-600" />
              )}
              <span className="text-gray-600">
                Citations {integrity.citations_provided ? 'provided' : 'not provided'}
              </span>
            </div>
          )}
          {integrity.retrieval_confidence && (
            <div className="flex items-center gap-1">
              <span className="text-gray-600">
                Retrieval confidence:
                <span className={clsx(
                  'ml-1 font-medium',
                  integrity.retrieval_confidence === 'high' && 'text-green-600',
                  integrity.retrieval_confidence === 'medium' && 'text-yellow-600',
                  integrity.retrieval_confidence === 'low' && 'text-orange-600',
                )}>
                  {integrity.retrieval_confidence}
                </span>
              </span>
            </div>
          )}
        </div>
      )}

      {/* Safety flags warning */}
      {integrity?.safety_flags && integrity.safety_flags.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-md p-3 flex items-start gap-2">
          <AlertCircle size={16} className="text-amber-600 mt-0.5" />
          <div>
            <p className="text-sm font-medium text-amber-900">Safety Flags</p>
            <p className="text-sm text-amber-700">
              {integrity.safety_flags.join(', ')}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
