/**
 * Search hook with AIKit integration
 */

import { useCallback, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { searchApi } from '@services/searchApi';
import { useSearchStore } from '@stores/searchStore';
import type { SearchRequest } from '@types/search';

export function useSearch() {
  const {
    currentQuery,
    currentFilters,
    currentNamespace,
    currentResults,
    isSearching,
    searchError,
    namespaces,
    setQuery,
    setFilters,
    setNamespace,
    setResults,
    setSearching,
    setError,
    setNamespaces,
    addToHistory,
    trackSearch,
    resetSearch,
  } = useSearchStore();

  // Load namespaces on mount
  useEffect(() => {
    const loadNamespaces = async () => {
      try {
        const response = await searchApi.listNamespaces();
        setNamespaces(response.namespaces);
      } catch (error) {
        console.error('Failed to load namespaces:', error);
      }
    };

    if (namespaces.length === 0) {
      loadNamespaces();
    }
  }, [namespaces.length, setNamespaces]);

  /**
   * Execute search
   */
  const executeSearch = useCallback(
    async (request?: Partial<SearchRequest>) => {
      const searchRequest: SearchRequest = {
        query: request?.query ?? currentQuery,
        namespace: request?.namespace ?? currentNamespace,
        filters: request?.filters ?? currentFilters,
        limit: request?.limit ?? 20,
        threshold: request?.threshold ?? 0.75,
        include_embeddings: request?.include_embeddings ?? false,
      };

      if (!searchRequest.query.trim()) {
        setError('Search query cannot be empty');
        return;
      }

      setSearching(true);
      setError(null);

      try {
        const response = await searchApi.search(searchRequest);
        setResults(response);
        trackSearch(response);

        // Add to history
        addToHistory({
          id: uuidv4(),
          query: searchRequest.query,
          namespace: searchRequest.namespace,
          filters: searchRequest.filters,
          timestamp: Date.now(),
        });

        return response;
      } catch (error) {
        const message = error instanceof Error ? error.message : 'Search failed';
        setError(message);
        throw error;
      } finally {
        setSearching(false);
      }
    },
    [
      currentQuery,
      currentNamespace,
      currentFilters,
      setResults,
      setSearching,
      setError,
      addToHistory,
      trackSearch,
    ]
  );

  /**
   * Re-run a saved search
   */
  const rerunSearch = useCallback(
    async (searchId: string) => {
      const { searchHistory } = useSearchStore.getState();
      const search = searchHistory.find(s => s.id === searchId);

      if (search) {
        setQuery(search.query);
        setFilters(search.filters);
        setNamespace(search.namespace);
        await executeSearch({
          query: search.query,
          filters: search.filters,
          namespace: search.namespace,
        });
      }
    },
    [setQuery, setFilters, setNamespace, executeSearch]
  );

  return {
    // State
    query: currentQuery,
    filters: currentFilters,
    namespace: currentNamespace,
    results: currentResults,
    isSearching,
    error: searchError,
    namespaces,

    // Actions
    setQuery,
    setFilters,
    setNamespace,
    executeSearch,
    rerunSearch,
    resetSearch,
  };
}
