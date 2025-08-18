import React, { useState } from 'react';
import { Technology } from '../types';
import { Wand2, AlertCircle, CheckCircle } from 'lucide-react';

interface ProjectGeneratorProps {
  docId: string | null;
  onProjectGenerated: (projectId: string, files: any[], instructions: string) => void;
}

const ProjectGenerator: React.FC<ProjectGeneratorProps> = ({ docId, onProjectGenerated }) => {
  const [prompt, setPrompt] = useState('');
  const [technology, setTechnology] = useState<Technology | ''>('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [status, setStatus] = useState<'idle' | 'generating' | 'success' | 'error'>('idle');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!docId || !prompt.trim()) return;

    setIsGenerating(true);
    setStatus('generating');
    setMessage('Generating your project...');

    try {
      const { apiService } = await import('../services/api');
      const response = await apiService.generateProject({
        doc_id: docId,
        prompt: prompt.trim(),
        technology: technology || undefined,
      });

      setStatus('success');
      setMessage('Project generated successfully!');
      onProjectGenerated(response.data.project_id, response.data.files, response.data.instructions);
    } catch (error: any) {
      setStatus('error');
      setMessage(error.response?.data?.detail || 'Failed to generate project');
    } finally {
      setIsGenerating(false);
    }
  };

  const examplePrompts = [
    "Create a Spring Boot REST API with CRUD operations for a User entity",
    "Build a React dashboard with charts and user authentication",
    "Create a Flask web app with SQLAlchemy and basic routes",
    "Generate a Next.js blog with markdown support",
    "Build an Express.js API with JWT authentication",
  ];

  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold mb-4">Step 2: Generate Project</h2>
      
      {!docId ? (
        <div className="bg-yellow-50 border border-yellow-200 rounded-md p-4">
          <div className="flex items-center space-x-2">
            <AlertCircle className="text-yellow-600" size={18} />
            <span className="text-yellow-800">Please process documentation first</span>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="technology" className="block text-sm font-medium text-gray-700 mb-2">
              Technology/Framework (Optional)
            </label>
            <select
              id="technology"
              value={technology}
              onChange={(e) => setTechnology(e.target.value as Technology)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isGenerating}
            >
              <option value="">Auto-detect from prompt</option>
              <option value={Technology.SPRING_BOOT}>Spring Boot</option>
              <option value={Technology.DJANGO}>Django</option>
              <option value={Technology.REACT}>React</option>
              <option value={Technology.EXPRESS}>Express.js</option>
              <option value={Technology.FLASK}>Flask</option>
              <option value={Technology.NEXTJS}>Next.js</option>
            </select>
          </div>

          <div>
            <label htmlFor="prompt" className="block text-sm font-medium text-gray-700 mb-2">
              Project Description
            </label>
            <textarea
              id="prompt"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe the project you want to generate..."
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isGenerating}
            />
          </div>

          <div>
            <p className="text-sm text-gray-600 mb-2">Example prompts:</p>
            <div className="space-y-1">
              {examplePrompts.map((example, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => setPrompt(example)}
                  className="block text-left text-sm text-blue-600 hover:text-blue-800 hover:underline"
                  disabled={isGenerating}
                >
                  "{example}"
                </button>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={!prompt.trim() || isGenerating}
            className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
          >
            <Wand2 size={18} />
            <span>{isGenerating ? 'Generating...' : 'Generate Project'}</span>
          </button>
        </form>
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

export default ProjectGenerator;