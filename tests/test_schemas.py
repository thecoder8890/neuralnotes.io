"""Tests for Pydantic schema validation.

Validates that request/response models properly validate input data,
enforce required fields, and handle edge cases correctly.
"""
import pytest
from pydantic import ValidationError

from backend.models.schemas import (
    Technology,
    GenerationRequest,
    FileContent,
    GenerationResponse,
    DocumentSummary,
    DocumentInfo
)


class TestTechnologyEnum:
    """Test Technology enumeration."""

    def test_all_technologies_defined(self):
        assert Technology.SPRING_BOOT == "spring_boot"
        assert Technology.DJANGO == "django"
        assert Technology.REACT == "react"
        assert Technology.EXPRESS == "express"
        assert Technology.FLASK == "flask"
        assert Technology.NEXTJS == "nextjs"

    def test_technology_values(self):
        values = [t.value for t in Technology]
        assert "spring_boot" in values
        assert "django" in values
        assert "react" in values
        assert "express" in values
        assert "flask" in values
        assert "nextjs" in values


class TestGenerationRequest:
    """Test GenerationRequest schema validation."""

    def test_valid_request_minimal(self):
        request = GenerationRequest(
            doc_id="abc123",
            prompt="Create a web application"
        )
        assert request.doc_id == "abc123"
        assert request.prompt == "Create a web application"
        assert request.technology is None

    def test_valid_request_with_technology(self):
        request = GenerationRequest(
            doc_id="abc123",
            prompt="Create a Spring Boot app",
            technology=Technology.SPRING_BOOT
        )
        assert request.doc_id == "abc123"
        assert request.prompt == "Create a Spring Boot app"
        assert request.technology == Technology.SPRING_BOOT

    def test_missing_doc_id_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            GenerationRequest(prompt="Create an app")
        assert "doc_id" in str(exc_info.value)

    def test_missing_prompt_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            GenerationRequest(doc_id="abc123")
        assert "prompt" in str(exc_info.value)

    def test_empty_doc_id_is_valid(self):
        # Pydantic allows empty strings by default
        request = GenerationRequest(doc_id="", prompt="Create an app")
        assert request.doc_id == ""

    def test_empty_prompt_is_valid(self):
        # Pydantic allows empty strings by default
        request = GenerationRequest(doc_id="abc123", prompt="")
        assert request.prompt == ""

    def test_technology_from_string(self):
        request = GenerationRequest(
            doc_id="abc123",
            prompt="Create an app",
            technology="react"
        )
        assert request.technology == Technology.REACT

    def test_invalid_technology_raises_error(self):
        with pytest.raises(ValidationError):
            GenerationRequest(
                doc_id="abc123",
                prompt="Create an app",
                technology="invalid_tech"
            )


class TestFileContent:
    """Test FileContent schema validation."""

    def test_valid_file_content(self):
        file = FileContent(
            name="src/main.py",
            content="print('Hello')",
            type="text"
        )
        assert file.name == "src/main.py"
        assert file.content == "print('Hello')"
        assert file.type == "text"

    def test_default_type_is_text(self):
        file = FileContent(
            name="file.txt",
            content="content"
        )
        assert file.type == "text"

    def test_missing_name_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            FileContent(content="content")
        assert "name" in str(exc_info.value)

    def test_missing_content_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            FileContent(name="file.txt")
        assert "content" in str(exc_info.value)

    def test_empty_name_is_valid(self):
        # Pydantic allows empty strings by default
        file = FileContent(name="", content="content")
        assert file.name == ""

    def test_empty_content_is_valid(self):
        # Empty files are allowed
        file = FileContent(name="empty.txt", content="")
        assert file.content == ""

    def test_binary_type(self):
        file = FileContent(
            name="image.png",
            content="binary_data_placeholder",
            type="binary"
        )
        assert file.type == "binary"


class TestGenerationResponse:
    """Test GenerationResponse schema validation."""

    def test_valid_response(self):
        response = GenerationResponse(
            project_id="proj_123",
            files=[
                FileContent(name="main.py", content="print('hello')"),
                FileContent(name="README.md", content="# Project")
            ],
            structure={"src": ["main.py"], "README.md": []},
            instructions="Run: python main.py"
        )
        assert response.project_id == "proj_123"
        assert len(response.files) == 2
        assert "src" in response.structure
        assert response.instructions == "Run: python main.py"

    def test_missing_project_id_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            GenerationResponse(
                files=[],
                structure={},
                instructions="Instructions"
            )
        assert "project_id" in str(exc_info.value)

    def test_missing_files_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            GenerationResponse(
                project_id="proj_123",
                structure={},
                instructions="Instructions"
            )
        assert "files" in str(exc_info.value)

    def test_missing_structure_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            GenerationResponse(
                project_id="proj_123",
                files=[],
                instructions="Instructions"
            )
        assert "structure" in str(exc_info.value)

    def test_missing_instructions_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            GenerationResponse(
                project_id="proj_123",
                files=[],
                structure={}
            )
        assert "instructions" in str(exc_info.value)

    def test_empty_files_list_is_valid(self):
        response = GenerationResponse(
            project_id="proj_123",
            files=[],
            structure={},
            instructions="No files generated"
        )
        assert response.files == []

    def test_empty_structure_is_valid(self):
        response = GenerationResponse(
            project_id="proj_123",
            files=[],
            structure={},
            instructions="Empty project"
        )
        assert response.structure == {}

    def test_complex_structure(self):
        response = GenerationResponse(
            project_id="proj_123",
            files=[],
            structure={
                "src": {
                    "main": ["app.py", "config.py"],
                    "tests": ["test_app.py"]
                },
                "README.md": []
            },
            instructions="Complex structure"
        )
        assert "src" in response.structure
        assert "main" in response.structure["src"]


class TestDocumentSummary:
    """Test DocumentSummary schema validation."""

    def test_valid_summary(self):
        summary = DocumentSummary(
            doc_id="doc_123",
            source_type="file",
            source_name="document.pdf",
            processed_at="2024-01-01T00:00:00",
            status="ready",
            char_count=1000,
            approx_chunks=5,
            preview="This is a preview of the document...",
            file_size=50000
        )
        assert summary.doc_id == "doc_123"
        assert summary.source_type == "file"
        assert summary.source_name == "document.pdf"
        assert summary.char_count == 1000
        assert summary.approx_chunks == 5
        assert summary.file_size == 50000

    def test_default_values(self):
        summary = DocumentSummary(
            doc_id="doc_123",
            source_type="url",
            source_name="https://example.com",
            processed_at="2024-01-01T00:00:00"
        )
        assert summary.status == "ready"
        assert summary.char_count == 0
        assert summary.approx_chunks == 0
        assert summary.preview == ""
        assert summary.file_size is None

    def test_missing_required_fields_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            DocumentSummary()
        errors = str(exc_info.value)
        assert "doc_id" in errors
        assert "source_type" in errors
        assert "source_name" in errors
        assert "processed_at" in errors

    def test_url_source_type(self):
        summary = DocumentSummary(
            doc_id="doc_123",
            source_type="url",
            source_name="https://docs.python.org",
            processed_at="2024-01-01T00:00:00"
        )
        assert summary.source_type == "url"
        assert summary.file_size is None

    def test_file_source_type_with_size(self):
        summary = DocumentSummary(
            doc_id="doc_123",
            source_type="file",
            source_name="guide.pdf",
            processed_at="2024-01-01T00:00:00",
            file_size=1024000
        )
        assert summary.source_type == "file"
        assert summary.file_size == 1024000

    def test_preview_truncation(self):
        long_preview = "A" * 500
        summary = DocumentSummary(
            doc_id="doc_123",
            source_type="file",
            source_name="doc.txt",
            processed_at="2024-01-01T00:00:00",
            preview=long_preview
        )
        # Preview can be any length (truncation happens elsewhere)
        assert len(summary.preview) == 500

    def test_negative_char_count_is_valid(self):
        # Pydantic allows negative integers by default
        summary = DocumentSummary(
            doc_id="doc_123",
            source_type="file",
            source_name="doc.txt",
            processed_at="2024-01-01T00:00:00",
            char_count=-1
        )
        assert summary.char_count == -1

    def test_zero_chunks(self):
        summary = DocumentSummary(
            doc_id="doc_123",
            source_type="file",
            source_name="empty.txt",
            processed_at="2024-01-01T00:00:00",
            char_count=0,
            approx_chunks=0
        )
        assert summary.approx_chunks == 0


class TestDocumentInfo:
    """Test DocumentInfo schema validation."""

    def test_valid_document_info_with_url(self):
        info = DocumentInfo(
            doc_id="doc_123",
            url="https://example.com",
            processed_at="2024-01-01T00:00:00",
            status="ready"
        )
        assert info.doc_id == "doc_123"
        assert info.url == "https://example.com"
        assert info.filename is None

    def test_valid_document_info_with_filename(self):
        info = DocumentInfo(
            doc_id="doc_123",
            filename="document.pdf",
            processed_at="2024-01-01T00:00:00",
            status="ready"
        )
        assert info.doc_id == "doc_123"
        assert info.filename == "document.pdf"
        assert info.url is None

    def test_valid_document_info_with_both(self):
        info = DocumentInfo(
            doc_id="doc_123",
            url="https://example.com",
            filename="cached.html",
            processed_at="2024-01-01T00:00:00",
            status="ready"
        )
        assert info.url == "https://example.com"
        assert info.filename == "cached.html"

    def test_missing_required_fields_raises_error(self):
        with pytest.raises(ValidationError) as exc_info:
            DocumentInfo()
        errors = str(exc_info.value)
        assert "doc_id" in errors
        assert "processed_at" in errors
        assert "status" in errors

    def test_optional_fields_default_to_none(self):
        info = DocumentInfo(
            doc_id="doc_123",
            processed_at="2024-01-01T00:00:00",
            status="processing"
        )
        assert info.url is None
        assert info.filename is None

    def test_status_values(self):
        statuses = ["ready", "processing", "error", "pending"]
        for status in statuses:
            info = DocumentInfo(
                doc_id="doc_123",
                processed_at="2024-01-01T00:00:00",
                status=status
            )
            assert info.status == status


class TestSchemaInteroperability:
    """Test schemas working together."""

    def test_generation_request_to_response_flow(self):
        # Create a request
        request = GenerationRequest(
            doc_id="doc_123",
            prompt="Create a Flask app",
            technology=Technology.FLASK
        )

        # Simulate generating a response
        response = GenerationResponse(
            project_id="proj_456",
            files=[
                FileContent(name="app.py", content="from flask import Flask"),
                FileContent(name="requirements.txt", content="Flask==2.3.0")
            ],
            structure={"app.py": [], "requirements.txt": []},
            instructions="Run: python app.py"
        )

        assert request.doc_id == "doc_123"
        assert response.project_id == "proj_456"
        assert len(response.files) == 2

    def test_document_summary_serialization(self):
        summary = DocumentSummary(
            doc_id="doc_123",
            source_type="file",
            source_name="guide.pdf",
            processed_at="2024-01-01T00:00:00",
            status="ready",
            char_count=5000,
            approx_chunks=7,
            preview="Preview text here",
            file_size=102400
        )

        # Test JSON serialization
        json_data = summary.model_dump()
        assert json_data["doc_id"] == "doc_123"
        assert json_data["char_count"] == 5000

        # Test JSON deserialization
        recreated = DocumentSummary(**json_data)
        assert recreated.doc_id == summary.doc_id
        assert recreated.char_count == summary.char_count