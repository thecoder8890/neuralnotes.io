"""Tests for documentation file upload functionality.

Validates file validation, the simplified document processor's text
extraction, and the upload API endpoints for single and multiple files.
"""
import io
import pytest

from backend.core.document_processor_simple import DocumentProcessor


@pytest.fixture
def processor():
    return DocumentProcessor()


# --- File Validation (main.py helpers) ---

class TestFileValidation:
    def test_validate_upload_rejects_unsupported_extension(self):
        from main import _validate_upload
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            _validate_upload("file.exe", b"data")
        assert exc_info.value.status_code == 400
        assert "Unsupported file type" in exc_info.value.detail

    def test_validate_upload_rejects_oversized_file(self):
        from main import _validate_upload, MAX_FILE_SIZE
        from fastapi import HTTPException

        big_content = b"x" * (MAX_FILE_SIZE + 1)
        with pytest.raises(HTTPException) as exc_info:
            _validate_upload("file.txt", big_content)
        assert exc_info.value.status_code == 400
        assert "exceeds maximum" in exc_info.value.detail

    def test_validate_upload_accepts_pdf(self):
        from main import _validate_upload
        # Should not raise
        _validate_upload("doc.pdf", b"small content")

    def test_validate_upload_accepts_markdown(self):
        from main import _validate_upload
        _validate_upload("readme.md", b"# Hello")

    def test_validate_upload_accepts_txt(self):
        from main import _validate_upload
        _validate_upload("notes.txt", b"plain text")

    def test_validate_upload_accepts_html(self):
        from main import _validate_upload
        _validate_upload("page.html", b"<html></html>")

    def test_validate_upload_accepts_rst(self):
        from main import _validate_upload
        _validate_upload("docs.rst", b"Title\n=====")

    def test_validate_upload_accepts_docx(self):
        from main import _validate_upload
        _validate_upload("report.docx", b"PK")

    def test_validate_upload_accepts_htm(self):
        from main import _validate_upload
        _validate_upload("page.htm", b"<html></html>")

    def test_validate_upload_accepts_markdown_long_ext(self):
        from main import _validate_upload
        _validate_upload("readme.markdown", b"# Hello")


# --- Simplified Document Processor: Text Extraction ---

class TestSimplifiedProcessorExtraction:
    @pytest.mark.asyncio
    async def test_process_txt_file(self, processor):
        content = b"Hello, this is a text document."
        doc_id = await processor.process_file(content, "test.txt")
        assert doc_id
        assert processor.processed_docs[doc_id]["content"] == "Hello, this is a text document."

    @pytest.mark.asyncio
    async def test_process_markdown_file(self, processor):
        content = b"# Title\n\nThis is **bold** text."
        doc_id = await processor.process_file(content, "readme.md")
        assert doc_id
        extracted = processor.processed_docs[doc_id]["content"]
        # Should contain the text (with HTML stripped)
        assert "Title" in extracted
        assert "bold" in extracted

    @pytest.mark.asyncio
    async def test_process_html_file(self, processor):
        content = b"<html><body><h1>Hello</h1><p>World</p></body></html>"
        doc_id = await processor.process_file(content, "page.html")
        assert doc_id
        extracted = processor.processed_docs[doc_id]["content"]
        assert "Hello" in extracted
        assert "World" in extracted

    @pytest.mark.asyncio
    async def test_process_rst_file(self, processor):
        content = b"Title\n=====\n\nParagraph text."
        doc_id = await processor.process_file(content, "docs.rst")
        assert doc_id
        extracted = processor.processed_docs[doc_id]["content"]
        assert "Title" in extracted
        assert "Paragraph text." in extracted

    @pytest.mark.asyncio
    async def test_file_size_stored(self, processor):
        content = b"Some content here"
        doc_id = await processor.process_file(content, "test.txt")
        assert processor.processed_docs[doc_id]["file_size"] == len(content)

    @pytest.mark.asyncio
    async def test_duplicate_file_returns_same_id(self, processor):
        content = b"Same content"
        id1 = await processor.process_file(content, "file1.txt")
        id2 = await processor.process_file(content, "file2.txt")
        assert id1 == id2


# --- Simplified Document Processor: Query with Real Content ---

class TestSimplifiedProcessorQuery:
    @pytest.mark.asyncio
    async def test_query_returns_real_chunks(self, processor):
        # Create content large enough to be chunked
        words = " ".join([f"word{i}" for i in range(200)])
        content = words.encode("utf-8")
        doc_id = await processor.process_file(content, "big.txt")
        chunks = await processor.query_documents(doc_id, "test query", n_results=3)
        assert len(chunks) > 0
        # Chunks should contain actual content, not simulated placeholders
        assert all("word" in chunk for chunk in chunks)

    @pytest.mark.asyncio
    async def test_query_url_returns_simulated(self, processor):
        doc_id = await processor.process_url("https://example.com")
        chunks = await processor.query_documents(doc_id, "test query", n_results=3)
        assert len(chunks) > 0

    @pytest.mark.asyncio
    async def test_query_missing_doc_returns_empty(self, processor):
        chunks = await processor.query_documents("nonexistent", "query")
        assert chunks == []


# --- Upload Endpoints ---

class TestUploadEndpoint:
    @pytest.mark.asyncio
    async def test_single_upload_txt(self):
        from httpx import AsyncClient, ASGITransport
        from main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/upload-documentation",
                files={"file": ("test.txt", b"Hello world", "text/plain")},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "doc_id" in data

    @pytest.mark.asyncio
    async def test_single_upload_markdown(self):
        from httpx import AsyncClient, ASGITransport
        from main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/upload-documentation",
                files={"file": ("readme.md", b"# Hello\nWorld", "text/markdown")},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    @pytest.mark.asyncio
    async def test_single_upload_rejects_bad_extension(self):
        from httpx import AsyncClient, ASGITransport
        from main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/upload-documentation",
                files={"file": ("malware.exe", b"bad content", "application/octet-stream")},
            )
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_multiple_upload(self):
        from httpx import AsyncClient, ASGITransport
        from main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/upload-multiple-documentation",
                files=[
                    ("files", ("doc1.txt", b"First document", "text/plain")),
                    ("files", ("doc2.md", b"# Second", "text/markdown")),
                ],
            )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["results"]) == 2
        assert len(data["errors"]) == 0

    @pytest.mark.asyncio
    async def test_multiple_upload_partial_failure(self):
        from httpx import AsyncClient, ASGITransport
        from main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.post(
                "/api/upload-multiple-documentation",
                files=[
                    ("files", ("good.txt", b"Good content", "text/plain")),
                    ("files", ("bad.exe", b"Bad content", "application/octet-stream")),
                ],
            )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "partial"
        assert len(data["results"]) == 1
        assert len(data["errors"]) == 1


# --- Supported Formats Endpoint ---

class TestSupportedFormatsEndpoint:
    @pytest.mark.asyncio
    async def test_returns_formats(self):
        from httpx import AsyncClient, ASGITransport
        from main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/supported-formats")
        assert response.status_code == 200
        data = response.json()
        assert ".pdf" in data["formats"]
        assert ".md" in data["formats"]
        assert ".txt" in data["formats"]
        assert ".rst" in data["formats"]
        assert ".docx" in data["formats"]
        assert data["max_file_size_mb"] == 50
