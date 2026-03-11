import axios from 'axios';
import {
  DocumentSummary,
  GenerationRequest,
  GenerationResponse,
  SupportedFormatsResponse,
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || '';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const apiService = {
  // Health check
  healthCheck: () => api.get('/api/health'),

  // Document processing
  processDocumentationUrl: (url: string) =>
    api.post('/api/process-documentation', null, { params: { url } }),

  uploadDocumentation: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/api/upload-documentation', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  uploadMultipleDocumentation: (files: File[]) => {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file);
    });
    return api.post('/api/upload-multiple-documentation', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },

  getSupportedFormats: (): Promise<{ data: SupportedFormatsResponse }> =>
    api.get('/api/supported-formats'),

  getDocumentSummary: (docId: string): Promise<{ data: DocumentSummary }> =>
    api.get(`/api/documents/${docId}`),

  // Project generation
  generateProject: (request: GenerationRequest): Promise<{ data: GenerationResponse }> =>
    api.post('/api/generate-project', request),

  // Project download
  downloadProject: (projectId: string) =>
    api.get(`/api/download-project/${projectId}`, {
      responseType: 'blob',
    }),
};
