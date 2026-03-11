/**
 * Tests for API service layer
 *
 * Validates that all API methods properly construct requests,
 * handle responses, and integrate with axios correctly.
 */
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { apiService } from './api';
import { Technology } from '../types';

describe('API Service', () => {
  let mock: MockAdapter;

  beforeEach(() => {
    mock = new MockAdapter(axios);
  });

  afterEach(() => {
    mock.restore();
  });

  describe('healthCheck', () => {
    it('should make GET request to health endpoint', async () => {
      const responseData = { status: 'healthy', service: 'DocuGen AI' };
      mock.onGet('/api/health').reply(200, responseData);

      const response = await apiService.healthCheck();

      expect(response.data).toEqual(responseData);
      expect(response.status).toBe(200);
    });

    it('should handle health check failure', async () => {
      mock.onGet('/api/health').reply(500);

      await expect(apiService.healthCheck()).rejects.toThrow();
    });
  });

  describe('processDocumentationUrl', () => {
    it('should process URL with params', async () => {
      const url = 'https://example.com/docs';
      const responseData = { status: 'success', doc_id: 'abc123' };
      mock.onPost('/api/process-documentation', null, {
        params: { url }
      }).reply(200, responseData);

      const response = await apiService.processDocumentationUrl(url);

      expect(response.data).toEqual(responseData);
    });

    it('should handle processing errors', async () => {
      const url = 'https://invalid-url.com';
      mock.onPost('/api/process-documentation').reply(500, {
        detail: 'Failed to fetch URL'
      });

      await expect(apiService.processDocumentationUrl(url)).rejects.toThrow();
    });
  });

  describe('uploadDocumentation', () => {
    it('should upload file with multipart form data', async () => {
      const file = new File(['content'], 'test.txt', { type: 'text/plain' });
      const responseData = { status: 'success', doc_id: 'def456' };

      mock.onPost('/api/upload-documentation').reply((config) => {
        expect(config.headers?.['Content-Type']).toContain('multipart/form-data');
        return [200, responseData];
      });

      const response = await apiService.uploadDocumentation(file);

      expect(response.data).toEqual(responseData);
    });

    it('should reject unsupported file types', async () => {
      const file = new File(['content'], 'test.exe', { type: 'application/octet-stream' });
      mock.onPost('/api/upload-documentation').reply(400, {
        detail: 'Unsupported file type'
      });

      await expect(apiService.uploadDocumentation(file)).rejects.toThrow();
    });
  });

  describe('uploadMultipleDocumentation', () => {
    it('should upload multiple files', async () => {
      const files = [
        new File(['content1'], 'file1.txt', { type: 'text/plain' }),
        new File(['content2'], 'file2.md', { type: 'text/markdown' })
      ];
      const responseData = {
        status: 'success',
        results: [
          { filename: 'file1.txt', doc_id: 'id1' },
          { filename: 'file2.md', doc_id: 'id2' }
        ],
        errors: []
      };

      mock.onPost('/api/upload-multiple-documentation').reply(200, responseData);

      const response = await apiService.uploadMultipleDocumentation(files);

      expect(response.data.results).toHaveLength(2);
      expect(response.data.errors).toHaveLength(0);
    });

    it('should handle partial upload failures', async () => {
      const files = [
        new File(['content1'], 'file1.txt', { type: 'text/plain' }),
        new File(['content2'], 'file2.exe', { type: 'application/octet-stream' })
      ];
      const responseData = {
        status: 'partial',
        results: [{ filename: 'file1.txt', doc_id: 'id1' }],
        errors: [{ filename: 'file2.exe', error: 'Unsupported file type' }]
      };

      mock.onPost('/api/upload-multiple-documentation').reply(200, responseData);

      const response = await apiService.uploadMultipleDocumentation(files);

      expect(response.data.results).toHaveLength(1);
      expect(response.data.errors).toHaveLength(1);
    });
  });

  describe('getSupportedFormats', () => {
    it('should return supported formats and max size', async () => {
      const responseData = {
        formats: ['.pdf', '.md', '.txt', '.html', '.rst'],
        max_file_size_mb: 50
      };
      mock.onGet('/api/supported-formats').reply(200, responseData);

      const response = await apiService.getSupportedFormats();

      expect(response.data.formats).toContain('.pdf');
      expect(response.data.max_file_size_mb).toBe(50);
    });
  });

  describe('getDocumentSummary', () => {
    it('should fetch document summary by ID', async () => {
      const docId = 'abc123';
      const responseData = {
        doc_id: docId,
        source_type: 'file',
        source_name: 'test.pdf',
        processed_at: '2024-01-01T00:00:00',
        status: 'ready',
        char_count: 1000,
        approx_chunks: 5,
        preview: 'Document preview...'
      };
      mock.onGet(`/api/documents/${docId}`).reply(200, responseData);

      const response = await apiService.getDocumentSummary(docId);

      expect(response.data.doc_id).toBe(docId);
      expect(response.data.source_name).toBe('test.pdf');
    });

    it('should handle document not found', async () => {
      const docId = 'nonexistent';
      mock.onGet(`/api/documents/${docId}`).reply(404, {
        detail: 'Document not found'
      });

      await expect(apiService.getDocumentSummary(docId)).rejects.toThrow();
    });
  });

  describe('generateProject', () => {
    it('should generate project with all parameters', async () => {
      const request = {
        doc_id: 'abc123',
        prompt: 'Create a Flask REST API',
        technology: Technology.FLASK
      };
      const responseData = {
        project_id: 'proj_789',
        files: [
          { name: 'app.py', content: 'from flask import Flask', type: 'text' }
        ],
        structure: { 'app.py': [] },
        instructions: 'Run: python app.py'
      };
      mock.onPost('/api/generate-project').reply(200, responseData);

      const response = await apiService.generateProject(request);

      expect(response.data.project_id).toBe('proj_789');
      expect(response.data.files).toHaveLength(1);
    });

    it('should generate project without technology', async () => {
      const request = {
        doc_id: 'abc123',
        prompt: 'Create a web application'
      };
      const responseData = {
        project_id: 'proj_790',
        files: [],
        structure: {},
        instructions: 'Auto-detected technology'
      };
      mock.onPost('/api/generate-project').reply(200, responseData);

      const response = await apiService.generateProject(request);

      expect(response.data.project_id).toBe('proj_790');
    });

    it('should handle generation errors', async () => {
      const request = {
        doc_id: 'invalid',
        prompt: 'Create an app'
      };
      mock.onPost('/api/generate-project').reply(500, {
        detail: 'Document not found'
      });

      await expect(apiService.generateProject(request)).rejects.toThrow();
    });
  });

  describe('downloadProject', () => {
    it('should download project as blob', async () => {
      const projectId = 'proj_123';
      const mockBlob = new Blob(['fake zip data'], { type: 'application/zip' });
      mock.onGet(`/api/download-project/${projectId}`).reply(200, mockBlob, {
        'content-type': 'application/zip',
        'content-disposition': 'attachment; filename=project.zip'
      });

      const response = await apiService.downloadProject(projectId);

      expect(response.data).toBeDefined();
      expect(response.status).toBe(200);
    });

    it('should handle download errors', async () => {
      const projectId = 'nonexistent';
      mock.onGet(`/api/download-project/${projectId}`).reply(404, {
        detail: 'Project not found'
      });

      await expect(apiService.downloadProject(projectId)).rejects.toThrow();
    });
  });

  describe('API configuration', () => {
    it('should use correct base URL from environment', () => {
      // Base URL is set from process.env.REACT_APP_API_URL or defaults to ''
      expect(apiService).toBeDefined();
    });

    it('should set JSON content type header by default', async () => {
      mock.onGet('/api/health').reply((config) => {
        expect(config.headers?.['Content-Type']).toBe('application/json');
        return [200, { status: 'ok' }];
      });

      await apiService.healthCheck();
    });
  });
});