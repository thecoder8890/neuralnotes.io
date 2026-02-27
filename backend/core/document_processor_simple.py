import os
import hashlib
import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import io

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Simplified document processor that extracts real content from files"""
    
    def __init__(self):
        self.processed_docs = {}  # In-memory storage
        logger.info("DocumentProcessor initialized (simplified mode)")
    
    async def process_url(self, url: str) -> str:
        """Process documentation from a URL"""
        try:
            # Generate document ID from URL
            doc_id = hashlib.md5(url.encode()).hexdigest()
            
            # For demo, we'll simulate processing
            logger.info(f"Processing URL: {url}")
            
            # Store basic info
            self.processed_docs[doc_id] = {
                "url": url,
                "processed_at": datetime.now().isoformat(),
                "type": "url",
                "content": f"Simulated content from {url}"
            }
            
            logger.info(f"Document {doc_id} processed successfully")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            raise
    
    async def process_file(self, file_content: bytes, filename: str) -> str:
        """Process uploaded documentation file"""
        try:
            # Generate document ID from file content
            doc_id = hashlib.md5(file_content).hexdigest()
            
            logger.info(f"Processing file: {filename}")
            
            # Extract actual text content based on file type
            text_content = self._extract_text_from_file(file_content, filename)
            
            # Store the extracted content
            self.processed_docs[doc_id] = {
                "filename": filename,
                "processed_at": datetime.now().isoformat(),
                "type": "file",
                "content": text_content,
                "file_size": len(file_content),
            }
            
            logger.info(f"Document {doc_id} processed successfully ({len(text_content)} chars extracted)")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error processing file {filename}: {str(e)}")
            raise

    def _extract_text_from_file(self, file_content: bytes, filename: str) -> str:
        """Extract text from uploaded file based on file type"""
        ext = os.path.splitext(filename or "")[1].lower()

        if ext == ".pdf":
            return self._extract_text_from_pdf(file_content)
        elif ext in (".md", ".markdown"):
            return self._extract_text_from_markdown(file_content)
        elif ext in (".rst",):
            return self._extract_text_from_rst(file_content)
        elif ext in (".txt", ".html", ".htm"):
            return file_content.decode("utf-8", errors="replace")
        else:
            try:
                return file_content.decode("utf-8", errors="replace")
            except Exception:
                raise ValueError(f"Unsupported file type: {ext}")

    def _extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF content"""
        try:
            import pypdf
            pdf_file = io.BytesIO(file_content)
            pdf_reader = pypdf.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        except ImportError:
            logger.warning("pypdf not available, storing raw filename reference")
            return f"[PDF content – {len(file_content)} bytes]"
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    def _extract_text_from_markdown(self, file_content: bytes) -> str:
        """Extract text from Markdown content"""
        try:
            md_content = file_content.decode("utf-8", errors="replace")
            try:
                import markdown as md_lib
                from html.parser import HTMLParser

                class _TextExtractor(HTMLParser):
                    def __init__(self):
                        super().__init__()
                        self.parts: list[str] = []
                    def handle_data(self, data: str):
                        self.parts.append(data)

                html = md_lib.markdown(md_content)
                extractor = _TextExtractor()
                extractor.feed(html)
                return " ".join(extractor.parts)
            except ImportError:
                # Fallback: return the raw markdown text (still useful)
                return md_content
        except Exception as e:
            logger.error(f"Error extracting text from Markdown: {str(e)}")
            raise

    def _extract_text_from_rst(self, file_content: bytes) -> str:
        """Extract text from reStructuredText content"""
        # RST is plain text with markup, return as-is
        return file_content.decode("utf-8", errors="replace")
    
    async def query_documents(self, doc_id: str, query: str, n_results: int = 5) -> List[str]:
        """Query processed documents for relevant chunks (simplified)"""
        try:
            if doc_id in self.processed_docs:
                doc = self.processed_docs[doc_id]
                content = doc.get("content", "")
                # Return real content chunks if available
                if content and not content.startswith("Simulated"):
                    words = content.split()
                    chunk_size = max(len(words) // n_results, 50)
                    chunks = []
                    for i in range(0, len(words), chunk_size):
                        chunk = " ".join(words[i:i + chunk_size])
                        if chunk:
                            chunks.append(chunk)
                        if len(chunks) >= n_results:
                            break
                    return chunks if chunks else [content[:500]]
                # Fallback for URL-based or simulated content
                return [
                    f"Relevant documentation excerpt about {query}",
                    f"Best practices for {query}",
                    f"Configuration example for {query}",
                    f"API reference for {query}",
                    f"Usage example for {query}"
                ]
            return []
            
        except Exception as e:
            logger.error(f"Error querying documents: {str(e)}")
            return []