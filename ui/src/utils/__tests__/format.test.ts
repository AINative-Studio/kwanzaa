import { describe, it, expect } from 'vitest';
import {
  formatDuration,
  formatNumber,
  formatPercent,
  truncate,
  getScoreColor,
  getScoreWidth,
} from '../format';

describe('format utilities', () => {
  describe('formatDuration', () => {
    it('formats milliseconds', () => {
      expect(formatDuration(500)).toBe('500ms');
    });

    it('formats seconds', () => {
      expect(formatDuration(2500)).toBe('2.5s');
    });

    it('formats minutes', () => {
      expect(formatDuration(125000)).toBe('2m 5s');
    });
  });

  describe('formatNumber', () => {
    it('formats numbers with commas', () => {
      expect(formatNumber(1000)).toBe('1,000');
      expect(formatNumber(1000000)).toBe('1,000,000');
    });

    it('handles small numbers', () => {
      expect(formatNumber(42)).toBe('42');
    });
  });

  describe('formatPercent', () => {
    it('formats as percentage', () => {
      expect(formatPercent(0.75)).toBe('75.0%');
      expect(formatPercent(0.5)).toBe('50.0%');
    });

    it('respects decimal places', () => {
      expect(formatPercent(0.333, 2)).toBe('33.30%');
      expect(formatPercent(0.333, 0)).toBe('33%');
    });
  });

  describe('truncate', () => {
    it('truncates long text', () => {
      const long = 'This is a very long text that needs truncation';
      expect(truncate(long, 20)).toBe('This is a very long ...');
    });

    it('does not truncate short text', () => {
      const short = 'Short';
      expect(truncate(short, 20)).toBe('Short');
    });
  });

  describe('getScoreColor', () => {
    it('returns green for high scores', () => {
      expect(getScoreColor(0.95)).toBe('text-green-600');
      expect(getScoreColor(0.85)).toBe('text-green-500');
    });

    it('returns yellow for medium scores', () => {
      expect(getScoreColor(0.75)).toBe('text-yellow-600');
      expect(getScoreColor(0.65)).toBe('text-yellow-500');
    });

    it('returns gray for low scores', () => {
      expect(getScoreColor(0.5)).toBe('text-gray-500');
    });
  });

  describe('getScoreWidth', () => {
    it('converts score to percentage width', () => {
      expect(getScoreWidth(0.95)).toBe('95%');
      expect(getScoreWidth(0.5)).toBe('50%');
      expect(getScoreWidth(1.0)).toBe('100%');
    });
  });
});
