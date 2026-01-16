/**
 * ModeToggles Component
 *
 * Toggles for base, base+adapter, base+adapter+RAG modes.
 * Enforces Kujichagulia (Self-Determination) through user control.
 */

import React from 'react';
import { clsx } from 'clsx';
import type { ModelMode } from '../../types/answer-json';

export interface ModeTogglesProps {
  selected: ModelMode;
  onChange: (mode: ModelMode) => void;
  className?: string;
}

const modes: Array<{
  key: ModelMode;
  label: string;
  description: string;
}> = [
  {
    key: 'base_only',
    label: 'Base Only',
    description: 'Raw LLM without fine-tuning or retrieval',
  },
  {
    key: 'adapter_only',
    label: 'Base + Adapter',
    description: 'Fine-tuned for citations and refusal',
  },
  {
    key: 'base_adapter_rag',
    label: 'Base + Adapter + RAG',
    description: 'Full system with retrieval (recommended)',
  },
  {
    key: 'creative',
    label: 'Creative Mode',
    description: 'More flexibility, fewer constraints',
  },
];

export const ModeToggles: React.FC<ModeTogglesProps> = ({
  selected,
  onChange,
  className,
}) => {
  return (
    <div className={clsx('mode-toggles', className)}>
      <label className="block text-sm font-medium text-gray-900 mb-2">
        Select Mode
      </label>
      <div className="space-y-2">
        {modes.map((mode) => (
          <button
            key={mode.key}
            onClick={() => onChange(mode.key)}
            className={clsx(
              'w-full flex items-start gap-3 p-3 rounded-lg border-2 transition-all text-left',
              selected === mode.key
                ? 'border-blue-600 bg-blue-50'
                : 'border-gray-200 bg-white hover:border-gray-300 hover:bg-gray-50'
            )}
          >
            <div
              className={clsx(
                'w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-0.5',
                selected === mode.key
                  ? 'border-blue-600 bg-blue-600'
                  : 'border-gray-300 bg-white'
              )}
            >
              {selected === mode.key && (
                <div className="w-2 h-2 rounded-full bg-white" />
              )}
            </div>
            <div className="flex-1">
              <p className={clsx(
                'font-medium text-sm',
                selected === mode.key ? 'text-blue-900' : 'text-gray-900'
              )}>
                {mode.label}
              </p>
              <p className="text-xs text-gray-600 mt-0.5">{mode.description}</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};
