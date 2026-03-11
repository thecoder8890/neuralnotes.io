/**
 * Tests for ProjectGenerator component
 *
 * Validates project generation form, technology selection,
 * prompt handling, and example prompt functionality.
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { apiService } from '../services/api';
import ProjectGenerator from './ProjectGenerator';
import { Technology } from '../types';

jest.mock('../services/api');

describe('ProjectGenerator Component', () => {
  const mockOnProjectGenerated = jest.fn();
  const mockOnGenerationStateChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Rendering', () => {
    it('should render when no doc ID is provided', () => {
      render(
        <ProjectGenerator
          docId={null}
          onProjectGenerated={mockOnProjectGenerated}
        />
      );

      expect(screen.getByText(/Step 02/i)).toBeInTheDocument();
      expect(screen.getByText(/Describe the project/i)).toBeInTheDocument();
      expect(screen.getByText(/Waiting for Step 01/i)).toBeInTheDocument();
    });

    it('should show message when documentation is not ready', () => {
      render(
        <ProjectGenerator
          docId={null}
          onProjectGenerated={mockOnProjectGenerated}
        />
      );

      expect(screen.getByText(/Process documentation first/i)).toBeInTheDocument();
    });

    it('should render form when doc ID is provided', () => {
      render(
        <ProjectGenerator
          docId="abc123"
          onProjectGenerated={mockOnProjectGenerated}
        />
      );

      expect(screen.getByLabelText(/Technology or framework/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/Project brief/i)).toBeInTheDocument();
      expect(screen.getByText(/Documentation ready/i)).toBeInTheDocument();
    });
  });

  describe('Technology Selection', () => {
    it('should have auto-detect option by default', () => {
      render(
        <ProjectGenerator
          docId="abc123"
          onProjectGenerated={mockOnProjectGenerated}
        />
      );

      const select = screen.getByLabelText(/Technology or framework/i) as HTMLSelectElement;
      expect(select.value).toBe('');
      expect(screen.getByText(/Auto-detect from prompt/i)).toBeInTheDocument();
    });

    it('should list all available technologies', () => {
      render(
        <ProjectGenerator
          docId="abc123"
          onProjectGenerated={mockOnProjectGenerated}
        />
      );

      expect(screen.getByText('Spring Boot')).toBeInTheDocument();
      expect(screen.getByText('Django')).toBeInTheDocument();
      expect(screen.getByText('React')).toBeInTheDocument();
      expect(screen.getByText('Express.js')).toBeInTheDocument();
      expect(screen.getByText('Flask')).toBeInTheDocument();
      expect(screen.getByText('Next.js')).toBeInTheDocument();
    });

    it('should allow technology selection', async () => {
      render(
        <ProjectGenerator
          docId="abc123"
          onProjectGenerated={mockOnProjectGenerated}
        />
      );

      const select = screen.getByLabelText(/Technology or framework/i) as HTMLSelectElement;

      await userEvent.selectOptions(select, Technology.FLASK);

      expect(select.value).toBe(Technology.FLASK);
    });
  });

  describe('Prompt Input', () => {
    it('should allow typing in prompt field', async () => {
      render(
        <ProjectGenerator
          docId="abc123"
          onProjectGenerated={mockOnProjectGenerated}
        />
      );

      const textarea = screen.getByLabelText(/Project brief/i) as HTMLTextAreaElement;

      await userEvent.type(textarea, 'Create a Flask REST API');

      expect(textarea.value).toBe('Create a Flask REST API');
    });

    it('should show character count', async () => {
      render(
        <ProjectGenerator
          docId="abc123"
          onProjectGenerated={mockOnProjectGenerated}
        />
      );

      const textarea = screen.getByLabelText(/Project brief/i);

      await userEvent.type(textarea, 'Test prompt');

      expect(screen.getByText(/11 chars/i)).toBeInTheDocument();
    });

    it('should disable submit when prompt is empty', () => {
      render(
        <ProjectGenerator
          docId="abc123"
          onProjectGenerated={mockOnProjectGenerated}
        />
      );

      const button = screen.getByRole('button', { name: /Generate project/i });
      expect(button).toBeDisabled();
    });
  });

  describe('Example Prompts', () => {
    it('should render all example prompts', () => {
      render(
        <ProjectGenerator
          docId="abc123"
          onProjectGenerated={mockOnProjectGenerated}
        />
      );

      expect(screen.getByText('Spring Boot CRUD API')).toBeInTheDocument();
      expect(screen.getByText('React admin dashboard')).toBeInTheDocument();
      expect(screen.getByText('Flask auth service')).toBeInTheDocument();
    });

    it('should populate prompt when example is clicked', async () => {
      render(
        <ProjectGenerator
          docId="abc123"
          onProjectGenerated={mockOnProjectGenerated}
        />
      );

      const exampleButton = screen.getByText('Spring Boot CRUD API').closest('button')!;
      fireEvent.click(exampleButton);

      const textarea = screen.getByLabelText(/Project brief/i) as HTMLTextAreaElement;

      await waitFor(() => {
        expect(textarea.value).toContain('Spring Boot');
        expect(textarea.value).toContain('CRUD');
      });
    });

    it('should set technology when example is clicked', async () => {
      render(
        <ProjectGenerator
          docId="abc123"
          onProjectGenerated={mockOnProjectGenerated}
        />
      );

      const exampleButton = screen.getByText('Flask auth service').closest('button')!;
      fireEvent.click(exampleButton);

      const select = screen.getByLabelText(/Technology or framework/i) as HTMLSelectElement;

      await waitFor(() => {
        expect(select.value).toBe(Technology.FLASK);
      });
    });
  });

  describe('Project Generation', () => {
    it('should generate project successfully', async () => {
      (apiService.generateProject as jest.Mock).mockResolvedValue({
        data: {
          project_id: 'proj_123',
          files: [{ name: 'app.py', content: 'code', type: 'text' }],
          instructions: 'Run the app'
        }
      });

      render(
        <ProjectGenerator
          docId="abc123"
          onProjectGenerated={mockOnProjectGenerated}
          onGenerationStateChange={mockOnGenerationStateChange}
        />
      );

      const textarea = screen.getByLabelText(/Project brief/i);
      await userEvent.type(textarea, 'Create a Flask API');

      const button = screen.getByRole('button', { name: /Generate project/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(mockOnGenerationStateChange).toHaveBeenCalledWith(true);
        expect(apiService.generateProject).toHaveBeenCalledWith({
          doc_id: 'abc123',
          prompt: 'Create a Flask API',
          technology: undefined
        });
      });

      await waitFor(() => {
        expect(mockOnProjectGenerated).toHaveBeenCalledWith(
          'proj_123',
          [{ name: 'app.py', content: 'code', type: 'text' }],
          'Run the app'
        );
        expect(mockOnGenerationStateChange).toHaveBeenCalledWith(false);
      });
    });

    it('should generate project with selected technology', async () => {
      (apiService.generateProject as jest.Mock).mockResolvedValue({
        data: {
          project_id: 'proj_124',
          files: [],
          instructions: 'Instructions'
        }
      });

      render(
        <ProjectGenerator
          docId="abc123"
          onProjectGenerated={mockOnProjectGenerated}
        />
      );

      const select = screen.getByLabelText(/Technology or framework/i);
      await userEvent.selectOptions(select, Technology.DJANGO);

      const textarea = screen.getByLabelText(/Project brief/i);
      await userEvent.type(textarea, 'Create a Django app');

      const button = screen.getByRole('button', { name: /Generate project/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(apiService.generateProject).toHaveBeenCalledWith({
          doc_id: 'abc123',
          prompt: 'Create a Django app',
          technology: Technology.DJANGO
        });
      });
    });

    it('should show error on generation failure', async () => {
      (apiService.generateProject as jest.Mock).mockRejectedValue({
        response: { data: { detail: 'Generation failed' } }
      });

      render(
        <ProjectGenerator
          docId="abc123"
          onProjectGenerated={mockOnProjectGenerated}
        />
      );

      const textarea = screen.getByLabelText(/Project brief/i);
      await userEvent.type(textarea, 'Create an app');

      const button = screen.getByRole('button', { name: /Generate project/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByText(/Generation failed/i)).toBeInTheDocument();
      });
    });

    it('should disable controls during generation', async () => {
      (apiService.generateProject as jest.Mock).mockImplementation(
        () => new Promise(() => {}) // Never resolves
      );

      render(
        <ProjectGenerator
          docId="abc123"
          onProjectGenerated={mockOnProjectGenerated}
        />
      );

      const textarea = screen.getByLabelText(/Project brief/i);
      await userEvent.type(textarea, 'Create an app');

      const button = screen.getByRole('button', { name: /Generate project/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /Generating project.../i })).toBeDisabled();
        expect(screen.getByLabelText(/Technology or framework/i)).toBeDisabled();
        expect(screen.getByLabelText(/Project brief/i)).toBeDisabled();
      });
    });
  });

  describe('Status Messages', () => {
    it('should show generating status', async () => {
      (apiService.generateProject as jest.Mock).mockImplementation(
        () => new Promise(() => {})
      );

      render(
        <ProjectGenerator
          docId="abc123"
          onProjectGenerated={mockOnProjectGenerated}
        />
      );

      const textarea = screen.getByLabelText(/Project brief/i);
      await userEvent.type(textarea, 'Create an app');

      const button = screen.getByRole('button', { name: /Generate project/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByText(/Generating your project scaffold/i)).toBeInTheDocument();
      });
    });

    it('should show success message', async () => {
      (apiService.generateProject as jest.Mock).mockResolvedValue({
        data: {
          project_id: 'proj_123',
          files: [],
          instructions: 'Done'
        }
      });

      render(
        <ProjectGenerator
          docId="abc123"
          onProjectGenerated={mockOnProjectGenerated}
        />
      );

      const textarea = screen.getByLabelText(/Project brief/i);
      await userEvent.type(textarea, 'Create an app');

      const button = screen.getByRole('button', { name: /Generate project/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByText(/Project generated successfully/i)).toBeInTheDocument();
      });
    });
  });

  describe('Form Reset', () => {
    it('should clear status when prompt changes', async () => {
      render(
        <ProjectGenerator
          docId="abc123"
          onProjectGenerated={mockOnProjectGenerated}
        />
      );

      const textarea = screen.getByLabelText(/Project brief/i);
      await userEvent.type(textarea, 'First prompt');

      // Simulate showing an error
      (apiService.generateProject as jest.Mock).mockRejectedValue({
        response: { data: { detail: 'Error' } }
      });

      const button = screen.getByRole('button', { name: /Generate project/i });
      fireEvent.click(button);

      await waitFor(() => {
        expect(screen.getByText(/Error/i)).toBeInTheDocument();
      });

      // Type more text
      await userEvent.type(textarea, ' - updated');

      await waitFor(() => {
        expect(screen.queryByText(/Error/i)).not.toBeInTheDocument();
      });
    });
  });
});