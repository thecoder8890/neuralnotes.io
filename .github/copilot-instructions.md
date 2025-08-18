# DocuGen AI - GitHub Copilot Instructions

DocuGen AI is a documentation-aware project scaffolding engine that processes official documentation and uses AI to generate accurate, runnable project code. It consists of a Python FastAPI backend with ChromaDB vector storage and a React TypeScript frontend.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

- **Bootstrap, build, and test the repository:**
  - Ensure Python 3.8+ and Node.js 16+ are installed
  - `./setup.sh` -- takes 5-6 minutes to complete. NEVER CANCEL. Set timeout to 10+ minutes.
    - Creates Python virtual environment
    - Installs Python dependencies from requirements.txt
    - Installs Node.js dependencies in frontend/
    - Creates .env file from .env.example
    - Creates data/ directory
    - NOTE: May fail due to PyPI connectivity issues - document any failures
  - Frontend build: `cd frontend && npm run build` -- takes 30 seconds. Set timeout to 2+ minutes.
  - Frontend tests: `cd frontend && npm test -- --watchAll=false --passWithNoTests` -- takes 10 seconds. Set timeout to 1+ minute.

- **Run the application:**
  - ALWAYS run the setup script first: `./setup.sh`
  - Development mode: `./run-dev.sh` -- starts both frontend (port 3000) and backend (port 8000) servers
    - Frontend: http://localhost:3000
    - Backend API: http://localhost:8000
    - API Docs: http://localhost:8000/docs
    - Takes ~15 seconds to start both servers
  - Production mode: `./run-prod.sh` -- builds frontend and serves from backend (port 8000)
    - Frontend build: ~30 seconds
    - Application: http://localhost:8000
    - API Docs: http://localhost:8000/docs

## Environment Setup

- **Required dependencies:**
  - Python 3.8+ with virtual environment
  - Node.js 16+ with npm
  - OpenAI API key (optional - fallback mode available)

- **Configuration:**
  - Copy `.env.example` to `.env` and configure OpenAI API key
  - Edit OPENAI_API_KEY in .env file for full functionality
  - Application works in demo mode without API key using simplified processors

- **Common setup issues:**
  - If `pip install` fails due to network timeouts, the backend has fallback simplified modules
  - Frontend requires tsconfig.json - create one if missing using standard React TypeScript config
  - Remove unused imports to fix ESLint errors during build

## Validation

- **ALWAYS manually validate changes by running through complete user scenarios:**
  1. Start the application in development mode
  2. Test document upload functionality (upload a file or provide URL)
  3. Test project generation with a simple prompt
  4. Test project download functionality
  5. Verify the generated files are correct and runnable

- **Build validation steps:**
  - Frontend: `cd frontend && npm run build` - must complete without errors
  - Frontend tests: `cd frontend && npm test -- --watchAll=false --passWithNoTests`
  - Backend: Starts successfully with `python main.py` (requires dependencies or uses simplified mode)

- **You can build and run both frontend and backend, and should test actual functionality through the web interface.**

- **NEVER CANCEL long-running builds or installs** - setup may take 5-6 minutes, be patient.

## Common Tasks

### Repository Structure
```
/
├── backend/           # Python FastAPI backend
│   ├── core/          # Core processing modules
│   │   ├── document_processor.py      # Full ChromaDB/LangChain processor  
│   │   ├── document_processor_simple.py # Fallback processor
│   │   ├── code_generator.py          # Full OpenAI generator
│   │   └── code_generator_simple.py   # Fallback generator
│   └── models/        # Pydantic schemas
├── frontend/          # React TypeScript frontend
│   ├── src/
│   │   ├── components/ # React components
│   │   ├── services/   # API service layer
│   │   └── types/      # TypeScript type definitions
│   ├── package.json
│   └── tsconfig.json   # TypeScript configuration (create if missing)
├── main.py            # FastAPI server entry point
├── requirements.txt   # Python dependencies
├── setup.sh          # Setup script (5-6 min runtime)
├── run-dev.sh        # Development mode runner
├── run-prod.sh       # Production mode runner
└── .env.example      # Environment template
```

### Key Technologies
- **Backend:** Python 3.8+, FastAPI, ChromaDB, LangChain, OpenAI API, BeautifulSoup, PyPDF2
- **Frontend:** React 18, TypeScript, Tailwind CSS, Axios, Lucide React
- **Build:** npm (frontend), pip (backend), bash scripts

### API Endpoints
- `GET /api/health` - Health check
- `POST /api/process-documentation` - Process documentation from URL  
- `POST /api/upload-documentation` - Upload and process documentation file
- `POST /api/generate-project` - Generate project from prompt
- `GET /api/download-project/{id}` - Download project as ZIP

### Expected Timing (set timeouts accordingly)
- Setup script: 5-6 minutes (may timeout due to network issues - normal)
- Frontend build: 30 seconds
- Frontend dev server start: 10 seconds  
- Backend startup: 5 seconds (with dependencies) or immediate (simplified mode)
- Project generation: 10-30 seconds (depends on complexity and API)

### File Locations
- **Configuration:** `.env` file in root (copy from `.env.example`)
- **Frontend components:** `frontend/src/components/`
- **Backend API:** `main.py` and `backend/` directory
- **Build output:** `frontend/build/` (production frontend build)
- **Data storage:** `data/` directory (created by setup)

### Common Debugging Steps
1. Check Python virtual environment is activated: `source venv/bin/activate`
2. Verify .env file exists and has required configuration
3. For frontend build issues, ensure tsconfig.json exists in frontend/
4. For import errors, check if dependencies installed correctly
5. Backend falls back to simplified mode if full dependencies unavailable
6. Check browser console and network tab for frontend issues

### Development Workflow
1. Make changes to backend code in `backend/` or `main.py`
2. Make changes to frontend code in `frontend/src/`
3. Run development mode: `./run-dev.sh` to test changes
4. Build frontend: `cd frontend && npm run build` to validate
5. Test complete user workflow through the web interface
6. For production deployment, use `./run-prod.sh`

## Fallback Behavior
- **When Python dependencies fail to install:** Backend uses simplified processors that work without ChromaDB/LangChain/OpenAI
- **When OpenAI API key missing:** Application generates basic project templates instead of AI-generated code
- **Simplified mode provides:** Basic project scaffolding for React, Spring Boot, and other frameworks without AI enhancement