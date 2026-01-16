/**
 * StreamingIndicator Component
 *
 * Displays loading and streaming indicators for AI responses.
 * Part of @ainative/ai-kit-react component library.
 */

import React from 'react';
import { clsx } from 'clsx';

export interface StreamingIndicatorProps {
  text?: string;
  className?: string;
}

export const StreamingIndicator: React.FC<StreamingIndicatorProps> = ({
  text = 'Thinking...',
  className,
}) => {
  return (
    <div className={clsx('streaming-indicator flex items-center gap-2', className)}>
      <div className="flex gap-1">
        <span className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
        <span className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
        <span className="w-2 h-2 bg-blue-600 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
      </div>
      <span className="text-sm text-gray-600">{text}</span>
    </div>
  );
};
