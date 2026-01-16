/**
 * FeedbackButtons Component
 *
 * Provides thumbs up/down feedback buttons for RLHF collection.
 * Part of @ainative/ai-kit-rlhf integration.
 */

import React, { useState } from 'react';
import { clsx } from 'clsx';
import { ThumbsUp, ThumbsDown } from 'lucide-react';
import type { RLHFeedback } from '../../types/answer-json';
import { DetailedFeedbackModal } from './DetailedFeedbackModal';

export interface FeedbackButtonsProps {
  messageId: string;
  onFeedback: (feedback: RLHFeedback) => void;
  className?: string;
}

export const FeedbackButtons: React.FC<FeedbackButtonsProps> = ({
  messageId,
  onFeedback,
  className,
}) => {
  const [feedback, setFeedback] = useState<'up' | 'down' | null>(null);
  const [showDetailedModal, setShowDetailedModal] = useState(false);

  const handleThumbsUp = () => {
    setFeedback('up');
    onFeedback({
      message_id: messageId,
      feedback_type: 'thumbs_up',
      timestamp: new Date(),
    });
  };

  const handleThumbsDown = () => {
    setFeedback('down');
    setShowDetailedModal(true);
  };

  const handleDetailedFeedback = (detailedFeedback: RLHFeedback) => {
    onFeedback(detailedFeedback);
    setShowDetailedModal(false);
  };

  return (
    <>
      <div className={clsx('feedback-buttons flex items-center gap-2', className)}>
        <button
          onClick={handleThumbsUp}
          disabled={feedback === 'up'}
          className={clsx(
            'p-2 rounded-md border transition-all',
            feedback === 'up'
              ? 'bg-green-100 border-green-300 text-green-700'
              : 'bg-white border-gray-300 text-gray-600 hover:bg-gray-50 hover:border-gray-400'
          )}
          title="This was helpful"
        >
          <ThumbsUp size={16} />
        </button>
        <button
          onClick={handleThumbsDown}
          disabled={feedback === 'down'}
          className={clsx(
            'p-2 rounded-md border transition-all',
            feedback === 'down'
              ? 'bg-red-100 border-red-300 text-red-700'
              : 'bg-white border-gray-300 text-gray-600 hover:bg-gray-50 hover:border-gray-400'
          )}
          title="This was not helpful"
        >
          <ThumbsDown size={16} />
        </button>
      </div>

      {showDetailedModal && (
        <DetailedFeedbackModal
          messageId={messageId}
          onSubmit={handleDetailedFeedback}
          onClose={() => setShowDetailedModal(false)}
        />
      )}
    </>
  );
};
