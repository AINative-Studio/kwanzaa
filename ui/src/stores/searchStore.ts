/**
 * Search state management with Zustand
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type {
  SearchRequest,
  SearchResponse,
  SavedSearch,
  SearchAnalytics,
  Namespace,
} from '@types/search';

interface SearchState {
  // Current search
  currentQuery: string;
  currentFilters: SearchRequest['filters'];
  currentNamespace?: string;
  currentResults: SearchResponse | null;
  isSearching: boolean;
  searchError: string | null;

  // Namespaces
  namespaces: Namespace[];
  isLoadingNamespaces: boolean;

  // Search history
  searchHistory: SavedSearch[];
  favoriteSearches: SavedSearch[];

  // Analytics
  analytics: SearchAnalytics;

  // Actions
  setQuery: (query: string) => void;
  setFilters: (filters: SearchRequest['filters']) => void;
  setNamespace: (namespace?: string) => void;
  setResults: (results: SearchResponse | null) => void;
  setSearching: (isSearching: boolean) => void;
  setError: (error: string | null) => void;
  setNamespaces: (namespaces: Namespace[]) => void;

  addToHistory: (search: SavedSearch) => void;
  removeFromHistory: (id: string) => void;
  toggleFavorite: (id: string) => void;
  clearHistory: () => void;

  trackSearch: (response: SearchResponse) => void;
  resetSearch: () => void;
}

export const useSearchStore = create<SearchState>()(
  persist(
    (set, get) => ({
      // Initial state
      currentQuery: '',
      currentFilters: undefined,
      currentNamespace: undefined,
      currentResults: null,
      isSearching: false,
      searchError: null,
      namespaces: [],
      isLoadingNamespaces: false,
      searchHistory: [],
      favoriteSearches: [],
      analytics: {
        total_searches: 0,
        average_search_time: 0,
        most_queried_namespaces: {},
        filter_usage_patterns: {},
        relevance_distribution: {},
      },

      // Actions
      setQuery: (query) => set({ currentQuery: query }),

      setFilters: (filters) => set({ currentFilters: filters }),

      setNamespace: (namespace) => set({ currentNamespace: namespace }),

      setResults: (results) => set({ currentResults: results }),

      setSearching: (isSearching) => set({ isSearching }),

      setError: (error) => set({ searchError: error }),

      setNamespaces: (namespaces) => set({ namespaces }),

      addToHistory: (search) => {
        const history = get().searchHistory;
        const newHistory = [search, ...history.filter(s => s.id !== search.id)].slice(0, 50);
        set({ searchHistory: newHistory });
      },

      removeFromHistory: (id) => {
        set({
          searchHistory: get().searchHistory.filter(s => s.id !== id),
        });
      },

      toggleFavorite: (id) => {
        const search = get().searchHistory.find(s => s.id === id);
        if (search) {
          const updated = { ...search, isFavorite: !search.isFavorite };
          const history = get().searchHistory.map(s => s.id === id ? updated : s);
          const favorites = history.filter(s => s.isFavorite);
          set({ searchHistory: history, favoriteSearches: favorites });
        }
      },

      clearHistory: () => set({ searchHistory: [], favoriteSearches: [] }),

      trackSearch: (response) => {
        const analytics = get().analytics;
        const namespace = response.query.namespace;
        const searchTime = response.search_metadata.execution_time_ms;

        // Update analytics
        const newAnalytics: SearchAnalytics = {
          total_searches: analytics.total_searches + 1,
          average_search_time:
            (analytics.average_search_time * analytics.total_searches + searchTime) /
            (analytics.total_searches + 1),
          most_queried_namespaces: {
            ...analytics.most_queried_namespaces,
            [namespace]: (analytics.most_queried_namespaces[namespace] || 0) + 1,
          },
          filter_usage_patterns: analytics.filter_usage_patterns,
          relevance_distribution: analytics.relevance_distribution,
        };

        // Track filter usage
        if (response.query.filters_applied) {
          Object.keys(response.query.filters_applied).forEach(filter => {
            newAnalytics.filter_usage_patterns[filter] =
              (newAnalytics.filter_usage_patterns[filter] || 0) + 1;
          });
        }

        // Track relevance distribution
        response.results.forEach(result => {
          const scoreBucket = Math.floor(result.score * 10) / 10;
          const key = scoreBucket.toFixed(1);
          newAnalytics.relevance_distribution[key] =
            (newAnalytics.relevance_distribution[key] || 0) + 1;
        });

        set({ analytics: newAnalytics });
      },

      resetSearch: () =>
        set({
          currentQuery: '',
          currentFilters: undefined,
          currentResults: null,
          isSearching: false,
          searchError: null,
        }),
    }),
    {
      name: 'kwanzaa-search-storage',
      partialize: (state) => ({
        searchHistory: state.searchHistory,
        favoriteSearches: state.favoriteSearches,
        analytics: state.analytics,
      }),
    }
  )
);
