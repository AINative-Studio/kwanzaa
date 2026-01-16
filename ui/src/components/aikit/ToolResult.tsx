/**
 * ToolResult Component
 *
 * Renders tool execution results with collapsible details.
 * Used for displaying retrieval results and other tool outputs.
 * Part of @ainative/ai-kit-react component library.
 */

import React, { useState } from 'react';
import { clsx } from 'clsx';
import { ChevronDown, ChevronRight, ExternalLink } from 'lucide-react';
import type { RetrievalResult } from '../../types/answer-json';

export interface ToolResultProps {
  title: string;
  results: RetrievalResult[];
  defaultExpanded?: boolean;
  className?: string;
}

export const ToolResult: React.FC<ToolResultProps> = ({
  title,
  results,
  defaultExpanded = false,
  className,
}) => {
  const [isExpanded, setIsExpanded] = useState(defaultExpanded);

  return (
    <div className={clsx('tool-result border border-gray-200 rounded-lg', className)}>
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center gap-2">
          {isExpanded ? <ChevronDown size={20} /> : <ChevronRight size={20} />}
          <span className="font-medium text-gray-900">{title}</span>
          <span className="text-sm text-gray-500">({results.length} results)</span>
        </div>
      </button>

      {isExpanded && (
        <div className="border-t border-gray-200 p-4 space-y-4">
          {results.map((result) => (
            <div
              key={result.chunk_id}
              className="bg-white border border-gray-200 rounded-md p-4 space-y-2"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-900">
                      Rank {result.rank}
                    </span>
                    <span className="text-sm text-gray-500">
                      Score: {(result.score * 100).toFixed(1)}%
                    </span>
                  </div>
                  <p className="text-sm text-gray-700 mt-1">{result.citation_label}</p>
                </div>
                <a
                  href={result.canonical_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 transition-colors"
                  title="View source"
                >
                  <ExternalLink size={16} />
                </a>
              </div>

              {result.snippet && (
                <div className="bg-gray-50 rounded-md p-3 text-sm text-gray-700">
                  "{result.snippet}"
                </div>
              )}

              <div className="flex items-center gap-4 text-xs text-gray-500">
                <span>Namespace: {result.namespace}</span>
                <span>Doc: {result.doc_id}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
