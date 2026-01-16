/**
 * Kwanzaa Answer JSON Contract - TypeScript Type Definitions
 * Version: 1.0.0
 *
 * Strict type definitions for AI responses with citations, provenance tracking,
 * and transparent uncertainty. Enforces Imani (Faith) through verifiable sources
 * and honest communication of limitations.
 */

/**
 * Contract version identifier
 */
export type ContractVersion = `kwanzaa.answer.v${number}`;

/**
 * Persona mode that generated the response
 */
export type Persona = 'educator' | 'researcher' | 'creator' | 'builder';

/**
 * Model mode used for generation
 */
export type ModelMode = 'base_adapter_rag' | 'base_only' | 'adapter_only' | 'creative';

/**
 * User-controlled behavior toggles enforcing Kujichagulia (Self-Determination)
 */
export interface Toggles {
  /** Whether citations are mandatory for this response */
  require_citations: boolean;
  /** Whether only primary sources should be used */
  primary_sources_only: boolean;
  /** Whether creative generation is enabled */
  creative_mode: boolean;
}

/**
 * Tone of the response
 */
export type Tone = 'neutral' | 'educational' | 'conversational' | 'formal' | 'creative';

/**
 * Assessment of answer completeness based on available data
 */
export type Completeness = 'complete' | 'partial' | 'insufficient_data';

/**
 * The main AI response with metadata
 */
export interface Answer {
  /** The main response text */
  text: string;
  /** Model confidence score for this answer (0.0 - 1.0) */
  confidence?: number;
  /** Tone of the response */
  tone?: Tone;
  /** Assessment of answer completeness based on available data */
  completeness?: Completeness;
}

/**
 * Source citation with full provenance metadata enforcing Imani (Faith)
 */
export interface Source {
  /** Human-readable citation label */
  citation_label: string;
  /** Canonical URL to source document */
  canonical_url: string;
  /** Source organization name */
  source_org: string;
  /** Year of document or content (1600-2100) */
  year: number;
  /** Content type classification */
  content_type: string;
  /** License information for the source */
  license: string;
  /** Vector namespace where this source resides */
  namespace: string;
  /** Unique document identifier */
  doc_id: string;
  /** Unique chunk identifier within the document */
  chunk_id: string;
  /** Content tags for categorization */
  tags?: string[];
  /** Relevance score for this source to the query (0.0 - 1.0) */
  relevance_score?: number;
  /** Additional metadata fields */
  [key: string]: unknown;
}

/**
 * Filters applied to the retrieval query
 */
export interface RetrievalFilters {
  /** Content type filters */
  content_type?: string[];
  /** Exact year filter */
  year?: number;
  /** Minimum year (inclusive) */
  year_gte?: number;
  /** Maximum year (inclusive) */
  year_lte?: number;
  /** Source organization filters */
  source_org?: string[];
  /** Tag filters */
  tags?: string[];
  /** Additional filter fields */
  [key: string]: unknown;
}

/**
 * Individual retrieval result with metadata
 */
export interface RetrievalResult {
  /** Result rank (1-indexed) */
  rank: number;
  /** Similarity or relevance score (0.0 - 1.0) */
  score: number;
  /** Text snippet from the retrieved chunk */
  snippet?: string;
  /** Human-readable citation label */
  citation_label: string;
  /** Canonical URL to source document */
  canonical_url: string;
  /** Document identifier */
  doc_id: string;
  /** Chunk identifier */
  chunk_id: string;
  /** Vector namespace */
  namespace: string;
}

/**
 * Summary of the retrieval process enforcing Ujima (Collective Work)
 * through transparent 'Show Your Work'
 */
export interface RetrievalSummary {
  /** The original query text that was processed */
  query: string;
  /** Number of results requested from retrieval (1-100) */
  top_k: number;
  /** Vector namespaces searched */
  namespaces: string[];
  /** Filters applied to the retrieval query */
  filters?: RetrievalFilters;
  /** Top retrieval results with metadata */
  results: RetrievalResult[];
  /** Total retrieval execution time in milliseconds */
  execution_time_ms?: number;
  /** Embedding model used for retrieval */
  embedding_model?: string;
}

/**
 * Transparent communication of limitations and gaps enforcing Imani (Faith)
 * through honest acknowledgment
 */
export interface Unknowns {
  /** Claims that cannot be supported by the corpus */
  unsupported_claims: string[];
  /** Context or information gaps in the corpus */
  missing_context: string[];
  /** Questions that would help provide a better answer */
  clarifying_questions: string[];
  /** Topics or queries that are outside the corpus scope */
  out_of_scope?: string[];
}

/**
 * Overall confidence in retrieval results
 */
export type RetrievalConfidence = 'high' | 'medium' | 'low' | 'none';

/**
 * Fallback behavior used when retrieval was insufficient
 */
export type FallbackBehavior = 'not_needed' | 'creative_generation' | 'refusal' | 'clarification_requested';

/**
 * Integrity metadata for trust and safety
 */
export interface Integrity {
  /** Whether citations were required for this response */
  citation_required?: boolean;
  /** Whether citations were actually provided */
  citations_provided?: boolean;
  /** Overall confidence in retrieval results */
  retrieval_confidence?: RetrievalConfidence;
  /** Fallback behavior used when retrieval was insufficient */
  fallback_behavior?: FallbackBehavior;
  /** Safety or policy flags triggered */
  safety_flags?: string[];
}

/**
 * Generation provenance metadata enforcing Ujamaa (Cooperative Economics)
 * through shared credit
 */
export interface Provenance {
  /** ISO 8601 timestamp of generation */
  generated_at: string;
  /** Unique identifier for the retrieval run */
  retrieval_run_id?: string;
  /** Unique identifier for the assistant message */
  assistant_message_id?: string;
  /** Session identifier for request correlation */
  session_id?: string;
  /** Model version or identifier used for generation */
  model_version?: string;
  /** Adapter version if used */
  adapter_version?: string;
}

/**
 * Complete Kwanzaa Answer JSON Contract
 *
 * This structure enforces the Seven Principles (Nguzo Saba):
 * - Umoja (Unity): Unified schema across all personas
 * - Kujichagulia (Self-Determination): User-controlled toggles
 * - Ujima (Collective Work): Transparent retrieval and 'Show Your Work'
 * - Ujamaa (Cooperative Economics): Shared credit through provenance
 * - Nia (Purpose): Education and research first
 * - Kuumba (Creativity): Creator tools grounded in retrieved context
 * - Imani (Faith): Trust through citations and honest communication
 */
export interface AnswerJsonContract {
  /** Contract version identifier */
  version: ContractVersion;
  /** Persona mode that generated this response */
  persona?: Persona;
  /** Model mode used for generation */
  model_mode?: ModelMode;
  /** User-controlled behavior toggles */
  toggles?: Toggles;
  /** The main AI response with metadata */
  answer: Answer;
  /** Array of source citations with full provenance metadata */
  sources: Source[];
  /** Summary of the retrieval process */
  retrieval_summary: RetrievalSummary;
  /** Transparent communication of limitations and gaps */
  unknowns: Unknowns;
  /** Integrity metadata for trust and safety */
  integrity?: Integrity;
  /** Generation provenance metadata */
  provenance?: Provenance;
}

/**
 * Type guard to validate if an object is a valid AnswerJsonContract
 */
export function isAnswerJsonContract(obj: unknown): obj is AnswerJsonContract {
  if (typeof obj !== 'object' || obj === null) {
    return false;
  }

  const contract = obj as Partial<AnswerJsonContract>;

  return (
    typeof contract.version === 'string' &&
    contract.version.startsWith('kwanzaa.answer.v') &&
    typeof contract.answer === 'object' &&
    contract.answer !== null &&
    typeof contract.answer.text === 'string' &&
    Array.isArray(contract.sources) &&
    typeof contract.retrieval_summary === 'object' &&
    contract.retrieval_summary !== null &&
    typeof contract.unknowns === 'object' &&
    contract.unknowns !== null &&
    Array.isArray(contract.unknowns.unsupported_claims) &&
    Array.isArray(contract.unknowns.missing_context) &&
    Array.isArray(contract.unknowns.clarifying_questions)
  );
}

/**
 * Helper function to create a minimal valid AnswerJsonContract
 */
export function createAnswerJsonContract(
  answer: string,
  query: string,
  options?: {
    version?: ContractVersion;
    persona?: Persona;
    modelMode?: ModelMode;
    sources?: Source[];
    retrievalResults?: RetrievalResult[];
    unknowns?: Partial<Unknowns>;
  }
): AnswerJsonContract {
  return {
    version: options?.version || 'kwanzaa.answer.v1',
    persona: options?.persona,
    model_mode: options?.modelMode,
    answer: {
      text: answer,
    },
    sources: options?.sources || [],
    retrieval_summary: {
      query,
      top_k: 10,
      namespaces: ['kwanzaa_primary_sources'],
      results: options?.retrievalResults || [],
    },
    unknowns: {
      unsupported_claims: options?.unknowns?.unsupported_claims || [],
      missing_context: options?.unknowns?.missing_context || [],
      clarifying_questions: options?.unknowns?.clarifying_questions || [],
      out_of_scope: options?.unknowns?.out_of_scope,
    },
    provenance: {
      generated_at: new Date().toISOString(),
    },
  };
}
