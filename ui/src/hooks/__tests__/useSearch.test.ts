import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useSearch } from '../useSearch';
import { searchApi } from '@services/searchApi';

vi.mock('@services/searchApi', () => ({
  searchApi: {
    search: vi.fn(),
    listNamespaces: vi.fn(),
  },
}));

describe('useSearch', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('initializes with empty state', () => {
    const { result } = renderHook(() => useSearch());

    expect(result.current.query).toBe('');
    expect(result.current.results).toBeNull();
    expect(result.current.isSearching).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('updates query state', () => {
    const { result } = renderHook(() => useSearch());

    result.current.setQuery('test query');

    expect(result.current.query).toBe('test query');
  });

  it('updates namespace state', () => {
    const { result } = renderHook(() => useSearch());

    result.current.setNamespace('kwanzaa_primary_sources');

    expect(result.current.namespace).toBe('kwanzaa_primary_sources');
  });

  it('executes search and updates state', async () => {
    const mockResponse = {
      status: 'success',
      query: {
        text: 'test',
        namespace: 'default',
        limit: 20,
        threshold: 0.75,
      },
      results: [],
      total_results: 0,
      search_metadata: {
        execution_time_ms: 100,
        embedding_model: 'test-model',
        query_embedding_time_ms: 10,
        search_time_ms: 90,
      },
    };

    vi.mocked(searchApi.search).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useSearch());

    result.current.setQuery('test');
    await result.current.executeSearch();

    await waitFor(() => {
      expect(result.current.isSearching).toBe(false);
      expect(result.current.results).toEqual(mockResponse);
    });
  });

  it('handles search errors', async () => {
    vi.mocked(searchApi.search).mockRejectedValue(new Error('Search failed'));

    const { result } = renderHook(() => useSearch());

    result.current.setQuery('test');

    await expect(result.current.executeSearch()).rejects.toThrow();

    await waitFor(() => {
      expect(result.current.isSearching).toBe(false);
      expect(result.current.error).toBe('Search failed');
    });
  });

  it('resets search state', () => {
    const { result } = renderHook(() => useSearch());

    result.current.setQuery('test');
    result.current.setNamespace('test_namespace');
    result.current.resetSearch();

    expect(result.current.query).toBe('');
    expect(result.current.namespace).toBeUndefined();
    expect(result.current.results).toBeNull();
  });
});
