/**
 * Namespace definitions and utilities
 */

export const NAMESPACES = [
  {
    value: 'kwanzaa_primary_sources',
    label: 'Primary Sources',
    description: 'Historical documents, artifacts, and primary materials',
    color: 'bg-blue-100 text-blue-800',
  },
  {
    value: 'kwanzaa_black_press',
    label: 'Black Press',
    description: 'Historical Black newspapers and journalism',
    color: 'bg-purple-100 text-purple-800',
  },
  {
    value: 'kwanzaa_speeches_letters',
    label: 'Speeches & Letters',
    description: 'Historical speeches, letters, and correspondence',
    color: 'bg-green-100 text-green-800',
  },
  {
    value: 'kwanzaa_black_stem',
    label: 'Black STEM',
    description: 'Contributions to science, technology, engineering, mathematics',
    color: 'bg-indigo-100 text-indigo-800',
  },
  {
    value: 'kwanzaa_teaching_kits',
    label: 'Teaching Kits',
    description: 'Educational materials and curriculum resources',
    color: 'bg-yellow-100 text-yellow-800',
  },
  {
    value: 'kwanzaa_dev_patterns',
    label: 'Development Patterns',
    description: 'Software patterns and technical documentation',
    color: 'bg-gray-100 text-gray-800',
  },
] as const;

export type NamespaceValue = typeof NAMESPACES[number]['value'];

export function getNamespaceConfig(value: string) {
  return NAMESPACES.find(ns => ns.value === value);
}

export function getNamespaceLabel(value: string): string {
  return getNamespaceConfig(value)?.label || value;
}

export function getNamespaceColor(value: string): string {
  return getNamespaceConfig(value)?.color || 'bg-gray-100 text-gray-800';
}
