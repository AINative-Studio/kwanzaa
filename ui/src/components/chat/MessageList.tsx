/**
 * MessageList Component
 *
 * Displays list of chat messages with answer_json rendering.
 */

import React from 'react';
import { clsx } from 'clsx';
import type { RLHFeedback } from '../../types/answer-json';
import { AnswerJsonRenderer } from '../answer/AnswerJsonRenderer';
import { User, Bot } from 'lucide-react';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  answerJson?: any;
  timestamp: Date;
}

export interface MessageListProps {
  messages: Message[];
  onFeedback: (feedback: RLHFeedback) => void;
  className?: string;
}

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  onFeedback,
  className,
}) => {
  if (messages.length === 0) {
    return (
      <div className={clsx('message-list-empty flex items-center justify-center h-full', className)}>
        <div className="text-center max-w-md">
          <Bot size={64} className="mx-auto text-gray-400 mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            Welcome to Kwanzaa Chat
          </h3>
          <p className="text-gray-600">
            Ask questions and get answers backed by primary sources and citations.
            Choose your persona and mode to customize the experience.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className={clsx('message-list space-y-6', className)}>
      {messages.map((message) => (
        <div
          key={message.id}
          className={clsx(
            'message flex gap-4',
            message.role === 'user' ? 'justify-end' : 'justify-start'
          )}
        >
          {message.role === 'assistant' && (
            <div className="flex-shrink-0 w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
              <Bot size={20} className="text-blue-600" />
            </div>
          )}

          <div
            className={clsx(
              'flex-1 max-w-3xl',
              message.role === 'user' ? 'text-right' : ''
            )}
          >
            {message.role === 'user' ? (
              <div className="inline-block bg-blue-600 text-white rounded-lg px-4 py-3">
                <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              </div>
            ) : message.answerJson ? (
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <AnswerJsonRenderer
                  data={message.answerJson}
                  messageId={message.id}
                  onFeedback={onFeedback}
                />
              </div>
            ) : (
              <div className="bg-white rounded-lg border border-gray-200 p-4">
                <p className="text-sm text-gray-900 whitespace-pre-wrap">{message.content}</p>
              </div>
            )}

            <p className="text-xs text-gray-500 mt-1">
              {message.timestamp.toLocaleTimeString()}
            </p>
          </div>

          {message.role === 'user' && (
            <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center">
              <User size={20} className="text-gray-600" />
            </div>
          )}
        </div>
      ))}
    </div>
  );
};
