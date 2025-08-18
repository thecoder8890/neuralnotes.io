import React, { useState } from 'react';
import { FileContent } from '../types';
import { Download, File, Folder, ChevronRight, ChevronDown, Copy, CheckCircle } from 'lucide-react';

interface ProjectViewerProps {
  projectId: string;
  files: FileContent[];
  instructions: string;
}

const ProjectViewer: React.FC<ProjectViewerProps> = ({ projectId, files, instructions }) => {
  const [selectedFile, setSelectedFile] = useState<FileContent | null>(files[0] || null);
  const [expandedFolders, setExpandedFolders] = useState<Set<string>>(new Set());
  const [copiedContent, setCopiedContent] = useState<string | null>(null);

  const handleDownload = async () => {
    try {
      const { apiService } = await import('../services/api');
      const response = await apiService.downloadProject(projectId);
      
      // Create download link
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
      console.error('Download failed:', error);
    }
  };

  const copyToClipboard = async (content: string) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopiedContent(content);
      setTimeout(() => setCopiedContent(null), 2000);
    } catch (error) {
      console.error('Copy failed:', error);
    }
  };

  // Build file tree structure
  const buildFileTree = () => {
    const tree: any = {};
    
    files.forEach(file => {
      const parts = file.name.split('/');
      let current = tree;
      
      for (let i = 0; i < parts.length - 1; i++) {
        const part = parts[i];
        if (!current[part]) {
          current[part] = { _type: 'folder', _children: {} };
        }
        current = current[part]._children;
      }
      
      const fileName = parts[parts.length - 1];
      current[fileName] = { _type: 'file', _data: file };
    });
    
    return tree;
  };

  const toggleFolder = (path: string) => {
    const newExpanded = new Set(expandedFolders);
    if (newExpanded.has(path)) {
      newExpanded.delete(path);
    } else {
      newExpanded.add(path);
    }
    setExpandedFolders(newExpanded);
  };

  const renderFileTree = (node: any, path: string = '', level: number = 0) => {
    return Object.entries(node).map(([name, item]: [string, any]) => {
      const currentPath = path ? `${path}/${name}` : name;
      const isExpanded = expandedFolders.has(currentPath);
      
      if (item._type === 'folder') {
        return (
          <div key={currentPath}>
            <div
              className={`flex items-center space-x-2 py-1 px-2 hover:bg-gray-100 cursor-pointer ${level > 0 ? `ml-${level * 4}` : ''}`}
              onClick={() => toggleFolder(currentPath)}
            >
              {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
              <Folder size={16} className="text-blue-600" />
              <span className="text-sm">{name}</span>
            </div>
            {isExpanded && (
              <div>
                {renderFileTree(item._children, currentPath, level + 1)}
              </div>
            )}
          </div>
        );
      } else {
        return (
          <div
            key={currentPath}
            className={`flex items-center space-x-2 py-1 px-2 hover:bg-gray-100 cursor-pointer ${
              selectedFile?.name === item._data.name ? 'bg-blue-50 border-r-2 border-blue-500' : ''
            } ${level > 0 ? `ml-${(level + 1) * 4}` : 'ml-4'}`}
            onClick={() => setSelectedFile(item._data)}
          >
            <File size={16} className="text-gray-600" />
            <span className="text-sm">{name}</span>
          </div>
        );
      }
    });
  };

  const fileTree = buildFileTree();

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">Step 3: Review & Download</h2>
        <button
          onClick={handleDownload}
          className="bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 flex items-center space-x-2"
        >
          <Download size={18} />
          <span>Download ZIP</span>
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* File Tree */}
        <div className="lg:col-span-1">
          <h3 className="font-medium mb-2">Project Structure</h3>
          <div className="border rounded-md p-2 max-h-96 overflow-y-auto bg-gray-50">
            {renderFileTree(fileTree)}
          </div>
        </div>

        {/* File Content */}
        <div className="lg:col-span-2">
          {selectedFile ? (
            <div>
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-medium">{selectedFile.name}</h3>
                <button
                  onClick={() => copyToClipboard(selectedFile.content)}
                  className="flex items-center space-x-1 text-sm text-gray-600 hover:text-gray-800"
                >
                  {copiedContent === selectedFile.content ? (
                    <CheckCircle size={16} className="text-green-600" />
                  ) : (
                    <Copy size={16} />
                  )}
                  <span>{copiedContent === selectedFile.content ? 'Copied!' : 'Copy'}</span>
                </button>
              </div>
              <pre className="bg-gray-100 p-4 rounded-md text-sm overflow-x-auto max-h-96 overflow-y-auto border">
                <code>{selectedFile.content}</code>
              </pre>
            </div>
          ) : (
            <div className="text-center text-gray-500 py-8">
              Select a file to view its content
            </div>
          )}
        </div>
      </div>

      {/* Instructions */}
      <div className="mt-6">
        <h3 className="font-medium mb-2">Setup Instructions</h3>
        <div className="bg-blue-50 p-4 rounded-md">
          <pre className="whitespace-pre-wrap text-sm">{instructions}</pre>
        </div>
      </div>
    </div>
  );
};

export default ProjectViewer;