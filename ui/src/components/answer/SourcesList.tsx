/**
 * SourcesList Component
 *
 * Displays citations and sources with full provenance metadata.
 * Enforces Imani (Faith) through transparent source attribution.
 */

import React from 'react';
import { clsx } from 'clsx';
import type { Source } from '../../types/answer-json';
import { ExternalLink, BookOpen, Calendar, Tag } from 'lucide-react';
import { Badge } from '../aikit/Badge';

export interface SourcesListProps {
  sources: Source[];
  className?: string;
}

export const SourcesList: React.FC<SourcesListProps> = ({ sources, className }) => {
  if (sources.length === 0) {
    return null;
  }

  return (
    <div className={clsx('sources-list space-y-3', className)}>
      <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
        <BookOpen size={16} />
        Sources ({sources.length})
      </h3>

      {sources.map((source, idx) => (
        <div
          key={source.chunk_id}
          className="bg-white border border-gray-200 rounded-lg p-4 space-y-2"
        >
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <a
                href={source.canonical_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 font-medium text-sm flex items-center gap-2 transition-colors"
              >
                {source.citation_label}
                <ExternalLink size={14} />
              </a>
              <p className="text-xs text-gray-600 mt-1">{source.source_org}</p>
            </div>
            {source.relevance_score !== undefined && (
              <Badge variant="purple" size="sm">
                {(source.relevance_score * 100).toFixed(0)}% match
              </Badge>
            )}
          </div>

          <div className="flex items-center gap-4 text-xs text-gray-500">
            <span className="flex items-center gap-1">
              <Calendar size={12} />
              {source.year}
            </span>
            <span className="capitalize">{source.content_type}</span>
            <span>{source.license}</span>
          </div>

          {source.tags && source.tags.length > 0 && (
            <div className="flex items-center gap-2 flex-wrap">
              <Tag size={12} className="text-gray-400" />
              {source.tags.map((tag) => (
                <Badge key={tag} variant="gray" size="sm">
                  {tag}
                </Badge>
              ))}
            </div>
          )}

          <div className="pt-2 border-t border-gray-100 text-xs text-gray-500">
            <span className="font-medium">Namespace:</span> {source.namespace}
          </div>
        </div>
      ))}
    </div>
  );
};
