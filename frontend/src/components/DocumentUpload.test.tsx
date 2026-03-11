/**
 * Tests for DocumentUpload component
 *
 * Validates file upload, URL processing, drag-and-drop,
 * and proper state management.
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { apiService } from '../services/api';
import DocumentUpload from './DocumentUpload';

jest.mock('../services/api');

describe('DocumentUpload Component', () => {
  const mockOnDocumentProcessed = jest.fn();
  const mockOnProcessingStateChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (apiService.getSupportedFormats as jest.Mock).mockResolvedValue({
      data: {
        formats: ['.pdf', '.md', '.txt', '.html', '.rst'],
        max_file_size_mb: 50
      }
    });
  });

  describe('Rendering', () => {
    it('should render component with URL input by default', () => {
      render(
        <DocumentUpload
          onDocumentProcessed={mockOnDocumentProcessed}
          isProcessing={false}
        />
      );

      expect(screen.getByLabelText(/Documentation URL/i)).toBeInTheDocument();
      expect(screen.getByText(/Process documentation URL/i)).toBeInTheDocument();
    });

    it('should render supported formats', async () => {
      render(
        <DocumentUpload
          onDocumentProcessed={mockOnDocumentProcessed}
          isProcessing={false}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('PDF')).toBeInTheDocument();
        expect(screen.getByText('MD')).toBeInTheDocument();
        expect(screen.getByText('TXT')).toBeInTheDocument();
      });
    });

    it('should show step 01 heading', () => {
      render(
        <DocumentUpload
          onDocumentProcessed={mockOnDocumentProcessed}
          isProcessing={false}
        />
      );

      expect(screen.getByText(/Step 01/i)).toBeInTheDocument();
      expect(screen.getByText(/Ingest documentation/i)).toBeInTheDocument();
    });
  });

  describe('Upload Method Toggle', () => {
    it('should switch to file upload mode', async () => {
      render(
        <DocumentUpload
          onDocumentProcessed={mockOnDocumentProcessed}
          isProcessing={false}
        />
      );

      const fileButton = screen.getByRole('button', { name: /Files/i });
      fireEvent.click(fileButton);

      expect(screen.getByText(/Drag files here/i)).toBeInTheDocument();
    });

    it('should switch back to URL mode', async () => {
      render(
        <DocumentUpload
          onDocumentProcessed={mockOnDocumentProcessed}
          isProcessing={false}
        />
      );

      const fileButton = screen.getByRole('button', { name: /Files/i });
      fireEvent.click(fileButton);

      const urlButton = screen.getByRole('button', { name: /URL/i });
      fireEvent.click(urlButton);

      expect(screen.getByLabelText(/Documentation URL/i)).toBeInTheDocument();
    });
  });

  describe('URL Processing', () => {
    it('should process URL successfully', async () => {
      (apiService.processDocumentationUrl as jest.Mock).mockResolvedValue({
        data: { doc_id: 'abc123' }
      });

      render(
        <DocumentUpload
          onDocumentProcessed={mockOnDocumentProcessed}
          isProcessing={false}
          onProcessingStateChange={mockOnProcessingStateChange}
        />
      );

      const input = screen.getByLabelText(/Documentation URL/i);
      const button = screen.getByRole('button', { name: /Process documentation URL/i });

      await userEvent.type(input, 'https://example.com/docs');
      fireEvent.click(button);

      await waitFor(() => {
        expect(mockOnProcessingStateChange).toHaveBeenCalledWith(true);
        expect(apiService.processDocumentationUrl).toHaveBeenCalledWith('https://example.com/docs');
      });

      await waitFor(() => {
        expect(mockOnDocumentProcessed).toHaveBeenCalledWith('abc123');
        expect(mockOnProcessingStateChange).toHaveBeenCalledWith(false);
      });
    });

    it('should show error on URL processing failure', async () => {
      (apiService.processDocumentationUrl as jest.Mock).mockRejectedValue({
        response: { data: { detail: 'Failed to fetch URL' } }
      });

      render(
        <DocumentUpload
          onDocumentProcessed={mockOnDocumentProcessed}
          isProcessing={false}
        />
      );

      const input = screen.getByLabelText(/Documentation URL/i);
      const button = screen.getByRole('button', { name: /Process documentation URL/i });

      await userEvent.type(input, 'https://invalid.com');
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByText(/Failed to fetch URL/i)).toBeInTheDocument();
      });
    });

    it('should disable submit when URL is empty', () => {
      render(
        <DocumentUpload
          onDocumentProcessed={mockOnDocumentProcessed}
          isProcessing={false}
        />
      );

      const button = screen.getByRole('button', { name: /Process documentation URL/i });
      expect(button).toBeDisabled();
    });

    it('should disable controls when processing', () => {
      render(
        <DocumentUpload
          onDocumentProcessed={mockOnDocumentProcessed}
          isProcessing={true}
        />
      );

      const input = screen.getByLabelText(/Documentation URL/i);
      const button = screen.getByRole('button', { name: /Processing documentation.../i });

      expect(input).toBeDisabled();
      expect(button).toBeDisabled();
    });
  });

  describe('File Upload', () => {
    it('should handle single file selection', async () => {
      render(
        <DocumentUpload
          onDocumentProcessed={mockOnDocumentProcessed}
          isProcessing={false}
        />
      );

      fireEvent.click(screen.getByRole('button', { name: /Files/i }));

      const file = new File(['content'], 'test.pdf', { type: 'application/pdf' });
      const input = screen.getByLabelText(/Select files/i);

      await userEvent.upload(input, file);

      await waitFor(() => {
        expect(screen.getByText('test.pdf')).toBeInTheDocument();
        expect(screen.getByText(/1 file ready/i)).toBeInTheDocument();
      });
    });

    it('should handle multiple file selection', async () => {
      render(
        <DocumentUpload
          onDocumentProcessed={mockOnDocumentProcessed}
          isProcessing={false}
        />
      );

      fireEvent.click(screen.getByRole('button', { name: /Files/i }));

      const files = [
        new File(['content1'], 'file1.pdf', { type: 'application/pdf' }),
        new File(['content2'], 'file2.md', { type: 'text/markdown' })
      ];
      const input = screen.getByLabelText(/Select files/i);

      await userEvent.upload(input, files);

      await waitFor(() => {
        expect(screen.getByText('file1.pdf')).toBeInTheDocument();
        expect(screen.getByText('file2.md')).toBeInTheDocument();
        expect(screen.getByText(/2 files ready/i)).toBeInTheDocument();
      });
    });

    it('should remove selected file', async () => {
      render(
        <DocumentUpload
          onDocumentProcessed={mockOnDocumentProcessed}
          isProcessing={false}
        />
      );

      fireEvent.click(screen.getByRole('button', { name: /Files/i }));

      const file = new File(['content'], 'test.pdf', { type: 'application/pdf' });
      const input = screen.getByLabelText(/Select files/i);

      await userEvent.upload(input, file);

      const removeButton = await screen.findByLabelText(/Remove test.pdf/i);
      fireEvent.click(removeButton);

      await waitFor(() => {
        expect(screen.queryByText('test.pdf')).not.toBeInTheDocument();
      });
    });

    it('should upload single file successfully', async () => {
      (apiService.uploadDocumentation as jest.Mock).mockResolvedValue({
        data: { doc_id: 'def456' }
      });

      render(
        <DocumentUpload
          onDocumentProcessed={mockOnDocumentProcessed}
          isProcessing={false}
          onProcessingStateChange={mockOnProcessingStateChange}
        />
      );

      fireEvent.click(screen.getByRole('button', { name: /Files/i }));

      const file = new File(['content'], 'test.pdf', { type: 'application/pdf' });
      const input = screen.getByLabelText(/Select files/i);

      await userEvent.upload(input, file);

      const uploadButton = await screen.findByRole('button', { name: /Upload and process/i });
      fireEvent.click(uploadButton);

      await waitFor(() => {
        expect(mockOnDocumentProcessed).toHaveBeenCalledWith('def456');
      });
    });

    it('should upload multiple files successfully', async () => {
      (apiService.uploadMultipleDocumentation as jest.Mock).mockResolvedValue({
        data: {
          results: [
            { filename: 'file1.pdf', doc_id: 'id1' },
            { filename: 'file2.md', doc_id: 'id2' }
          ],
          errors: []
        }
      });

      render(
        <DocumentUpload
          onDocumentProcessed={mockOnDocumentProcessed}
          isProcessing={false}
        />
      );

      fireEvent.click(screen.getByRole('button', { name: /Files/i }));

      const files = [
        new File(['content1'], 'file1.pdf', { type: 'application/pdf' }),
        new File(['content2'], 'file2.md', { type: 'text/markdown' })
      ];
      const input = screen.getByLabelText(/Select files/i);

      await userEvent.upload(input, files);

      const uploadButton = await screen.findByRole('button', { name: /Upload and process/i });
      fireEvent.click(uploadButton);

      await waitFor(() => {
        expect(mockOnDocumentProcessed).toHaveBeenCalledWith('id1');
      });
    });
  });

  describe('Drag and Drop', () => {
    it('should handle file drop', async () => {
      render(
        <DocumentUpload
          onDocumentProcessed={mockOnDocumentProcessed}
          isProcessing={false}
        />
      );

      fireEvent.click(screen.getByRole('button', { name: /Files/i }));

      const dropZone = screen.getByText(/Drag files here/i).closest('div');
      const file = new File(['content'], 'dropped.pdf', { type: 'application/pdf' });

      fireEvent.drop(dropZone!, {
        dataTransfer: {
          files: [file]
        }
      });

      await waitFor(() => {
        expect(screen.getByText('dropped.pdf')).toBeInTheDocument();
      });
    });

    it('should show drag active state', () => {
      render(
        <DocumentUpload
          onDocumentProcessed={mockOnDocumentProcessed}
          isProcessing={false}
        />
      );

      fireEvent.click(screen.getByRole('button', { name: /Files/i }));

      const dropZone = screen.getByText(/Drag files here/i).closest('div');

      fireEvent.dragEnter(dropZone!);

      // The border color should change when drag is active
      expect(dropZone).toHaveClass('border-amber-500');
    });
  });

  describe('Status Messages', () => {
    it('should show processing status', async () => {
      (apiService.processDocumentationUrl as jest.Mock).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      render(
        <DocumentUpload
          onDocumentProcessed={mockOnDocumentProcessed}
          isProcessing={false}
        />
      );

      const input = screen.getByLabelText(/Documentation URL/i);
      await userEvent.type(input, 'https://example.com');

      const button = screen.getByRole('button', { name: /Process documentation URL/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByText(/Fetching and indexing documentation/i)).toBeInTheDocument();
      });
    });

    it('should show success message', async () => {
      (apiService.processDocumentationUrl as jest.Mock).mockResolvedValue({
        data: { doc_id: 'abc123' }
      });

      render(
        <DocumentUpload
          onDocumentProcessed={mockOnDocumentProcessed}
          isProcessing={false}
        />
      );

      const input = screen.getByLabelText(/Documentation URL/i);
      await userEvent.type(input, 'https://example.com');

      const button = screen.getByRole('button', { name: /Process documentation URL/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByText(/Documentation processed successfully/i)).toBeInTheDocument();
      });
    });
  });

  describe('File Size Display', () => {
    it('should display file sizes correctly', async () => {
      render(
        <DocumentUpload
          onDocumentProcessed={mockOnDocumentProcessed}
          isProcessing={false}
        />
      );

      fireEvent.click(screen.getByRole('button', { name: /Files/i }));

      const file = new File(['a'.repeat(1024)], 'test.txt', { type: 'text/plain' });
      Object.defineProperty(file, 'size', { value: 1024 });

      const input = screen.getByLabelText(/Select files/i);
      await userEvent.upload(input, file);

      await waitFor(() => {
        expect(screen.getByText(/1\.0 KB/i)).toBeInTheDocument();
      });
    });
  });
});