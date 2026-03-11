import React, { useEffect, useState } from 'react';
import {
  CheckCircle,
  ChevronDown,
  ChevronRight,
  Copy,
  Download,
  File,
  Folder,
} from 'lucide-react';
import { apiService } from '../services/api';
import { FileContent } from '../types';

interface ProjectViewerProps {
  projectId: string;
  files: FileContent[];
  instructions: string;
}

type TreeItem =
  | { type: 'file'; file: FileContent }
  | { type: 'folder'; children: Record<string, TreeItem> };

function buildFileTree(files: FileContent[]): Record<string, TreeItem> {
  const tree: Record<string, TreeItem> = {};

  files.forEach((file) => {
    const parts = file.name.split('/');
    let current: Record<string, TreeItem> = tree;

    parts.forEach((part, index) => {
      const isFile = index === parts.length - 1;

      if (isFile) {
        current[part] = { type: 'file', file };
        return;
      }

      if (!current[part] || current[part].type !== 'folder') {
        current[part] = { type: 'folder', children: {} };
      }

      const nextFolder = current[part];
      if (nextFolder.type === 'folder') {
        current = nextFolder.children;
      }
    });
  });

  return tree;
}

function getInitialExpandedFolders(files: FileContent[]): Set<string> {
  const expanded = new Set<string>();

  files.forEach((file) => {
    const folders = file.name.split('/').slice(0, -1);
    let path = '';

    folders.forEach((folder, index) => {
      path = path ? `${path}/${folder}` : folder;
      if (index < 2) {
        expanded.add(path);
      }
    });
  });

  return expanded;
}

function sortTreeEntries(node: Record<string, TreeItem>): Array<[string, TreeItem]> {
  return Object.entries(node).sort(([leftName, leftItem], [rightName, rightItem]) => {
    if (leftItem.type !== rightItem.type) {
      return leftItem.type === 'folder' ? -1 : 1;
    }

    return leftName.localeCompare(rightName);
  });
}

function getDefaultSelectedFile(files: FileContent[]): FileContent | null {
  if (files.length === 0) {
    return null;
  }

  return (
    files.find((file) => file.name.toLowerCase() === 'readme.md') ??
    [...files].sort((left, right) => left.name.localeCompare(right.name))[0]
  );
}

const ProjectViewer: React.FC<ProjectViewerProps> = ({ projectId, files, instructions }) => {
  const [selectedFile, setSelectedFile] = useState<FileContent | null>(getDefaultSelectedFile(files));
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(getInitialExpandedFolders(files));
  const [copiedFileName, setCopiedFileName] = useState<string | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadError, setDownloadError] = useState<string | null>(null);

  useEffect(() => {
    setSelectedFile(getDefaultSelectedFile(files));
    setExpandedFolders(getInitialExpandedFolders(files));
    setCopiedFileName(null);
    setDownloadError(null);
  }, [files, projectId]);

  const handleDownload = async () => {
    setIsDownloading(true);
    setDownloadError(null);

    try {
      const response = await apiService.downloadProject(projectId);
      const blob = new Blob([response.data], { type: 'application/zip' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `project_${projectId}.zip`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      setDownloadError('Download failed. Try again.');
    } finally {
      setIsDownloading(false);
    }
  };

  const copyToClipboard = async (file: FileContent) => {
    try {
      await navigator.clipboard.writeText(file.content);
      setCopiedFileName(file.name);
      window.setTimeout(() => setCopiedFileName(null), 2000);
    } catch (error) {
      setCopiedFileName(null);
    }
  };

  const toggleFolder = (path: string) => {
    setExpandedFolders((previous) => {
      const next = new Set(previous);

      if (next.has(path)) {
        next.delete(path);
      } else {
        next.add(path);
      }

      return next;
    });
  };

  const renderFileTree = (
    node: Record<string, TreeItem>,
    path = '',
    depth = 0
  ): React.ReactNode =>
    sortTreeEntries(node).map(([name, item]) => {
      const currentPath = path ? `${path}/${name}` : name;

      if (item.type === 'folder') {
        const isExpanded = expandedFolders.has(currentPath);

        return (
          <div key={currentPath}>
            <button
              type="button"
              onClick={() => toggleFolder(currentPath)}
              className="flex w-full items-center gap-2 rounded-2xl px-3 py-2 text-left text-sm text-slate-700 transition hover:bg-slate-100"
              style={{ paddingLeft: `${12 + depth * 14}px` }}
            >
              {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
              <Folder size={16} className="text-amber-700" />
              <span className="font-medium">{name}</span>
            </button>
            {isExpanded && <div>{renderFileTree(item.children, currentPath, depth + 1)}</div>}
          </div>
        );
      }

      const isSelected = selectedFile?.name === item.file.name;

      return (
        <button
          key={currentPath}
          type="button"
          onClick={() => setSelectedFile(item.file)}
          className={`flex w-full items-center gap-2 rounded-2xl px-3 py-2 text-left text-sm transition ${
            isSelected
              ? 'bg-amber-100 text-slate-950'
              : 'text-slate-700 hover:bg-slate-100'
          }`}
          style={{ paddingLeft: `${22 + depth * 14}px` }}
        >
          <File size={16} className="flex-shrink-0 text-slate-500" />
          <span className="truncate">{name}</span>
        </button>
      );
    });

  const totalLines = files.reduce((count, file) => count + file.content.split('\n').length, 0);
  const fileTree = buildFileTree(files);

  return (
    <section className="rounded-[32px] border border-white/70 bg-white/78 p-6 shadow-[0_24px_80px_rgba(28,35,38,0.08)] backdrop-blur">
      <div className="flex flex-col gap-3 border-b border-slate-200/80 pb-5 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">
            Step 03
          </p>
          <h2 className="mt-2 text-2xl font-semibold text-slate-950">Review and export</h2>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
            The viewer now resets correctly on fresh generations, keeps useful folders expanded,
            and surfaces project size so larger outputs stay navigable.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <span className="rounded-full border border-slate-200 bg-slate-100 px-4 py-2 text-sm font-medium text-slate-700">
            {files.length} files
          </span>
          <span className="rounded-full border border-slate-200 bg-slate-100 px-4 py-2 text-sm font-medium text-slate-700">
            {totalLines} lines
          </span>
          <button
            type="button"
            onClick={handleDownload}
            disabled={isDownloading}
            className="inline-flex items-center gap-2 rounded-full bg-slate-950 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400"
          >
            <Download size={18} />
            {isDownloading ? 'Preparing ZIP...' : 'Download ZIP'}
          </button>
        </div>
      </div>

      <div className="mt-5 grid gap-5 xl:grid-cols-[0.8fr_1.2fr]">
        <div className="rounded-3xl border border-slate-200 bg-slate-50/85 p-4">
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-base font-semibold text-slate-950">Project structure</h3>
            <span className="text-xs font-medium uppercase tracking-[0.2em] text-slate-500">
              Explorer
            </span>
          </div>
          <div className="max-h-[30rem] overflow-y-auto rounded-3xl border border-slate-200 bg-white p-2">
            {renderFileTree(fileTree)}
          </div>
        </div>

        <div className="rounded-3xl border border-slate-200 bg-slate-50/85 p-4">
          {selectedFile ? (
            <div>
              <div className="mb-3 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm font-semibold text-slate-950">{selectedFile.name}</p>
                  <p className="text-sm text-slate-500">{selectedFile.type}</p>
                </div>
                <button
                  type="button"
                  onClick={() => copyToClipboard(selectedFile)}
                  className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-slate-300 hover:bg-slate-100"
                >
                  {copiedFileName === selectedFile.name ? (
                    <CheckCircle size={16} className="text-emerald-600" />
                  ) : (
                    <Copy size={16} />
                  )}
                  {copiedFileName === selectedFile.name ? 'Copied' : 'Copy file'}
                </button>
              </div>

              <pre className="max-h-[30rem] overflow-auto rounded-[28px] border border-slate-200 bg-[#111827] p-4 text-sm leading-6 text-slate-100">
                <code>{selectedFile.content}</code>
              </pre>
            </div>
          ) : (
            <div className="flex min-h-[18rem] items-center justify-center rounded-[28px] border border-dashed border-slate-300 bg-white text-sm text-slate-500">
              Select a file to inspect its contents.
            </div>
          )}
        </div>
      </div>

      <div className="mt-5 rounded-3xl border border-amber-200 bg-amber-50/80 p-5">
        <h3 className="text-base font-semibold text-slate-950">Setup instructions</h3>
        <pre className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-700">
          {instructions}
        </pre>
      </div>

      {downloadError && (
        <div className="mt-4 rounded-3xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-900">
          {downloadError}
        </div>
      )}
    </section>
  );
};

export default ProjectViewer;
