import React, { useEffect, useState } from 'react';
import {
  AlertCircle,
  CheckCircle,
  FileText,
  Link,
  Upload,
  X,
} from 'lucide-react';
import { apiService } from '../services/api';

interface DocumentUploadProps {
  onDocumentProcessed: (docId: string) => void;
  isProcessing: boolean;
  onProcessingStateChange?: (isProcessing: boolean) => void;
}

interface SelectedFile {
  file: File;
  id: string;
}

type UploadStatus = 'idle' | 'processing' | 'success' | 'warning' | 'error';

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatExtension(extension: string): string {
  return extension.replace('.', '').toUpperCase();
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onDocumentProcessed,
  isProcessing,
  onProcessingStateChange,
}) => {
  const [url, setUrl] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [uploadMethod, setUploadMethod] = useState<'url' | 'file'>('url');
  const [status, setStatus] = useState<UploadStatus>('idle');
  const [message, setMessage] = useState('');
  const [selectedFiles, setSelectedFiles] = useState<SelectedFile[]>([]);
  const [supportedFormats, setSupportedFormats] = useState<string[]>([]);
  const [maxFileSizeMb, setMaxFileSizeMb] = useState(50);

  useEffect(() => {
    let ignore = false;

    apiService
      .getSupportedFormats()
      .then(({ data }) => {
        if (!ignore) {
          setSupportedFormats(data.formats);
          setMaxFileSizeMb(data.max_file_size_mb);
        }
      })
      .catch(() => {
        if (!ignore) {
          setSupportedFormats(['.pdf', '.md', '.txt', '.html', '.rst', '.docx']);
        }
      });

    return () => {
      ignore = true;
    };
  }, []);

  const setProcessingState = (value: boolean) => {
    onProcessingStateChange?.(value);
  };

  const resetFeedback = () => {
    setStatus('idle');
    setMessage('');
  };

  const handleUrlSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!url.trim()) return;

    setStatus('processing');
    setMessage('Fetching and indexing documentation from the provided URL...');
    setProcessingState(true);

    try {
      const response = await apiService.processDocumentationUrl(url.trim());
      setStatus('success');
      setMessage('Documentation processed successfully.');
      setUrl('');
      onDocumentProcessed(response.data.doc_id);
    } catch (error: any) {
      setStatus('error');
      setMessage(error.response?.data?.detail || 'Failed to process documentation URL.');
    } finally {
      setProcessingState(false);
    }
  };

  const addFiles = (files: FileList | File[]) => {
    const incomingFiles = Array.from(files);

    setSelectedFiles((previous) => {
      const seen = new Set(
        previous.map(({ file }) => `${file.name}-${file.size}-${file.lastModified}`)
      );
      const additions = incomingFiles
        .filter((file) => {
          const key = `${file.name}-${file.size}-${file.lastModified}`;
          return !seen.has(key);
        })
        .map((file) => ({
          file,
          id: `${file.name}-${file.size}-${file.lastModified}`,
        }));

      return [...previous, ...additions];
    });

    resetFeedback();
  };

  const removeFile = (id: string) => {
    setSelectedFiles((previous) => previous.filter((item) => item.id !== id));
  };

  const handleUploadFiles = async () => {
    if (selectedFiles.length === 0) return;

    setStatus('processing');
    setMessage('Uploading files and extracting documentation content...');
    setProcessingState(true);

    try {
      if (selectedFiles.length === 1) {
        const response = await apiService.uploadDocumentation(selectedFiles[0].file);
        setStatus('success');
        setMessage(`Processed ${selectedFiles[0].file.name}.`);
        onDocumentProcessed(response.data.doc_id);
      } else {
        const response = await apiService.uploadMultipleDocumentation(
          selectedFiles.map(({ file }) => file)
        );
        const data = response.data;

        if (data.results && data.results.length > 0) {
          setStatus(data.errors && data.errors.length > 0 ? 'warning' : 'success');
          setMessage(
            data.errors && data.errors.length > 0
              ? `${data.message}. ${data.errors.length} file failed validation.`
              : data.message
          );
          onDocumentProcessed(data.results[0].doc_id);
        } else {
          setStatus('error');
          setMessage('All selected file uploads failed.');
        }
      }

      setSelectedFiles([]);
    } catch (error: any) {
      setStatus('error');
      setMessage(error.response?.data?.detail || 'Failed to process uploaded files.');
    } finally {
      setProcessingState(false);
    }
  };

  const handleDrag = (event: React.DragEvent) => {
    event.preventDefault();
    event.stopPropagation();

    if (event.type === 'dragenter' || event.type === 'dragover') {
      setDragActive(true);
    } else if (event.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (event: React.DragEvent) => {
    event.preventDefault();
    event.stopPropagation();
    setDragActive(false);

    if (event.dataTransfer.files && event.dataTransfer.files.length > 0) {
      addFiles(event.dataTransfer.files);
    }
  };

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      addFiles(event.target.files);
    }
    event.target.value = '';
  };

  const totalSelectedSize = selectedFiles.reduce((sum, item) => sum + item.file.size, 0);

  return (
    <section className="rounded-[32px] border border-white/70 bg-white/78 p-6 shadow-[0_24px_80px_rgba(28,35,38,0.08)] backdrop-blur">
      <div className="flex flex-col gap-3 border-b border-slate-200/80 pb-5 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">
            Step 01
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">Ingest documentation</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
            Start with a public documentation URL or upload files directly. The improved flow now
            reports supported formats and keeps source metadata visible after processing.
          </p>
        </div>

        <div className="inline-flex rounded-full border border-slate-200 bg-slate-100 p-1">
          <button
            type="button"
            onClick={() => {
              setUploadMethod('url');
              resetFeedback();
            }}
            className={`rounded-full px-4 py-2 text-sm font-medium ${
              uploadMethod === 'url'
                ? 'bg-slate-950 text-white'
                : 'text-slate-600 hover:text-slate-950'
            }`}
          >
            <span className="inline-flex items-center gap-2">
              <Link size={16} />
              URL
            </span>
          </button>
          <button
            type="button"
            onClick={() => {
              setUploadMethod('file');
              resetFeedback();
            }}
            className={`rounded-full px-4 py-2 text-sm font-medium ${
              uploadMethod === 'file'
                ? 'bg-slate-950 text-white'
                : 'text-slate-600 hover:text-slate-950'
            }`}
          >
            <span className="inline-flex items-center gap-2">
              <Upload size={16} />
              Files
            </span>
          </button>
        </div>
      </div>

      <div className="mt-5 grid gap-4 md:grid-cols-[1.1fr_0.9fr]">
        <div className="rounded-3xl border border-slate-200 bg-slate-50/85 p-4">
          {uploadMethod === 'url' ? (
            <form onSubmit={handleUrlSubmit} className="space-y-4">
              <label htmlFor="url-input" className="block">
                <span className="mb-2 block text-sm font-medium text-slate-700">
                  Documentation URL
                </span>
                <input
                  id="url-input"
                  type="url"
                  value={url}
                  onChange={(event) => {
                    setUrl(event.target.value);
                    if (status !== 'processing') resetFeedback();
                  }}
                  placeholder="https://react.dev/learn"
                  className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-slate-900 outline-none transition focus:border-amber-400 focus:ring-4 focus:ring-amber-100"
                  disabled={isProcessing}
                />
              </label>

              <button
                type="submit"
                disabled={!url.trim() || isProcessing}
                className="inline-flex w-full items-center justify-center rounded-2xl bg-slate-950 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
              >
                {isProcessing ? 'Processing documentation...' : 'Process documentation URL'}
              </button>
            </form>
          ) : (
            <div>
              <div
                className={`rounded-[28px] border-2 border-dashed p-6 text-center transition ${
                  dragActive
                    ? 'border-amber-500 bg-amber-50'
                    : 'border-slate-300 bg-white hover:border-slate-400'
                }`}
                onDragEnter={handleDrag}
                onDragLeave={handleDrag}
                onDragOver={handleDrag}
                onDrop={handleDrop}
              >
                <Upload className="mx-auto mb-4 text-slate-400" size={40} />
                <p className="text-base font-medium text-slate-800">
                  Drag files here or choose them manually
                </p>
                <p className="mt-2 text-sm leading-6 text-slate-500">
                  Multiple files are supported. Duplicate picks are filtered automatically.
                </p>
                <input
                  id="file-upload"
                  type="file"
                  onChange={handleFileSelect}
                  accept={supportedFormats.join(',')}
                  className="hidden"
                  disabled={isProcessing}
                  multiple
                />
                <label
                  htmlFor="file-upload"
                  className="mt-5 inline-flex cursor-pointer items-center justify-center rounded-full bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
                >
                  Select files
                </label>
              </div>

              {selectedFiles.length > 0 && (
                <div className="mt-4 rounded-3xl border border-slate-200 bg-white p-4">
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <div>
                      <p className="text-sm font-semibold text-slate-900">
                        {selectedFiles.length} file{selectedFiles.length > 1 ? 's' : ''} ready
                      </p>
                      <p className="text-sm text-slate-500">
                        {formatFileSize(totalSelectedSize)} total selected
                      </p>
                    </div>
                    <button
                      type="button"
                      onClick={handleUploadFiles}
                      disabled={isProcessing}
                      className="rounded-full bg-amber-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-amber-400 disabled:cursor-not-allowed disabled:bg-slate-300"
                    >
                      {isProcessing ? 'Processing...' : 'Upload and process'}
                    </button>
                  </div>

                  <div className="space-y-2">
                    {selectedFiles.map((item) => (
                      <div
                        key={item.id}
                        className="flex items-center justify-between rounded-2xl border border-slate-200 bg-slate-50 px-3 py-3"
                      >
                        <div className="flex min-w-0 items-center gap-3">
                          <FileText size={18} className="flex-shrink-0 text-slate-500" />
                          <div className="min-w-0">
                            <p className="truncate text-sm font-medium text-slate-900">
                              {item.file.name}
                            </p>
                            <p className="text-xs text-slate-500">
                              {formatFileSize(item.file.size)}
                            </p>
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={() => removeFile(item.id)}
                          className="rounded-full p-2 text-slate-400 transition hover:bg-red-50 hover:text-red-600"
                          aria-label={`Remove ${item.file.name}`}
                        >
                          <X size={16} />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        <div className="rounded-3xl border border-amber-200 bg-amber-50/80 p-4">
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-amber-900">
            Ingestion notes
          </p>
          <div className="mt-4 flex flex-wrap gap-2">
            {supportedFormats.map((extension) => (
              <span
                key={extension}
                className="rounded-full border border-amber-200 bg-white px-3 py-1 text-xs font-semibold text-slate-700"
              >
                {formatExtension(extension)}
              </span>
            ))}
          </div>
          <p className="mt-4 text-sm leading-6 text-slate-700">
            Maximum file size: {maxFileSizeMb} MB each. File uploads are the most reliable way to
            capture exact source content when a URL is behind auth or dynamic rendering.
          </p>
        </div>
      </div>

      {status !== 'idle' && (
        <div
          className={`mt-5 flex items-start gap-3 rounded-3xl border px-4 py-4 text-sm ${
            status === 'success'
              ? 'border-emerald-200 bg-emerald-50 text-emerald-900'
              : status === 'warning'
                ? 'border-amber-200 bg-amber-50 text-amber-950'
                : status === 'error'
                  ? 'border-rose-200 bg-rose-50 text-rose-900'
                  : 'border-blue-200 bg-blue-50 text-blue-900'
          }`}
        >
          {status === 'success' ? (
            <CheckCircle size={18} className="mt-0.5 flex-shrink-0" />
          ) : status === 'error' || status === 'warning' ? (
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

export default DocumentUpload;
