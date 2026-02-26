import os
import hashlib
import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
try:
    from langchain_community.embeddings import OpenAIEmbeddings
except ImportError:
    from langchain.embeddings import OpenAIEmbeddings
import chromadb
from chromadb.config import Settings
import markdown
import pypdf
import io

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.chroma_client = None
        self.embeddings = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize ChromaDB and OpenAI embeddings"""
        try:
            # Initialize ChromaDB
            db_path = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            
            self.chroma_client = chromadb.PersistentClient(path=db_path)
            
            # Initialize OpenAI embeddings if API key is available
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key:
                self.embeddings = OpenAIEmbeddings(openai_api_key=openai_api_key)
            else:
                logger.warning("OpenAI API key not found. Some features may not work.")
                
        except Exception as e:
            logger.error(f"Error initializing document processor: {str(e)}")
            raise
    
    async def process_url(self, url: str) -> str:
        """Process documentation from a URL"""
        try:
            # Generate document ID from URL
            doc_id = hashlib.md5(url.encode()).hexdigest()
            
            # Check if already processed
            if self._is_processed(doc_id):
                logger.info(f"Document {doc_id} already processed")
                return doc_id
            
            # Fetch content from URL
            logger.info(f"Fetching content from {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract text content
            text_content = self._extract_text_from_html(soup)
            
            # Process and store the content
            await self._process_and_store(doc_id, text_content, url=url)
            
            return doc_id
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            raise
    
    async def process_file(self, file_content: bytes, filename: str) -> str:
        """Process uploaded documentation file"""
        try:
            # Generate document ID from file content
            doc_id = hashlib.md5(file_content).hexdigest()
            
            # Check if already processed
            if self._is_processed(doc_id):
                logger.info(f"Document {doc_id} already processed")
                return doc_id
            
            # Extract text based on file type
            text_content = self._extract_text_from_file(file_content, filename)
            
            # Process and store the content
            await self._process_and_store(doc_id, text_content, filename=filename)
            
            return doc_id
            
        except Exception as e:
            logger.error(f"Error processing file {filename}: {str(e)}")
            raise
    
    def _extract_text_from_html(self, soup: BeautifulSoup) -> str:
        """Extract clean text from HTML soup"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _extract_text_from_file(self, file_content: bytes, filename: str) -> str:
        """Extract text from uploaded file based on file type"""
        file_extension = filename.lower().split('.')[-1]
        
        if file_extension == 'pdf':
            return self._extract_text_from_pdf(file_content)
        elif file_extension in ['md', 'markdown']:
            return self._extract_text_from_markdown(file_content)
        elif file_extension in ['txt', 'html']:
            return file_content.decode('utf-8')
        else:
            # Try to decode as text
            try:
                return file_content.decode('utf-8')
            except UnicodeDecodeError:
                raise ValueError(f"Unsupported file type: {file_extension}")
    
    def _extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF content"""
        try:
            pdf_file = io.BytesIO(file_content)
            pdf_reader = pypdf.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise
    
    def _extract_text_from_markdown(self, file_content: bytes) -> str:
        """Extract text from Markdown content"""
        try:
            md_content = file_content.decode('utf-8')
            html = markdown.markdown(md_content)
            soup = BeautifulSoup(html, 'html.parser')
            return soup.get_text()
        except Exception as e:
            logger.error(f"Error extracting text from Markdown: {str(e)}")
            raise
    
    async def _process_and_store(self, doc_id: str, text_content: str, url: Optional[str] = None, filename: Optional[str] = None):
        """Process text content and store in vector database"""
        try:
            # Split text into chunks
            chunks = self.text_splitter.split_text(text_content)
            logger.info(f"Split document into {len(chunks)} chunks")
            
            # Create or get collection
            collection = self.chroma_client.get_or_create_collection(
                name=f"doc_{doc_id}",
                metadata={"doc_id": doc_id, "url": url, "filename": filename, "processed_at": datetime.now().isoformat()}
            )
            
            # Generate embeddings and store chunks
            if self.embeddings:
                for i, chunk in enumerate(chunks):
                    # Generate embedding
                    embedding = await asyncio.get_event_loop().run_in_executor(
                        None, self.embeddings.embed_query, chunk
                    )
                    
                    # Store in ChromaDB
                    collection.add(
                        embeddings=[embedding],
                        documents=[chunk],
                        ids=[f"{doc_id}_{i}"],
                        metadatas=[{"chunk_index": i, "doc_id": doc_id}]
                    )
            else:
                # Store without embeddings (for fallback)
                for i, chunk in enumerate(chunks):
                    collection.add(
                        documents=[chunk],
                        ids=[f"{doc_id}_{i}"],
                        metadatas=[{"chunk_index": i, "doc_id": doc_id}]
                    )
            
            logger.info(f"Stored {len(chunks)} chunks for document {doc_id}")
            
        except Exception as e:
            logger.error(f"Error processing and storing document: {str(e)}")
            raise
    
    def _is_processed(self, doc_id: str) -> bool:
        """Check if document is already processed"""
        try:
            collection_name = f"doc_{doc_id}"
            collections = self.chroma_client.list_collections()
            return any(col.name == collection_name for col in collections)
        except Exception:
            return False
    
    async def query_documents(self, doc_id: str, query: str, n_results: int = 5) -> List[str]:
        """Query processed documents for relevant chunks"""
        try:
            collection = self.chroma_client.get_collection(f"doc_{doc_id}")
            
            if self.embeddings:
                # Generate query embedding
                query_embedding = await asyncio.get_event_loop().run_in_executor(
                    None, self.embeddings.embed_query, query
                )
                
                # Search with embedding
                results = collection.query(
                    query_embeddings=[query_embedding],
                    n_results=n_results
                )
            else:
                # Fallback to text search
                results = collection.query(
                    query_texts=[query],
                    n_results=n_results
                )
            
            return results['documents'][0] if results['documents'] else []
            
        except Exception as e:
            logger.error(f"Error querying documents: {str(e)}")
            return []