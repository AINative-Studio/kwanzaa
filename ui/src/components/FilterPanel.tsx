/**
 * FilterPanel component with all search filters
 */

import React, { useState } from 'react';
import { Filter, X, ChevronDown, ChevronUp } from 'lucide-react';
import type { ProvenanceFilters } from '@types/search';
import { NAMESPACES, getNamespaceColor } from '@utils/namespaces';
import clsx from 'clsx';

interface FilterPanelProps {
  filters?: ProvenanceFilters;
  namespace?: string;
  onChange: (filters: ProvenanceFilters) => void;
  onNamespaceChange: (namespace?: string) => void;
  className?: string;
}

export function FilterPanel({
  filters = {},
  namespace,
  onChange,
  onNamespaceChange,
  className,
}: FilterPanelProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [yearRangeMin, setYearRangeMin] = useState(filters.year_gte ?? 1600);
  const [yearRangeMax, setYearRangeMax] = useState(filters.year_lte ?? 2026);

  const contentTypes = [
    'speech',
    'letter',
    'proclamation',
    'article',
    'book',
    'report',
    'testimony',
    'interview',
  ];

  const handleYearRangeChange = (min: number, max: number) => {
    setYearRangeMin(min);
    setYearRangeMax(max);
    onChange({
      ...filters,
      year_gte: min,
      year_lte: max,
    });
  };

  const handleContentTypeToggle = (type: string) => {
    const current = filters.content_type || [];
    const updated = current.includes(type)
      ? current.filter(t => t !== type)
      : [...current, type];

    onChange({
      ...filters,
      content_type: updated.length > 0 ? updated : undefined,
    });
  };

  const handleSourceOrgChange = (orgs: string[]) => {
    onChange({
      ...filters,
      source_org: orgs.length > 0 ? orgs : undefined,
    });
  };

  const handleTagsChange = (tags: string[]) => {
    onChange({
      ...filters,
      tags: tags.length > 0 ? tags : undefined,
    });
  };

  const clearAllFilters = () => {
    setYearRangeMin(1600);
    setYearRangeMax(2026);
    onChange({});
    onNamespaceChange(undefined);
  };

  const hasActiveFilters =
    filters.year_gte ||
    filters.year_lte ||
    filters.source_org?.length ||
    filters.content_type?.length ||
    filters.tags?.length ||
    namespace;

  return (
    <div className={clsx('rounded-lg border border-gray-200 bg-white shadow-sm', className)}>
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3">
        <div className="flex items-center gap-2">
          <Filter className="h-5 w-5 text-gray-600" />
          <h3 className="text-sm font-medium text-gray-900">Filters</h3>
          {hasActiveFilters && (
            <span className="rounded-full bg-primary-100 px-2 py-0.5 text-xs font-medium text-primary-700">
              Active
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {hasActiveFilters && (
            <button
              onClick={clearAllFilters}
              className="text-sm text-gray-600 hover:text-gray-900"
            >
              Clear all
            </button>
          )}
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="rounded-md p-1 hover:bg-gray-100"
          >
            {isExpanded ? (
              <ChevronUp className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </button>
        </div>
      </div>

      {/* Filter Content */}
      {isExpanded && (
        <div className="space-y-6 p-4">
          {/* Namespace Selector */}
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">
              Namespace
            </label>
            <div className="space-y-2">
              <button
                onClick={() => onNamespaceChange(undefined)}
                className={clsx(
                  'w-full rounded-md px-3 py-2 text-left text-sm transition-colors',
                  !namespace
                    ? 'bg-primary-100 text-primary-900 font-medium'
                    : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                )}
              >
                All Namespaces
              </button>
              {NAMESPACES.map((ns) => (
                <button
                  key={ns.value}
                  onClick={() => onNamespaceChange(ns.value)}
                  className={clsx(
                    'w-full rounded-md px-3 py-2 text-left text-sm transition-colors',
                    namespace === ns.value
                      ? `${ns.color} font-medium`
                      : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
                  )}
                >
                  <div className="font-medium">{ns.label}</div>
                  <div className="text-xs opacity-75">{ns.description}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Year Range */}
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">
              Year Range
            </label>
            <div className="space-y-3">
              <input
                type="range"
                min="1600"
                max="2026"
                value={yearRangeMin}
                onChange={(e) => handleYearRangeChange(Number(e.target.value), yearRangeMax)}
                className="w-full"
              />
              <input
                type="range"
                min="1600"
                max="2026"
                value={yearRangeMax}
                onChange={(e) => handleYearRangeChange(yearRangeMin, Number(e.target.value))}
                className="w-full"
              />
              <div className="flex items-center justify-between text-sm text-gray-600">
                <input
                  type="number"
                  min="1600"
                  max={yearRangeMax}
                  value={yearRangeMin}
                  onChange={(e) => handleYearRangeChange(Number(e.target.value), yearRangeMax)}
                  className="w-20 rounded border border-gray-300 px-2 py-1 text-center"
                />
                <span>to</span>
                <input
                  type="number"
                  min={yearRangeMin}
                  max="2026"
                  value={yearRangeMax}
                  onChange={(e) => handleYearRangeChange(yearRangeMin, Number(e.target.value))}
                  className="w-20 rounded border border-gray-300 px-2 py-1 text-center"
                />
              </div>
            </div>
          </div>

          {/* Content Type */}
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">
              Content Type
            </label>
            <div className="space-y-2">
              {contentTypes.map((type) => (
                <label key={type} className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    checked={filters.content_type?.includes(type) ?? false}
                    onChange={() => handleContentTypeToggle(type)}
                    className="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700 capitalize">{type}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Active Filter Chips */}
          {hasActiveFilters && (
            <div className="space-y-2 border-t border-gray-200 pt-4">
              <div className="text-xs font-medium text-gray-700">Active Filters:</div>
              <div className="flex flex-wrap gap-2">
                {namespace && (
                  <FilterChip
                    label={`Namespace: ${NAMESPACES.find(ns => ns.value === namespace)?.label}`}
                    onRemove={() => onNamespaceChange(undefined)}
                  />
                )}
                {(filters.year_gte || filters.year_lte) && (
                  <FilterChip
                    label={`Year: ${yearRangeMin}-${yearRangeMax}`}
                    onRemove={() => handleYearRangeChange(1600, 2026)}
                  />
                )}
                {filters.content_type?.map((type) => (
                  <FilterChip
                    key={type}
                    label={`Type: ${type}`}
                    onRemove={() => handleContentTypeToggle(type)}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

interface FilterChipProps {
  label: string;
  onRemove: () => void;
}

function FilterChip({ label, onRemove }: FilterChipProps) {
  return (
    <div className="flex items-center gap-1 rounded-full bg-primary-100 px-3 py-1 text-xs text-primary-900">
      <span>{label}</span>
      <button
        onClick={onRemove}
        className="hover:text-primary-700"
        aria-label="Remove filter"
      >
        <X className="h-3 w-3" />
      </button>
    </div>
  );
}
