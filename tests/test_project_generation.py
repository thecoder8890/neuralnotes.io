"""Tests for multi-technology project generation pipeline.

Validates that Spring Boot, Django, and React.js project generation
works reliably in the simplified (fallback) code generator.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.models.schemas import Technology, FileContent, GenerationResponse
from backend.core.code_generator_simple import CodeGenerator


@pytest.fixture
def generator():
    return CodeGenerator()


# --- Technology Detection ---

class TestTechnologyDetection:
    def test_detect_spring_boot(self, generator):
        assert generator._detect_technology("Create a Spring Boot REST API") == Technology.SPRING_BOOT
        assert generator._detect_technology("Build a Java application") == Technology.SPRING_BOOT
        assert generator._detect_technology("Maven project with REST endpoints") == Technology.SPRING_BOOT

    def test_detect_django(self, generator):
        assert generator._detect_technology("Create a Django web app") == Technology.DJANGO
        assert generator._detect_technology("Build a python web application") == Technology.DJANGO

    def test_detect_react(self, generator):
        assert generator._detect_technology("Build a React dashboard") == Technology.REACT
        assert generator._detect_technology("Create a TSX component library") == Technology.REACT

    def test_detect_none(self, generator):
        assert generator._detect_technology("Build something cool") is None


# --- Spring Boot Generation ---

class TestSpringBootGeneration:
    @pytest.mark.asyncio
    async def test_generates_valid_response(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Create a Spring Boot REST API", technology=Technology.SPRING_BOOT
        )
        assert isinstance(result, GenerationResponse)
        assert result.project_id
        assert len(result.files) > 0
        assert result.instructions

    @pytest.mark.asyncio
    async def test_contains_required_files(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Create a Spring Boot REST API", technology=Technology.SPRING_BOOT
        )
        file_names = [f.name for f in result.files]
        assert "pom.xml" in file_names
        assert "src/main/java/com/example/Application.java" in file_names
        assert "src/main/java/com/example/controller/HomeController.java" in file_names
        assert "src/main/resources/application.properties" in file_names
        assert "README.md" in file_names

    @pytest.mark.asyncio
    async def test_pom_has_spring_boot_dependency(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Create a Spring Boot REST API", technology=Technology.SPRING_BOOT
        )
        pom = next(f for f in result.files if f.name == "pom.xml")
        assert "spring-boot-starter-web" in pom.content
        assert "spring-boot-starter-parent" in pom.content

    @pytest.mark.asyncio
    async def test_conditional_jpa_dependency(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Spring Boot app with JPA database", technology=Technology.SPRING_BOOT
        )
        pom = next(f for f in result.files if f.name == "pom.xml")
        assert "spring-boot-starter-data-jpa" in pom.content

    @pytest.mark.asyncio
    async def test_structure_has_correct_nesting(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Create a Spring Boot REST API", technology=Technology.SPRING_BOOT
        )
        assert "src" in result.structure
        assert "main" in result.structure["src"]


# --- Django Generation ---

class TestDjangoGeneration:
    @pytest.mark.asyncio
    async def test_generates_valid_response(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Create a Django web app", technology=Technology.DJANGO
        )
        assert isinstance(result, GenerationResponse)
        assert result.project_id
        assert len(result.files) > 0
        assert result.instructions

    @pytest.mark.asyncio
    async def test_contains_required_files(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Create a Django web app", technology=Technology.DJANGO
        )
        file_names = [f.name for f in result.files]
        assert "requirements.txt" in file_names
        assert "django_app/__init__.py" in file_names
        assert "django_app/settings.py" in file_names
        assert "django_app/urls.py" in file_names
        assert "django_app/wsgi.py" in file_names
        assert "core/__init__.py" in file_names
        assert "core/models.py" in file_names
        assert "core/views.py" in file_names
        assert "core/urls.py" in file_names
        assert "manage.py" in file_names

    @pytest.mark.asyncio
    async def test_settings_has_correct_module_ref(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Create a Django web app", technology=Technology.DJANGO
        )
        settings = next(f for f in result.files if f.name == "django_app/settings.py")
        assert "django_app.urls" in settings.content or "ROOT_URLCONF" in settings.content

    @pytest.mark.asyncio
    async def test_manage_py_references_settings(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Create a Django web app", technology=Technology.DJANGO
        )
        manage = next(f for f in result.files if f.name == "manage.py")
        assert "django_app.settings" in manage.content

    @pytest.mark.asyncio
    async def test_requirements_has_django(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Create a Django web app", technology=Technology.DJANGO
        )
        req = next(f for f in result.files if f.name == "requirements.txt")
        assert "Django" in req.content

    @pytest.mark.asyncio
    async def test_conditional_drf_dependency(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Create a Django REST API", technology=Technology.DJANGO
        )
        req = next(f for f in result.files if f.name == "requirements.txt")
        assert "djangorestframework" in req.content

    @pytest.mark.asyncio
    async def test_structure_includes_init_py(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Create a Django web app", technology=Technology.DJANGO
        )
        assert "__init__.py" in result.structure.get("django_app", [])


# --- React Generation ---

class TestReactGeneration:
    @pytest.mark.asyncio
    async def test_generates_valid_response(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Build a React dashboard", technology=Technology.REACT
        )
        assert isinstance(result, GenerationResponse)
        assert result.project_id
        assert len(result.files) > 0
        assert result.instructions

    @pytest.mark.asyncio
    async def test_contains_required_files(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Build a React dashboard", technology=Technology.REACT
        )
        file_names = [f.name for f in result.files]
        assert "package.json" in file_names
        assert "public/index.html" in file_names
        assert "src/index.tsx" in file_names
        assert "src/App.tsx" in file_names
        assert "tsconfig.json" in file_names
        assert "README.md" in file_names

    @pytest.mark.asyncio
    async def test_package_json_has_react(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Build a React dashboard", technology=Technology.REACT
        )
        pkg = next(f for f in result.files if f.name == "package.json")
        assert '"react"' in pkg.content
        assert '"react-dom"' in pkg.content

    @pytest.mark.asyncio
    async def test_conditional_axios_dependency(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="React app with API integration", technology=Technology.REACT
        )
        pkg = next(f for f in result.files if f.name == "package.json")
        assert "axios" in pkg.content

    @pytest.mark.asyncio
    async def test_tsconfig_has_jsx_support(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Build a React dashboard", technology=Technology.REACT
        )
        tsconfig = next(f for f in result.files if f.name == "tsconfig.json")
        assert "react-jsx" in tsconfig.content


# --- ZIP Export ---

class TestZipExport:
    @pytest.mark.asyncio
    async def test_spring_boot_zip(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Create a Spring Boot REST API", technology=Technology.SPRING_BOOT
        )
        zip_data = await generator.get_project_zip(result.project_id)
        assert isinstance(zip_data, bytes)
        assert len(zip_data) > 0

    @pytest.mark.asyncio
    async def test_django_zip(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Create a Django web app", technology=Technology.DJANGO
        )
        zip_data = await generator.get_project_zip(result.project_id)
        assert isinstance(zip_data, bytes)
        assert len(zip_data) > 0

    @pytest.mark.asyncio
    async def test_react_zip(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Build a React dashboard", technology=Technology.REACT
        )
        zip_data = await generator.get_project_zip(result.project_id)
        assert isinstance(zip_data, bytes)
        assert len(zip_data) > 0

    @pytest.mark.asyncio
    async def test_invalid_project_id_raises(self, generator):
        with pytest.raises(ValueError, match="Project not found"):
            await generator.get_project_zip("nonexistent-id")


# --- Auto-detection End-to-End ---

class TestAutoDetection:
    @pytest.mark.asyncio
    async def test_spring_boot_auto_detected(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Create a Spring Boot REST API with CRUD operations"
        )
        file_names = [f.name for f in result.files]
        assert "pom.xml" in file_names

    @pytest.mark.asyncio
    async def test_django_auto_detected(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Create a Django web application with models"
        )
        file_names = [f.name for f in result.files]
        assert "manage.py" in file_names

    @pytest.mark.asyncio
    async def test_react_auto_detected(self, generator):
        result = await generator.generate_project(
            doc_id="test", prompt="Build a React dashboard with components"
        )
        file_names = [f.name for f in result.files]
        assert "src/App.tsx" in file_names
