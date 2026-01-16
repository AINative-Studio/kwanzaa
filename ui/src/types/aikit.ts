/**
 * AIKit component type definitions
 * These are placeholder types for AIKit packages that will be installed
 */

export interface AIStreamOptions {
  endpoint: string;
  method?: 'GET' | 'POST';
  headers?: Record<string, string>;
  body?: any;
  onData?: (data: any) => void;
  onError?: (error: Error) => void;
  onComplete?: () => void;
}

export interface AIStreamResult<T = any> {
  data: T | null;
  error: Error | null;
  isLoading: boolean;
  isStreaming: boolean;
  stream: () => void;
  cancel: () => void;
}

export interface AgentResponseProps {
  data: any;
  className?: string;
  showMetadata?: boolean;
}

export interface ToolResultProps {
  tool: string;
  result: any;
  className?: string;
}

export interface StreamingToolResultProps extends ToolResultProps {
  isStreaming: boolean;
}

export interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export interface CodeBlockProps {
  code: string;
  language?: string;
  showLineNumbers?: boolean;
  className?: string;
}

export interface UsageDashboardProps {
  metrics: UsageMetrics;
  timeRange?: 'hour' | 'day' | 'week' | 'month';
  className?: string;
}

export interface UsageMetrics {
  total_requests: number;
  average_latency_ms: number;
  success_rate: number;
  error_rate: number;
  categories: Record<string, CategoryMetrics>;
}

export interface CategoryMetrics {
  count: number;
  average_latency_ms: number;
  success_rate: number;
}

export interface ObservabilityEvent {
  id: string;
  type: string;
  timestamp: number;
  data: Record<string, any>;
  metadata?: Record<string, any>;
}
