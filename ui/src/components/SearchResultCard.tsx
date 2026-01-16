/**
 * SearchResultCard component with provenance display
 */

import React, { useState } from 'react';
import {
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  FileText,
  Calendar,
  Tag,
  Scale,
} from 'lucide-react';
import type { SearchResult } from '@types/search';
import { getNamespaceColor } from '@utils/namespaces';
import { formatPercent, getScoreColor, getScoreWidth } from '@utils/format';
import { ExportService } from '@services/exportService';
import clsx from 'clsx';

interface SearchResultCardProps {
  result: SearchResult;
  query?: string;
  className?: string;
}

export function SearchResultCard({ result, query, className }: SearchResultCardProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copiedFormat, setCopiedFormat] = useState<string | null>(null);

  const handleCopy = async (format: 'bibtex' | 'apa' | 'mla') => {
    let citation: string;
    switch (format) {
      case 'bibtex':
        citation = ExportService.toBibTeX(result);
        break;
      case 'apa':
        citation = ExportService.toAPA(result);
        break;
      case 'mla':
        citation = ExportService.toMLA(result);
        break;
    }

    await ExportService.copyToClipboard(citation);
    setCopiedFormat(format);
    setTimeout(() => setCopiedFormat(null), 2000);
  };

  const highlightQuery = (text: string) => {
    if (!query) return text;

    const parts = text.split(new RegExp(`(${query})`, 'gi'));
    return parts.map((part, i) =>
      part.toLowerCase() === query.toLowerCase() ? (
        <mark key={i} className="bg-yellow-200 font-medium">
          {part}
        </mark>
      ) : (
        part
      )
    );
  };

  return (
    <div
      className={clsx(
        'rounded-lg border border-gray-200 bg-white p-5 shadow-sm transition-shadow hover:shadow-md',
        className
      )}
    >
      {/* Header with rank and score */}
      <div className="mb-3 flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-100 text-sm font-bold text-primary-900">
            {result.rank}
          </div>
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {result.metadata.citation_label}
            </h3>
            <a
              href={result.metadata.canonical_url}
              target="_blank"
              rel="noopener noreferrer"
              className="group flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700"
            >
              <span className="underline">{result.metadata.canonical_url}</span>
              <ExternalLink className="h-3 w-3 transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5" />
            </a>
          </div>
        </div>

        {/* Relevance Score */}
        <div className="flex flex-col items-end gap-1">
          <span className={clsx('text-sm font-semibold', getScoreColor(result.score))}>
            {formatPercent(result.score, 0)}
          </span>
          <div className="h-1 w-24 overflow-hidden rounded-full bg-gray-200">
            <div
              className="h-full bg-gradient-to-r from-yellow-400 via-green-400 to-green-600"
              style={{ width: getScoreWidth(result.score) }}
            />
          </div>
        </div>
      </div>

      {/* Content Preview */}
      <div className="mb-4">
        <p className="text-sm leading-relaxed text-gray-700">
          {highlightQuery(result.content)}
        </p>
      </div>

      {/* Metadata Badges */}
      <div className="mb-4 flex flex-wrap gap-2">
        {/* Namespace */}
        <span className={clsx('rounded-md px-2 py-1 text-xs font-medium', getNamespaceColor(result.namespace))}>
          {result.namespace}
        </span>

        {/* Source Organization */}
        <span className="flex items-center gap-1 rounded-md bg-blue-100 px-2 py-1 text-xs font-medium text-blue-900">
          <FileText className="h-3 w-3" />
          {result.metadata.source_org}
        </span>

        {/* Year */}
        <span className="flex items-center gap-1 rounded-md bg-gray-100 px-2 py-1 text-xs font-medium text-gray-900">
          <Calendar className="h-3 w-3" />
          {result.metadata.year}
        </span>

        {/* Content Type */}
        <span className="rounded-md bg-purple-100 px-2 py-1 text-xs font-medium text-purple-900 capitalize">
          {result.metadata.content_type}
        </span>

        {/* License */}
        <span className="flex items-center gap-1 rounded-md bg-green-100 px-2 py-1 text-xs font-medium text-green-900">
          <Scale className="h-3 w-3" />
          {result.metadata.license}
        </span>
      </div>

      {/* Tags */}
      {result.metadata.tags.length > 0 && (
        <div className="mb-4 flex flex-wrap items-center gap-2">
          <Tag className="h-4 w-4 text-gray-400" />
          {result.metadata.tags.map((tag) => (
            <span
              key={tag}
              className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-700"
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Citation Export Actions */}
      <div className="flex items-center justify-between border-t border-gray-100 pt-4">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center gap-1 text-sm font-medium text-gray-600 hover:text-gray-900"
        >
          {isExpanded ? (
            <>
              <ChevronUp className="h-4 w-4" />
              Hide citation formats
            </>
          ) : (
            <>
              <ChevronDown className="h-4 w-4" />
              Show citation formats
            </>
          )}
        </button>

        <div className="flex gap-2">
          {(['bibtex', 'apa', 'mla'] as const).map((format) => (
            <button
              key={format}
              onClick={() => handleCopy(format)}
              className={clsx(
                'flex items-center gap-1 rounded-md px-3 py-1.5 text-xs font-medium transition-colors',
                copiedFormat === format
                  ? 'bg-green-100 text-green-900'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              )}
            >
              {copiedFormat === format ? (
                <>
                  <Check className="h-3 w-3" />
                  Copied
                </>
              ) : (
                <>
                  <Copy className="h-3 w-3" />
                  {format.toUpperCase()}
                </>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Expanded Citation Formats */}
      {isExpanded && (
        <div className="mt-4 space-y-3 border-t border-gray-100 pt-4">
          <CitationBlock
            title="BibTeX"
            content={ExportService.toBibTeX(result)}
          />
          <CitationBlock
            title="APA"
            content={ExportService.toAPA(result)}
          />
          <CitationBlock
            title="MLA"
            content={ExportService.toMLA(result)}
          />
        </div>
      )}
    </div>
  );
}

interface CitationBlockProps {
  title: string;
  content: string;
}

function CitationBlock({ title, content }: CitationBlockProps) {
  return (
    <div>
      <div className="mb-1 text-xs font-medium text-gray-600">{title}</div>
      <pre className="overflow-x-auto rounded-md bg-gray-50 p-3 text-xs text-gray-800">
        {content}
      </pre>
    </div>
  );
}
