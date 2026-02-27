"""Tests for multi-file project ZIP download functionality.

Validates that Flask, Express, and Next.js project generation produces
correct ZIP archives with expected file contents, and that the download
endpoint returns valid ZIP responses.
"""
import io
import zipfile

import pytest

from backend.models.schemas import Technology, FileContent, GenerationResponse
from backend.core.code_generator_simple import CodeGenerator


@pytest.fixture
def generator():
    return CodeGenerator()


# --- Flask Generation ---

class TestFlaskGeneration:
    @pytest.mark.asyncio
    async def test_generates_valid_response(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Create a Flask REST API", technology=Technology.FLASK
        )
        assert isinstance(result, GenerationResponse)
        assert result.project_id
        assert len(result.files) > 0
        assert result.instructions

    @pytest.mark.asyncio
    async def test_contains_required_files(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Create a Flask REST API", technology=Technology.FLASK
        )
        file_names = [f.name for f in result.files]
        assert "requirements.txt" in file_names
        assert "app.py" in file_names
        assert "README.md" in file_names

    @pytest.mark.asyncio
    async def test_requirements_has_flask(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Create a Flask REST API", technology=Technology.FLASK
        )
        req = next(f for f in result.files if f.name == "requirements.txt")
        assert "Flask" in req.content

    @pytest.mark.asyncio
    async def test_conditional_sqlalchemy_dependency(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Flask app with database integration", technology=Technology.FLASK
        )
        req = next(f for f in result.files if f.name == "requirements.txt")
        assert "SQLAlchemy" in req.content


# --- Express Generation ---

class TestExpressGeneration:
    @pytest.mark.asyncio
    async def test_generates_valid_response(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Build an Express.js API", technology=Technology.EXPRESS
        )
        assert isinstance(result, GenerationResponse)
        assert result.project_id
        assert len(result.files) > 0
        assert result.instructions

    @pytest.mark.asyncio
    async def test_contains_required_files(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Build an Express.js API", technology=Technology.EXPRESS
        )
        file_names = [f.name for f in result.files]
        assert "package.json" in file_names
        assert "src/index.js" in file_names
        assert "src/routes/api.js" in file_names
        assert "README.md" in file_names

    @pytest.mark.asyncio
    async def test_package_json_has_express(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Build an Express.js API", technology=Technology.EXPRESS
        )
        pkg = next(f for f in result.files if f.name == "package.json")
        assert '"express"' in pkg.content
        assert '"cors"' in pkg.content

    @pytest.mark.asyncio
    async def test_conditional_jwt_dependency(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Express API with JWT auth", technology=Technology.EXPRESS
        )
        pkg = next(f for f in result.files if f.name == "package.json")
        assert "jsonwebtoken" in pkg.content


# --- Next.js Generation ---

class TestNextjsGeneration:
    @pytest.mark.asyncio
    async def test_generates_valid_response(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Create a Next.js application", technology=Technology.NEXTJS
        )
        assert isinstance(result, GenerationResponse)
        assert result.project_id
        assert len(result.files) > 0
        assert result.instructions

    @pytest.mark.asyncio
    async def test_contains_required_files(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Create a Next.js application", technology=Technology.NEXTJS
        )
        file_names = [f.name for f in result.files]
        assert "package.json" in file_names
        assert "tsconfig.json" in file_names
        assert "src/app/layout.tsx" in file_names
        assert "src/app/page.tsx" in file_names
        assert "README.md" in file_names

    @pytest.mark.asyncio
    async def test_package_json_has_next(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Create a Next.js application", technology=Technology.NEXTJS
        )
        pkg = next(f for f in result.files if f.name == "package.json")
        assert '"next"' in pkg.content
        assert '"react"' in pkg.content

    @pytest.mark.asyncio
    async def test_conditional_api_route(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Next.js app with API routes", technology=Technology.NEXTJS
        )
        file_names = [f.name for f in result.files]
        assert "src/app/api/hello/route.ts" in file_names


# --- ZIP Content Validation ---

class TestZipContents:
    @pytest.mark.asyncio
    async def test_flask_zip_contains_all_files(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Create a Flask REST API", technology=Technology.FLASK
        )
        zip_data = await generator.get_project_zip(result.project_id)
        with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zf:
            zip_names = zf.namelist()
            for f in result.files:
                assert f.name in zip_names, f"Missing {f.name} in ZIP"

    @pytest.mark.asyncio
    async def test_express_zip_contains_all_files(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Build an Express.js API", technology=Technology.EXPRESS
        )
        zip_data = await generator.get_project_zip(result.project_id)
        with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zf:
            zip_names = zf.namelist()
            for f in result.files:
                assert f.name in zip_names, f"Missing {f.name} in ZIP"

    @pytest.mark.asyncio
    async def test_nextjs_zip_contains_all_files(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Create a Next.js application", technology=Technology.NEXTJS
        )
        zip_data = await generator.get_project_zip(result.project_id)
        with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zf:
            zip_names = zf.namelist()
            for f in result.files:
                assert f.name in zip_names, f"Missing {f.name} in ZIP"

    @pytest.mark.asyncio
    async def test_zip_file_content_matches(self, generator):
        """Verify that file content inside the ZIP matches the generated content."""
        result = await generator.generate_project(
            doc_id="test", prompt="Create a Flask REST API", technology=Technology.FLASK
        )
        zip_data = await generator.get_project_zip(result.project_id)
        with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zf:
            for f in result.files:
                content = zf.read(f.name).decode('utf-8')
                assert content == f.content, f"Content mismatch for {f.name}"

    @pytest.mark.asyncio
    async def test_zip_is_valid_archive(self, generator):
        """Verify the generated bytes form a valid ZIP archive."""
        result = await generator.generate_project(
            doc_id="test", prompt="Build a React dashboard", technology=Technology.REACT
        )
        zip_data = await generator.get_project_zip(result.project_id)
        assert zipfile.is_zipfile(io.BytesIO(zip_data))

    @pytest.mark.asyncio
    async def test_zip_file_count_matches(self, generator):
        """Verify the ZIP contains exactly the number of generated files."""
        result = await generator.generate_project(
            doc_id="test", prompt="Create a Spring Boot REST API", technology=Technology.SPRING_BOOT
        )
        zip_data = await generator.get_project_zip(result.project_id)
        with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zf:
            assert len(zf.namelist()) == len(result.files)


# --- Download Endpoint ---

class TestDownloadEndpoint:
    @pytest.mark.asyncio
    async def test_download_returns_zip(self):
        """Test that the download endpoint returns a valid ZIP response."""
        from httpx import AsyncClient, ASGITransport
        from main import app, code_generator

        # Generate a project using the app's code_generator instance
        result = await code_generator.generate_project(
            doc_id="test", prompt="Create a Flask REST API", technology=Technology.FLASK
        )

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get(f"/api/download-project/{result.project_id}")

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/zip"
        assert "attachment" in response.headers["content-disposition"]
        assert zipfile.is_zipfile(io.BytesIO(response.content))

    @pytest.mark.asyncio
    async def test_download_invalid_id_returns_not_found(self):
        """Test that requesting a non-existent project returns 404."""
        from httpx import AsyncClient, ASGITransport
        from main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/api/download-project/nonexistent-id")

        assert response.status_code == 404
