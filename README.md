# DocuGen AI

**Documentation-aware project scaffolding engine**

DocuGen AI is an intelligent development assistant that accelerates project setup and boilerplate code generation. It processes official documentation for any technology and uses AI to generate accurate, runnable, and best-practice-compliant starter projects based on natural language prompts.

## 🚀 Features

- **Smart Documentation Analysis**: Advanced AI processes and understands documentation to extract patterns and best practices
- **Natural Language Prompting**: Describe your project in plain English and get complete code structures
- **Multi-Technology Support**: Works with Spring Boot, React, Django, Flask, Express.js, Next.js, and more
- **Complete Project Generation**: Generates entire project structures with dependencies, configurations, and setup instructions
- **RAG Pipeline**: Retrieval-Augmented Generation for context-aware code generation
- **File Management**: Download projects as ZIP files or browse individual files in the web interface

## 🏗️ Architecture

### Backend (Python + FastAPI)
- **FastAPI** for REST API endpoints
- **ChromaDB** for vector storage and semantic search
- **LangChain** for document processing and text splitting
- **OpenAI API** for code generation (configurable)
- **BeautifulSoup** for web scraping
- **PyPDF2** for PDF processing

### Frontend (React + TypeScript)
- **React 18** with TypeScript for type safety
- **Tailwind CSS** for styling
- **Axios** for API communication
- **Lucide React** for icons
- **File tree viewer** and **code syntax highlighting**

### Data Flow
1. **Document Ingestion**: Process documentation from URLs or uploaded files
2. **RAG Processing**: Split documents into chunks and generate embeddings
3. **Vector Storage**: Store embeddings in ChromaDB for semantic search
4. **Query Processing**: Retrieve relevant documentation context for user prompts
5. **AI Generation**: Use LLM with retrieved context to generate complete projects
6. **File Assembly**: Structure generated code into downloadable project packages

## 🚀 Quick Start

### Option 1: Docker (Recommended)

**Using Docker Compose:**
```bash
git clone https://github.com/thecoder8890/neuralnotes.io.git
cd neuralnotes.io
cp .env.example .env
# Edit .env and add your OpenAI API key (optional)
docker-compose up -d
```

**Using pre-built image:**
```bash
docker run -d \
  --name neuralnotes-io \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  -v neuralnotes_data:/app/data \
  thecoder8890/neuralnotes-io:latest
```

Access the application at http://localhost:8000

📖 **[Complete Docker Guide](DOCKER.md)**

### Option 2: Local Development

#### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key (optional, fallback generation available)

#### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/thecoder8890/neuralnotes.io.git
   cd neuralnotes.io
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

3. **Install backend dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

5. **Start the application**
   
   **Option A: Development mode (separate terminals)**
   ```bash
   # Terminal 1: Start backend
   python main.py
   
   # Terminal 2: Start frontend
   cd frontend && npm start
   ```
   
   **Option B: Production mode**
   ```bash
   # Build frontend
   cd frontend && npm run build && cd ..
   
   # Start backend (serves both API and frontend)
   python main.py
   ```

6. **Open your browser**
   - Development: http://localhost:3000 (frontend) + http://localhost:8000 (API)
   - Production: http://localhost:8000

## 📖 Usage

### 1. Add Documentation
- **From URL**: Enter a documentation URL (e.g., https://docs.spring.io/spring-boot/)
- **Upload File**: Upload PDF, Markdown, TXT, or HTML documentation files

### 2. Generate Project
- Select target technology/framework (optional)
- Describe your project in natural language
- Examples:
  - "Create a Spring Boot REST API with CRUD operations for a User entity"
  - "Build a React dashboard with user authentication and charts"
  - "Generate a Flask web app with SQLAlchemy and basic routes"

### 3. Review & Download
- Browse generated files in the web interface
- Copy individual file contents
- Download complete project as ZIP file
- Follow provided setup instructions

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key for AI generation | Required for full functionality |
| `DEBUG` | Enable debug mode | `false` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `CHROMA_DB_PATH` | ChromaDB storage path | `./data/chroma_db` |

### Supported Technologies

- **Spring Boot** (Java/Maven projects)
- **React** (TypeScript/JavaScript SPAs)
- **Django** (Python web frameworks)
- **Flask** (Python microservices)
- **Express.js** (Node.js APIs)
- **Next.js** (Full-stack React applications)

## 🧪 Examples

### Spring Boot REST API
```
Documentation: https://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/
Prompt: "Create a Spring Boot web application using Maven with Java 17. Include Spring Web for a REST controller and Spring Data JPA with PostgreSQL driver. Add a basic 'Hello World' REST endpoint at /api/greeting."
```

### React Dashboard
```
Documentation: https://react.dev/learn
Prompt: "Build a React TypeScript application with a dashboard layout, user authentication, and data visualization charts using modern React patterns."
```

### Flask API
```
Documentation: https://flask.palletsprojects.com/
Prompt: "Create a Flask REST API with SQLAlchemy ORM, JWT authentication, and CRUD operations for a blog system with users and posts."
```

## 🏗️ Development

### Project Structure
```
neuralnotes.io/
├── backend/
│   ├── core/
│   │   ├── document_processor.py  # Documentation processing
│   │   └── code_generator.py      # AI code generation
│   ├── models/
│   │   └── schemas.py             # Pydantic models
│   └── utils/                     # Utility functions
├── frontend/
│   ├── src/
│   │   ├── components/            # React components
│   │   ├── services/              # API services
│   │   └── types/                 # TypeScript types
│   └── public/                    # Static assets
├── data/                          # ChromaDB storage
├── main.py                        # FastAPI application
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/process-documentation` | POST | Process documentation from URL |
| `/api/upload-documentation` | POST | Upload and process documentation file |
| `/api/generate-project` | POST | Generate project from prompt |
| `/api/download-project/{id}` | GET | Download project as ZIP |

### Running Tests
```bash
# Backend tests
python -m pytest

# Frontend tests
cd frontend && npm test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests for new functionality
5. Run tests and ensure they pass
6. Commit your changes: `git commit -am 'Add feature'`
7. Push to the branch: `git push origin feature-name`
8. Submit a pull request

## 📋 Roadmap

### Phase 1: MVP ✅
- [x] Documentation ingestion from URLs and files
- [x] RAG pipeline with vector embeddings
- [x] Natural language prompting interface
- [x] Core code generation with OpenAI
- [x] Structured file output and download

### Phase 2: Core Features (In Progress)
- [ ] Multi-file project generation with complex structures
- [ ] Enhanced caching for processed documentation
- [ ] Support for additional file formats and technologies
- [ ] Improved error handling and validation
- [ ] Basic project templates and examples

### Phase 3: Advanced Features (Planned)
- [ ] Interactive UI with live file editing
- [ ] Conversational refinement ("add authentication to this project")
- [ ] User accounts and project history
- [ ] Feedback system and quality improvements
- [ ] Advanced prompt engineering and context optimization

## 🚀 Deployment

### Docker Hub

Pre-built Docker images are available on Docker Hub:
- **Latest stable**: `thecoder8890/neuralnotes-io:latest`
- **Version tags**: `thecoder8890/neuralnotes-io:v1.0.0`

### Cloud Deployment

#### Heroku
```bash
# Using Heroku Container Registry
heroku container:push web --app your-app-name
heroku container:release web --app your-app-name
```

#### AWS ECS / Azure Container Instances / Google Cloud Run
See [DOCKER.md](DOCKER.md) for complete cloud deployment guides.

#### Kubernetes
```bash
kubectl apply -f k8s/deployment.yaml
```

### Environment Setup

**Required for full functionality:**
- `OPENAI_API_KEY`: Your OpenAI API key

**Optional configuration:**
- `DEBUG=false`: Production mode
- `HOST=0.0.0.0`: Listen on all interfaces
- `PORT=8000`: Application port

📖 **[Complete Deployment Guide](DOCKER.md)**

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- Create an issue for bug reports or feature requests
- Check existing issues before creating new ones
- Provide detailed information including error messages and steps to reproduce

## 🏆 Acknowledgments

- OpenAI for GPT models and embeddings
- LangChain for document processing capabilities
- ChromaDB for vector storage
- The open-source community for amazing tools and libraries