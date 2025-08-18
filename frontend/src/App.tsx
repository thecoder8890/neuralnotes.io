import React, { useState } from 'react';
import DocumentUpload from './components/DocumentUpload';
import ProjectGenerator from './components/ProjectGenerator';
import ProjectViewer from './components/ProjectViewer';
import { FileContent } from './types';
import { Brain, Zap, Code } from 'lucide-react';

function App() {
  const [docId, setDocId] = useState<string | null>(null);
  const [projectId, setProjectId] = useState<string | null>(null);
  const [projectFiles, setProjectFiles] = useState<FileContent[]>([]);
  const [instructions, setInstructions] = useState<string>('');

  const handleDocumentProcessed = (newDocId: string) => {
    setDocId(newDocId);
    // Reset project state when new document is processed
    setProjectId(null);
    setProjectFiles([]);
    setInstructions('');
  };

  const handleProjectGenerated = (newProjectId: string, files: FileContent[], newInstructions: string) => {
    setProjectId(newProjectId);
    setProjectFiles(files);
    setInstructions(newInstructions);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-600 rounded-lg">
              <Brain className="text-white" size={24} />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">DocuGen AI</h1>
              <p className="text-gray-600">Documentation-aware project scaffolding engine</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">
            Generate Projects from Documentation
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Upload documentation or provide a URL, describe your project in natural language, 
            and get a complete, runnable codebase generated instantly.
          </p>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          <div className="text-center">
            <div className="p-3 bg-blue-100 rounded-full w-fit mx-auto mb-4">
              <Brain className="text-blue-600" size={32} />
            </div>
            <h3 className="text-lg font-semibold mb-2">Smart Documentation Analysis</h3>
            <p className="text-gray-600">
              Advanced AI processes and understands your documentation to extract relevant patterns and best practices.
            </p>
          </div>
          <div className="text-center">
            <div className="p-3 bg-green-100 rounded-full w-fit mx-auto mb-4">
              <Zap className="text-green-600" size={32} />
            </div>
            <h3 className="text-lg font-semibold mb-2">Instant Generation</h3>
            <p className="text-gray-600">
              Describe your project in plain English and get a complete, structured codebase in seconds.
            </p>
          </div>
          <div className="text-center">
            <div className="p-3 bg-purple-100 rounded-full w-fit mx-auto mb-4">
              <Code className="text-purple-600" size={32} />
            </div>
            <h3 className="text-lg font-semibold mb-2">Production Ready</h3>
            <p className="text-gray-600">
              Generated projects follow best practices with proper structure, dependencies, and setup instructions.
            </p>
          </div>
        </div>

        {/* Main Workflow */}
        <div className="space-y-8">
          {/* Step 1: Document Upload */}
          <DocumentUpload 
            onDocumentProcessed={handleDocumentProcessed}
            isProcessing={false}
          />

          {/* Step 2: Project Generation */}
          <ProjectGenerator 
            docId={docId}
            onProjectGenerated={handleProjectGenerated}
          />

          {/* Step 3: Project Viewer */}
          {projectId && projectFiles.length > 0 && (
            <ProjectViewer 
              projectId={projectId}
              files={projectFiles}
              instructions={instructions}
            />
          )}
        </div>

        {/* Examples Section */}
        <div className="mt-16">
          <h3 className="text-2xl font-bold text-center mb-8">Example Use Cases</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h4 className="font-semibold mb-2">Spring Boot REST API</h4>
              <p className="text-gray-600 text-sm mb-3">
                "Create a Spring Boot web application with CRUD operations for a User entity using JPA and PostgreSQL"
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">Java</span>
                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">Spring Boot</span>
                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded">JPA</span>
              </div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h4 className="font-semibold mb-2">React Dashboard</h4>
              <p className="text-gray-600 text-sm mb-3">
                "Build a React dashboard with user authentication, charts, and a responsive design using Material-UI"
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">React</span>
                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">TypeScript</span>
                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">Material-UI</span>
              </div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h4 className="font-semibold mb-2">Flask API Server</h4>
              <p className="text-gray-600 text-sm mb-3">
                "Create a Flask REST API with SQLAlchemy, JWT authentication, and API documentation"
              </p>
              <div className="flex flex-wrap gap-2">
                <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded">Python</span>
                <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded">Flask</span>
                <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded">SQLAlchemy</span>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-600">
            <p>&copy; 2024 DocuGen AI. Powered by advanced AI and documentation understanding.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;