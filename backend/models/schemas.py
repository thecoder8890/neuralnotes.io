from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum

class Technology(str, Enum):
    SPRING_BOOT = "spring_boot"
    DJANGO = "django"
    REACT = "react"
    EXPRESS = "express"
    FLASK = "flask"
    NEXTJS = "nextjs"

class GenerationRequest(BaseModel):
    doc_id: str = Field(..., description="ID of processed documentation")
    prompt: str = Field(..., description="User's natural language prompt for project generation")
    technology: Optional[Technology] = Field(None, description="Target technology/framework")
    
class FileContent(BaseModel):
    name: str = Field(..., description="File name with path")
    content: str = Field(..., description="File content")
    type: str = Field(default="text", description="File type (text, binary, etc.)")

class GenerationResponse(BaseModel):
    project_id: str = Field(..., description="Unique identifier for the generated project")
    files: List[FileContent] = Field(..., description="List of generated files")
    structure: Dict[str, Any] = Field(..., description="Project structure tree")
    instructions: str = Field(..., description="Setup and run instructions")
    
class DocumentInfo(BaseModel):
    doc_id: str
    url: Optional[str] = None
    filename: Optional[str] = None
    processed_at: str
    status: str