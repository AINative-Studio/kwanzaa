import { describe, it, expect } from 'vitest';
import { ExportService } from '../exportService';
import type { SearchResult } from '@types/search';

const mockResult: SearchResult = {
  rank: 1,
  score: 0.95,
  chunk_id: 'test::chunk::1',
  doc_id: 'test_doc',
  namespace: 'kwanzaa_primary_sources',
  content: 'This is test content for the search result.',
  metadata: {
    citation_label: 'Test Document (2024)',
    canonical_url: 'https://example.com/test',
    source_org: 'Test Organization',
    year: 2024,
    content_type: 'article',
    license: 'Public Domain',
    tags: ['test', 'example'],
  },
};

describe('ExportService', () => {
  describe('toBibTeX', () => {
    it('formats result as BibTeX', () => {
      const bibtex = ExportService.toBibTeX(mockResult);

      expect(bibtex).toContain('@misc{test_chunk_1');
      expect(bibtex).toContain('title = {Test Document (2024)}');
      expect(bibtex).toContain('author = {Test Organization}');
      expect(bibtex).toContain('year = {2024}');
      expect(bibtex).toContain('url = {https://example.com/test}');
      expect(bibtex).toContain('license = {Public Domain}');
    });
  });

  describe('toAPA', () => {
    it('formats result as APA citation', () => {
      const apa = ExportService.toAPA(mockResult);

      expect(apa).toContain('Test Organization');
      expect(apa).toContain('(2024)');
      expect(apa).toContain('Test Document (2024)');
      expect(apa).toContain('https://example.com/test');
    });
  });

  describe('toMLA', () => {
    it('formats result as MLA citation', () => {
      const mla = ExportService.toMLA(mockResult);

      expect(mla).toContain('Test Organization');
      expect(mla).toContain('"Test Document (2024)."');
      expect(mla).toContain('2024');
      expect(mla).toContain('<https://example.com/test>');
    });
  });

  describe('exportAsJSON', () => {
    it('exports results as JSON string', () => {
      const results = [mockResult];
      const json = ExportService.exportAsJSON(results);

      expect(json).toBeTruthy();
      const parsed = JSON.parse(json);
      expect(parsed).toHaveLength(1);
      expect(parsed[0].chunk_id).toBe('test::chunk::1');
    });
  });

  describe('exportAsCSV', () => {
    it('exports results as CSV string', () => {
      const results = [mockResult];
      const csv = ExportService.exportAsCSV(results);

      expect(csv).toContain('rank,score,chunk_id');
      expect(csv).toContain('1,0.95,test::chunk::1');
      expect(csv).toContain('Test Organization');
      expect(csv).toContain('2024');
    });

    it('escapes quotes in content', () => {
      const resultWithQuotes = {
        ...mockResult,
        content: 'Content with "quotes" inside',
      };

      const csv = ExportService.exportAsCSV([resultWithQuotes]);
      expect(csv).toContain('""quotes""');
    });
  });

  describe('exportAsBibTeX', () => {
    it('exports multiple results', () => {
      const results = [mockResult, { ...mockResult, rank: 2, chunk_id: 'test::chunk::2' }];
      const bibtex = ExportService.exportAsBibTeX(results);

      expect(bibtex).toContain('@misc{test_chunk_1');
      expect(bibtex).toContain('@misc{test_chunk_2');
    });
  });
});
