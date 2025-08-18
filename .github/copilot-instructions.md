# DocuGen AI - GitHub Copilot Instructions

**Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

DocuGen AI is a documentation-aware project scaffolding engine with a Python FastAPI backend and React TypeScript frontend that generates complete, runnable projects from natural language prompts.

## Working Effectively

### Initial Setup - CRITICAL DEPENDENCY INSTALLATION REQUIREMENTS
- **Python 3.8+ is REQUIRED** - The setup script will fail if not met
- **Node.js 16+ is REQUIRED** - The setup script will fail if not met
- **NETWORK CONNECTIVITY ISSUES**: PyPI dependency installation frequently times out due to network limitations
- **TIMEOUT EXPECTATION**: Python dependency installation can take 10-15+ minutes. NEVER CANCEL. Set timeout to 30+ minutes.
- **Frontend NPM Install**: Takes approximately 5-6 minutes. NEVER CANCEL. Set timeout to 15+ minutes.

### Bootstrap and Build Process
Run these commands in sequence. DO NOT skip the setup script:

```bash
# 1. Initial setup (handles all dependencies)
chmod +x setup.sh
./setup.sh   # Takes 5-15 minutes. NEVER CANCEL. Set timeout to 30+ minutes.

# 2. Configure environment (REQUIRED)
cp .env.example .env
# Edit .env file and add OpenAI API key for full functionality (optional for demo mode)

# 3. Build frontend 
cd frontend
npm run build   # Takes 10-15 seconds
cd ..
```

### Development Mode (Recommended for Coding)
```bash
# Start backend and frontend in separate processes (requires 2 terminals)
./run-dev.sh   # Starts both services automatically
# Backend: http://localhost:8000
# Frontend: http://localhost:3000
```

### Production Mode
```bash
# Builds frontend and serves everything from backend
./run-prod.sh   # Takes 15-20 seconds total
# Application: http://localhost:8000
```

### Timing Expectations - NEVER CANCEL THESE OPERATIONS
- **Initial setup.sh**: 5-15 minutes (network dependent) - Set timeout to 30+ minutes
- **npm install**: 5-6 minutes - Set timeout to 15+ minutes  
- **Frontend build**: 10-15 seconds - Set timeout to 2+ minutes
- **Backend startup**: 2-3 seconds - Instant
- **Full production build**: 15-20 seconds total - Set timeout to 2+ minutes

## Validation and Testing

### Manual Validation Requirements
After making any changes, ALWAYS:

1. **Build and run the application**:
   ```bash
   ./run-dev.sh   # or ./run-prod.sh
   ```

2. **Test core API endpoints**:
   ```bash
   # Health check
   curl http://localhost:8000/api/health
   
   # Process documentation (simplified mode works without OpenAI key)
   curl -X POST "http://localhost:8000/api/process-documentation?url=https://docs.spring.io/"
   
   # Generate project
   curl -X POST "http://localhost:8000/api/generate-project" \
     -H "Content-Type: application/json" \
     -d '{"doc_id": "test_doc", "prompt": "Create a simple web app", "technology": "react"}'
   ```

3. **Frontend validation**:
   - Open http://localhost:3000 (dev) or http://localhost:8000 (prod)
   - Verify UI loads without console errors
   - Test documentation upload functionality
   - Test project generation workflow

### Known Working Configurations
- **Simplified Mode**: Works without OpenAI API key, provides demo functionality
- **Full Mode**: Requires OpenAI API key in .env file for AI-powered generation
- **Fallback Support**: Application automatically detects missing dependencies and uses simplified versions

### Network Issues and Troubleshooting
- **PyPI Timeouts**: Common during pip install. Retry with longer timeout (30+ minutes)
- **Dependency Installation**: Use `pip install --timeout 1000` if standard install fails
- **Alternative**: Use existing system packages if pip consistently fails
- **Frontend Issues**: Ensure tsconfig.json exists (created automatically by build process)

## Code Organization and Key Files

### Backend Structure
```
backend/
├── core/
│   ├── document_processor.py      # Full AI processing (requires dependencies)
│   ├── document_processor_simple.py  # Fallback mode (minimal deps)
│   ├── code_generator.py          # Full AI generation (requires OpenAI)
│   └── code_generator_simple.py   # Fallback mode (demo generation)
├── models/
│   └── schemas.py                 # Pydantic data models
main.py                            # FastAPI application entry point
```

### Frontend Structure  
```
frontend/
├── src/
│   ├── components/                # React components
│   │   ├── DocumentUpload.tsx     # File upload interface
│   │   ├── ProjectGenerator.tsx   # Generation interface
│   │   └── ProjectViewer.tsx      # Generated project viewer
│   ├── services/
│   │   └── api.ts                 # API communication layer
│   ├── types/                     # TypeScript type definitions
│   └── App.tsx                    # Main application component
├── package.json                   # Dependencies and scripts
└── tsconfig.json                  # TypeScript configuration (auto-created)
```

### Critical Build Scripts
- **setup.sh**: Complete environment setup (Python + Node.js dependencies)
- **run-dev.sh**: Development mode (separate frontend/backend)  
- **run-prod.sh**: Production mode (integrated serving)

## Development Workflow

### Making Changes
1. **Always run setup first** if working in fresh environment
2. **Use development mode** for active coding: `./run-dev.sh`
3. **Test changes immediately** using the validation steps above
4. **Frontend changes**: Auto-reload in development mode
5. **Backend changes**: Restart `./run-dev.sh` to see changes

### Adding New Features
1. **Backend API**: Add endpoints in `main.py`, implement logic in `backend/core/`
2. **Frontend UI**: Add components in `src/components/`, update `App.tsx`
3. **Data Models**: Update `backend/models/schemas.py` for API contracts
4. **Always add fallback support** in simplified mode files when adding dependencies

### Common Commands Reference
```bash
# Quick health check
curl http://localhost:8000/api/health

# Frontend build only
cd frontend && npm run build && cd ..

# Check running processes
ps aux | grep -E "(python|node|npm)"

# Clean restart
pkill -f "python|node" && ./run-dev.sh
```

## Technology Stack and Dependencies

### Backend (Python)
- **FastAPI**: Web framework and API
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation and serialization
- **ChromaDB**: Vector database (optional, fallback available)
- **LangChain**: Document processing (optional, fallback available)
- **OpenAI API**: AI generation (optional, fallback available)

### Frontend (React)
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Axios**: HTTP client
- **React Scripts**: Build tooling

### API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Service health check |
| `/api/process-documentation` | POST | Process documentation from URL |
| `/api/upload-documentation` | POST | Upload and process documentation file |
| `/api/generate-project` | POST | Generate project from prompt |
| `/api/download-project/{id}` | GET | Download project as ZIP |

## Special Considerations

### Dependency Management
- **Fallback Architecture**: Application works with or without heavy AI dependencies
- **Simplified Mode**: Provides demo functionality when full dependencies unavailable
- **Network Resilience**: Handles PyPI timeout issues gracefully

### Environment Configuration
- **.env file**: Required for configuration, created from .env.example
- **OpenAI API Key**: Optional for simplified mode, required for full AI features
- **Port Configuration**: Default backend=8000, frontend=3000

### CI/CD Considerations
- **No automated tests**: Repository does not include test framework
- **No linting configuration**: No ESLint, Prettier, or Python linting configured
- **Manual validation required**: Always test functionality manually after changes

## Supported Technologies for Generation
- **Spring Boot**: Java/Maven applications with REST APIs
- **React**: TypeScript applications with modern tooling  
- **Django**: Python web frameworks
- **Flask**: Python web APIs with proper structure
- **Express.js**: Node.js applications
- **Next.js**: Full-stack React applications

Generated projects include complete file structures, build configurations, starter code, README files, and setup instructions.