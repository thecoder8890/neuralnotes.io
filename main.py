from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import os
import sys
import logging
from typing import Optional, List
import io
import zipfile

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Try to import core modules, provide fallback if dependencies are missing
try:
    from backend.core.document_processor import DocumentProcessor
    from backend.core.code_generator import CodeGenerator
    from backend.models.schemas import GenerationRequest, GenerationResponse
    CORE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some dependencies are missing: {e}")
    print("Using simplified mode for demonstration.")
    try:
        from backend.core.document_processor_simple import DocumentProcessor
        from backend.core.code_generator_simple import CodeGenerator
        from backend.models.schemas import GenerationRequest, GenerationResponse
        CORE_AVAILABLE = True
    except ImportError as e2:
        print(f"Error: Cannot load simplified modules: {e2}")
        CORE_AVAILABLE = False
        
        # Minimal fallback schemas
        from pydantic import BaseModel
        
        class GenerationRequest(BaseModel):
            doc_id: str
            prompt: str
            technology: Optional[str] = None
        
        class GenerationResponse(BaseModel):
            project_id: str
            files: List[dict]
            structure: dict
            instructions: str

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="DocuGen AI", description="Documentation-aware project scaffolding engine")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core components
if CORE_AVAILABLE:
    document_processor = DocumentProcessor()
    code_generator = CodeGenerator()
else:
    document_processor = None
    code_generator = None

@app.get("/")
async def root():
    return {"message": "DocuGen AI - Documentation-aware project scaffolding engine"}

@app.post("/api/process-documentation")
async def process_documentation(url: str):
    """Process documentation from a URL"""
    try:
        result = await document_processor.process_url(url)
        return {"status": "success", "message": "Documentation processed successfully", "doc_id": result}
    except Exception as e:
        logger.error(f"Error processing documentation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload-documentation")
async def upload_documentation(file: UploadFile = File(...)):
    """Upload and process documentation file"""
    try:
        content = await file.read()
        result = await document_processor.process_file(content, file.filename)
        return {"status": "success", "message": "Documentation uploaded and processed", "doc_id": result}
    except Exception as e:
        logger.error(f"Error uploading documentation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-project", response_model=GenerationResponse)
async def generate_project(request: GenerationRequest):
    """Generate project based on documentation and user prompt"""
    try:
        result = await code_generator.generate_project(
            doc_id=request.doc_id,
            prompt=request.prompt,
            technology=request.technology
        )
        return result
    except Exception as e:
        logger.error(f"Error generating project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/download-project/{project_id}")
async def download_project(project_id: str):
    """Download generated project as ZIP file"""
    try:
        zip_data = await code_generator.get_project_zip(project_id)
        
        return StreamingResponse(
            io.BytesIO(zip_data),
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename=project_{project_id}.zip"}
        )
    except Exception as e:
        logger.error(f"Error downloading project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "DocuGen AI"}

# Serve static files (React frontend)
if os.path.exists("frontend/build"):
    app.mount("/static", StaticFiles(directory="frontend/build/static"), name="static")
    
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        """Serve React app for all non-API routes"""
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")
        
        index_file = "frontend/build/index.html"
        if os.path.exists(index_file):
            return FileResponse(index_file)
        else:
            return {"message": "Frontend not built yet. Run 'npm run build' in the frontend directory."}

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )