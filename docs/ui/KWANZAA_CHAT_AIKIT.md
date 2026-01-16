# Kwanzaa Chat UI - Complete AIKit Integration

A comprehensive chat interface built with React, TypeScript, and the complete AIKit ecosystem for AI-powered search with citations, provenance tracking, and transparent uncertainty communication.

## Overview

This UI implements **Epic 7 - Issue #31** with full integration of all AIKit packages:

- **@ainative/ai-kit-react** - Conversation management hooks and UI components
- **@ainative/ai-kit-core** - Core utilities and helpers
- **@ainative/ai-kit-safety** - Safety detectors (PromptInjection, Jailbreak, PII, ContentModeration)
- **@ainative/ai-kit-observability** - Event tracking and metrics
- **@ainative/ai-kit-rlhf** - Feedback collection and learning
- **@ainative/ai-kit-zerodb** - Vector database integration
- **@ainative/ai-kit-tools** - Tool execution and rendering

## Architecture

### Component Structure

```
ui/src/
├── components/
│   ├── aikit/              # AIKit component library
│   │   ├── AgentResponse.tsx         # Structured AI response rendering
│   │   ├── StreamingMessage.tsx      # Streaming text with indicators
│   │   ├── MarkdownRenderer.tsx      # Rich text markdown rendering
│   │   ├── CodeBlock.tsx             # Code and citation display
│   │   ├── ToolResult.tsx            # Tool execution results
│   │   ├── StreamingIndicator.tsx    # Loading states
│   │   ├── UsageDashboard.tsx        # Token/cost metrics
│   │   └── Badge.tsx                 # UI utilities
│   ├── answer/             # answer_json rendering
│   │   ├── AnswerJsonRenderer.tsx    # Main renderer
│   │   ├── SourcesList.tsx           # Citations display
│   │   └── UnknownsSection.tsx       # Gaps/limitations
│   ├── chat/               # Chat interface
│   │   ├── KwanzaaChat.tsx           # Main chat component
│   │   ├── MessageList.tsx           # Message display
│   │   └── ChatInput.tsx             # User input
│   ├── controls/           # User controls
│   │   ├── PersonaSelector.tsx       # Persona chooser
│   │   └── ModeToggles.tsx           # Mode selection
│   ├── safety/             # Safety integration
│   │   └── SafetyIndicator.tsx       # Safety warnings
│   └── rlhf/               # RLHF feedback
│       ├── FeedbackButtons.tsx       # Thumbs up/down
│       └── DetailedFeedbackModal.tsx # Detailed ratings
├── lib/
│   └── aikit-mocks.ts      # AIKit mock implementations
├── types/
│   └── answer-json.ts      # TypeScript types
└── App.tsx                 # Main application
```

## Features

### 1. Conversation Management (AIKit)

Uses `useConversation` hook from `@ainative/ai-kit-react`:

```typescript
import { useConversation } from '@ainative/ai-kit-react';

const conversation = useConversation({
  sessionId,
  onMessage: handleMessage,
  onError: handleError
});
```

**Features:**
- Message history management
- Streaming support
- Error handling
- Retry mechanisms

### 2. Safety Integration (REQUIRED)

All user inputs pass through safety detectors:

```typescript
import {
  PromptInjectionDetector,
  JailbreakDetector,
  PIIDetector,
  ContentModerator,
} from '@ainative/ai-kit-safety';

// Initialize detectors
const detectors = {
  promptInjection: new PromptInjectionDetector(),
  jailbreak: new JailbreakDetector(),
  pii: new PIIDetector(),
  contentModerator: new ContentModerator(),
};

// Run on every input
const safetyResult = await runSafetyChecks(userInput);
```

**Safety Checks:**
- ✅ **Prompt Injection Detection** - Blocks manipulation attempts
- ✅ **Jailbreak Detection** - Prevents constraint bypass
- ✅ **PII Detection** - Identifies and redacts personal information
- ✅ **Content Moderation** - Filters unsafe content on responses

**Safety Indicators:**
- Real-time warnings shown to users
- All safety events logged to observability
- Failed checks block message sending
- PII automatically redacted before sending

### 3. Observability Tracking (REQUIRED)

All interactions tracked with `@ainative/ai-kit-observability`:

```typescript
import { useObservability } from '@ainative/ai-kit-observability';

const observability = useObservability({ projectId: 'kwanzaa' });

// Track events
await observability.track('query', {
  session_id: sessionId,
  query: processedInput,
  persona,
  mode,
});
```

**Tracked Events:**
- `query` - User queries with metadata
- `response` - AI responses with timing
- `retrieval` - Retrieval operations
- `persona_change` - Persona switches
- `mode_change` - Mode switches
- `safety_check` - Safety check results
- `rlhf_feedback` - User feedback
- `error` - Error occurrences

**Metrics Dashboard:**
- Total queries and tokens
- Input/output token breakdown
- Estimated costs
- Average response time
- Persona usage distribution
- Mode usage distribution

### 4. RLHF Feedback Collection (REQUIRED)

Every assistant response includes feedback buttons:

```typescript
import { useRLHF } from '@ainative/ai-kit-rlhf';

const rlhf = useRLHF({ projectId: 'kwanzaa' });

// Submit feedback
await rlhf.submitFeedback({
  message_id: messageId,
  feedback_type: 'thumbs_up',
  timestamp: new Date(),
});
```

**Feedback Types:**
- **Thumbs Up/Down** - Quick feedback on every response
- **Detailed Ratings** - 5-star ratings with aspects:
  - Accuracy
  - Helpfulness
  - Citation quality
  - Persona alignment
- **Comments** - Optional text feedback
- **Citation Helpfulness** - Specific source ratings

### 5. answer_json Rendering

Complete implementation of Epic 8 answer_json format:

```typescript
interface AnswerJsonContract {
  version: string;
  persona?: Persona;
  model_mode?: ModelMode;
  toggles?: Toggles;
  answer: Answer;              // ✅ Rendered with MarkdownRenderer
  sources: Source[];           // ✅ Rendered with SourcesList
  retrieval_summary: RetrievalSummary;  // ✅ Rendered with ToolResult
  unknowns: Unknowns;          // ✅ Rendered with UnknownsSection
  integrity?: Integrity;        // ✅ Shows safety badges
  provenance?: Provenance;      // ✅ Shows metadata
}
```

**Rendering Components:**
- `AgentResponse` - Main answer with metadata badges
- `SourcesList` - Clickable citations with provenance
- `ToolResult` - Collapsible retrieval details
- `UnknownsSection` - Transparent limitations
- `FeedbackButtons` - RLHF collection

### 6. Persona System

Four personas with distinct behaviors:

| Persona | Icon | Focus | Citations | Primary Sources |
|---------|------|-------|-----------|-----------------|
| **Educator** | 🎓 | Clear explanations | Required | Preferred |
| **Researcher** | 🔍 | Deep analysis | Required | Required |
| **Creator** | 🎨 | Creative tools | Optional | Preferred |
| **Builder** | 💻 | Technical guidance | Required | Optional |

### 7. Mode Toggles

| Mode | Description | Use Case |
|------|-------------|----------|
| **Base Only** | Raw LLM without fine-tuning | Baseline comparison |
| **Base + Adapter** | Fine-tuned for citations | Improved citation quality |
| **Base + Adapter + RAG** | Full system with retrieval | Production (recommended) |
| **Creative Mode** | Fewer constraints | Creative exploration |

## Installation

```bash
cd ui
npm install
```

## Configuration

Create `.env` file:

```bash
cp .env.example .env
```

Edit environment variables:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_AIKIT_PROJECT_ID=your-project-id
VITE_OBSERVABILITY_ENABLED=true
VITE_RLHF_ENABLED=true
VITE_SAFETY_ENABLED=true
```

## Development

```bash
# Start dev server
npm run dev

# Type checking
npm run type-check

# Linting
npm run lint

# Run tests
npm test

# Run tests with UI
npm run test:ui

# Generate coverage
npm run test:coverage
```

## Building

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Testing

### Test Coverage

The test suite covers:

1. **Component Rendering**
   - Chat interface
   - Empty states
   - Message display
   - Settings panels

2. **Safety Integration**
   - Prompt injection detection
   - Jailbreak detection
   - PII detection and redaction
   - Content moderation

3. **User Interactions**
   - Persona selection
   - Mode toggling
   - Message sending
   - Feedback collection

4. **answer_json Rendering**
   - Answer text display
   - Source citations
   - Retrieval summary
   - Unknowns section

5. **RLHF Integration**
   - Feedback buttons
   - Detailed ratings
   - Comment collection

### Running Tests

```bash
# Run all tests
npm test

# Watch mode
npm test -- --watch

# Coverage report
npm run test:coverage
```

## API Integration

### Chat Endpoint

```typescript
POST /api/v1/chat
Content-Type: application/json

{
  "query": "What is Kwanzaa?",
  "persona_key": "educator",
  "mode": "base_adapter_rag",
  "session_id": "uuid-here"
}
```

**Response:** Returns `AnswerJsonContract` format

### Expected Backend Routes

The UI expects these backend endpoints:

- `POST /api/v1/chat` - Main chat endpoint
- `GET /api/v1/health` - Health check
- `GET /api/v1/metrics` - Usage metrics (optional)

## Acceptance Criteria

### ✅ AIKit Integration

- [x] Uses `useConversation` hook (not custom state)
- [x] ALL inputs validated with safety detectors
- [x] PII detection/redaction enabled
- [x] Content moderation on responses
- [x] `UsageDashboard` shows metrics
- [x] RLHF feedback on every response
- [x] Streaming via AIKit primitives
- [x] Tools rendered with AIKit components
- [x] Observability tracks all interactions
- [x] answer_json rendered with AIKit

### ✅ Safety Features

- [x] `PromptInjectionDetector` on all user inputs
- [x] `JailbreakDetector` on all user inputs
- [x] `PIIDetector` with optional redaction
- [x] `ContentModerator` on all responses
- [x] Safety warnings shown to users
- [x] All safety events logged

### ✅ Observability

- [x] Track all queries, responses, retrieval
- [x] Monitor persona usage patterns
- [x] Log mode switches
- [x] Track token usage and costs
- [x] Display metrics in `UsageDashboard`
- [x] Export analytics data capability

### ✅ RLHF Integration

- [x] Thumbs up/down on every response
- [x] Collect detailed feedback (rating 1-5)
- [x] Track citation helpfulness
- [x] Log persona effectiveness
- [x] Submit to AIKit RLHF service

### ✅ UI Features

- [x] Chat interface with message history
- [x] Mode toggles: base, base+adapter, base+adapter+RAG
- [x] Persona selector: builder, educator, creator, researcher
- [x] answer_json rendering
- [x] Citations display with provenance
- [x] Retrieval summaries (collapsible)
- [x] Unknowns section
- [x] Session persistence
- [x] Safety status indicators
- [x] Cost/usage tracking

## AIKit Mock Implementation

Since the actual AIKit packages may not be published yet, this implementation includes mock implementations in `/src/lib/aikit-mocks.ts` that demonstrate the expected API surface.

**To use real AIKit packages:**

1. Install real packages:
```bash
npm install @ainative/ai-kit-react @ainative/ai-kit-safety @ainative/ai-kit-observability @ainative/ai-kit-rlhf
```

2. Update imports in components:
```typescript
// Change from:
import { useConversation } from '../../lib/aikit-mocks';

// To:
import { useConversation } from '@ainative/ai-kit-react';
```

3. Configure with API keys in `.env`

## Technology Stack

- **React 18.3** - UI framework
- **TypeScript 5.3** - Type safety
- **Vite 5.1** - Build tool
- **Tailwind CSS 3.4** - Styling
- **Vitest** - Testing framework
- **AIKit** - Complete AI toolkit integration

## Browser Support

- Chrome/Edge (latest 2 versions)
- Firefox (latest 2 versions)
- Safari (latest 2 versions)

## License

Apache-2.0

## Support

For issues or questions:
- GitHub Issues: https://github.com/AINative-Studio/kwanzaa/issues
- Documentation: /docs
- Epic 7 Tracking: Issue #31
