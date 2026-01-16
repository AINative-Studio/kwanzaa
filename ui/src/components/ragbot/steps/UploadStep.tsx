/**
 * Upload Step Component
 *
 * Drag-and-drop file upload with AIKit ProgressBar integration.
 */

import React, { useState, useCallback } from 'react';
import ProgressBar from '../../../lib/aikit/react/ProgressBar';
import StreamingIndicator from '../../../lib/aikit/react/StreamingIndicator';

interface UploadStepProps {
  onFileUploaded: (file: File, documentId: string) => void;
}

export const UploadStep: React.FC<UploadStepProps> = ({ onFileUploaded }) => {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const ALLOWED_TYPES = ['application/pdf', 'text/plain', 'text/markdown', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
  const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

  const validateFile = (file: File): string | null => {
    if (!ALLOWED_TYPES.includes(file.type) && !file.name.match(/\.(pdf|txt|md|docx)$/i)) {
      return 'Invalid file type. Please upload PDF, TXT, MD, or DOCX files.';
    }
    if (file.size > MAX_FILE_SIZE) {
      return 'File size exceeds 50MB limit.';
    }
    return null;
  };

  const uploadFile = async (file: File) => {
    const validationError = validateFile(file);
    if (validationError) {
      setError(validationError);
      return;
    }

    setUploading(true);
    setProgress(0);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Simulate upload progress
      const xhr = new XMLHttpRequest();

      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const percentComplete = (e.loaded / e.total) * 100;
          setProgress(percentComplete);
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText);
          setTimeout(() => {
            onFileUploaded(file, response.document_id);
          }, 500);
        } else {
          setError(`Upload failed: ${xhr.statusText}`);
          setUploading(false);
        }
      });

      xhr.addEventListener('error', () => {
        setError('Upload failed. Please try again.');
        setUploading(false);
      });

      xhr.open('POST', '/api/v1/ragbot/upload');
      xhr.send(formData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed');
      setUploading(false);
    }
  };

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      uploadFile(e.dataTransfer.files[0]);
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      uploadFile(e.target.files[0]);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Upload Document</h2>
        <p className="text-gray-600">
          Upload a document to begin the curation process. Supported formats: PDF, TXT, MD, DOCX
          (max 50MB)
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
          <div className="flex items-center space-x-2">
            <span className="text-xl">⚠️</span>
            <span className="font-medium">{error}</span>
          </div>
        </div>
      )}

      {!uploading ? (
        <div
          className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
            dragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <div className="flex flex-col items-center space-y-4">
            <svg
              className="w-16 h-16 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
              />
            </svg>

            <div>
              <p className="text-lg font-medium text-gray-900 mb-1">
                Drag and drop your file here
              </p>
              <p className="text-sm text-gray-600">or</p>
            </div>

            <label className="cursor-pointer">
              <input
                type="file"
                className="hidden"
                accept=".pdf,.txt,.md,.docx"
                onChange={handleFileSelect}
              />
              <span className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors inline-block">
                Choose File
              </span>
            </label>

            <div className="text-xs text-gray-500 space-y-1">
              <div>Supported formats: PDF, TXT, MD, DOCX</div>
              <div>Maximum file size: 50MB</div>
            </div>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-center space-x-3">
            <StreamingIndicator variant="spinner" size="lg" color="primary" />
            <span className="text-lg font-medium text-gray-900">Uploading document...</span>
          </div>

          <ProgressBar
            value={progress}
            color="primary"
            showPercentage
            animated
            label="Upload Progress"
          />
        </div>
      )}

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 mb-2">What happens next?</h3>
        <ol className="list-decimal list-inside space-y-1 text-sm text-blue-800">
          <li>Enter provenance metadata (source, license, etc.)</li>
          <li>Automatic safety scan for PII and harmful content</li>
          <li>Document chunking and preview</li>
          <li>Review and validation</li>
          <li>Publish to vector database</li>
        </ol>
      </div>
    </div>
  );
};

export default UploadStep;
