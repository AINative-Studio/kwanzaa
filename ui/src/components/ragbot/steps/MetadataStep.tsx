/**
 * Metadata Step Component
 *
 * Form for entering provenance metadata with validation.
 */

import React, { useState } from 'react';
import { DocumentMetadata } from '../RAGBotUploadWorkflow';

interface MetadataStepProps {
  file: File;
  onSubmit: (metadata: DocumentMetadata) => void;
  onBack: () => void;
}

export const MetadataStep: React.FC<MetadataStepProps> = ({ file, onSubmit, onBack }) => {
  const [metadata, setMetadata] = useState<Partial<DocumentMetadata>>({
    content_type: 'article',
    year: new Date().getFullYear(),
  });
  const [errors, setErrors] = useState<Partial<Record<keyof DocumentMetadata, string>>>({});

  const validateMetadata = (): boolean => {
    const newErrors: Partial<Record<keyof DocumentMetadata, string>> = {};

    if (!metadata.source_org?.trim()) {
      newErrors.source_org = 'Source organization is required';
    }

    if (!metadata.canonical_url?.trim()) {
      newErrors.canonical_url = 'Canonical URL is required';
    } else if (!/^https?:\/\/.+/.test(metadata.canonical_url)) {
      newErrors.canonical_url = 'Must be a valid URL';
    }

    if (!metadata.license?.trim()) {
      newErrors.license = 'License is required';
    }

    if (!metadata.year || metadata.year < 1800 || metadata.year > new Date().getFullYear()) {
      newErrors.year = 'Valid year is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateMetadata()) {
      onSubmit(metadata as DocumentMetadata);
    }
  };

  const handleChange = (field: keyof DocumentMetadata, value: any) => {
    setMetadata((prev) => ({ ...prev, [field]: value }));
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors[field];
        return newErrors;
      });
    }
  };

  const commonLicenses = [
    'Public Domain',
    'CC0',
    'CC BY 4.0',
    'CC BY-SA 4.0',
    'CC BY-NC 4.0',
    'MIT',
    'Apache 2.0',
    'Custom',
  ];

  const contentTypes = [
    'article',
    'book',
    'speech',
    'letter',
    'report',
    'paper',
    'interview',
    'other',
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Document Metadata</h2>
        <p className="text-gray-600">
          Enter provenance information for <strong>{file.name}</strong>
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Source Organization */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Source Organization <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={metadata.source_org || ''}
            onChange={(e) => handleChange('source_org', e.target.value)}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
              errors.source_org ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="e.g., Library of Congress, Project Gutenberg"
          />
          {errors.source_org && (
            <p className="mt-1 text-sm text-red-600">{errors.source_org}</p>
          )}
        </div>

        {/* Canonical URL */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Canonical URL <span className="text-red-500">*</span>
          </label>
          <input
            type="url"
            value={metadata.canonical_url || ''}
            onChange={(e) => handleChange('canonical_url', e.target.value)}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
              errors.canonical_url ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="https://example.org/document"
          />
          {errors.canonical_url && (
            <p className="mt-1 text-sm text-red-600">{errors.canonical_url}</p>
          )}
        </div>

        {/* License */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            License <span className="text-red-500">*</span>
          </label>
          <select
            value={metadata.license || ''}
            onChange={(e) => handleChange('license', e.target.value)}
            className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
              errors.license ? 'border-red-500' : 'border-gray-300'
            }`}
          >
            <option value="">Select license...</option>
            {commonLicenses.map((license) => (
              <option key={license} value={license}>
                {license}
              </option>
            ))}
          </select>
          {errors.license && <p className="mt-1 text-sm text-red-600">{errors.license}</p>}
        </div>

        <div className="grid grid-cols-2 gap-4">
          {/* Year */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Year <span className="text-red-500">*</span>
            </label>
            <input
              type="number"
              value={metadata.year || ''}
              onChange={(e) => handleChange('year', parseInt(e.target.value))}
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 ${
                errors.year ? 'border-red-500' : 'border-gray-300'
              }`}
              min="1800"
              max={new Date().getFullYear()}
            />
            {errors.year && <p className="mt-1 text-sm text-red-600">{errors.year}</p>}
          </div>

          {/* Content Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Content Type <span className="text-red-500">*</span>
            </label>
            <select
              value={metadata.content_type || ''}
              onChange={(e) => handleChange('content_type', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              {contentTypes.map((type) => (
                <option key={type} value={type}>
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Author (Optional) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Author</label>
          <input
            type="text"
            value={metadata.author || ''}
            onChange={(e) => handleChange('author', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Document author (optional)"
          />
        </div>

        {/* Title (Optional) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
          <input
            type="text"
            value={metadata.title || ''}
            onChange={(e) => handleChange('title', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="Document title (optional)"
          />
        </div>

        {/* Tags (Optional) */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Tags (comma-separated)
          </label>
          <input
            type="text"
            value={metadata.tags?.join(', ') || ''}
            onChange={(e) =>
              handleChange(
                'tags',
                e.target.value.split(',').map((t) => t.trim()).filter(Boolean)
              )
            }
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            placeholder="history, civil-rights, primary-source"
          />
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-between pt-4 border-t">
          <button
            type="button"
            onClick={onBack}
            className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Back
          </button>
          <button
            type="submit"
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            Continue to Safety Scan
          </button>
        </div>
      </form>
    </div>
  );
};

export default MetadataStep;
