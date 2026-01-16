/**
 * StreamingMessage Component
 *
 * Renders streaming AI responses with typing indicators and smooth animations.
 * Part of @ainative/ai-kit-react component library.
 */

import React from 'react';
import { clsx } from 'clsx';

export interface StreamingMessageProps {
  content: string;
  isStreaming?: boolean;
  className?: string;
}

export const StreamingMessage: React.FC<StreamingMessageProps> = ({
  content,
  isStreaming = false,
  className,
}) => {
  return (
    <div className={clsx('streaming-message', className)}>
      <div className="prose prose-slate max-w-none">
        {content}
      </div>
      {isStreaming && (
        <span className="inline-flex items-center ml-2">
          <span className="animate-pulse">▋</span>
        </span>
      )}
    </div>
  );
};
