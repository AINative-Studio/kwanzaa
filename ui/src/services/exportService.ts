/**
 * Export service for search results
 * Supports BibTeX, APA, MLA, JSON, and CSV formats
 */

import type { SearchResult } from '@types/search';

export class ExportService {
  /**
   * Export single result as BibTeX
   */
  static toBibTeX(result: SearchResult): string {
    const { metadata } = result;
    const id = result.chunk_id.replace(/::/g, '_');

    return `@misc{${id},
  title = {${metadata.citation_label}},
  author = {${metadata.source_org}},
  year = {${metadata.year}},
  url = {${metadata.canonical_url}},
  note = {${metadata.content_type}},
  license = {${metadata.license}}
}`;
  }

  /**
   * Export single result as APA citation
   */
  static toAPA(result: SearchResult): string {
    const { metadata } = result;
    return `${metadata.source_org} (${metadata.year}). ${metadata.citation_label}. Retrieved from ${metadata.canonical_url}`;
  }

  /**
   * Export single result as MLA citation
   */
  static toMLA(result: SearchResult): string {
    const { metadata } = result;
    return `${metadata.source_org}. "${metadata.citation_label}." ${metadata.year}. Web. <${metadata.canonical_url}>.`;
  }

  /**
   * Export multiple results as BibTeX
   */
  static exportAsBibTeX(results: SearchResult[]): string {
    return results.map(r => this.toBibTeX(r)).join('\n\n');
  }

  /**
   * Export multiple results as APA
   */
  static exportAsAPA(results: SearchResult[]): string {
    return results.map(r => this.toAPA(r)).join('\n\n');
  }

  /**
   * Export multiple results as MLA
   */
  static exportAsMLA(results: SearchResult[]): string {
    return results.map(r => this.toMLA(r)).join('\n\n');
  }

  /**
   * Export results as JSON
   */
  static exportAsJSON(results: SearchResult[]): string {
    return JSON.stringify(results, null, 2);
  }

  /**
   * Export results as CSV
   */
  static exportAsCSV(results: SearchResult[]): string {
    const headers = [
      'rank',
      'score',
      'chunk_id',
      'doc_id',
      'namespace',
      'content',
      'citation_label',
      'canonical_url',
      'source_org',
      'year',
      'content_type',
      'license',
      'tags'
    ];

    const rows = results.map(r => [
      r.rank,
      r.score,
      r.chunk_id,
      r.doc_id,
      r.namespace,
      `"${r.content.replace(/"/g, '""')}"`,
      r.metadata.citation_label,
      r.metadata.canonical_url,
      r.metadata.source_org,
      r.metadata.year,
      r.metadata.content_type,
      r.metadata.license,
      r.metadata.tags.join(';')
    ]);

    return [
      headers.join(','),
      ...rows.map(row => row.join(','))
    ].join('\n');
  }

  /**
   * Download content as file
   */
  static downloadFile(content: string, filename: string, mimeType: string): void {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  /**
   * Copy text to clipboard
   */
  static async copyToClipboard(text: string): Promise<void> {
    await navigator.clipboard.writeText(text);
  }
}
