/**
 * KwanzaaChat Component
 *
 * Main chat interface with complete AIKit integration:
 * - useConversation hook for state management
 * - Safety detection on all inputs (PromptInjection, Jailbreak, PII, ContentModeration)
 * - Observability tracking for all interactions
 * - RLHF feedback collection on every response
 * - answer_json rendering with AIKit components
 * - Persona selector and mode toggles
 * - UsageDashboard for token/cost tracking
 */

import React, { useState, useEffect, useRef } from 'react';
import { clsx } from 'clsx';
import { v4 as uuidv4 } from 'uuid';
import axios from 'axios';

// AIKit imports (mocked for development)
import {
  useConversation,
  PromptInjectionDetector,
  JailbreakDetector,
  PIIDetector,
  ContentModerator,
  useObservability,
  useRLHF,
} from '../../lib/aikit-mocks';

// Type imports
import type {
  Persona,
  ModelMode,
  ChatRequest,
  AnswerJsonContract,
  SafetyResult,
  RLHFeedback,
  UsageMetrics,
} from '../../types/answer-json';

// Component imports
import { PersonaSelector } from '../controls/PersonaSelector';
import { ModeToggles } from '../controls/ModeToggles';
import { ChatInput } from './ChatInput';
import { MessageList } from './MessageList';
import { SafetyIndicator } from '../safety/SafetyIndicator';
import { UsageDashboard } from '../aikit/UsageDashboard';
import { StreamingIndicator } from '../aikit/StreamingIndicator';
import { Settings, BarChart3, MessageSquare } from 'lucide-react';

export interface KwanzaaChatProps {
  apiBaseUrl?: string;
  className?: string;
}

export const KwanzaaChat: React.FC<KwanzaaChatProps> = ({
  apiBaseUrl = 'http://localhost:8000/api/v1',
  className,
}) => {
  // Session and state management
  const [sessionId] = useState(() => uuidv4());
  const [persona, setPersona] = useState<Persona>('educator');
  const [mode, setMode] = useState<ModelMode>('base_adapter_rag');
  const [showSettings, setShowSettings] = useState(false);
  const [showMetrics, setShowMetrics] = useState(false);

  // AIKit hooks
  const conversation = useConversation({ sessionId });
  const observability = useObservability({ projectId: 'kwanzaa' });
  const rlhf = useRLHF({ projectId: 'kwanzaa' });

  // Safety detectors
  const [safetyDetectors] = useState(() => ({
    promptInjection: new PromptInjectionDetector(),
    jailbreak: new JailbreakDetector(),
    pii: new PIIDetector(),
    contentModerator: new ContentModerator(),
  }));

  // Safety state
  const [currentSafetyResult, setCurrentSafetyResult] = useState<SafetyResult | null>(null);

  // Usage metrics
  const [metrics, setMetrics] = useState<UsageMetrics | null>(null);

  // Messages with answer_json
  const [messages, setMessages] = useState<Array<{
    id: string;
    role: 'user' | 'assistant';
    content: string;
    answerJson?: AnswerJsonContract;
    timestamp: Date;
  }>>([]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Load metrics periodically
  useEffect(() => {
    const loadMetrics = async () => {
      try {
        const metricsData = await observability.getMetrics(sessionId);
        setMetrics(metricsData);
      } catch (error) {
        console.error('Failed to load metrics:', error);
      }
    };

    loadMetrics();
    const interval = setInterval(loadMetrics, 30000); // Every 30 seconds
    return () => clearInterval(interval);
  }, [sessionId, observability]);

  // Track persona and mode changes
  useEffect(() => {
    observability.track('persona_change', {
      session_id: sessionId,
      persona,
      timestamp: new Date().toISOString(),
    });
  }, [persona, sessionId, observability]);

  useEffect(() => {
    observability.track('mode_change', {
      session_id: sessionId,
      mode,
      timestamp: new Date().toISOString(),
    });
  }, [mode, sessionId, observability]);

  /**
   * Run all safety checks on input text
   */
  const runSafetyChecks = async (text: string): Promise<SafetyResult> => {
    const checks = await Promise.all([
      safetyDetectors.promptInjection.detect(text),
      safetyDetectors.jailbreak.detect(text),
      safetyDetectors.pii.detect(text),
      safetyDetectors.contentModerator.moderate(text),
    ]);

    const overallSafe = checks.every(check => check.passed);
    const warnings: string[] = [];

    checks.forEach(check => {
      if (!check.passed && check.details) {
        warnings.push(check.details);
      }
    });

    // Get PII redaction if needed
    const piiCheck = checks[2] as any;
    const redactedText = piiCheck.redactedText;

    return {
      checks,
      overallSafe,
      warnings,
      redactedText,
    };
  };

  /**
   * Handle user message submission
   */
  const handleSendMessage = async (userInput: string) => {
    if (!userInput.trim()) return;

    // Track query start
    const queryStartTime = Date.now();

    // Run safety checks
    const safetyResult = await runSafetyChecks(userInput);
    setCurrentSafetyResult(safetyResult);

    // Log safety check results
    observability.track('safety_check', {
      session_id: sessionId,
      overall_safe: safetyResult.overallSafe,
      checks: safetyResult.checks,
      timestamp: new Date().toISOString(),
    });

    if (!safetyResult.overallSafe) {
      // Don't send if unsafe
      return;
    }

    // Use redacted text if PII was detected
    const processedInput = safetyResult.redactedText || userInput;

    // Add user message
    const userMessage = {
      id: uuidv4(),
      role: 'user' as const,
      content: processedInput,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);

    // Track query
    observability.track('query', {
      session_id: sessionId,
      query: processedInput,
      persona,
      mode,
      timestamp: new Date().toISOString(),
    });

    try {
      // Call backend API
      const request: ChatRequest = {
        query: processedInput,
        persona_key: persona,
        mode,
        session_id: sessionId,
      };

      const response = await axios.post<AnswerJsonContract>(
        `${apiBaseUrl}/chat`,
        request
      );

      const answerJson = response.data;
      const responseTime = Date.now() - queryStartTime;

      // Add assistant message
      const assistantMessage = {
        id: uuidv4(),
        role: 'assistant' as const,
        content: answerJson.answer.text,
        answerJson,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);

      // Track response
      observability.track('response', {
        session_id: sessionId,
        response_time_ms: responseTime,
        persona: answerJson.persona,
        mode: answerJson.model_mode,
        sources_count: answerJson.sources.length,
        retrieval_confidence: answerJson.integrity?.retrieval_confidence,
        timestamp: new Date().toISOString(),
      });

      // Track retrieval
      observability.track('retrieval', {
        session_id: sessionId,
        retrieval_run_id: answerJson.provenance?.retrieval_run_id,
        results_count: answerJson.retrieval_summary.results.length,
        execution_time_ms: answerJson.retrieval_summary.execution_time_ms,
        timestamp: new Date().toISOString(),
      });

      // Content moderation on response
      const responseModeration = await safetyDetectors.contentModerator.moderate(
        answerJson.answer.text
      );

      if (!responseModeration.passed) {
        observability.track('safety_flag', {
          session_id: sessionId,
          type: 'response_moderation_failed',
          details: responseModeration.details,
          timestamp: new Date().toISOString(),
        });
      }

      // Clear safety result after successful response
      setCurrentSafetyResult(null);
    } catch (error) {
      console.error('Chat error:', error);

      // Track error
      observability.track('error', {
        session_id: sessionId,
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString(),
      });

      // Add error message
      const errorMessage = {
        id: uuidv4(),
        role: 'assistant' as const,
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  /**
   * Handle RLHF feedback
   */
  const handleFeedback = async (feedback: RLHFeedback) => {
    await rlhf.submitFeedback(feedback);

    // Track feedback
    observability.track('rlhf_feedback', {
      session_id: sessionId,
      feedback_type: feedback.feedback_type,
      rating: feedback.rating,
      timestamp: new Date().toISOString(),
    });
  };

  return (
    <div className={clsx('kwanzaa-chat flex flex-col h-screen bg-gray-50', className)}>
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Kwanzaa Chat</h1>
            <p className="text-sm text-gray-600">
              AI-powered search with citations and provenance
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowMetrics(!showMetrics)}
              className={clsx(
                'p-2 rounded-md transition-colors',
                showMetrics
                  ? 'bg-blue-100 text-blue-700'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              )}
              title="Toggle metrics"
            >
              <BarChart3 size={20} />
            </button>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className={clsx(
                'p-2 rounded-md transition-colors',
                showSettings
                  ? 'bg-blue-100 text-blue-700'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              )}
              title="Toggle settings"
            >
              <Settings size={20} />
            </button>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Sidebar - Settings */}
        {showSettings && (
          <div className="w-80 bg-white border-r border-gray-200 overflow-y-auto p-6 space-y-6">
            <PersonaSelector selected={persona} onChange={setPersona} />
            <ModeToggles selected={mode} onChange={setMode} />
          </div>
        )}

        {/* Chat area */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6">
            <MessageList
              messages={messages}
              onFeedback={handleFeedback}
            />
            {conversation.isLoading && (
              <div className="flex justify-center py-4">
                <StreamingIndicator text="Searching and generating response..." />
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Safety indicator */}
          {currentSafetyResult && (
            <div className="px-6 pb-4">
              <SafetyIndicator result={currentSafetyResult} />
            </div>
          )}

          {/* Input */}
          <div className="border-t border-gray-200 bg-white p-6">
            <ChatInput
              onSend={handleSendMessage}
              disabled={conversation.isLoading}
              placeholder={`Ask ${persona} a question...`}
            />
          </div>
        </div>

        {/* Sidebar - Metrics */}
        {showMetrics && metrics && (
          <div className="w-96 bg-white border-l border-gray-200 overflow-y-auto p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <MessageSquare size={20} />
              Session Metrics
            </h2>
            <UsageDashboard metrics={metrics} />
          </div>
        )}
      </div>
    </div>
  );
};
