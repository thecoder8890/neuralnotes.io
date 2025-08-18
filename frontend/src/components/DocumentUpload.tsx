import React, { useState } from 'react';
import { Upload, Link, AlertCircle, CheckCircle } from 'lucide-react';

interface DocumentUploadProps {
  onDocumentProcessed: (docId: string) => void;
  isProcessing: boolean;
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({ onDocumentProcessed, isProcessing }) => {
  const [url, setUrl] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const [uploadMethod, setUploadMethod] = useState<'url' | 'file'>('url');
  const [status, setStatus] = useState<'idle' | 'processing' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const handleUrlSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setStatus('processing');
    try {
      const { apiService } = await import('../services/api');
      const response = await apiService.processDocumentationUrl(url);
      setStatus('success');
      setMessage('Documentation processed successfully!');
      onDocumentProcessed(response.data.doc_id);
    } catch (error: any) {
      setStatus('error');
      setMessage(error.response?.data?.detail || 'Failed to process documentation URL');
    }
  };

  const handleFileUpload = async (file: File) => {
    setStatus('processing');
    try {
      const { apiService } = await import('../services/api');
      const response = await apiService.uploadDocumentation(file);
      setStatus('success');
      setMessage(`File "${file.name}" processed successfully!`);
      onDocumentProcessed(response.data.doc_id);
    } catch (error: any) {
      setStatus('error');
      setMessage(error.response?.data?.detail || 'Failed to process uploaded file');
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Step 1: Add Documentation</h2>
      
      <div className="mb-4">
        <div className="flex space-x-4 mb-4">
          <button
            onClick={() => setUploadMethod('url')}
            className={`px-4 py-2 rounded-md flex items-center space-x-2 ${
              uploadMethod === 'url'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            <Link size={18} />
            <span>From URL</span>
          </button>
          <button
            onClick={() => setUploadMethod('file')}
            className={`px-4 py-2 rounded-md flex items-center space-x-2 ${
              uploadMethod === 'file'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            <Upload size={18} />
            <span>Upload File</span>
          </button>
        </div>
      </div>

      {uploadMethod === 'url' ? (
        <form onSubmit={handleUrlSubmit} className="space-y-4">
          <div>
            <label htmlFor="doc-url" className="block text-sm font-medium text-gray-700 mb-2">
              Documentation URL
            </label>
            <input
              id="doc-url"
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://docs.example.com/"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isProcessing}
            />
          </div>
          <button
            type="submit"
            disabled={!url.trim() || isProcessing}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          >
            {isProcessing ? 'Processing...' : 'Process Documentation'}
          </button>
        </form>
      ) : (
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center ${
            dragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <Upload className="mx-auto mb-4 text-gray-400" size={48} />
          <p className="mb-4 text-gray-600">
            Drag and drop your documentation file here, or click to select
          </p>
          <input
            type="file"
            onChange={handleFileSelect}
            accept=".pdf,.md,.txt,.html"
            className="hidden"
            id="file-upload"
            disabled={isProcessing}
          />
          <label
            htmlFor="file-upload"
            className="inline-block bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 cursor-pointer disabled:bg-gray-400"
          >
            Select File
          </label>
          <p className="mt-2 text-sm text-gray-500">
            Supported formats: PDF, Markdown, TXT, HTML
          </p>
        </div>
      )}

      {status !== 'idle' && (
        <div className={`mt-4 p-3 rounded-md flex items-center space-x-2 ${
          status === 'success' ? 'bg-green-50 text-green-800' :
          status === 'error' ? 'bg-red-50 text-red-800' :
          'bg-blue-50 text-blue-800'
        }`}>
          {status === 'success' ? <CheckCircle size={18} /> :
           status === 'error' ? <AlertCircle size={18} /> :
           <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          }
          <span>{message}</span>
        </div>
      )}
    </div>
  );
};

export default DocumentUpload;