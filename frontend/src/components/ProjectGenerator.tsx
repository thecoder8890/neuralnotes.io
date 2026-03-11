import React, { useState } from 'react';
import { AlertCircle, CheckCircle, Sparkles, Wand2 } from 'lucide-react';
import { apiService } from '../services/api';
import { Technology } from '../types';

interface ProjectGeneratorProps {
  docId: string | null;
  onProjectGenerated: (projectId: string, files: any[], instructions: string) => void;
  onGenerationStateChange?: (isGenerating: boolean) => void;
}

type GeneratorStatus = 'idle' | 'generating' | 'success' | 'error';

const examplePrompts = [
  {
    title: 'Spring Boot CRUD API',
    technology: Technology.SPRING_BOOT,
    prompt:
      'Create a Spring Boot web application using Maven with REST CRUD endpoints for a User entity, validation, service and repository layers, and PostgreSQL configuration.',
  },
  {
    title: 'React admin dashboard',
    technology: Technology.REACT,
    prompt:
      'Build a React TypeScript dashboard with login flow, charts, table filtering, reusable layout components, and API integration placeholders.',
  },
  {
    title: 'Flask auth service',
    technology: Technology.FLASK,
    prompt:
      'Create a Flask REST API with SQLAlchemy, JWT authentication, environment-based configuration, and CRUD routes for blog posts.',
  },
];

const ProjectGenerator: React.FC<ProjectGeneratorProps> = ({
  docId,
  onProjectGenerated,
  onGenerationStateChange,
}) => {
  const [prompt, setPrompt] = useState('');
  const [technology, setTechnology] = useState<Technology | ''>('');
  const [status, setStatus] = useState<GeneratorStatus>('idle');
  const [message, setMessage] = useState('');

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!docId || !prompt.trim()) return;

    setStatus('generating');
    setMessage('Generating your project scaffold...');
    onGenerationStateChange?.(true);

    try {
      const response = await apiService.generateProject({
        doc_id: docId,
        prompt: prompt.trim(),
        technology: technology || undefined,
      });

      setStatus('success');
      setMessage('Project generated successfully.');
      onProjectGenerated(response.data.project_id, response.data.files, response.data.instructions);
    } catch (error: any) {
      setStatus('error');
      setMessage(error.response?.data?.detail || 'Failed to generate project.');
    } finally {
      onGenerationStateChange?.(false);
    }
  };

  return (
    <section className="rounded-[32px] border border-white/70 bg-white/78 p-6 shadow-[0_24px_80px_rgba(28,35,38,0.08)] backdrop-blur">
      <div className="flex flex-col gap-3 border-b border-slate-200/80 pb-5 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">
            Step 02
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">Describe the project</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
            The generator is more guided now. Pick a framework if you want tighter control, or
            leave it on auto-detect and anchor the result with a stronger prompt.
          </p>
        </div>

        <div
          className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium ${
            docId
              ? 'border border-emerald-200 bg-emerald-50 text-emerald-900'
              : 'border border-slate-200 bg-slate-100 text-slate-500'
          }`}
        >
          <Sparkles size={16} />
          {docId ? 'Documentation ready' : 'Waiting for Step 01'}
        </div>
      </div>

      {!docId ? (
        <div className="mt-5 rounded-3xl border border-amber-200 bg-amber-50/80 p-5 text-sm leading-6 text-amber-950">
          Process documentation first so the project generator has a source to ground the output.
        </div>
      ) : (
        <div className="mt-5 grid gap-4 xl:grid-cols-[1.1fr_0.9fr]">
          <form onSubmit={handleSubmit} className="rounded-3xl border border-slate-200 bg-slate-50/85 p-4">
            <div className="space-y-4">
              <label htmlFor="technology" className="block">
                <span className="mb-2 block text-sm font-medium text-slate-700">
                  Technology or framework
                </span>
                <select
                  id="technology"
                  value={technology}
                  onChange={(event) => setTechnology(event.target.value as Technology)}
                  className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-900 outline-none transition focus:border-amber-400 focus:ring-4 focus:ring-amber-100"
                  disabled={status === 'generating'}
                >
                  <option value="">Auto-detect from prompt</option>
                  <option value={Technology.SPRING_BOOT}>Spring Boot</option>
                  <option value={Technology.DJANGO}>Django</option>
                  <option value={Technology.REACT}>React</option>
                  <option value={Technology.EXPRESS}>Express.js</option>
                  <option value={Technology.FLASK}>Flask</option>
                  <option value={Technology.NEXTJS}>Next.js</option>
                </select>
              </label>

              <label htmlFor="prompt" className="block">
                <span className="mb-2 block text-sm font-medium text-slate-700">
                  Project brief
                </span>
                <textarea
                  id="prompt"
                  value={prompt}
                  onChange={(event) => {
                    setPrompt(event.target.value);
                    if (status !== 'generating') {
                      setStatus('idle');
                      setMessage('');
                    }
                  }}
                  placeholder="Describe the project you want to generate..."
                  rows={6}
                  className="w-full rounded-[24px] border border-slate-200 bg-white px-4 py-3 text-slate-900 outline-none transition focus:border-amber-400 focus:ring-4 focus:ring-amber-100"
                  disabled={status === 'generating'}
                />
              </label>

              <div className="flex items-center justify-between text-sm text-slate-500">
                <span>Be explicit about stack, auth, database, and deployment needs.</span>
                <span>{prompt.trim().length} chars</span>
              </div>

              <button
                type="submit"
                disabled={!prompt.trim() || status === 'generating'}
                className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-slate-950 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
              >
                <Wand2 size={18} />
                {status === 'generating' ? 'Generating project...' : 'Generate project'}
              </button>
            </div>
          </form>

          <div className="rounded-3xl border border-amber-200 bg-amber-50/80 p-4">
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-amber-900">
              Prompt starters
            </p>
            <div className="mt-4 space-y-3">
              {examplePrompts.map((example) => (
                <button
                  key={example.title}
                  type="button"
                  onClick={() => {
                    setPrompt(example.prompt);
                    setTechnology(example.technology);
                    setStatus('idle');
                    setMessage('');
                  }}
                  className="block w-full rounded-3xl border border-amber-200 bg-white px-4 py-4 text-left transition hover:border-amber-400 hover:bg-amber-100/40"
                  disabled={status === 'generating'}
                >
                  <p className="text-sm font-semibold text-slate-950">{example.title}</p>
                  <p className="mt-2 text-sm leading-6 text-slate-600">{example.prompt}</p>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {status !== 'idle' && (
        <div
          className={`mt-5 flex items-start gap-3 rounded-3xl border px-4 py-4 text-sm ${
            status === 'success'
              ? 'border-emerald-200 bg-emerald-50 text-emerald-900'
              : status === 'error'
                ? 'border-rose-200 bg-rose-50 text-rose-900'
                : 'border-blue-200 bg-blue-50 text-blue-900'
          }`}
        >
          {status === 'success' ? (
            <CheckCircle size={18} className="mt-0.5 flex-shrink-0" />
          ) : status === 'error' ? (
            <AlertCircle size={18} className="mt-0.5 flex-shrink-0" />
          ) : (
            <div className="mt-1 h-4 w-4 flex-shrink-0 animate-spin rounded-full border-2 border-current border-r-transparent" />
          )}
          <span>{message}</span>
        </div>
      )}
    </section>
  );
};

export default ProjectGenerator;
