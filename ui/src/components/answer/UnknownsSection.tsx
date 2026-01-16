/**
 * UnknownsSection Component
 *
 * Displays gaps, limitations, and clarifying questions.
 * Enforces Imani (Faith) through honest communication.
 */

import React from 'react';
import { clsx } from 'clsx';
import type { Unknowns } from '../../types/answer-json';
import { AlertCircle, HelpCircle, AlertTriangle } from 'lucide-react';

export interface UnknownsSectionProps {
  unknowns: Unknowns;
  className?: string;
}

export const UnknownsSection: React.FC<UnknownsSectionProps> = ({ unknowns, className }) => {
  const hasUnknowns =
    unknowns.unsupported_claims.length > 0 ||
    unknowns.missing_context.length > 0 ||
    unknowns.clarifying_questions.length > 0 ||
    (unknowns.out_of_scope && unknowns.out_of_scope.length > 0);

  if (!hasUnknowns) {
    return null;
  }

  return (
    <div className={clsx('unknowns-section space-y-3', className)}>
      <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
        <AlertCircle size={16} />
        What We Don't Know
      </h3>

      {unknowns.unsupported_claims.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <p className="text-sm font-medium text-red-900 mb-2 flex items-center gap-2">
            <AlertTriangle size={14} />
            Unsupported Claims
          </p>
          <ul className="space-y-1">
            {unknowns.unsupported_claims.map((claim, idx) => (
              <li key={idx} className="text-sm text-red-800">• {claim}</li>
            ))}
          </ul>
        </div>
      )}

      {unknowns.missing_context.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
          <p className="text-sm font-medium text-amber-900 mb-2 flex items-center gap-2">
            <AlertCircle size={14} />
            Missing Context
          </p>
          <ul className="space-y-1">
            {unknowns.missing_context.map((context, idx) => (
              <li key={idx} className="text-sm text-amber-800">• {context}</li>
            ))}
          </ul>
        </div>
      )}

      {unknowns.clarifying_questions.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <p className="text-sm font-medium text-blue-900 mb-2 flex items-center gap-2">
            <HelpCircle size={14} />
            Clarifying Questions
          </p>
          <ul className="space-y-1">
            {unknowns.clarifying_questions.map((question, idx) => (
              <li key={idx} className="text-sm text-blue-800">• {question}</li>
            ))}
          </ul>
        </div>
      )}

      {unknowns.out_of_scope && unknowns.out_of_scope.length > 0 && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
          <p className="text-sm font-medium text-gray-900 mb-2">Out of Scope</p>
          <ul className="space-y-1">
            {unknowns.out_of_scope.map((item, idx) => (
              <li key={idx} className="text-sm text-gray-700">• {item}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};
