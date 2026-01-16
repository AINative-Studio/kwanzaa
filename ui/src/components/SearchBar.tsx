/**
 * SearchBar component with debounced input and voice support
 */

import React, { useState, useEffect } from 'react';
import { Search, Loader2, X } from 'lucide-react';
import { useDebounce } from '@hooks/useDebounce';
import clsx from 'clsx';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onSearch: () => void;
  isSearching?: boolean;
  placeholder?: string;
  className?: string;
}

export function SearchBar({
  value,
  onChange,
  onSearch,
  isSearching = false,
  placeholder = 'Search the Kwanzaa corpus...',
  className,
}: SearchBarProps) {
  const [inputValue, setInputValue] = useState(value);
  const debouncedValue = useDebounce(inputValue, 300);

  useEffect(() => {
    onChange(debouncedValue);
  }, [debouncedValue, onChange]);

  useEffect(() => {
    setInputValue(value);
  }, [value]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputValue.trim()) {
      onSearch();
    }
  };

  const handleClear = () => {
    setInputValue('');
    onChange('');
  };

  return (
    <form onSubmit={handleSubmit} className={clsx('relative', className)}>
      <div className="relative flex items-center">
        <Search className="absolute left-4 h-5 w-5 text-gray-400" />

        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder={placeholder}
          disabled={isSearching}
          className={clsx(
            'w-full rounded-lg border border-gray-300 py-3 pl-12 pr-24',
            'text-base text-gray-900 placeholder-gray-500',
            'focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20',
            'disabled:bg-gray-50 disabled:cursor-not-allowed',
            'transition-colors'
          )}
        />

        <div className="absolute right-2 flex items-center gap-2">
          {inputValue && !isSearching && (
            <button
              type="button"
              onClick={handleClear}
              className="rounded-md p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
              aria-label="Clear search"
            >
              <X className="h-4 w-4" />
            </button>
          )}

          <button
            type="submit"
            disabled={!inputValue.trim() || isSearching}
            className={clsx(
              'rounded-md bg-primary-600 px-4 py-1.5 text-sm font-medium text-white',
              'hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2',
              'disabled:bg-gray-300 disabled:cursor-not-allowed',
              'transition-colors'
            )}
          >
            {isSearching ? (
              <div className="flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Searching...</span>
              </div>
            ) : (
              'Search'
            )}
          </button>
        </div>
      </div>
    </form>
  );
}
