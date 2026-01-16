/**
 * Search type definitions matching backend API contract
 */

export interface ProvenanceFilters {
  year?: number;
  year_gte?: number;
  year_lte?: number;
  source_org?: string[];
  content_type?: string[];
  tags?: string[];
}

export interface SearchRequest {
  query: string;
  namespace?: string;
  filters?: ProvenanceFilters;
  limit?: number;
  threshold?: number;
  include_embeddings?: boolean;
  persona_key?: 'educator' | 'researcher' | 'creator' | 'builder';
}

export interface ChunkMetadata {
  citation_label: string;
  canonical_url: string;
  source_org: string;
  year: number;
  content_type: string;
  license: string;
  tags: string[];
  [key: string]: any;
}

export interface SearchResult {
  rank: number;
  score: number;
  chunk_id: string;
  doc_id: string;
  namespace: string;
  content: string;
  metadata: ChunkMetadata;
  embedding?: number[];
}

export interface SearchQuery {
  text: string;
  namespace: string;
  filters_applied?: Record<string, any>;
  limit: number;
  threshold: number;
}

export interface SearchMetadata {
  execution_time_ms: number;
  embedding_model: string;
  query_embedding_time_ms: number;
  search_time_ms: number;
}

export interface SearchResponse {
  status: string;
  query: SearchQuery;
  results: SearchResult[];
  total_results: number;
  search_metadata: SearchMetadata;
}

export interface Namespace {
  name: string;
  display_name: string;
  description: string;
  document_count: number;
  chunk_count: number;
  content_types: string[];
  year_range: [number, number];
  source_orgs: string[];
}

export interface SavedSearch {
  id: string;
  query: string;
  namespace?: string;
  filters?: ProvenanceFilters;
  timestamp: number;
  name?: string;
  isFavorite?: boolean;
}

export interface ExportFormat {
  type: 'bibtex' | 'apa' | 'mla' | 'json' | 'csv';
  label: string;
  extension: string;
}

export interface SearchAnalytics {
  total_searches: number;
  average_search_time: number;
  most_queried_namespaces: Record<string, number>;
  filter_usage_patterns: Record<string, number>;
  relevance_distribution: Record<string, number>;
}
