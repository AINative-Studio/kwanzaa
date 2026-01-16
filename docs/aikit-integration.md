# AIKit Integration Guide for Answer JSON Contract

**Version:** 1.0.0
**Last Updated:** January 16, 2026
**For:** Epic 8 - Issue #23

## Overview

This guide provides comprehensive instructions for integrating the Kwanzaa Answer JSON Contract with **AIKit** (@ainative/ai-kit-react) UI components. The contract is designed to prevent raw text blobs from reaching the UI and enable structured, citation-rich rendering.

## Table of Contents

- [Core Concepts](#core-concepts)
- [AIKit Component Mapping](#aikit-component-mapping)
- [Component Implementation Patterns](#component-implementation-patterns)
- [Streaming Support](#streaming-support)
- [Observability Integration](#observability-integration)
- [RLHF Feedback Collection](#rlhf-feedback-collection)
- [Error Handling](#error-handling)
- [Accessibility Guidelines](#accessibility-guidelines)
- [Testing Rendered Components](#testing-rendered-components)

## Core Concepts

### Contract-First Rendering

The Answer JSON Contract enforces a **contract-first** approach where:

1. **No raw text blobs**: All responses are structured JSON conforming to the schema
2. **Citations required**: Every answer includes provenance metadata
3. **Transparent retrieval**: "Show Your Work" through retrieval_summary
4. **Honest unknowns**: Explicit acknowledgment of gaps and limitations

### AIKit Philosophy Alignment

| Kwanzaa Principle | AIKit Pattern |
|-------------------|---------------|
| **Imani (Faith)** | Trust through citations and source transparency |
| **Ujima (Collective Work)** | "Show Your Work" collapsible sections |
| **Kujichagulia (Self-Determination)** | User controls for citation requirements |
| **Umoja (Unity)** | Unified rendering across all personas |

## AIKit Component Mapping

### Primary Components

The Answer JSON Contract maps to these AIKit components:

| Contract Section | AIKit Component | Purpose |
|------------------|-----------------|---------|
| `answer` | `AgentResponse` | Main answer display with metadata |
| `sources` | `CitationList` | Clickable citation references |
| `retrieval_summary` | `ToolResult` | Retrieval transparency (collapsible) |
| `unknowns` | `UnknownsCard` | Knowledge gaps and clarifications |
| `integrity` | `IntegrityBadges` | Trust indicators |
| `provenance` | `ProvenanceFooter` | Generation metadata |

### Component Hierarchy

```
<AnswerContainer>
  ├─ <AgentResponse>           // answer.text + metadata
  │  ├─ <ConfidenceBadge />    // answer.confidence
  │  └─ <ToneIndicator />      // answer.tone
  ├─ <CitationList>            // sources[]
  │  └─ <Citation />           // individual source
  ├─ <UnknownsCard>            // unknowns (conditional)
  │  ├─ <UnsupportedClaims />
  │  ├─ <MissingContext />
  │  └─ <ClarifyingQuestions />
  ├─ <ToolResult>              // retrieval_summary (collapsible)
  │  ├─ <QueryInfo />
  │  └─ <RetrievalResults />
  ├─ <IntegrityBadges>         // integrity
  └─ <ProvenanceFooter>        // provenance
</AnswerContainer>
```

## Component Implementation Patterns

### 1. Main Answer Section

```typescript
import { AgentResponse, ConfidenceBadge, ToneIndicator } from '@ainative/ai-kit-react';
import { AnswerJsonContract } from '@/schemas/answer_json';

interface AnswerSectionProps {
  contract: AnswerJsonContract;
}

export const AnswerSection: React.FC<AnswerSectionProps> = ({ contract }) => {
  return (
    <AgentResponse
      content={contract.answer.text}
      persona={contract.persona}
      modelMode={contract.model_mode}
      metadata={{
        confidence: contract.answer.confidence,
        tone: contract.answer.tone,
        completeness: contract.answer.completeness,
      }}
    >
      {/* Header badges */}
      <div className="flex gap-2 mb-4">
        {contract.answer.confidence && (
          <ConfidenceBadge
            value={contract.answer.confidence}
            threshold={{ high: 0.85, medium: 0.65 }}
          />
        )}
        {contract.answer.tone && (
          <ToneIndicator tone={contract.answer.tone} />
        )}
        {contract.answer.completeness && (
          <CompletenessBadge status={contract.answer.completeness} />
        )}
      </div>

      {/* Main answer text (markdown rendered) */}
      <MarkdownContent content={contract.answer.text} />
    </AgentResponse>
  );
};
```

### 2. Citation List

```typescript
import { CitationList, Citation, CitationMeta } from '@ainative/ai-kit-react';

interface CitationSectionProps {
  sources: Source[];
}

export const CitationSection: React.FC<CitationSectionProps> = ({ sources }) => {
  if (sources.length === 0) {
    return null; // No citations to display
  }

  return (
    <CitationList
      title={`Sources (${sources.length})`}
      collapsible={sources.length > 5}
      defaultOpen={sources.length <= 5}
    >
      {sources.map((source, idx) => (
        <Citation
          key={`${source.doc_id}-${source.chunk_id}`}
          number={idx + 1}
          href={source.canonical_url}
          label={source.citation_label}
          verified={true}
          aria-label={`Citation ${idx + 1}: ${source.citation_label}`}
        >
          <CitationMeta>
            <span className="source-org">{source.source_org}</span>
            <span className="separator">•</span>
            <span className="year">{source.year}</span>
            <span className="separator">•</span>
            <span className="content-type">{source.content_type}</span>
            <span className="separator">•</span>
            <span className="license">{source.license}</span>
          </CitationMeta>

          {/* Optional: Show relevance score */}
          {source.relevance_score && (
            <RelevanceIndicator score={source.relevance_score} />
          )}

          {/* Optional: Show tags */}
          {source.tags && source.tags.length > 0 && (
            <TagList tags={source.tags} />
          )}
        </Citation>
      ))}
    </CitationList>
  );
};
```

### 3. Retrieval Summary (Show Your Work)

```typescript
import { ToolResult, Collapsible } from '@ainative/ai-kit-react';

interface RetrievalSummaryProps {
  summary: RetrievalSummarySection;
}

export const RetrievalSummary: React.FC<RetrievalSummaryProps> = ({ summary }) => {
  return (
    <Collapsible
      title="Show Your Work"
      subtitle="See how this answer was retrieved"
      defaultOpen={false}
      icon={<SearchIcon />}
    >
      <ToolResult
        toolName="semantic_search"
        status="success"
        executionTime={summary.execution_time_ms}
      >
        {/* Query information */}
        <div className="query-info mb-4">
          <h4 className="text-sm font-semibold mb-2">Search Query</h4>
          <code className="block bg-gray-100 p-2 rounded text-sm">
            {summary.query}
          </code>
        </div>

        {/* Search parameters */}
        <div className="search-params mb-4 grid grid-cols-2 gap-4">
          <div>
            <span className="text-sm font-semibold">Namespaces:</span>
            <div className="flex flex-wrap gap-1 mt-1">
              {summary.namespaces.map((ns) => (
                <Badge key={ns} variant="secondary">{ns}</Badge>
              ))}
            </div>
          </div>
          <div>
            <span className="text-sm font-semibold">Results Retrieved:</span>
            <span className="ml-2">{summary.top_k}</span>
          </div>
        </div>

        {/* Filters applied */}
        {summary.filters && Object.keys(summary.filters).length > 0 && (
          <div className="filters-applied mb-4">
            <h4 className="text-sm font-semibold mb-2">Filters Applied</h4>
            <pre className="bg-gray-100 p-2 rounded text-xs overflow-x-auto">
              {JSON.stringify(summary.filters, null, 2)}
            </pre>
          </div>
        )}

        {/* Retrieval results */}
        <div className="retrieval-results">
          <h4 className="text-sm font-semibold mb-2">
            Top Results ({summary.results.length})
          </h4>
          {summary.results.map((result) => (
            <RetrievalResultCard key={result.chunk_id} result={result} />
          ))}
        </div>

        {/* Model info */}
        {summary.embedding_model && (
          <div className="model-info mt-4 text-xs text-gray-600">
            Embedding Model: {summary.embedding_model}
          </div>
        )}
      </ToolResult>
    </Collapsible>
  );
};

const RetrievalResultCard: React.FC<{ result: RetrievalResult }> = ({ result }) => {
  return (
    <div className="result-card border rounded p-3 mb-2 hover:bg-gray-50 transition">
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="rank-badge">{result.rank}</span>
          <span className="score-badge">
            {(result.score * 100).toFixed(1)}%
          </span>
        </div>
        <a
          href={result.canonical_url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-sm text-blue-600 hover:underline"
        >
          View Source
        </a>
      </div>

      {result.snippet && (
        <p className="text-sm text-gray-700 mb-2">{result.snippet}</p>
      )}

      <div className="text-xs text-gray-600">
        <span>{result.citation_label}</span>
        <span className="mx-2">•</span>
        <span>{result.namespace}</span>
      </div>
    </div>
  );
};
```

### 4. Unknowns Section

```typescript
import { UnknownsCard, InfoBox } from '@ainative/ai-kit-react';

interface UnknownsSectionProps {
  unknowns: UnknownsSection;
}

export const UnknownsSection: React.FC<UnknownsSectionProps> = ({ unknowns }) => {
  // Only render if there are any unknowns
  const hasUnknowns =
    unknowns.unsupported_claims.length > 0 ||
    unknowns.missing_context.length > 0 ||
    unknowns.clarifying_questions.length > 0 ||
    (unknowns.out_of_scope && unknowns.out_of_scope.length > 0);

  if (!hasUnknowns) {
    return null;
  }

  return (
    <UnknownsCard
      title="What's Missing or Unclear"
      icon={<AlertCircleIcon />}
      variant="info"
    >
      {/* Unsupported claims */}
      {unknowns.unsupported_claims.length > 0 && (
        <InfoBox title="Unsupported Claims" variant="warning">
          <ul className="list-disc list-inside space-y-1">
            {unknowns.unsupported_claims.map((claim, idx) => (
              <li key={idx} className="text-sm">{claim}</li>
            ))}
          </ul>
        </InfoBox>
      )}

      {/* Missing context */}
      {unknowns.missing_context.length > 0 && (
        <InfoBox title="Missing Context" variant="info">
          <ul className="list-disc list-inside space-y-1">
            {unknowns.missing_context.map((context, idx) => (
              <li key={idx} className="text-sm">{context}</li>
            ))}
          </ul>
        </InfoBox>
      )}

      {/* Clarifying questions */}
      {unknowns.clarifying_questions.length > 0 && (
        <InfoBox title="Clarifying Questions" variant="help">
          <ul className="list-disc list-inside space-y-1">
            {unknowns.clarifying_questions.map((question, idx) => (
              <li key={idx} className="text-sm">{question}</li>
            ))}
          </ul>
        </InfoBox>
      )}

      {/* Out of scope */}
      {unknowns.out_of_scope && unknowns.out_of_scope.length > 0 && (
        <InfoBox title="Out of Scope" variant="neutral">
          <ul className="list-disc list-inside space-y-1">
            {unknowns.out_of_scope.map((item, idx) => (
              <li key={idx} className="text-sm">{item}</li>
            ))}
          </ul>
        </InfoBox>
      )}
    </UnknownsCard>
  );
};
```

### 5. Integrity Badges

```typescript
import { Badge, Tooltip } from '@ainative/ai-kit-react';

interface IntegrityBadgesProps {
  integrity?: IntegritySection;
}

export const IntegrityBadges: React.FC<IntegrityBadgesProps> = ({ integrity }) => {
  if (!integrity) {
    return null;
  }

  return (
    <div className="integrity-badges flex flex-wrap gap-2 my-4">
      {/* Citation status */}
      <Tooltip content={
        integrity.citations_provided
          ? "All claims are properly cited"
          : "No citations provided for this response"
      }>
        <Badge
          variant={integrity.citations_provided ? 'success' : 'warning'}
          icon={integrity.citations_provided ? <CheckIcon /> : <AlertIcon />}
        >
          {integrity.citations_provided ? 'Cited' : 'Uncited'}
        </Badge>
      </Tooltip>

      {/* Retrieval confidence */}
      {integrity.retrieval_confidence && (
        <Tooltip content={`Retrieval confidence: ${integrity.retrieval_confidence}`}>
          <Badge
            variant={getConfidenceVariant(integrity.retrieval_confidence)}
            icon={<SearchIcon />}
          >
            Confidence: {integrity.retrieval_confidence.toUpperCase()}
          </Badge>
        </Tooltip>
      )}

      {/* Fallback behavior */}
      {integrity.fallback_behavior && integrity.fallback_behavior !== 'not_needed' && (
        <Tooltip content={`Fallback: ${integrity.fallback_behavior.replace('_', ' ')}`}>
          <Badge variant="info">
            {getFallbackLabel(integrity.fallback_behavior)}
          </Badge>
        </Tooltip>
      )}

      {/* Safety flags */}
      {integrity.safety_flags && integrity.safety_flags.length > 0 && (
        <Tooltip content={integrity.safety_flags.join(', ')}>
          <Badge variant="error" icon={<ShieldIcon />}>
            Safety Flags ({integrity.safety_flags.length})
          </Badge>
        </Tooltip>
      )}
    </div>
  );
};

function getConfidenceVariant(confidence: string): 'success' | 'warning' | 'error' {
  switch (confidence) {
    case 'high': return 'success';
    case 'medium': return 'warning';
    case 'low':
    case 'none': return 'error';
    default: return 'warning';
  }
}

function getFallbackLabel(fallback: string): string {
  switch (fallback) {
    case 'creative_generation': return 'Creative Mode';
    case 'refusal': return 'Refused';
    case 'clarification_requested': return 'Needs Clarification';
    default: return fallback;
  }
}
```

### 6. Provenance Footer

```typescript
import { ProvenanceFooter, Timestamp } from '@ainative/ai-kit-react';

interface ProvenanceProps {
  provenance?: ProvenanceSection;
  version: string;
}

export const Provenance: React.FC<ProvenanceProps> = ({ provenance, version }) => {
  if (!provenance) {
    return null;
  }

  return (
    <ProvenanceFooter className="mt-8 pt-4 border-t">
      <div className="grid grid-cols-2 gap-4 text-xs text-gray-600">
        {/* Left column */}
        <div>
          <div className="mb-2">
            <span className="font-semibold">Generated:</span>{' '}
            <Timestamp value={provenance.generated_at} format="relative" />
          </div>

          {provenance.model_version && (
            <div className="mb-2">
              <span className="font-semibold">Model:</span>{' '}
              {provenance.model_version}
            </div>
          )}

          {provenance.adapter_version && (
            <div className="mb-2">
              <span className="font-semibold">Adapter:</span>{' '}
              {provenance.adapter_version}
            </div>
          )}
        </div>

        {/* Right column */}
        <div>
          <div className="mb-2">
            <span className="font-semibold">Contract Version:</span>{' '}
            {version}
          </div>

          {provenance.retrieval_run_id && (
            <div className="mb-2 font-mono text-xs">
              <span className="font-semibold">Retrieval ID:</span>{' '}
              <span className="opacity-70">{provenance.retrieval_run_id}</span>
            </div>
          )}

          {provenance.session_id && (
            <div className="mb-2 font-mono text-xs">
              <span className="font-semibold">Session ID:</span>{' '}
              <span className="opacity-70">{provenance.session_id}</span>
            </div>
          )}
        </div>
      </div>
    </ProvenanceFooter>
  );
};
```

### 7. Complete Container Component

```typescript
import { AnswerContainer } from '@ainative/ai-kit-react';
import { AnswerJsonContract } from '@/schemas/answer_json';

interface KwanzaaAnswerProps {
  contract: AnswerJsonContract;
  onFeedback?: (feedback: FeedbackPayload) => void;
}

export const KwanzaaAnswer: React.FC<KwanzaaAnswerProps> = ({
  contract,
  onFeedback
}) => {
  return (
    <AnswerContainer
      className="kwanzaa-answer"
      persona={contract.persona}
      mode={contract.model_mode}
    >
      {/* Main answer */}
      <AnswerSection contract={contract} />

      {/* Integrity indicators */}
      <IntegrityBadges integrity={contract.integrity} />

      {/* Citations */}
      <CitationSection sources={contract.sources} />

      {/* Unknowns (conditional) */}
      <UnknownsSection unknowns={contract.unknowns} />

      {/* Retrieval summary (collapsible) */}
      <RetrievalSummary summary={contract.retrieval_summary} />

      {/* Provenance footer */}
      <Provenance
        provenance={contract.provenance}
        version={contract.version}
      />

      {/* RLHF Feedback (if callback provided) */}
      {onFeedback && (
        <FeedbackButtons
          onThumbsUp={() => onFeedback({
            type: 'thumbs_up',
            message_id: contract.provenance?.assistant_message_id
          })}
          onThumbsDown={() => onFeedback({
            type: 'thumbs_down',
            message_id: contract.provenance?.assistant_message_id
          })}
        />
      )}
    </AnswerContainer>
  );
};
```

## Streaming Support

For streaming responses, use AIKit's `StreamingMessage` component:

```typescript
import { StreamingMessage } from '@ainative/ai-kit-react';

export const StreamingAnswer: React.FC<{ stream: ReadableStream }> = ({ stream }) => {
  const [partialContract, setPartialContract] = useState<Partial<AnswerJsonContract>>(null);

  useEffect(() => {
    const reader = stream.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    const processStream = async () => {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Try to parse partial JSON
        try {
          const partial = JSON.parse(buffer);
          setPartialContract(partial);
        } catch {
          // Continue buffering
        }
      }
    };

    processStream();
  }, [stream]);

  return (
    <StreamingMessage
      content={partialContract?.answer?.text || ''}
      isComplete={!!partialContract?.version}
    >
      {partialContract?.version && (
        <KwanzaaAnswer contract={partialContract as AnswerJsonContract} />
      )}
    </StreamingMessage>
  );
};
```

## Observability Integration

Track answer rendering events with AIKit observability:

```typescript
import { useObservability } from '@ainative/ai-kit-react';

export const ObservableAnswer: React.FC<{ contract: AnswerJsonContract }> = ({ contract }) => {
  const { trackEvent } = useObservability();

  useEffect(() => {
    // Track answer display
    trackEvent('answer_displayed', {
      version: contract.version,
      persona: contract.persona,
      model_mode: contract.model_mode,
      source_count: contract.sources.length,
      has_unknowns:
        contract.unknowns.unsupported_claims.length > 0 ||
        contract.unknowns.missing_context.length > 0,
      retrieval_confidence: contract.integrity?.retrieval_confidence,
      execution_time_ms: contract.retrieval_summary.execution_time_ms,
    });
  }, [contract, trackEvent]);

  const handleCitationClick = (citation: Source, index: number) => {
    trackEvent('citation_clicked', {
      citation_index: index,
      doc_id: citation.doc_id,
      source_org: citation.source_org,
      year: citation.year,
      canonical_url: citation.canonical_url,
    });
  };

  return (
    <KwanzaaAnswer
      contract={contract}
      onCitationClick={handleCitationClick}
    />
  );
};
```

## RLHF Feedback Collection

Integrate with ZeroDB RLHF for feedback collection:

```typescript
import { useMutation } from '@tanstack/react-query';

interface FeedbackPayload {
  type: 'thumbs_up' | 'thumbs_down' | 'rating';
  message_id?: string;
  rating?: number;
  comment?: string;
}

export const useFeedback = () => {
  const collectFeedback = useMutation({
    mutationFn: async (payload: FeedbackPayload) => {
      // Call ZeroDB RLHF endpoint
      const response = await fetch('/api/rlhf/feedback', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      return response.json();
    },
  });

  return {
    submitFeedback: collectFeedback.mutate,
    isSubmitting: collectFeedback.isPending,
  };
};

// Usage in component
export const AnswerWithFeedback: React.FC<{ contract: AnswerJsonContract }> = ({ contract }) => {
  const { submitFeedback } = useFeedback();

  const handleFeedback = (type: 'thumbs_up' | 'thumbs_down') => {
    submitFeedback({
      type,
      message_id: contract.provenance?.assistant_message_id,
    });
  };

  return (
    <KwanzaaAnswer
      contract={contract}
      onFeedback={handleFeedback}
    />
  );
};
```

## Error Handling

Handle validation errors gracefully:

```typescript
import { ErrorBoundary } from '@ainative/ai-kit-react';
import { validateAnswerJson, AnswerValidationError } from '@/utils/answer_validation';

export const SafeAnswer: React.FC<{ data: unknown }> = ({ data }) => {
  const [contract, setContract] = useState<AnswerJsonContract | null>(null);
  const [error, setError] = useState<AnswerValidationError | null>(null);

  useEffect(() => {
    try {
      const validated = validateAnswerJson(data as any);
      setContract(validated);
      setError(null);
    } catch (err) {
      if (err instanceof AnswerValidationError) {
        setError(err);
      } else {
        throw err; // Re-throw unexpected errors
      }
    }
  }, [data]);

  if (error) {
    return (
      <ErrorCard
        title="Invalid Answer Format"
        message={error.message}
        errors={error.errors}
      />
    );
  }

  if (!contract) {
    return <LoadingSpinner />;
  }

  return (
    <ErrorBoundary fallback={<ErrorCard title="Rendering Error" />}>
      <KwanzaaAnswer contract={contract} />
    </ErrorBoundary>
  );
};
```

## Accessibility Guidelines

### Semantic HTML

```typescript
// Use semantic HTML elements
<article className="kwanzaa-answer">
  <section className="answer-section" aria-labelledby="answer-heading">
    <h2 id="answer-heading">Answer</h2>
    {/* Answer content */}
  </section>

  <section className="citations" aria-labelledby="citations-heading">
    <h2 id="citations-heading">Sources</h2>
    <ol>
      {sources.map((source, idx) => (
        <li key={idx}>
          <cite>
            <a href={source.canonical_url} aria-label={`Citation ${idx + 1}: ${source.citation_label}`}>
              {source.citation_label}
            </a>
          </cite>
        </li>
      ))}
    </ol>
  </section>
</article>
```

### Keyboard Navigation

```typescript
// Ensure all interactive elements are keyboard accessible
<button
  onClick={handleCitationClick}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleCitationClick();
    }
  }}
  aria-label={`View citation: ${citation.citation_label}`}
  tabIndex={0}
>
  {citation.citation_label}
</button>
```

### Screen Reader Support

```typescript
// Provide live regions for dynamic content
<div
  aria-live="polite"
  aria-atomic="true"
  className="sr-only"
>
  {isLoading ? 'Loading answer...' : `Answer loaded with ${sources.length} citations`}
</div>
```

### Color Independence

```typescript
// Don't rely solely on color for information
<Badge
  variant={confidence === 'high' ? 'success' : 'warning'}
  icon={confidence === 'high' ? <CheckIcon /> : <AlertIcon />}
  aria-label={`Confidence level: ${confidence}`}
>
  Confidence: {confidence}
</Badge>
```

## Testing Rendered Components

### Unit Tests

```typescript
import { render, screen } from '@testing-library/react';
import { KwanzaaAnswer } from './KwanzaaAnswer';
import { mockContract } from '@/test/fixtures/answer_json';

describe('KwanzaaAnswer', () => {
  it('renders answer text', () => {
    render(<KwanzaaAnswer contract={mockContract} />);
    expect(screen.getByText(mockContract.answer.text)).toBeInTheDocument();
  });

  it('renders all citations', () => {
    render(<KwanzaaAnswer contract={mockContract} />);
    const citations = screen.getAllByRole('link', { name: /citation/i });
    expect(citations).toHaveLength(mockContract.sources.length);
  });

  it('shows unknowns when present', () => {
    const contractWithUnknowns = {
      ...mockContract,
      unknowns: {
        ...mockContract.unknowns,
        missing_context: ['Some context is missing'],
      },
    };
    render(<KwanzaaAnswer contract={contractWithUnknowns} />);
    expect(screen.getByText('What\'s Missing or Unclear')).toBeInTheDocument();
  });

  it('hides unknowns when empty', () => {
    render(<KwanzaaAnswer contract={mockContract} />);
    expect(screen.queryByText('What\'s Missing or Unclear')).not.toBeInTheDocument();
  });
});
```

### Integration Tests

```typescript
import { renderWithProviders } from '@/test/utils';
import { waitFor } from '@testing-library/react';

describe('KwanzaaAnswer Integration', () => {
  it('tracks observability events', async () => {
    const trackEvent = jest.fn();
    renderWithProviders(
      <KwanzaaAnswer contract={mockContract} />,
      { observability: { trackEvent } }
    );

    await waitFor(() => {
      expect(trackEvent).toHaveBeenCalledWith('answer_displayed', expect.any(Object));
    });
  });

  it('submits RLHF feedback', async () => {
    const { user } = renderWithProviders(<KwanzaaAnswer contract={mockContract} />);

    const thumbsUpButton = screen.getByRole('button', { name: /thumbs up/i });
    await user.click(thumbsUpButton);

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith('/api/rlhf/feedback', expect.objectContaining({
        method: 'POST',
      }));
    });
  });
});
```

### Visual Regression Tests

```typescript
import { expect, test } from '@playwright/test';

test('answer renders correctly', async ({ page }) => {
  await page.goto('/answer/test-id');

  // Wait for answer to load
  await page.waitForSelector('.kwanzaa-answer');

  // Take screenshot
  await expect(page).toHaveScreenshot('kwanzaa-answer.png');
});

test('citation popover displays on hover', async ({ page }) => {
  await page.goto('/answer/test-id');

  // Hover over first citation
  await page.hover('cite a:first-child');

  // Wait for popover
  await page.waitForSelector('.citation-popover');

  // Take screenshot
  await expect(page).toHaveScreenshot('citation-popover.png');
});
```

## Summary

This integration guide provides:

1. **Complete component mapping** from Answer JSON Contract to AIKit components
2. **Implementation patterns** for all contract sections
3. **Streaming support** for real-time responses
4. **Observability integration** for tracking and analytics
5. **RLHF feedback collection** for continuous improvement
6. **Error handling** for validation failures
7. **Accessibility guidelines** for inclusive UX
8. **Testing strategies** for reliable rendering

By following these patterns, you ensure that the Answer JSON Contract is properly rendered in AIKit with full support for citations, provenance tracking, and transparent retrieval information.

---

**Related Documentation:**
- [Answer JSON Contract Documentation](/Users/aideveloper/kwanzaa/docs/answer_json_contract.md)
- [Answer JSON Quick Reference](/Users/aideveloper/kwanzaa/docs/answer_json_quick_reference.md)
- [Validation Guide](/Users/aideveloper/kwanzaa/docs/development/answer-json-validation.md)
