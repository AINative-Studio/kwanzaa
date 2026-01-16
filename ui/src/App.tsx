/**
 * Main App component - Semantic Search Explorer
 */

import React, { useState } from 'react';
import { Toaster, toast } from 'react-hot-toast';
import { SearchBar } from '@components/SearchBar';
import { FilterPanel } from '@components/FilterPanel';
import { SearchResults } from '@components/SearchResults';
import { SearchHistory } from '@components/SearchHistory';
import { AnalyticsDashboard } from '@components/AnalyticsDashboard';
import { useSearch } from '@hooks/useSearch';
import type { SavedSearch } from '@types/search';
import { BookOpen, BarChart3, History as HistoryIcon } from 'lucide-react';
import clsx from 'clsx';

type View = 'search' | 'analytics' | 'history';

export function App() {
  const [activeView, setActiveView] = useState<View>('search');
  const {
    query,
    filters,
    namespace,
    results,
    isSearching,
    error,
    setQuery,
    setFilters,
    setNamespace,
    executeSearch,
    rerunSearch,
  } = useSearch();

  const handleSearch = async () => {
    try {
      await executeSearch();
      toast.success('Search completed successfully');
    } catch (err) {
      toast.error(error || 'Search failed');
    }
  };

  const handleHistorySelect = async (search: SavedSearch) => {
    setActiveView('search');
    try {
      await rerunSearch(search.id);
      toast.success('Search executed from history');
    } catch (err) {
      toast.error('Failed to execute search');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Toaster position="top-right" />

      {/* Header */}
      <header className="border-b border-gray-200 bg-white shadow-sm">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Kwanzaa Semantic Search Explorer
              </h1>
              <p className="mt-1 text-sm text-gray-600">
                Search the corpus with provenance and citation tracking
              </p>
            </div>

            {/* View Tabs */}
            <div className="flex gap-2">
              <TabButton
                icon={<BookOpen className="h-5 w-5" />}
                label="Search"
                active={activeView === 'search'}
                onClick={() => setActiveView('search')}
              />
              <TabButton
                icon={<BarChart3 className="h-5 w-5" />}
                label="Analytics"
                active={activeView === 'analytics'}
                onClick={() => setActiveView('analytics')}
              />
              <TabButton
                icon={<HistoryIcon className="h-5 w-5" />}
                label="History"
                active={activeView === 'history'}
                onClick={() => setActiveView('history')}
              />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {activeView === 'search' && (
          <div className="space-y-6">
            {/* Search Bar */}
            <SearchBar
              value={query}
              onChange={setQuery}
              onSearch={handleSearch}
              isSearching={isSearching}
            />

            {/* Main Content Grid */}
            <div className="grid gap-6 lg:grid-cols-4">
              {/* Filters Sidebar */}
              <div className="lg:col-span-1">
                <FilterPanel
                  filters={filters}
                  namespace={namespace}
                  onChange={setFilters}
                  onNamespaceChange={setNamespace}
                />
              </div>

              {/* Results Area */}
              <div className="lg:col-span-3">
                {error && (
                  <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
                    {error}
                  </div>
                )}

                {results ? (
                  <SearchResults response={results} />
                ) : (
                  <div className="rounded-lg border border-gray-200 bg-white p-12 text-center">
                    <BookOpen className="mx-auto mb-4 h-16 w-16 text-gray-400" />
                    <h3 className="mb-2 text-lg font-semibold text-gray-900">
                      Ready to Search
                    </h3>
                    <p className="text-gray-600">
                      Enter a search query to explore the Kwanzaa corpus with full provenance tracking
                    </p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeView === 'analytics' && (
          <AnalyticsDashboard />
        )}

        {activeView === 'history' && (
          <SearchHistory onSearchSelect={handleHistorySelect} />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-gray-200 bg-white">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <p>
              Kwanzaa Model — Cultural AI with Provenance
            </p>
            <p>
              Built with AIKit and ZeroDB
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

interface TabButtonProps {
  icon: React.ReactNode;
  label: string;
  active: boolean;
  onClick: () => void;
}

function TabButton({ icon, label, active, onClick }: TabButtonProps) {
  return (
    <button
      onClick={onClick}
      className={clsx(
        'flex items-center gap-2 rounded-lg px-4 py-2 text-sm font-medium transition-colors',
        active
          ? 'bg-primary-100 text-primary-900'
          : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
      )}
    >
      {icon}
      {label}
    </button>
  );
}
