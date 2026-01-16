/**
 * CodeBlock Component
 *
 * Renders code blocks with syntax highlighting and copy functionality.
 * Also used for displaying citations and structured data.
 * Part of @ainative/ai-kit-react component library.
 */

import React, { useState } from 'react';
import { clsx } from 'clsx';
import { Copy, Check } from 'lucide-react';

export interface CodeBlockProps {
  code: string;
  language?: string;
  title?: string;
  showCopy?: boolean;
  className?: string;
}

export const CodeBlock: React.FC<CodeBlockProps> = ({
  code,
  language = 'text',
  title,
  showCopy = true,
  className,
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={clsx('code-block rounded-lg border border-gray-200 bg-gray-50', className)}>
      {title && (
        <div className="flex items-center justify-between px-4 py-2 border-b border-gray-200 bg-gray-100">
          <span className="text-sm font-medium text-gray-700">{title}</span>
          {showCopy && (
            <button
              onClick={handleCopy}
              className="text-gray-500 hover:text-gray-700 transition-colors"
              title="Copy to clipboard"
            >
              {copied ? <Check size={16} /> : <Copy size={16} />}
            </button>
          )}
        </div>
      )}
      <pre className="p-4 overflow-x-auto">
        <code className={`language-${language} text-sm`}>{code}</code>
      </pre>
    </div>
  );
};
