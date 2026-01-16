/**
 * SafetyIndicator Component
 *
 * Displays safety check results and warnings to users.
 * Part of @ainative/ai-kit-safety integration.
 */

import React from 'react';
import { clsx } from 'clsx';
import type { SafetyResult } from '../../types/answer-json';
import { Shield, ShieldAlert, AlertTriangle } from 'lucide-react';

export interface SafetyIndicatorProps {
  result: SafetyResult;
  className?: string;
}

export const SafetyIndicator: React.FC<SafetyIndicatorProps> = ({ result, className }) => {
  if (result.overallSafe && result.warnings.length === 0) {
    return null; // Don't show anything if all is safe
  }

  return (
    <div className={clsx('safety-indicator', className)}>
      {!result.overallSafe && (
        <div className="bg-red-50 border border-red-200 rounded-md p-3 flex items-start gap-2">
          <ShieldAlert size={20} className="text-red-600 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-medium text-red-900">Safety Check Failed</p>
            <p className="text-sm text-red-700 mt-1">
              This content may violate safety policies and cannot be processed.
            </p>
            <div className="mt-2 space-y-1">
              {result.checks
                .filter(check => !check.passed)
                .map((check, idx) => (
                  <div key={idx} className="text-xs text-red-600">
                    {check.type}: {check.details || 'Failed'}
                  </div>
                ))}
            </div>
          </div>
        </div>
      )}

      {result.overallSafe && result.warnings.length > 0 && (
        <div className="bg-amber-50 border border-amber-200 rounded-md p-3 flex items-start gap-2">
          <AlertTriangle size={20} className="text-amber-600 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-sm font-medium text-amber-900">Safety Warnings</p>
            <ul className="mt-1 space-y-1">
              {result.warnings.map((warning, idx) => (
                <li key={idx} className="text-sm text-amber-700">{warning}</li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};
