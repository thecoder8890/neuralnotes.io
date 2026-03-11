"""Tests for the full document processor with ChromaDB and embeddings.

Validates text extraction from various file types, document processing,
vector storage, and query functionality.
"""
import io
import os
import pytest
import hashlib
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from backend.core.document_processor import DocumentProcessor


@pytest.fixture
def processor():
    """Create a document processor with mocked ChromaDB and embeddings."""
    with patch('backend.core.document_processor.chromadb.PersistentClient') as mock_chroma, \
         patch('backend.core.document_processor.OpenAIEmbeddings') as mock_embeddings:

        # Mock ChromaDB client
        mock_client = MagicMock()
        mock_chroma.return_value = mock_client

        # Mock embeddings
        mock_embed = MagicMock()
        mock_embeddings.return_value = mock_embed

        # Set environment variable for OpenAI
        os.environ['OPENAI_API_KEY'] = 'test-key'

        proc = DocumentProcessor()
        proc.chroma_client = mock_client
        proc.embeddings = mock_embed

        yield proc


class TestDocumentProcessorInitialization:
    """Test processor initialization."""

    def test_initializes_text_splitter(self, processor):
        assert processor.text_splitter is not None
        assert processor.text_splitter.chunk_size == 1000
        assert processor.text_splitter.chunk_overlap == 200

    def test_initializes_document_index(self, processor):
        assert isinstance(processor.document_index, dict)
        assert len(processor.document_index) == 0


class TestTextExtraction:
    """Test text extraction from various file formats."""

    def test_extract_text_from_html(self, processor):
        from bs4 import BeautifulSoup
        html = "<html><body><h1>Title</h1><p>Content</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        text = processor._extract_text_from_html(soup)
        assert "Title" in text
        assert "Content" in text

    def test_extract_text_from_html_removes_scripts(self, processor):
        from bs4 import BeautifulSoup
        html = "<html><body><script>alert('xss')</script><p>Content</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        text = processor._extract_text_from_html(soup)
        assert "alert" not in text
        assert "Content" in text

    def test_extract_text_from_html_cleans_whitespace(self, processor):
        from bs4 import BeautifulSoup
        html = "<html><body><p>Line  1</p>   <p>Line  2</p></body></html>"
        soup = BeautifulSoup(html, 'html.parser')
        text = processor._extract_text_from_html(soup)
        # Should have normalized whitespace
        assert "Line 1" in text
        assert "Line 2" in text

    def test_extract_text_from_pdf(self, processor):
        # Create a minimal PDF content (simplified test)
        pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n%%EOF"
        with patch('backend.core.document_processor.pypdf.PdfReader') as mock_reader:
            mock_page = MagicMock()
            mock_page.extract_text.return_value = "PDF content here"
            mock_pdf = MagicMock()
            mock_pdf.pages = [mock_page]
            mock_reader.return_value = mock_pdf

            text = processor._extract_text_from_pdf(pdf_content)
            assert "PDF content here" in text

    def test_extract_text_from_markdown(self, processor):
        md_content = b"# Heading\n\nThis is **bold** text."
        text = processor._extract_text_from_markdown(md_content)
        assert "Heading" in text
        assert "bold" in text

    def test_extract_text_from_markdown_strips_html(self, processor):
        md_content = b"# Title\n\n[Link](http://example.com)"
        text = processor._extract_text_from_markdown(md_content)
        assert "Title" in text
        assert "Link" in text

    def test_extract_text_from_file_pdf(self, processor):
        with patch.object(processor, '_extract_text_from_pdf', return_value="PDF text"):
            text = processor._extract_text_from_file(b"content", "file.pdf")
            assert text == "PDF text"

    def test_extract_text_from_file_markdown(self, processor):
        with patch.object(processor, '_extract_text_from_markdown', return_value="MD text"):
            text = processor._extract_text_from_file(b"content", "file.md")
            assert text == "MD text"

    def test_extract_text_from_file_markdown_long_ext(self, processor):
        with patch.object(processor, '_extract_text_from_markdown', return_value="MD text"):
            text = processor._extract_text_from_file(b"content", "file.markdown")
            assert text == "MD text"

    def test_extract_text_from_file_rst(self, processor):
        text = processor._extract_text_from_file(b"Title\n=====", "file.rst")
        assert "Title" in text

    def test_extract_text_from_file_txt(self, processor):
        text = processor._extract_text_from_file(b"Plain text", "file.txt")
        assert text == "Plain text"

    def test_extract_text_from_file_html(self, processor):
        text = processor._extract_text_from_file(b"<p>HTML</p>", "file.html")
        assert "HTML" in text

    def test_extract_text_from_file_unsupported_type(self, processor):
        with pytest.raises(ValueError, match="Unsupported file type"):
            processor._extract_text_from_file(b"\x00\x01\x02", "file.bin")


class TestURLProcessing:
    """Test URL processing functionality."""

    @pytest.mark.asyncio
    async def test_process_url_generates_doc_id(self, processor):
        url = "https://example.com/docs"
        expected_id = hashlib.md5(url.encode()).hexdigest()

        # Mock requests.get
        with patch('backend.core.document_processor.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.content = b"<html><body>Content</body></html>"
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            # Mock collection operations
            mock_collection = MagicMock()
            processor.chroma_client.get_or_create_collection.return_value = mock_collection
            processor.chroma_client.list_collections.return_value = []

            doc_id = await processor.process_url(url)
            assert doc_id == expected_id

    @pytest.mark.asyncio
    async def test_process_url_already_processed(self, processor):
        url = "https://example.com/docs"
        doc_id = hashlib.md5(url.encode()).hexdigest()

        # Mock that document is already processed
        mock_collection = MagicMock()
        mock_collection.name = f"doc_{doc_id}"
        processor.chroma_client.list_collections.return_value = [mock_collection]

        result = await processor.process_url(url)
        assert result == doc_id

    @pytest.mark.asyncio
    async def test_process_url_handles_http_error(self, processor):
        url = "https://example.com/notfound"

        with patch('backend.core.document_processor.requests.get') as mock_get:
            mock_get.side_effect = Exception("404 Not Found")

            with pytest.raises(Exception):
                await processor.process_url(url)


class TestFileProcessing:
    """Test file processing functionality."""

    @pytest.mark.asyncio
    async def test_process_file_generates_doc_id(self, processor):
        content = b"File content here"
        filename = "test.txt"
        expected_id = hashlib.md5(content).hexdigest()

        # Mock collection operations
        mock_collection = MagicMock()
        processor.chroma_client.get_or_create_collection.return_value = mock_collection
        processor.chroma_client.list_collections.return_value = []

        doc_id = await processor.process_file(content, filename)
        assert doc_id == expected_id

    @pytest.mark.asyncio
    async def test_process_file_already_processed(self, processor):
        content = b"File content"
        filename = "test.txt"
        doc_id = hashlib.md5(content).hexdigest()

        # Mock that file is already processed
        mock_collection = MagicMock()
        mock_collection.name = f"doc_{doc_id}"
        processor.chroma_client.list_collections.return_value = [mock_collection]

        result = await processor.process_file(content, filename)
        assert result == doc_id

    @pytest.mark.asyncio
    async def test_process_file_extracts_text(self, processor):
        content = b"# Markdown Content\n\nParagraph text."
        filename = "test.md"

        mock_collection = MagicMock()
        processor.chroma_client.get_or_create_collection.return_value = mock_collection
        processor.chroma_client.list_collections.return_value = []

        with patch.object(processor, '_extract_text_from_file', return_value="Extracted") as mock_extract:
            await processor.process_file(content, filename)
            mock_extract.assert_called_once_with(content, filename)


class TestDocumentStorage:
    """Test document storage and indexing."""

    @pytest.mark.asyncio
    async def test_process_and_store_creates_collection(self, processor):
        doc_id = "test123"
        text_content = "Short text content"

        mock_collection = MagicMock()
        processor.chroma_client.get_or_create_collection.return_value = mock_collection

        await processor._process_and_store(doc_id, text_content, filename="test.txt")

        processor.chroma_client.get_or_create_collection.assert_called_once()
        call_args = processor.chroma_client.get_or_create_collection.call_args
        assert call_args[1]['name'] == f"doc_{doc_id}"

    @pytest.mark.asyncio
    async def test_process_and_store_adds_to_index(self, processor):
        doc_id = "test123"
        text_content = "Content for testing"

        mock_collection = MagicMock()
        processor.chroma_client.get_or_create_collection.return_value = mock_collection

        await processor._process_and_store(doc_id, text_content, filename="test.txt")

        assert doc_id in processor.document_index
        assert processor.document_index[doc_id]['doc_id'] == doc_id
        assert processor.document_index[doc_id]['source_type'] == 'file'

    @pytest.mark.asyncio
    async def test_process_and_store_with_embeddings(self, processor):
        doc_id = "test123"
        text_content = "A" * 2000  # Long enough to create multiple chunks

        mock_collection = MagicMock()
        processor.chroma_client.get_or_create_collection.return_value = mock_collection
        processor.embeddings.embed_query = Mock(return_value=[0.1] * 1536)

        await processor._process_and_store(doc_id, text_content, filename="test.txt")

        # Should have called add on collection
        assert mock_collection.add.called

    @pytest.mark.asyncio
    async def test_process_and_store_without_embeddings(self, processor):
        doc_id = "test123"
        text_content = "Short content"

        mock_collection = MagicMock()
        processor.chroma_client.get_or_create_collection.return_value = mock_collection
        processor.embeddings = None  # No embeddings available

        await processor._process_and_store(doc_id, text_content, filename="test.txt")

        # Should still store documents without embeddings
        assert mock_collection.add.called


class TestDocumentQuerying:
    """Test document query functionality."""

    @pytest.mark.asyncio
    async def test_query_documents_with_embeddings(self, processor):
        doc_id = "test123"
        query = "test query"

        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            'documents': [["chunk1", "chunk2", "chunk3"]]
        }
        processor.chroma_client.get_collection.return_value = mock_collection
        processor.embeddings.embed_query = Mock(return_value=[0.1] * 1536)

        results = await processor.query_documents(doc_id, query, n_results=3)

        assert len(results) == 3
        assert results == ["chunk1", "chunk2", "chunk3"]

    @pytest.mark.asyncio
    async def test_query_documents_without_embeddings(self, processor):
        doc_id = "test123"
        query = "test query"

        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            'documents': [["chunk1", "chunk2"]]
        }
        processor.chroma_client.get_collection.return_value = mock_collection
        processor.embeddings = None

        results = await processor.query_documents(doc_id, query, n_results=2)

        assert len(results) == 2
        mock_collection.query.assert_called_once()
        # Should use query_texts instead of query_embeddings
        assert 'query_texts' in mock_collection.query.call_args[1]

    @pytest.mark.asyncio
    async def test_query_documents_handles_error(self, processor):
        doc_id = "test123"
        query = "test query"

        processor.chroma_client.get_collection.side_effect = Exception("Collection not found")

        results = await processor.query_documents(doc_id, query)
        assert results == []


class TestDocumentSummary:
    """Test document summary retrieval."""

    def test_get_document_summary_from_index(self, processor):
        doc_id = "test123"
        processor.document_index[doc_id] = {
            "doc_id": doc_id,
            "source_type": "file",
            "source_name": "test.txt",
            "processed_at": "2024-01-01T00:00:00",
            "status": "ready",
            "char_count": 100,
            "approx_chunks": 1,
            "preview": "Preview text",
            "file_size": None
        }

        summary = processor.get_document_summary(doc_id)
        assert summary["doc_id"] == doc_id
        assert summary["source_name"] == "test.txt"

    def test_get_document_summary_from_collection(self, processor):
        doc_id = "test123"

        mock_collection = MagicMock()
        mock_collection.metadata = {
            "filename": "test.txt",
            "processed_at": "2024-01-01T00:00:00"
        }
        mock_collection.get.return_value = {
            "documents": [["Preview content here"]]
        }
        mock_collection.count.return_value = 5
        processor.chroma_client.get_collection.return_value = mock_collection

        summary = processor.get_document_summary(doc_id)

        assert summary["doc_id"] == doc_id
        assert summary["source_name"] == "test.txt"
        assert summary["approx_chunks"] == 5
        assert "Preview" in summary["preview"]

    def test_get_document_summary_not_found(self, processor):
        doc_id = "nonexistent"

        processor.chroma_client.get_collection.side_effect = Exception("Not found")

        with pytest.raises(ValueError, match="Document not found"):
            processor.get_document_summary(doc_id)

    def test_build_document_summary_from_url(self, processor):
        summary = processor._build_document_summary(
            doc_id="test123",
            text_content="A" * 300,
            processed_at="2024-01-01T00:00:00",
            chunk_count=1,
            url="https://example.com"
        )

        assert summary["source_type"] == "url"
        assert summary["source_name"] == "https://example.com"
        assert summary["char_count"] == 300
        assert len(summary["preview"]) <= 280

    def test_build_document_summary_from_file(self, processor):
        summary = processor._build_document_summary(
            doc_id="test123",
            text_content="File content here",
            processed_at="2024-01-01T00:00:00",
            chunk_count=1,
            filename="document.pdf"
        )

        assert summary["source_type"] == "file"
        assert summary["source_name"] == "document.pdf"


class TestIsProcessed:
    """Test checking if document is already processed."""

    def test_is_processed_returns_true(self, processor):
        doc_id = "test123"

        mock_collection = MagicMock()
        mock_collection.name = f"doc_{doc_id}"
        processor.chroma_client.list_collections.return_value = [mock_collection]

        assert processor._is_processed(doc_id) is True

    def test_is_processed_returns_false(self, processor):
        doc_id = "test123"

        processor.chroma_client.list_collections.return_value = []

        assert processor._is_processed(doc_id) is False

    def test_is_processed_handles_error(self, processor):
        doc_id = "test123"

        processor.chroma_client.list_collections.side_effect = Exception("Error")

        assert processor._is_processed(doc_id) is False