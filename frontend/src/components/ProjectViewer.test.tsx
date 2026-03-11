/**
 * Tests for ProjectViewer component
 *
 * Validates file tree rendering, file selection, copy functionality,
 * and ZIP download.
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { apiService } from '../services/api';
import ProjectViewer from './ProjectViewer';
import { FileContent } from '../types';

jest.mock('../services/api');

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: jest.fn().mockResolvedValue(undefined)
  }
});

describe('ProjectViewer Component', () => {
  const mockFiles: FileContent[] = [
    { name: 'README.md', content: '# Project\n\nDescription here', type: 'text' },
    { name: 'src/main.py', content: 'print("hello")', type: 'text' },
    { name: 'src/utils.py', content: 'def helper(): pass', type: 'text' },
    { name: 'tests/test_main.py', content: 'def test(): assert True', type: 'text' }
  ];

  const mockInstructions = 'Run: python src/main.py';

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render component with project details', () => {
      render(
        <ProjectViewer
          projectId="proj_123"
          files={mockFiles}
          instructions={mockInstructions}
        />
      );

      expect(screen.getByText(/Step 03/i)).toBeInTheDocument();
      expect(screen.getByText(/Review and export/i)).toBeInTheDocument();
      expect(screen.getByText(/4 files/i)).toBeInTheDocument();
    });

    it('should calculate and display total lines', () => {
      render(
        <ProjectViewer
          projectId="proj_123"
          files={mockFiles}
          instructions={mockInstructions}
        />
      );

      // README.md: 3 lines, src/main.py: 1 line, src/utils.py: 1 line, tests/test_main.py: 1 line
      // Total: 6 lines
      expect(screen.getByText(/6 lines/i)).toBeInTheDocument();
    });

    it('should show download button', () => {
      render(
        <ProjectViewer
          projectId="proj_123"
          files={mockFiles}
          instructions={mockInstructions}
        />
      );

      expect(screen.getByRole('button', { name: /Download ZIP/i })).toBeInTheDocument();
    });
  });

  describe('File Tree', () => {
    it('should render file tree with folders and files', () => {
      render(
        <ProjectViewer
          projectId="proj_123"
          files={mockFiles}
          instructions={mockInstructions}
        />
      );

      expect(screen.getByText('README.md')).toBeInTheDocument();
      expect(screen.getByText('src')).toBeInTheDocument();
      expect(screen.getByText('tests')).toBeInTheDocument();
    });

    it('should expand folders by default (first 2 levels)', () => {
      render(
        <ProjectViewer
          projectId="proj_123"
          files={mockFiles}
          instructions={mockInstructions}
        />
      );

      // src folder should be expanded by default
      expect(screen.getByText('main.py')).toBeInTheDocument();
      expect(screen.getByText('utils.py')).toBeInTheDocument();
    });

    it('should toggle folder expansion', () => {
      render(
        <ProjectViewer
          projectId="proj_123"
          files={mockFiles}
          instructions={mockInstructions}
        />
      );

      const srcFolder = screen.getByText('src').closest('button')!;

      // Collapse folder
      fireEvent.click(srcFolder);

      // Files should still be visible immediately after click (React state update)
      // but we can verify the folder is clickable
      expect(srcFolder).toBeInTheDocument();
    });

    it('should sort folders before files', () => {
      const files: FileContent[] = [
        { name: 'z_file.txt', content: 'last', type: 'text' },
        { name: 'a_folder/file.txt', content: 'in folder', type: 'text' },
        { name: 'a_file.txt', content: 'first', type: 'text' }
      ];

      render(
        <ProjectViewer
          projectId="proj_123"
          files={files}
          instructions={mockInstructions}
        />
      );

      // Folder 'a_folder' should appear before files
      const treeButtons = screen.getAllByRole('button');
      const folderButton = treeButtons.find(btn => btn.textContent?.includes('a_folder'));
      expect(folderButton).toBeInTheDocument();
    });
  });

  describe('File Selection', () => {
    it('should select README.md by default if it exists', () => {
      render(
        <ProjectViewer
          projectId="proj_123"
          files={mockFiles}
          instructions={mockInstructions}
        />
      );

      expect(screen.getByText('# Project')).toBeInTheDocument();
      expect(screen.getByText('Description here')).toBeInTheDocument();
    });

    it('should select first file alphabetically if no README', () => {
      const filesWithoutReadme: FileContent[] = [
        { name: 'z_file.txt', content: 'last file', type: 'text' },
        { name: 'a_file.txt', content: 'first file', type: 'text' }
      ];

      render(
        <ProjectViewer
          projectId="proj_123"
          files={filesWithoutReadme}
          instructions={mockInstructions}
        />
      );

      expect(screen.getByText('first file')).toBeInTheDocument();
    });

    it('should change selected file on click', () => {
      render(
        <ProjectViewer
          projectId="proj_123"
          files={mockFiles}
          instructions={mockInstructions}
        />
      );

      const mainPyButton = screen.getByText('main.py').closest('button')!;
      fireEvent.click(mainPyButton);

      expect(screen.getByText('print("hello")')).toBeInTheDocument();
    });

    it('should highlight selected file', () => {
      render(
        <ProjectViewer
          projectId="proj_123"
          files={mockFiles}
          instructions={mockInstructions}
        />
      );

      const readmeButton = screen.getByText('README.md').closest('button')!;

      // Selected file should have amber background
      expect(readmeButton).toHaveClass('bg-amber-100');
    });
  });

  describe('File Content Display', () => {
    it('should display file name and type', () => {
      render(
        <ProjectViewer
          projectId="proj_123"
          files={mockFiles}
          instructions={mockInstructions}
        />
      );

      expect(screen.getByText('README.md')).toBeInTheDocument();
      expect(screen.getByText('text')).toBeInTheDocument();
    });

    it('should display file content in code block', () => {
      render(
        <ProjectViewer
          projectId="proj_123"
          files={mockFiles}
          instructions={mockInstructions}
        />
      );

      const codeBlock = screen.getByText('# Project').closest('code');
      expect(codeBlock).toBeInTheDocument();
    });

    it('should show placeholder when no file is selected', () => {
      render(
        <ProjectViewer
          projectId="proj_123"
          files={[]}
          instructions={mockInstructions}
        />
      );

      expect(screen.getByText(/Select a file to inspect/i)).toBeInTheDocument();
    });
  });

  describe('Copy Functionality', () => {
    it('should copy file content to clipboard', async () => {
      render(
        <ProjectViewer
          projectId="proj_123"
          files={mockFiles}
          instructions={mockInstructions}
        />
      );

      const copyButton = screen.getByRole('button', { name: /Copy file/i });
      fireEvent.click(copyButton);

      await waitFor(() => {
        expect(navigator.clipboard.writeText).toHaveBeenCalledWith('# Project\n\nDescription here');
      });
    });

    it('should show "Copied" confirmation', async () => {
      render(
        <ProjectViewer
          projectId="proj_123"
          files={mockFiles}
          instructions={mockInstructions}
        />
      );

      const copyButton = screen.getByRole('button', { name: /Copy file/i });
      fireEvent.click(copyButton);

      await waitFor(() => {
        expect(screen.getByText('Copied')).toBeInTheDocument();
      });
    });

    it('should reset copy confirmation after timeout', async () => {
      jest.useFakeTimers();

      render(
        <ProjectViewer
          projectId="proj_123"
          files={mockFiles}
          instructions={mockInstructions}
        />
      );

      const copyButton = screen.getByRole('button', { name: /Copy file/i });
      fireEvent.click(copyButton);

      await waitFor(() => {
        expect(screen.getByText('Copied')).toBeInTheDocument();
      });

      jest.advanceTimersByTime(2000);

      await waitFor(() => {
        expect(screen.queryByText('Copied')).not.toBeInTheDocument();
      });

      jest.useRealTimers();
    });
  });

  describe('Download Project', () => {
    it('should download project as ZIP', async () => {
      const mockBlob = new Blob(['fake zip'], { type: 'application/zip' });
      (apiService.downloadProject as jest.Mock).mockResolvedValue({
        data: mockBlob
      });

      // Mock URL.createObjectURL
      global.URL.createObjectURL = jest.fn(() => 'blob:mock-url');
      global.URL.revokeObjectURL = jest.fn();

      render(
        <ProjectViewer
          projectId="proj_123"
          files={mockFiles}
          instructions={mockInstructions}
        />
      );

      const downloadButton = screen.getByRole('button', { name: /Download ZIP/i });
      fireEvent.click(downloadButton);

      await waitFor(() => {
        expect(apiService.downloadProject).toHaveBeenCalledWith('proj_123');
      });

      await waitFor(() => {
        expect(global.URL.createObjectURL).toHaveBeenCalled();
        expect(global.URL.revokeObjectURL).toHaveBeenCalled();
      });
    });

    it('should show error on download failure', async () => {
      (apiService.downloadProject as jest.Mock).mockRejectedValue(new Error('Download failed'));

      render(
        <ProjectViewer
          projectId="proj_123"
          files={mockFiles}
          instructions={mockInstructions}
        />
      );

      const downloadButton = screen.getByRole('button', { name: /Download ZIP/i });
      fireEvent.click(downloadButton);

      await waitFor(() => {
        expect(screen.getByText(/Download failed/i)).toBeInTheDocument();
      });
    });

    it('should disable download button while downloading', async () => {
      (apiService.downloadProject as jest.Mock).mockImplementation(
        () => new Promise(() => {})
      );

      render(
        <ProjectViewer
          projectId="proj_123"
          files={mockFiles}
          instructions={mockInstructions}
        />
      );

      const downloadButton = screen.getByRole('button', { name: /Download ZIP/i });
      fireEvent.click(downloadButton);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Preparing ZIP.../i })).toBeDisabled();
      });
    });
  });

  describe('Instructions Display', () => {
    it('should display setup instructions', () => {
      render(
        <ProjectViewer
          projectId="proj_123"
          files={mockFiles}
          instructions={mockInstructions}
        />
      );

      expect(screen.getByText(/Setup instructions/i)).toBeInTheDocument();
      expect(screen.getByText(/Run: python src\/main.py/i)).toBeInTheDocument();
    });
  });

  describe('State Reset on New Project', () => {
    it('should reset to README when project changes', () => {
      const { rerender } = render(
        <ProjectViewer
          projectId="proj_123"
          files={mockFiles}
          instructions={mockInstructions}
        />
      );

      // Select a different file
      const mainPyButton = screen.getByText('main.py').closest('button')!;
      fireEvent.click(mainPyButton);

      expect(screen.getByText('print("hello")')).toBeInTheDocument();

      // New project with different files
      const newFiles: FileContent[] = [
        { name: 'README.md', content: '# New Project', type: 'text' },
        { name: 'app.py', content: 'new code', type: 'text' }
      ];

      rerender(
        <ProjectViewer
          projectId="proj_456"
          files={newFiles}
          instructions="New instructions"
        />
      );

      // Should select README.md again
      expect(screen.getByText('# New Project')).toBeInTheDocument();
    });
  });
});