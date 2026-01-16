/**
 * ChatInput Component
 *
 * Input field for user queries with send button.
 */

import React, { useState, useRef, useEffect } from 'react';
import { clsx } from 'clsx';
import { Send } from 'lucide-react';

export interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  className?: string;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSend,
  disabled = false,
  placeholder = 'Ask a question...',
  className,
}) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  }, [input]);

  return (
    <form onSubmit={handleSubmit} className={clsx('chat-input', className)}>
      <div className="flex gap-3">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder={placeholder}
          className={clsx(
            'flex-1 px-4 py-3 border border-gray-300 rounded-lg resize-none',
            'focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'disabled:bg-gray-100 disabled:text-gray-500 disabled:cursor-not-allowed'
          )}
          rows={1}
          maxLength={2000}
        />
        <button
          type="submit"
          disabled={!input.trim() || disabled}
          className={clsx(
            'px-6 py-3 rounded-lg font-medium transition-all flex items-center gap-2',
            'disabled:bg-gray-300 disabled:text-gray-500 disabled:cursor-not-allowed',
            !disabled && input.trim()
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-gray-300 text-gray-500'
          )}
        >
          <Send size={18} />
          Send
        </button>
      </div>
      <p className="text-xs text-gray-500 mt-2">
        Press Enter to send, Shift+Enter for new line
      </p>
    </form>
  );
};
