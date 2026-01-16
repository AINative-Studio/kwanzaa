/**
 * SearchResults component with pagination
 */

import React, { useState } from 'react';
import { AlertCircle, Download, FileDown } from 'lucide-react';
import type { SearchResponse } from '@types/search';
import { SearchResultCard } from './SearchResultCard';
import { ExportService } from '@services/exportService';
import { formatDuration, formatNumber } from '@utils/format';
import clsx from 'clsx';

interface SearchResultsProps {
  response: SearchResponse;
  className?: string;
}

export function SearchResults({ response, className }: SearchResultsProps) {
  const [currentPage, setCurrentPage] = useState(1);
  const resultsPerPage = 10;

  const totalPages = Math.ceil(response.results.length / resultsPerPage);
  const startIndex = (currentPage - 1) * resultsPerPage;
  const endIndex = startIndex + resultsPerPage;
  const currentResults = response.results.slice(startIndex, endIndex);

  const handleExport = (format: 'bibtex' | 'apa' | 'mla' | 'json' | 'csv') => {
    let content: string;
    let filename: string;
    let mimeType: string;

    switch (format) {
      case 'bibtex':
        content = ExportService.exportAsBibTeX(response.results);
        filename = 'search-results.bib';
        mimeType = 'text/plain';
        break;
      case 'apa':
        content = ExportService.exportAsAPA(response.results);
        filename = 'search-results-apa.txt';
        mimeType = 'text/plain';
        break;
      case 'mla':
        content = ExportService.exportAsMLA(response.results);
        filename = 'search-results-mla.txt';
        mimeType = 'text/plain';
        break;
      case 'json':
        content = ExportService.exportAsJSON(response.results);
        filename = 'search-results.json';
        mimeType = 'application/json';
        break;
      case 'csv':
        content = ExportService.exportAsCSV(response.results);
        filename = 'search-results.csv';
        mimeType = 'text/csv';
        break;
    }

    ExportService.downloadFile(content, filename, mimeType);
  };

  if (response.results.length === 0) {
    return (
      <div className={clsx('rounded-lg border border-gray-200 bg-white p-12 text-center', className)}>
        <AlertCircle className="mx-auto mb-4 h-12 w-12 text-gray-400" />
        <h3 className="mb-2 text-lg font-semibold text-gray-900">No results found</h3>
        <p className="text-gray-600">
          Try adjusting your search query or filters to find what you're looking for.
        </p>
      </div>
    );
  }

  return (
    <div className={clsx('space-y-6', className)}>
      {/* Results Header */}
      <div className="flex items-center justify-between rounded-lg border border-gray-200 bg-white px-5 py-4 shadow-sm">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <h2 className="text-lg font-semibold text-gray-900">
              Search Results
            </h2>
            <span className="rounded-full bg-primary-100 px-2.5 py-0.5 text-sm font-medium text-primary-900">
              {formatNumber(response.total_results)} results
            </span>
          </div>
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <span>Query: "{response.query.text}"</span>
            <span>•</span>
            <span>Namespace: {response.query.namespace || 'All'}</span>
            <span>•</span>
            <span>Time: {formatDuration(response.search_metadata.execution_time_ms)}</span>
          </div>
        </div>

        {/* Export Dropdown */}
        <div className="relative">
          <button
            onClick={() => {}}
            className="flex items-center gap-2 rounded-md bg-gray-100 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-200"
          >
            <Download className="h-4 w-4" />
            Export
          </button>

          {/* Export Menu (simplified for now) */}
          <div className="absolute right-0 top-full z-10 mt-2 hidden w-48 rounded-md border border-gray-200 bg-white shadow-lg">
            {(['bibtex', 'apa', 'mla', 'json', 'csv'] as const).map((format) => (
              <button
                key={format}
                onClick={() => handleExport(format)}
                className="flex w-full items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
              >
                <FileDown className="h-4 w-4" />
                {format.toUpperCase()}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Results List */}
      <div className="space-y-4">
        {currentResults.map((result) => (
          <SearchResultCard
            key={result.chunk_id}
            result={result}
            query={response.query.text}
          />
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
            disabled={currentPage === 1}
            className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>

          <div className="flex items-center gap-1">
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
              <button
                key={page}
                onClick={() => setCurrentPage(page)}
                className={clsx(
                  'h-10 w-10 rounded-md text-sm font-medium transition-colors',
                  page === currentPage
                    ? 'bg-primary-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'
                )}
              >
                {page}
              </button>
            ))}
          </div>

          <button
            onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
            disabled={currentPage === totalPages}
            className="rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
