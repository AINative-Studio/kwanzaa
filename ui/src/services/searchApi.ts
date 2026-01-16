/**
 * Search API service
 * Handles communication with Kwanzaa backend search endpoints
 */

import axios, { AxiosInstance } from 'axios';
import type { SearchRequest, SearchResponse, Namespace } from '@types/search';

class SearchApiService {
  private client: AxiosInstance;

  constructor(baseURL: string = '/api/v1') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    // Add response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        const message = error.response?.data?.detail || error.message;
        throw new Error(message);
      }
    );
  }

  /**
   * Perform semantic search
   */
  async search(request: SearchRequest): Promise<SearchResponse> {
    const response = await this.client.post<SearchResponse>(
      '/search/semantic',
      request
    );
    return response.data;
  }

  /**
   * Generate text embedding
   */
  async generateEmbedding(text: string): Promise<{
    status: string;
    text: string;
    embedding: number[];
    dimensions: number;
    model: string;
    generation_time_ms: number;
  }> {
    const response = await this.client.post('/search/embed', { text });
    return response.data;
  }

  /**
   * List available namespaces
   */
  async listNamespaces(): Promise<{
    status: string;
    namespaces: Namespace[];
  }> {
    const response = await this.client.get('/search/namespaces');
    return response.data;
  }
}

export const searchApi = new SearchApiService();
