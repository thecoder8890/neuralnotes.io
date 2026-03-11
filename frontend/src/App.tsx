import React, { useEffect, useState } from 'react';
import {
  Brain,
  CheckCircle2,
  Clock3,
  Code2,
  FileText,
  Sparkles,
} from 'lucide-react';
import DocumentUpload from './components/DocumentUpload';
import ProjectGenerator from './components/ProjectGenerator';
import ProjectViewer from './components/ProjectViewer';
import { apiService } from './services/api';
import { DocumentSummary, FileContent } from './types';

type StepState = 'done' | 'active' | 'upcoming';

function formatCount(value: number): string {
  return new Intl.NumberFormat().format(value);
}

function formatDate(value: string): string {
  return new Date(value).toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  });
}

function getStepStyle(state: StepState): string {
  if (state === 'done') {
    return 'border-emerald-200 bg-emerald-50/90 text-emerald-900';
  }

  if (state === 'active') {
    return 'border-amber-200 bg-amber-50/90 text-amber-950';
  }

  return 'border-slate-200 bg-white/70 text-slate-600';
}

function App() {
  const [docId, setDocId] = useState<string | null>(null);
  const [documentSummary, setDocumentSummary] = useState<DocumentSummary | null>(null);
  const [documentSummaryError, setDocumentSummaryError] = useState<string | null>(null);
  const [isDocumentSummaryLoading, setIsDocumentSummaryLoading] = useState(false);
  const [isDocumentProcessing, setIsDocumentProcessing] = useState(false);
  const [isGeneratingProject, setIsGeneratingProject] = useState(false);
  const [projectId, setProjectId] = useState<string | null>(null);
  const [projectFiles, setProjectFiles] = useState<FileContent[]>([]);
  const [instructions, setInstructions] = useState<string>('');

  useEffect(() => {
    let ignore = false;

    if (!docId) {
      setDocumentSummary(null);
      setDocumentSummaryError(null);
      return () => {
        ignore = true;
      };
    }

    setIsDocumentSummaryLoading(true);
    setDocumentSummaryError(null);

    apiService
      .getDocumentSummary(docId)
      .then(({ data }) => {
        if (!ignore) {
          setDocumentSummary(data);
        }
      })
      .catch((error: any) => {
        if (!ignore) {
          setDocumentSummary(null);
          setDocumentSummaryError(
            error.response?.data?.detail || 'Unable to load document details.'
          );
        }
      })
      .finally(() => {
        if (!ignore) {
          setIsDocumentSummaryLoading(false);
        }
      });

    return () => {
      ignore = true;
    };
  }, [docId]);

  const handleDocumentProcessed = (newDocId: string) => {
    setDocId(newDocId);
    setDocumentSummary(null);
    setDocumentSummaryError(null);
    setProjectId(null);
    setProjectFiles([]);
    setInstructions('');
  };

  const handleProjectGenerated = (
    newProjectId: string,
    files: FileContent[],
    newInstructions: string
  ) => {
    setProjectId(newProjectId);
    setProjectFiles(files);
    setInstructions(newInstructions);
  };

  const hasProject = Boolean(projectId && projectFiles.length > 0);

  const steps: Array<{ id: string; title: string; description: string; state: StepState }> = [
    {
      id: '01',
      title: 'Ingest documentation',
      description: documentSummary
        ? `Indexed ${documentSummary.source_name}`
        : isDocumentProcessing
          ? 'Processing documentation now'
          : 'Add a URL or upload source files',
      state: documentSummary || docId ? 'done' : isDocumentProcessing ? 'active' : 'upcoming',
    },
    {
      id: '02',
      title: 'Describe the project',
      description: hasProject
        ? 'Prompt locked into a generated project'
        : isGeneratingProject
          ? 'Generating files and instructions'
          : docId
            ? 'Ready for your project brief'
            : 'Waiting for documentation',
      state: hasProject ? 'done' : isGeneratingProject ? 'active' : docId ? 'active' : 'upcoming',
    },
    {
      id: '03',
      title: 'Review the output',
      description: hasProject
        ? `${projectFiles.length} files ready to inspect`
        : 'Browse files, copy code, and export ZIP',
      state: hasProject ? 'done' : 'upcoming',
    },
  ];

  return (
    <div className="min-h-screen text-slate-900">
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <header className="mb-8 flex flex-col gap-4 rounded-[28px] border border-white/70 bg-white/70 px-6 py-5 shadow-[0_24px_80px_rgba(28,35,38,0.08)] backdrop-blur sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-950 text-amber-200 shadow-lg">
              <Brain size={28} />
            </div>
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">
                DocuGen AI
              </p>
              <h1 className="text-2xl font-semibold tracking-tight text-slate-950">
                Documentation-aware project scaffolding
              </h1>
            </div>
          </div>
          <div className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-4 py-2 text-sm font-medium text-emerald-900">
            <Sparkles size={16} />
            Improved workflow branch
          </div>
        </header>

        <main className="space-y-8 pb-12">
          <section className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
            <div className="rounded-[32px] border border-white/70 bg-white/78 p-7 shadow-[0_32px_100px_rgba(28,35,38,0.09)] backdrop-blur">
              <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-xs font-semibold uppercase tracking-[0.22em] text-amber-900">
                <Sparkles size={14} />
                Suggested + implemented improvements
              </div>
              <h2 className="max-w-3xl text-4xl font-semibold leading-tight tracking-tight text-slate-950 sm:text-5xl">
                The app now shows what it ingests, keeps the flow visible, and makes generated
                code easier to review.
              </h2>
              <p className="mt-4 max-w-3xl text-lg leading-8 text-slate-600">
                This pass focuses on three practical issues in the original prototype: weak
                workflow visibility, no post-upload document context, and a project browser that
                became hard to use as file trees grew.
              </p>
              <div className="mt-8 grid gap-4 md:grid-cols-3">
                <div className="rounded-3xl border border-slate-200/80 bg-slate-50/90 p-4">
                  <FileText className="mb-3 text-amber-700" size={24} />
                  <h3 className="text-base font-semibold text-slate-900">Document summary</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-600">
                    Every processed source now exposes preview, size, chunk estimate, and
                    timestamp metadata.
                  </p>
                </div>
                <div className="rounded-3xl border border-slate-200/80 bg-slate-50/90 p-4">
                  <Clock3 className="mb-3 text-amber-700" size={24} />
                  <h3 className="text-base font-semibold text-slate-900">Clear step status</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-600">
                    The main screen now tracks ingestion, generation, and review instead of
                    leaving the user to infer state.
                  </p>
                </div>
                <div className="rounded-3xl border border-slate-200/80 bg-slate-50/90 p-4">
                  <Code2 className="mb-3 text-amber-700" size={24} />
                  <h3 className="text-base font-semibold text-slate-900">Better file review</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-600">
                    The project viewer now resets correctly, expands predictable folders, and
                    exposes output stats.
                  </p>
                </div>
              </div>
            </div>

            <div className="rounded-[32px] border border-white/70 bg-[#13262f] p-6 text-white shadow-[0_36px_90px_rgba(8,15,18,0.22)]">
              <div className="mb-5 flex items-center justify-between">
                <div>
                  <p className="text-sm uppercase tracking-[0.24em] text-slate-300">
                    Pipeline Status
                  </p>
                  <h2 className="mt-2 text-2xl font-semibold text-white">Three-step workflow</h2>
                </div>
                {hasProject ? (
                  <CheckCircle2 className="text-emerald-300" size={26} />
                ) : (
                  <Clock3 className="text-amber-300" size={26} />
                )}
              </div>

              <div className="space-y-3">
                {steps.map((step) => (
                  <div
                    key={step.id}
                    className={`rounded-3xl border px-4 py-4 ${getStepStyle(step.state)}`}
                  >
                    <div className="mb-2 flex items-center justify-between gap-3">
                      <span className="text-xs font-semibold uppercase tracking-[0.24em]">
                        Step {step.id}
                      </span>
                      <span className="rounded-full bg-white/70 px-3 py-1 text-xs font-semibold text-slate-800">
                        {step.state === 'done'
                          ? 'Completed'
                          : step.state === 'active'
                            ? 'In focus'
                            : 'Queued'}
                      </span>
                    </div>
                    <h3 className="text-lg font-semibold">{step.title}</h3>
                    <p className="mt-1 text-sm leading-6 opacity-90">{step.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </section>

          {docId && (
            <section className="rounded-[32px] border border-white/70 bg-white/78 p-6 shadow-[0_24px_80px_rgba(28,35,38,0.08)] backdrop-blur">
              <div className="flex flex-col gap-3 border-b border-slate-200/80 pb-5 md:flex-row md:items-center md:justify-between">
                <div>
                  <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">
                    Processed Document
                  </p>
                  <h2 className="mt-2 text-2xl font-semibold text-slate-950">
                    {documentSummary?.source_name || 'Loading source details'}
                  </h2>
                </div>
                <div className="text-sm text-slate-500">
                  {isDocumentSummaryLoading
                    ? 'Refreshing summary...'
                    : documentSummary
                      ? `Processed ${formatDate(documentSummary.processed_at)}`
                      : documentSummaryError || 'Waiting for metadata'}
                </div>
              </div>

              {documentSummary && (
                <div className="mt-5 grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
                  <div className="grid gap-3 sm:grid-cols-2">
                    <div className="rounded-3xl border border-slate-200 bg-slate-50/90 p-4">
                      <p className="text-sm font-medium text-slate-500">Source type</p>
                      <p className="mt-2 text-lg font-semibold capitalize text-slate-950">
                        {documentSummary.source_type}
                      </p>
                    </div>
                    <div className="rounded-3xl border border-slate-200 bg-slate-50/90 p-4">
                      <p className="text-sm font-medium text-slate-500">Characters</p>
                      <p className="mt-2 text-lg font-semibold text-slate-950">
                        {formatCount(documentSummary.char_count)}
                      </p>
                    </div>
                    <div className="rounded-3xl border border-slate-200 bg-slate-50/90 p-4">
                      <p className="text-sm font-medium text-slate-500">Approx. chunks</p>
                      <p className="mt-2 text-lg font-semibold text-slate-950">
                        {formatCount(documentSummary.approx_chunks)}
                      </p>
                    </div>
                    <div className="rounded-3xl border border-slate-200 bg-slate-50/90 p-4">
                      <p className="text-sm font-medium text-slate-500">Document ID</p>
                      <p className="mt-2 truncate font-mono text-sm text-slate-700">
                        {documentSummary.doc_id}
                      </p>
                    </div>
                  </div>

                  <div className="rounded-3xl border border-amber-200 bg-amber-50/80 p-5">
                    <p className="text-sm font-semibold uppercase tracking-[0.22em] text-amber-900">
                      Preview
                    </p>
                    <p className="mt-3 text-sm leading-7 text-slate-700">
                      {documentSummary.preview ||
                        'No preview is available for this source yet, but the document is ready for generation.'}
                    </p>
                  </div>
                </div>
              )}
            </section>
          )}

          <section className="space-y-6">
            <DocumentUpload
              onDocumentProcessed={handleDocumentProcessed}
              isProcessing={isDocumentProcessing}
              onProcessingStateChange={setIsDocumentProcessing}
            />

            <ProjectGenerator
              docId={docId}
              onProjectGenerated={handleProjectGenerated}
              onGenerationStateChange={setIsGeneratingProject}
            />

            {projectId && hasProject && (
              <ProjectViewer projectId={projectId} files={projectFiles} instructions={instructions} />
            )}
          </section>

          <section className="grid gap-4 md:grid-cols-3">
            <div className="rounded-[28px] border border-white/70 bg-white/75 p-5 shadow-[0_22px_70px_rgba(28,35,38,0.08)] backdrop-blur">
              <p className="text-sm font-semibold uppercase tracking-[0.22em] text-slate-500">
                Example brief
              </p>
              <h3 className="mt-2 text-lg font-semibold text-slate-950">Spring Boot API</h3>
              <p className="mt-3 text-sm leading-6 text-slate-600">
                Create a Spring Boot service with user CRUD, PostgreSQL, validation, and a clean
                layered structure.
              </p>
            </div>
            <div className="rounded-[28px] border border-white/70 bg-white/75 p-5 shadow-[0_22px_70px_rgba(28,35,38,0.08)] backdrop-blur">
              <p className="text-sm font-semibold uppercase tracking-[0.22em] text-slate-500">
                Example brief
              </p>
              <h3 className="mt-2 text-lg font-semibold text-slate-950">React dashboard</h3>
              <p className="mt-3 text-sm leading-6 text-slate-600">
                Build a responsive React dashboard with auth, charts, filtered tables, and API
                integration points.
              </p>
            </div>
            <div className="rounded-[28px] border border-white/70 bg-white/75 p-5 shadow-[0_22px_70px_rgba(28,35,38,0.08)] backdrop-blur">
              <p className="text-sm font-semibold uppercase tracking-[0.22em] text-slate-500">
                Example brief
              </p>
              <h3 className="mt-2 text-lg font-semibold text-slate-950">Flask service</h3>
              <p className="mt-3 text-sm leading-6 text-slate-600">
                Generate a Flask API with SQLAlchemy models, JWT auth, environment config, and a
                deployment-ready README.
              </p>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}

export default App;
