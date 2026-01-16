/**
 * DetailedFeedbackModal Component
 *
 * Modal for collecting detailed RLHF feedback with ratings and comments.
 * Part of @ainative/ai-kit-rlhf integration.
 */

import React, { useState } from 'react';
import { clsx } from 'clsx';
import { X } from 'lucide-react';
import type { RLHFeedback } from '../../types/answer-json';

export interface DetailedFeedbackModalProps {
  messageId: string;
  onSubmit: (feedback: RLHFeedback) => void;
  onClose: () => void;
}

export const DetailedFeedbackModal: React.FC<DetailedFeedbackModalProps> = ({
  messageId,
  onSubmit,
  onClose,
}) => {
  const [rating, setRating] = useState<number>(3);
  const [comment, setComment] = useState('');
  const [aspects, setAspects] = useState({
    accuracy: 3,
    helpfulness: 3,
    citation_quality: 3,
    persona_alignment: 3,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      message_id: messageId,
      feedback_type: 'detailed',
      rating,
      comment: comment.trim() || undefined,
      aspects,
      timestamp: new Date(),
    });
  };

  const renderStarRating = (value: number, onChange: (val: number) => void) => {
    return (
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <button
            key={star}
            type="button"
            onClick={() => onChange(star)}
            className={clsx(
              'text-2xl transition-colors',
              star <= value ? 'text-yellow-500' : 'text-gray-300'
            )}
          >
            ★
          </button>
        ))}
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Provide Feedback</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-4 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">
              Overall Rating
            </label>
            {renderStarRating(rating, setRating)}
          </div>

          <div className="space-y-4">
            <p className="text-sm font-medium text-gray-900">Rate Specific Aspects</p>

            <div>
              <label className="block text-sm text-gray-700 mb-1">Accuracy</label>
              {renderStarRating(aspects.accuracy, (val) => setAspects({ ...aspects, accuracy: val }))}
            </div>

            <div>
              <label className="block text-sm text-gray-700 mb-1">Helpfulness</label>
              {renderStarRating(aspects.helpfulness, (val) => setAspects({ ...aspects, helpfulness: val }))}
            </div>

            <div>
              <label className="block text-sm text-gray-700 mb-1">Citation Quality</label>
              {renderStarRating(aspects.citation_quality, (val) => setAspects({ ...aspects, citation_quality: val }))}
            </div>

            <div>
              <label className="block text-sm text-gray-700 mb-1">Persona Alignment</label>
              {renderStarRating(aspects.persona_alignment, (val) => setAspects({ ...aspects, persona_alignment: val }))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">
              Comments (optional)
            </label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={4}
              placeholder="What could be improved?"
            />
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Submit Feedback
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
