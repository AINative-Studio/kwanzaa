import { describe, it, expect, beforeEach } from 'vitest';
import { useSearchStore } from '../searchStore';

describe('searchStore', () => {
  beforeEach(() => {
    // Reset store before each test
    useSearchStore.setState({
      currentQuery: '',
      currentFilters: undefined,
      currentNamespace: undefined,
      currentResults: null,
      isSearching: false,
      searchError: null,
      searchHistory: [],
      favoriteSearches: [],
      analytics: {
        total_searches: 0,
        average_search_time: 0,
        most_queried_namespaces: {},
        filter_usage_patterns: {},
        relevance_distribution: {},
      },
    });
  });

  it('sets query', () => {
    const { setQuery } = useSearchStore.getState();
    setQuery('test query');

    expect(useSearchStore.getState().currentQuery).toBe('test query');
  });

  it('sets filters', () => {
    const { setFilters } = useSearchStore.getState();
    const filters = { year_gte: 2000, year_lte: 2020 };
    setFilters(filters);

    expect(useSearchStore.getState().currentFilters).toEqual(filters);
  });

  it('sets namespace', () => {
    const { setNamespace } = useSearchStore.getState();
    setNamespace('kwanzaa_primary_sources');

    expect(useSearchStore.getState().currentNamespace).toBe('kwanzaa_primary_sources');
  });

  it('adds to search history', () => {
    const { addToHistory } = useSearchStore.getState();
    const search = {
      id: '1',
      query: 'test',
      timestamp: Date.now(),
    };

    addToHistory(search);

    const history = useSearchStore.getState().searchHistory;
    expect(history).toHaveLength(1);
    expect(history[0]).toEqual(search);
  });

  it('removes from search history', () => {
    const { addToHistory, removeFromHistory } = useSearchStore.getState();
    const search = {
      id: '1',
      query: 'test',
      timestamp: Date.now(),
    };

    addToHistory(search);
    removeFromHistory('1');

    expect(useSearchStore.getState().searchHistory).toHaveLength(0);
  });

  it('toggles favorite', () => {
    const { addToHistory, toggleFavorite } = useSearchStore.getState();
    const search = {
      id: '1',
      query: 'test',
      timestamp: Date.now(),
      isFavorite: false,
    };

    addToHistory(search);
    toggleFavorite('1');

    const history = useSearchStore.getState().searchHistory;
    expect(history[0].isFavorite).toBe(true);

    const favorites = useSearchStore.getState().favoriteSearches;
    expect(favorites).toHaveLength(1);
  });

  it('clears history', () => {
    const { addToHistory, clearHistory } = useSearchStore.getState();

    addToHistory({ id: '1', query: 'test1', timestamp: Date.now() });
    addToHistory({ id: '2', query: 'test2', timestamp: Date.now() });

    clearHistory();

    expect(useSearchStore.getState().searchHistory).toHaveLength(0);
    expect(useSearchStore.getState().favoriteSearches).toHaveLength(0);
  });

  it('tracks search analytics', () => {
    const { trackSearch } = useSearchStore.getState();
    const response = {
      status: 'success',
      query: {
        text: 'test',
        namespace: 'kwanzaa_primary_sources',
        limit: 10,
        threshold: 0.75,
        filters_applied: { year_gte: 2000 },
      },
      results: [
        {
          rank: 1,
          score: 0.95,
          chunk_id: 'test::1',
          doc_id: 'test',
          namespace: 'kwanzaa_primary_sources',
          content: 'test',
          metadata: {
            citation_label: 'Test',
            canonical_url: 'https://test.com',
            source_org: 'Test',
            year: 2000,
            content_type: 'article',
            license: 'Public Domain',
            tags: [],
          },
        },
      ],
      total_results: 1,
      search_metadata: {
        execution_time_ms: 100,
        embedding_model: 'test',
        query_embedding_time_ms: 10,
        search_time_ms: 90,
      },
    };

    trackSearch(response);

    const analytics = useSearchStore.getState().analytics;
    expect(analytics.total_searches).toBe(1);
    expect(analytics.average_search_time).toBe(100);
    expect(analytics.most_queried_namespaces['kwanzaa_primary_sources']).toBe(1);
    expect(analytics.filter_usage_patterns['year_gte']).toBe(1);
  });

  it('limits history to 50 items', () => {
    const { addToHistory } = useSearchStore.getState();

    // Add 60 items
    for (let i = 0; i < 60; i++) {
      addToHistory({
        id: `${i}`,
        query: `test ${i}`,
        timestamp: Date.now(),
      });
    }

    const history = useSearchStore.getState().searchHistory;
    expect(history).toHaveLength(50);
  });
});
