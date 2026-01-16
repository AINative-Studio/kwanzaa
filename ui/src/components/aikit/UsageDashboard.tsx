/**
 * UsageDashboard Component
 *
 * Displays token usage, costs, and performance metrics.
 * Part of @ainative/ai-kit-observability component library.
 */

import React from 'react';
import { clsx } from 'clsx';
import type { UsageMetrics, Persona, ModelMode } from '../../types/answer-json';
import { Activity, Clock, DollarSign, Zap } from 'lucide-react';

export interface UsageDashboardProps {
  metrics: UsageMetrics;
  className?: string;
}

export const UsageDashboard: React.FC<UsageDashboardProps> = ({ metrics, className }) => {
  const formatNumber = (num: number): string => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(2)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(2)}K`;
    return num.toString();
  };

  const formatCurrency = (amount: number): string => {
    return `$${amount.toFixed(4)}`;
  };

  const formatTime = (ms: number): string => {
    if (ms >= 1000) return `${(ms / 1000).toFixed(2)}s`;
    return `${ms}ms`;
  };

  return (
    <div className={clsx('usage-dashboard space-y-6', className)}>
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-gray-600 mb-2">
            <Activity size={18} />
            <span className="text-sm font-medium">Total Queries</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">{metrics.total_queries}</p>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-gray-600 mb-2">
            <Zap size={18} />
            <span className="text-sm font-medium">Total Tokens</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {formatNumber(metrics.total_tokens)}
          </p>
          <p className="text-xs text-gray-500 mt-1">
            In: {formatNumber(metrics.input_tokens)} | Out: {formatNumber(metrics.output_tokens)}
          </p>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-gray-600 mb-2">
            <DollarSign size={18} />
            <span className="text-sm font-medium">Est. Cost</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {formatCurrency(metrics.estimated_cost)}
          </p>
        </div>

        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-gray-600 mb-2">
            <Clock size={18} />
            <span className="text-sm font-medium">Avg Response Time</span>
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {formatTime(metrics.avg_response_time_ms)}
          </p>
        </div>
      </div>

      {/* Persona Usage */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-gray-900 mb-4">Persona Usage</h3>
        <div className="space-y-3">
          {Object.entries(metrics.persona_usage).map(([persona, count]) => {
            const percentage = (count / metrics.total_queries) * 100;
            return (
              <div key={persona}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm text-gray-700 capitalize">{persona}</span>
                  <span className="text-sm text-gray-600">{count} ({percentage.toFixed(0)}%)</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Mode Usage */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-gray-900 mb-4">Mode Usage</h3>
        <div className="space-y-3">
          {Object.entries(metrics.mode_usage).map(([mode, count]) => {
            const percentage = (count / metrics.total_queries) * 100;
            return (
              <div key={mode}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm text-gray-700">{mode}</span>
                  <span className="text-sm text-gray-600">{count} ({percentage.toFixed(0)}%)</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-purple-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
