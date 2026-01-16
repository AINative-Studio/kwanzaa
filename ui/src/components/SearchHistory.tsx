/**
 * SearchHistory component with saved searches
 */

import React from 'react';
import { History, Star, Trash2, Search, Clock } from 'lucide-react';
import type { SavedSearch } from '@types/search';
import { useSearchStore } from '@stores/searchStore';
import { formatRelativeTime } from '@utils/format';
import { getNamespaceLabel } from '@utils/namespaces';
import clsx from 'clsx';

interface SearchHistoryProps {
  onSearchSelect: (search: SavedSearch) => void;
  className?: string;
}

export function SearchHistory({ onSearchSelect, className }: SearchHistoryProps) {
  const { searchHistory, favoriteSearches, removeFromHistory, toggleFavorite, clearHistory } =
    useSearchStore();

  const [showOnlyFavorites, setShowOnlyFavorites] = React.useState(false);

  const displayedSearches = showOnlyFavorites
    ? favoriteSearches
    : searchHistory;

  if (searchHistory.length === 0) {
    return (
      <div className={clsx('rounded-lg border border-gray-200 bg-white p-6 text-center', className)}>
        <History className="mx-auto mb-3 h-8 w-8 text-gray-400" />
        <p className="text-sm text-gray-600">No search history yet</p>
      </div>
    );
  }

  return (
    <div className={clsx('rounded-lg border border-gray-200 bg-white shadow-sm', className)}>
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-200 px-4 py-3">
        <div className="flex items-center gap-2">
          <History className="h-5 w-5 text-gray-600" />
          <h3 className="text-sm font-medium text-gray-900">Search History</h3>
          <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-700">
            {searchHistory.length}
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowOnlyFavorites(!showOnlyFavorites)}
            className={clsx(
              'rounded-md px-3 py-1.5 text-xs font-medium transition-colors',
              showOnlyFavorites
                ? 'bg-yellow-100 text-yellow-900'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            )}
          >
            <Star className="mr-1 inline h-3 w-3" />
            Favorites {favoriteSearches.length > 0 && `(${favoriteSearches.length})`}
          </button>

          {searchHistory.length > 0 && (
            <button
              onClick={clearHistory}
              className="text-xs text-gray-600 hover:text-gray-900"
            >
              Clear all
            </button>
          )}
        </div>
      </div>

      {/* History List */}
      <div className="divide-y divide-gray-100">
        {displayedSearches.length === 0 ? (
          <div className="p-6 text-center">
            <Star className="mx-auto mb-2 h-6 w-6 text-gray-400" />
            <p className="text-sm text-gray-600">No favorite searches yet</p>
          </div>
        ) : (
          displayedSearches.slice(0, 10).map((search) => (
            <SearchHistoryItem
              key={search.id}
              search={search}
              onSelect={() => onSearchSelect(search)}
              onToggleFavorite={() => toggleFavorite(search.id)}
              onRemove={() => removeFromHistory(search.id)}
            />
          ))
        )}
      </div>
    </div>
  );
}

interface SearchHistoryItemProps {
  search: SavedSearch;
  onSelect: () => void;
  onToggleFavorite: () => void;
  onRemove: () => void;
}

function SearchHistoryItem({
  search,
  onSelect,
  onToggleFavorite,
  onRemove,
}: SearchHistoryItemProps) {
  return (
    <div className="group flex items-start gap-3 p-4 hover:bg-gray-50">
      <button
        onClick={onSelect}
        className="flex flex-1 items-start gap-3 text-left"
      >
        <Search className="mt-1 h-4 w-4 flex-shrink-0 text-gray-400" />

        <div className="min-w-0 flex-1">
          <div className="mb-1 font-medium text-gray-900 line-clamp-2">
            {search.query}
          </div>

          <div className="flex flex-wrap items-center gap-2 text-xs text-gray-600">
            <span className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {formatRelativeTime(search.timestamp)}
            </span>

            {search.namespace && (
              <>
                <span>•</span>
                <span>{getNamespaceLabel(search.namespace)}</span>
              </>
            )}

            {search.filters && Object.keys(search.filters).length > 0 && (
              <>
                <span>•</span>
                <span className="rounded-full bg-primary-100 px-2 py-0.5 text-primary-900">
                  {Object.keys(search.filters).length} filters
                </span>
              </>
            )}
          </div>
        </div>
      </button>

      <div className="flex items-center gap-1 opacity-0 transition-opacity group-hover:opacity-100">
        <button
          onClick={onToggleFavorite}
          className={clsx(
            'rounded-md p-1.5 transition-colors',
            search.isFavorite
              ? 'text-yellow-600 hover:bg-yellow-50'
              : 'text-gray-400 hover:bg-gray-100 hover:text-gray-600'
          )}
          aria-label={search.isFavorite ? 'Remove from favorites' : 'Add to favorites'}
        >
          <Star
            className={clsx('h-4 w-4', search.isFavorite && 'fill-current')}
          />
        </button>

        <button
          onClick={onRemove}
          className="rounded-md p-1.5 text-gray-400 hover:bg-red-50 hover:text-red-600"
          aria-label="Remove from history"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
