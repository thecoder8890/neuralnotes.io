/**
 * Tests for App component
 *
 * Validates main application state management, step tracking,
 * document summary display, and component integration.
 */
import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { apiService } from './services/api';
import App from './App';

jest.mock('./services/api');
jest.mock('./components/DocumentUpload', () => {
  return function MockDocumentUpload({ onDocumentProcessed }: any) {
    return (
      <div data-testid="document-upload">
        <button onClick={() => onDocumentProcessed('doc_123')}>
          Mock Process Document
        </button>
      </div>
    );
  };
});

jest.mock('./components/ProjectGenerator', () => {
  return function MockProjectGenerator({ docId, onProjectGenerated }: any) {
    return (
      <div data-testid="project-generator">
        <span>Doc ID: {docId || 'none'}</span>
        <button
          onClick={() =>
            onProjectGenerated(
              'proj_123',
              [{ name: 'test.py', content: 'code', type: 'text' }],
              'instructions'
            )
          }
        >
          Mock Generate Project
        </button>
      </div>
    );
  };
});

jest.mock('./components/ProjectViewer', () => {
  return function MockProjectViewer({ projectId, files, instructions }: any) {
    return (
      <div data-testid="project-viewer">
        <span>Project: {projectId}</span>
        <span>Files: {files.length}</span>
        <span>Instructions: {instructions}</span>
      </div>
    );
  };
});

describe('App Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render main header', () => {
      render(<App />);

      expect(screen.getByText(/DocuGen AI/i)).toBeInTheDocument();
      expect(screen.getByText(/Documentation-aware project scaffolding/i)).toBeInTheDocument();
    });

    it('should render three-step workflow section', () => {
      render(<App />);

      expect(screen.getByText(/Pipeline Status/i)).toBeInTheDocument();
      expect(screen.getByText(/Three-step workflow/i)).toBeInTheDocument();
    });

    it('should render all three steps', () => {
      render(<App />);

      expect(screen.getByText(/Step 01/i)).toBeInTheDocument();
      expect(screen.getByText(/Ingest documentation/i)).toBeInTheDocument();

      expect(screen.getByText(/Step 02/i)).toBeInTheDocument();
      expect(screen.getByText(/Describe the project/i)).toBeInTheDocument();

      expect(screen.getByText(/Step 03/i)).toBeInTheDocument();
      expect(screen.getByText(/Review the output/i)).toBeInTheDocument();
    });

    it('should render all child components', () => {
      render(<App />);

      expect(screen.getByTestId('document-upload')).toBeInTheDocument();
      expect(screen.getByTestId('project-generator')).toBeInTheDocument();
    });

    it('should render example briefs section', () => {
      render(<App />);

      expect(screen.getByText('Spring Boot API')).toBeInTheDocument();
      expect(screen.getByText('React dashboard')).toBeInTheDocument();
      expect(screen.getByText('Flask service')).toBeInTheDocument();
    });
  });

  describe('Step States', () => {
    it('should show all steps as upcoming initially', () => {
      render(<App />);

      const steps = screen.getAllByText(/Queued/i);
      expect(steps.length).toBeGreaterThan(0);
    });

    it('should mark step 1 as done when document is processed', () => {
      (apiService.getDocumentSummary as jest.Mock).mockResolvedValue({
        data: {
          doc_id: 'doc_123',
          source_type: 'file',
          source_name: 'test.pdf',
          processed_at: '2024-01-01T00:00:00',
          status: 'ready',
          char_count: 1000,
          approx_chunks: 5,
          preview: 'Preview text'
        }
      });

      render(<App />);

      const processButton = screen.getByText('Mock Process Document');
      processButton.click();

      waitFor(() => {
        expect(screen.getByText(/Completed/i)).toBeInTheDocument();
      });
    });

    it('should mark step 2 as active when document is ready', () => {
      (apiService.getDocumentSummary as jest.Mock).mockResolvedValue({
        data: {
          doc_id: 'doc_123',
          source_type: 'file',
          source_name: 'test.pdf',
          processed_at: '2024-01-01T00:00:00',
          status: 'ready',
          char_count: 1000,
          approx_chunks: 5,
          preview: 'Preview'
        }
      });

      render(<App />);

      const processButton = screen.getByText('Mock Process Document');
      processButton.click();

      waitFor(() => {
        expect(screen.getByText(/In focus/i)).toBeInTheDocument();
      });
    });
  });

  describe('Document Summary', () => {
    it('should fetch and display document summary', async () => {
      const mockSummary = {
        doc_id: 'doc_123',
        source_type: 'file',
        source_name: 'documentation.pdf',
        processed_at: '2024-01-01T12:00:00',
        status: 'ready',
        char_count: 5000,
        approx_chunks: 7,
        preview: 'This is a preview of the documentation content.',
        file_size: 102400
      };

      (apiService.getDocumentSummary as jest.Mock).mockResolvedValue({
        data: mockSummary
      });

      render(<App />);

      const processButton = screen.getByText('Mock Process Document');
      processButton.click();

      await waitFor(() => {
        expect(apiService.getDocumentSummary).toHaveBeenCalledWith('doc_123');
      });

      await waitFor(() => {
        expect(screen.getByText('documentation.pdf')).toBeInTheDocument();
        expect(screen.getByText('5,000')).toBeInTheDocument(); // formatted char count
        expect(screen.getByText('7')).toBeInTheDocument(); // approx chunks
      });
    });

    it('should show loading state while fetching summary', async () => {
      (apiService.getDocumentSummary as jest.Mock).mockImplementation(
        () => new Promise(() => {})
      );

      render(<App />);

      const processButton = screen.getByText('Mock Process Document');
      processButton.click();

      await waitFor(() => {
        expect(screen.getByText(/Refreshing summary.../i)).toBeInTheDocument();
      });
    });

    it('should show error when summary fetch fails', async () => {
      (apiService.getDocumentSummary as jest.Mock).mockRejectedValue({
        response: { data: { detail: 'Document not found' } }
      });

      render(<App />);

      const processButton = screen.getByText('Mock Process Document');
      processButton.click();

      await waitFor(() => {
        expect(screen.getByText(/Document not found/i)).toBeInTheDocument();
      });
    });

    it('should display document preview', async () => {
      const mockSummary = {
        doc_id: 'doc_123',
        source_type: 'url',
        source_name: 'https://example.com',
        processed_at: '2024-01-01T00:00:00',
        status: 'ready',
        char_count: 2000,
        approx_chunks: 3,
        preview: 'This is a long preview text that shows what the document contains.',
        file_size: null
      };

      (apiService.getDocumentSummary as jest.Mock).mockResolvedValue({
        data: mockSummary
      });

      render(<App />);

      const processButton = screen.getByText('Mock Process Document');
      processButton.click();

      await waitFor(() => {
        expect(screen.getByText(/This is a long preview text/i)).toBeInTheDocument();
      });
    });
  });

  describe('Project Generation Flow', () => {
    it('should show project viewer after generation', async () => {
      (apiService.getDocumentSummary as jest.Mock).mockResolvedValue({
        data: {
          doc_id: 'doc_123',
          source_type: 'file',
          source_name: 'test.pdf',
          processed_at: '2024-01-01T00:00:00',
          status: 'ready',
          char_count: 1000,
          approx_chunks: 5,
          preview: 'Preview'
        }
      });

      render(<App />);

      // Process document
      const processButton = screen.getByText('Mock Process Document');
      processButton.click();

      await waitFor(() => {
        expect(screen.getByTestId('project-generator')).toBeInTheDocument();
      });

      // Generate project
      const generateButton = screen.getByText('Mock Generate Project');
      generateButton.click();

      await waitFor(() => {
        expect(screen.getByTestId('project-viewer')).toBeInTheDocument();
        expect(screen.getByText('Project: proj_123')).toBeInTheDocument();
      });
    });

    it('should pass doc ID to project generator', async () => {
      (apiService.getDocumentSummary as jest.Mock).mockResolvedValue({
        data: {
          doc_id: 'doc_123',
          source_type: 'file',
          source_name: 'test.pdf',
          processed_at: '2024-01-01T00:00:00',
          status: 'ready',
          char_count: 1000,
          approx_chunks: 5,
          preview: 'Preview'
        }
      });

      render(<App />);

      const processButton = screen.getByText('Mock Process Document');
      processButton.click();

      await waitFor(() => {
        expect(screen.getByText('Doc ID: doc_123')).toBeInTheDocument();
      });
    });
  });

  describe('State Management', () => {
    it('should reset project state when new document is processed', async () => {
      (apiService.getDocumentSummary as jest.Mock).mockResolvedValue({
        data: {
          doc_id: 'doc_123',
          source_type: 'file',
          source_name: 'test.pdf',
          processed_at: '2024-01-01T00:00:00',
          status: 'ready',
          char_count: 1000,
          approx_chunks: 5,
          preview: 'Preview'
        }
      });

      render(<App />);

      // Process first document and generate project
      const processButton = screen.getByText('Mock Process Document');
      processButton.click();

      await waitFor(() => {
        expect(screen.getByTestId('project-generator')).toBeInTheDocument();
      });

      const generateButton = screen.getByText('Mock Generate Project');
      generateButton.click();

      await waitFor(() => {
        expect(screen.getByTestId('project-viewer')).toBeInTheDocument();
      });

      // Process new document - should reset project state
      (apiService.getDocumentSummary as jest.Mock).mockResolvedValue({
        data: {
          doc_id: 'doc_456',
          source_type: 'url',
          source_name: 'https://new.com',
          processed_at: '2024-01-02T00:00:00',
          status: 'ready',
          char_count: 2000,
          approx_chunks: 8,
          preview: 'New preview'
        }
      });

      processButton.click();

      await waitFor(() => {
        expect(screen.queryByTestId('project-viewer')).not.toBeInTheDocument();
      });
    });
  });

  describe('Formatting Utilities', () => {
    it('should format large numbers with commas', async () => {
      const mockSummary = {
        doc_id: 'doc_123',
        source_type: 'file',
        source_name: 'large.pdf',
        processed_at: '2024-01-01T00:00:00',
        status: 'ready',
        char_count: 123456,
        approx_chunks: 150,
        preview: 'Preview',
        file_size: null
      };

      (apiService.getDocumentSummary as jest.Mock).mockResolvedValue({
        data: mockSummary
      });

      render(<App />);

      const processButton = screen.getByText('Mock Process Document');
      processButton.click();

      await waitFor(() => {
        expect(screen.getByText('123,456')).toBeInTheDocument();
        expect(screen.getByText('150')).toBeInTheDocument();
      });
    });
  });
});