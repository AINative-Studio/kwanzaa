/**
 * Kwanzaa Answer JSON Contract - TypeScript Types
 *
 * Complete type definitions matching the backend Pydantic models.
 * These types ensure type-safe rendering of AI responses with citations,
 * provenance tracking, and transparent uncertainty.
 */

export type Persona = 'educator' | 'researcher' | 'creator' | 'builder';

export type ModelMode = 'base_adapter_rag' | 'base_only' | 'adapter_only' | 'creative';

export type Tone = 'neutral' | 'educational' | 'conversational' | 'formal' | 'creative';

export type Completeness = 'complete' | 'partial' | 'insufficient_data';

export type RetrievalConfidence = 'high' | 'medium' | 'low' | 'none';

export type FallbackBehavior = 'not_needed' | 'creative_generation' | 'refusal' | 'clarification_requested';

export interface Toggles {
  require_citations: boolean;
  primary_sources_only: boolean;
  creative_mode: boolean;
}

export interface Answer {
  text: string;
  confidence?: number;
  tone?: Tone;
  completeness?: Completeness;
}

export interface Source {
  citation_label: string;
  canonical_url: string;
  source_org: string;
  year: number;
  content_type: string;
  license: string;
  namespace: string;
  doc_id: string;
  chunk_id: string;
  tags?: string[];
  relevance_score?: number;
}

export interface RetrievalFilters {
  content_type?: string[];
  year?: number;
  year_gte?: number;
  year_lte?: number;
  source_org?: string[];
  tags?: string[];
}

export interface RetrievalResult {
  rank: number;
  score: number;
  snippet?: string;
  citation_label: string;
  canonical_url: string;
  doc_id: string;
  chunk_id: string;
  namespace: string;
}

export interface RetrievalSummary {
  query: string;
  top_k: number;
  namespaces: string[];
  filters?: RetrievalFilters;
  results: RetrievalResult[];
  execution_time_ms?: number;
  embedding_model?: string;
}

export interface Unknowns {
  unsupported_claims: string[];
  missing_context: string[];
  clarifying_questions: string[];
  out_of_scope?: string[];
}

export interface Integrity {
  citation_required?: boolean;
  citations_provided?: boolean;
  retrieval_confidence?: RetrievalConfidence;
  fallback_behavior?: FallbackBehavior;
  safety_flags?: string[];
}

export interface Provenance {
  generated_at: string;
  retrieval_run_id?: string;
  assistant_message_id?: string;
  session_id?: string;
  model_version?: string;
  adapter_version?: string;
}

export interface AnswerJsonContract {
  version: string;
  persona?: Persona;
  model_mode?: ModelMode;
  toggles?: Toggles;
  answer: Answer;
  sources: Source[];
  retrieval_summary: RetrievalSummary;
  unknowns: Unknowns;
  integrity?: Integrity;
  provenance?: Provenance;
}

// Chat message types
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  answerJson?: AnswerJsonContract;
  timestamp: Date;
  isStreaming?: boolean;
}

// Chat request/response types
export interface ChatRequest {
  query: string;
  persona_key: Persona;
  mode: ModelMode;
  session_id: string;
}

export interface ChatResponse extends AnswerJsonContract {
  // Extended with any additional response fields
}

// Safety types
export interface SafetyCheck {
  type: 'prompt_injection' | 'jailbreak' | 'pii' | 'content_moderation';
  passed: boolean;
  confidence: number;
  details?: string;
  flags?: string[];
}

export interface SafetyResult {
  checks: SafetyCheck[];
  overallSafe: boolean;
  warnings: string[];
  redactedText?: string;
}

// Observability types
export interface ObservabilityEvent {
  event_type: 'query' | 'response' | 'retrieval' | 'persona_change' | 'mode_change';
  timestamp: Date;
  data: Record<string, any>;
  session_id: string;
}

// RLHF types
export interface RLHFeedback {
  message_id: string;
  feedback_type: 'thumbs_up' | 'thumbs_down' | 'rating' | 'detailed';
  rating?: number; // 1-5
  comment?: string;
  aspects?: {
    accuracy?: number;
    helpfulness?: number;
    citation_quality?: number;
    persona_alignment?: number;
  };
  timestamp: Date;
}

// Usage tracking types
export interface UsageMetrics {
  total_queries: number;
  total_tokens: number;
  input_tokens: number;
  output_tokens: number;
  estimated_cost: number;
  avg_response_time_ms: number;
  persona_usage: Record<Persona, number>;
  mode_usage: Record<ModelMode, number>;
}
