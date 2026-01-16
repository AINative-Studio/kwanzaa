/**
 * AnalyticsDashboard component with search metrics
 * Placeholder for AIKit UsageDashboard integration
 */

import React from 'react';
import { BarChart3, TrendingUp, Clock, Filter, Database } from 'lucide-react';
import { useSearchStore } from '@stores/searchStore';
import { formatDuration, formatNumber } from '@utils/format';
import { getNamespaceLabel } from '@utils/namespaces';
import clsx from 'clsx';

interface AnalyticsDashboardProps {
  className?: string;
}

export function AnalyticsDashboard({ className }: AnalyticsDashboardProps) {
  const { analytics } = useSearchStore();

  const topNamespaces = Object.entries(analytics.most_queried_namespaces)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5);

  const topFilters = Object.entries(analytics.filter_usage_patterns)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 5);

  const relevanceData = Object.entries(analytics.relevance_distribution)
    .sort(([a], [b]) => parseFloat(b) - parseFloat(a))
    .map(([score, count]) => ({
      score: parseFloat(score),
      count,
    }));

  if (analytics.total_searches === 0) {
    return (
      <div className={clsx('rounded-lg border border-gray-200 bg-white p-8 text-center', className)}>
        <BarChart3 className="mx-auto mb-3 h-12 w-12 text-gray-400" />
        <h3 className="mb-2 text-lg font-semibold text-gray-900">No Analytics Yet</h3>
        <p className="text-gray-600">
          Start searching to see analytics and usage patterns
        </p>
      </div>
    );
  }

  return (
    <div className={clsx('space-y-6', className)}>
      {/* Header */}
      <div className="flex items-center gap-3">
        <BarChart3 className="h-6 w-6 text-primary-600" />
        <h2 className="text-xl font-bold text-gray-900">Search Analytics</h2>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <MetricCard
          icon={<TrendingUp className="h-5 w-5" />}
          label="Total Searches"
          value={formatNumber(analytics.total_searches)}
          color="blue"
        />

        <MetricCard
          icon={<Clock className="h-5 w-5" />}
          label="Avg Search Time"
          value={formatDuration(Math.round(analytics.average_search_time))}
          color="green"
        />

        <MetricCard
          icon={<Filter className="h-5 w-5" />}
          label="Filters Used"
          value={formatNumber(Object.values(analytics.filter_usage_patterns).reduce((a, b) => a + b, 0))}
          color="purple"
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Most Queried Namespaces */}
        <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex items-center gap-2">
            <Database className="h-5 w-5 text-gray-600" />
            <h3 className="font-semibold text-gray-900">Most Queried Namespaces</h3>
          </div>

          <div className="space-y-3">
            {topNamespaces.map(([namespace, count]) => {
              const total = analytics.total_searches;
              const percentage = (count / total) * 100;

              return (
                <div key={namespace}>
                  <div className="mb-1 flex items-center justify-between text-sm">
                    <span className="font-medium text-gray-700">
                      {getNamespaceLabel(namespace)}
                    </span>
                    <span className="text-gray-600">
                      {formatNumber(count)} ({percentage.toFixed(0)}%)
                    </span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-gray-100">
                    <div
                      className="h-full bg-primary-600"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}

            {topNamespaces.length === 0 && (
              <p className="text-sm text-gray-500">No namespace data yet</p>
            )}
          </div>
        </div>

        {/* Filter Usage Patterns */}
        <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex items-center gap-2">
            <Filter className="h-5 w-5 text-gray-600" />
            <h3 className="font-semibold text-gray-900">Filter Usage Patterns</h3>
          </div>

          <div className="space-y-3">
            {topFilters.map(([filter, count]) => {
              const total = Object.values(analytics.filter_usage_patterns).reduce((a, b) => a + b, 0);
              const percentage = (count / total) * 100;

              return (
                <div key={filter}>
                  <div className="mb-1 flex items-center justify-between text-sm">
                    <span className="font-medium capitalize text-gray-700">
                      {filter.replace(/_/g, ' ')}
                    </span>
                    <span className="text-gray-600">
                      {formatNumber(count)} ({percentage.toFixed(0)}%)
                    </span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-gray-100">
                    <div
                      className="h-full bg-purple-600"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                </div>
              );
            })}

            {topFilters.length === 0 && (
              <p className="text-sm text-gray-500">No filter data yet</p>
            )}
          </div>
        </div>
      </div>

      {/* Relevance Distribution */}
      {relevanceData.length > 0 && (
        <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
          <div className="mb-4 flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-gray-600" />
            <h3 className="font-semibold text-gray-900">Relevance Score Distribution</h3>
          </div>

          <div className="flex items-end gap-2">
            {relevanceData.map(({ score, count }) => {
              const maxCount = Math.max(...relevanceData.map(d => d.count));
              const height = (count / maxCount) * 100;

              return (
                <div key={score} className="flex flex-1 flex-col items-center gap-2">
                  <div
                    className="w-full rounded-t-md bg-gradient-to-t from-green-600 to-yellow-400"
                    style={{ height: `${height}px`, minHeight: '20px' }}
                  />
                  <div className="text-center">
                    <div className="text-xs font-medium text-gray-900">{score.toFixed(1)}</div>
                    <div className="text-xs text-gray-500">{count}</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

interface MetricCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  color: 'blue' | 'green' | 'purple';
}

function MetricCard({ icon, label, value, color }: MetricCardProps) {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
  };

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-5 shadow-sm">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <div className="mb-1 text-sm font-medium text-gray-600">{label}</div>
          <div className="text-2xl font-bold text-gray-900">{value}</div>
        </div>
        <div className={clsx('rounded-lg p-2.5', colorClasses[color])}>
          {icon}
        </div>
      </div>
    </div>
  );
}
