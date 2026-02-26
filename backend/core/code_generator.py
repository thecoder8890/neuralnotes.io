import os
import json
import uuid
import logging
import zipfile
import io
from typing import Dict, List, Any, Optional
from datetime import datetime
import openai
from openai import AsyncOpenAI
from backend.core.document_processor import DocumentProcessor
from backend.models.schemas import GenerationResponse, FileContent, Technology

logger = logging.getLogger(__name__)

class CodeGenerator:
    def __init__(self):
        self.document_processor = DocumentProcessor()
        self.openai_client = None
        self.generated_projects = {}  # In-memory storage for generated projects
        self._initialize_openai()
    
    def _initialize_openai(self):
        """Initialize OpenAI client"""
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.openai_client = AsyncOpenAI(api_key=api_key)
        else:
            logger.warning("OpenAI API key not found. Code generation will be limited.")
    
    async def generate_project(self, doc_id: str, prompt: str, technology: Optional[Technology] = None) -> GenerationResponse:
        """Generate a complete project based on documentation and user prompt"""
        try:
            project_id = str(uuid.uuid4())
            
            # Query relevant documentation
            relevant_docs = await self.document_processor.query_documents(doc_id, prompt, n_results=10)
            
            # Generate project structure and files
            if self.openai_client:
                files, structure, instructions = await self._generate_with_openai(
                    relevant_docs, prompt, technology
                )
            else:
                files, structure, instructions = self._generate_fallback(prompt, technology)
            
            # Store generated project
            self.generated_projects[project_id] = {
                "files": files,
                "structure": structure,
                "instructions": instructions,
                "generated_at": datetime.now().isoformat()
            }
            
            return GenerationResponse(
                project_id=project_id,
                files=files,
                structure=structure,
                instructions=instructions
            )
            
        except Exception as e:
            logger.error(f"Error generating project: {str(e)}")
            raise
    
    async def _generate_with_openai(self, relevant_docs: List[str], prompt: str, technology: Optional[Technology]) -> tuple:
        """Generate project using OpenAI API"""
        try:
            # Prepare context from documentation
            context = "\n\n".join(relevant_docs[:5])  # Use top 5 most relevant chunks
            
            # Create system prompt
            system_prompt = self._create_system_prompt(technology)
            
            # Create user prompt with context
            user_prompt = f"""
Documentation Context:
{context}

User Request:
{prompt}

Please generate a complete project structure with all necessary files and configurations.
Provide the response as a JSON object with the following structure:
{{
    "files": [
        {{"name": "file_path", "content": "file_content", "type": "text"}},
        ...
    ],
    "structure": {{"directory": ["subdirectory1", "subdirectory2"], "files": ["file1", "file2"]}},
    "instructions": "Detailed setup and run instructions"
}}
"""
            
            # Call OpenAI API
            response = await self._call_openai_api(system_prompt, user_prompt)
            
            # Parse response
            return self._parse_openai_response(response)
            
        except Exception as e:
            logger.error(f"Error generating with OpenAI: {str(e)}")
            raise
    
    def _create_system_prompt(self, technology: Optional[Technology]) -> str:
        """Create system prompt based on technology"""
        base_prompt = """
You are DocuGen AI, an expert software architect and developer specializing in generating complete, runnable project scaffolding based on official documentation.

Your task is to create a complete project structure with all necessary files, configurations, and dependencies based on the provided documentation context and user requirements.

Key requirements:
1. Generate COMPLETE, RUNNABLE code - not just examples or snippets
2. Include all necessary configuration files (package.json, pom.xml, requirements.txt, etc.)
3. Follow best practices and official conventions from the documentation
4. Include proper error handling and basic security measures
5. Provide clear, actionable setup instructions
6. Ensure all dependencies are correctly specified
7. Include a basic example that demonstrates the requested functionality

Response format: Valid JSON with 'files', 'structure', and 'instructions' keys.
Each file must have 'name', 'content', and 'type' properties.
"""
        
        if technology:
            tech_specific = {
                Technology.SPRING_BOOT: "Focus on Spring Boot best practices, Maven configuration, and proper Java project structure.",
                Technology.DJANGO: "Focus on Django best practices, proper Python project structure, and requirements.txt.",
                Technology.REACT: "Focus on React best practices, modern JavaScript/TypeScript, and npm configuration.",
                Technology.EXPRESS: "Focus on Express.js best practices, Node.js project structure, and npm configuration.",
                Technology.FLASK: "Focus on Flask best practices, Python project structure, and requirements.txt.",
                Technology.NEXTJS: "Focus on Next.js best practices, React patterns, and modern web development."
            }
            base_prompt += f"\n\nTechnology-specific guidance: {tech_specific.get(technology, '')}"
        
        return base_prompt
    
    async def _call_openai_api(self, system_prompt: str, user_prompt: str) -> str:
        """Call OpenAI API with prompts"""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=4000,
                temperature=0.1
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            # Fallback to gpt-3.5-turbo if gpt-4 fails
            try:
                response = await self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=3000,
                    temperature=0.1
                )
                return response.choices[0].message.content
            except Exception as fallback_error:
                logger.error(f"Fallback API call also failed: {str(fallback_error)}")
                raise e
    
    def _parse_openai_response(self, response: str) -> tuple:
        """Parse OpenAI response into files, structure, and instructions"""
        try:
            # Try to extract JSON from response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.endswith("```"):
                response = response[:-3]
            
            data = json.loads(response)
            
            # Convert to FileContent objects
            files = [
                FileContent(
                    name=file_data["name"],
                    content=file_data["content"],
                    type=file_data.get("type", "text")
                )
                for file_data in data.get("files", [])
            ]
            
            structure = data.get("structure", {})
            instructions = data.get("instructions", "No setup instructions provided.")
            
            return files, structure, instructions
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing OpenAI response as JSON: {str(e)}")
            # Fallback: try to extract files from text
            return self._parse_text_response(response)
        except Exception as e:
            logger.error(f"Error parsing OpenAI response: {str(e)}")
            raise
    
    def _parse_text_response(self, response: str) -> tuple:
        """Fallback method to parse text response"""
        # Simple fallback implementation
        files = [
            FileContent(
                name="README.md",
                content=f"# Generated Project\n\n{response}",
                type="text"
            )
        ]
        
        structure = {"root": ["README.md"]}
        instructions = "This is a fallback response. Please check the README.md file for details."
        
        return files, structure, instructions
    
    def _generate_fallback(self, prompt: str, technology: Optional[Technology]) -> tuple:
        """Generate basic project structure without AI when API is not available"""
        project_name = "generated_project"
        
        if technology == Technology.SPRING_BOOT:
            return self._generate_spring_boot_fallback(prompt, project_name)
        elif technology == Technology.REACT:
            return self._generate_react_fallback(prompt, project_name)
        elif technology == Technology.DJANGO:
            return self._generate_django_fallback(prompt, project_name)
        elif technology == Technology.FLASK:
            return self._generate_flask_fallback(prompt, project_name)
        elif technology == Technology.EXPRESS:
            return self._generate_express_fallback(prompt, project_name)
        elif technology == Technology.NEXTJS:
            return self._generate_nextjs_fallback(prompt, project_name)
        else:
            return self._generate_generic_fallback(prompt, project_name)
    
    def _generate_spring_boot_fallback(self, prompt: str, project_name: str) -> tuple:
        """Generate basic Spring Boot project"""
        files = [
            FileContent(
                name="pom.xml",
                content=f"""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    
    <groupId>com.example</groupId>
    <artifactId>{project_name}</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <packaging>jar</packaging>
    
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
        <relativePath/>
    </parent>
    
    <properties>
        <java.version>17</java.version>
    </properties>
    
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-test</artifactId>
            <scope>test</scope>
        </dependency>
    </dependencies>
    
    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>""",
                type="text"
            ),
            FileContent(
                name="src/main/java/com/example/Application.java",
                content="""package com.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}""",
                type="text"
            ),
            FileContent(
                name="src/main/java/com/example/controller/GreetingController.java",
                content="""package com.example.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class GreetingController {
    
    @GetMapping("/greeting")
    public String greeting() {
        return "Hello World from Spring Boot!";
    }
}""",
                type="text"
            )
        ]
        
        structure = {
            "src": {
                "main": {
                    "java": {
                        "com": {
                            "example": ["Application.java"],
                            "controller": ["GreetingController.java"]
                        }
                    }
                }
            },
            "files": ["pom.xml"]
        }
        
        instructions = """
# Setup Instructions

1. Ensure you have Java 17+ and Maven installed
2. Navigate to the project directory
3. Run: `mvn clean install`
4. Run: `mvn spring-boot:run`
5. Visit: http://localhost:8080/api/greeting

The application will start on port 8080 with a basic REST endpoint.
"""
        
        return files, structure, instructions
    
    def _generate_react_fallback(self, prompt: str, project_name: str) -> tuple:
        """Generate basic React project"""
        files = [
            FileContent(
                name="package.json",
                content=f"""{{
  "name": "{project_name}",
  "version": "0.1.0",
  "private": true,
  "dependencies": {{
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  }},
  "scripts": {{
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  }},
  "eslintConfig": {{
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  }},
  "browserslist": {{
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }}
}}""",
                type="text"
            ),
            FileContent(
                name="public/index.html",
                content=f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{project_name}</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>""",
                type="text"
            ),
            FileContent(
                name="src/index.js",
                content="""import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);""",
                type="text"
            ),
            FileContent(
                name="src/App.js",
                content="""import React from 'react';

function App() {
  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>Hello World from React!</h1>
      <p>This is a generated React application.</p>
    </div>
  );
}

export default App;""",
                type="text"
            )
        ]
        
        structure = {
            "public": ["index.html"],
            "src": ["index.js", "App.js"],
            "files": ["package.json"]
        }
        
        instructions = """
# Setup Instructions

1. Ensure you have Node.js 16+ and npm installed
2. Navigate to the project directory
3. Run: `npm install`
4. Run: `npm start`
5. Visit: http://localhost:3000

The application will start in development mode with hot reloading.
"""
        
        return files, structure, instructions
    
    def _generate_flask_fallback(self, prompt: str, project_name: str) -> tuple:
        """Generate basic Flask project"""
        files = [
            FileContent(
                name="requirements.txt",
                content="Flask==3.0.0\nWerkzeug==3.0.1",
                type="text"
            ),
            FileContent(
                name="app.py",
                content="""from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World from Flask!'

@app.route('/api/greeting')
def greeting():
    return jsonify({"message": "Hello World from Flask API!"})

if __name__ == '__main__':
    app.run(debug=True)""",
                type="text"
            )
        ]
        
        structure = {"files": ["requirements.txt", "app.py"]}
        
        instructions = """
# Setup Instructions

1. Ensure you have Python 3.8+ installed
2. Create a virtual environment: `python -m venv venv`
3. Activate virtual environment:
   - Windows: `venv\\Scripts\\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `python app.py`
6. Visit: http://localhost:5000

The application will start in debug mode with auto-reloading.
"""
        
        return files, structure, instructions
    
    def _generate_django_fallback(self, prompt: str, project_name: str) -> tuple:
        """Generate basic Django project"""
        files = [
            FileContent(
                name="requirements.txt",
                content="Django==4.2.8\npython-dotenv==1.0.0",
                type="text"
            ),
            FileContent(
                name=f"{project_name}/__init__.py",
                content="",
                type="text"
            ),
            FileContent(
                name=f"{project_name}/settings.py",
                content=f"""import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-dev-key-change-in-production')

DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = '{project_name}.urls'

TEMPLATES = [
    {{
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {{
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        }},
    }},
]

WSGI_APPLICATION = '{project_name}.wsgi.application'

DATABASES = {{
    'default': {{
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }}
}}

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
""",
                type="text"
            ),
            FileContent(
                name=f"{project_name}/urls.py",
                content=f"""from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
]
""",
                type="text"
            ),
            FileContent(
                name=f"{project_name}/wsgi.py",
                content=f"""import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project_name}.settings')

application = get_wsgi_application()
""",
                type="text"
            ),
            FileContent(
                name="core/__init__.py",
                content="",
                type="text"
            ),
            FileContent(
                name="core/models.py",
                content="""from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']
""",
                type="text"
            ),
            FileContent(
                name="core/views.py",
                content="""from django.http import JsonResponse
from .models import Item


def hello(request):
    return JsonResponse({'message': 'Hello from Django!', 'status': 'running'})


def items_list(request):
    items = list(Item.objects.values('id', 'name', 'description', 'created_at'))
    return JsonResponse({'items': items})
""",
                type="text"
            ),
            FileContent(
                name="core/urls.py",
                content="""from django.urls import path
from . import views

urlpatterns = [
    path('', views.hello, name='hello'),
    path('api/items/', views.items_list, name='items-list'),
]
""",
                type="text"
            ),
            FileContent(
                name="manage.py",
                content=f"""#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', '{project_name}.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
""",
                type="text"
            ),
        ]
        
        structure = {
            project_name: ["__init__.py", "settings.py", "urls.py", "wsgi.py"],
            "core": ["__init__.py", "models.py", "views.py", "urls.py"],
            "files": ["manage.py", "requirements.txt"]
        }
        
        instructions = """
# Setup Instructions

1. Ensure you have Python 3.8+ installed
2. Create a virtual environment: `python -m venv venv`
3. Activate virtual environment:
   - Windows: `venv\\Scripts\\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Run: `python manage.py runserver`
7. Visit: http://localhost:8000

The application will start in debug mode with auto-reloading.
"""
        
        return files, structure, instructions
    
    def _generate_express_fallback(self, prompt: str, project_name: str) -> tuple:
        """Generate basic Express.js project"""
        files = [
            FileContent(
                name="package.json",
                content=f"""{{
  "name": "{project_name}",
  "version": "1.0.0",
  "description": "Express.js application generated by DocuGen AI",
  "main": "src/index.js",
  "scripts": {{
    "start": "node src/index.js",
    "dev": "nodemon src/index.js"
  }},
  "dependencies": {{
    "express": "^4.18.2",
    "dotenv": "^16.3.1",
    "cors": "^2.8.5"
  }},
  "devDependencies": {{
    "nodemon": "^3.0.2"
  }}
}}""",
                type="text"
            ),
            FileContent(
                name="src/index.js",
                content=f"""const express = require('express');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

app.get('/', (req, res) => {{
  res.json({{ message: 'Hello from Express.js!', project: '{project_name}' }});
}});

app.get('/health', (req, res) => {{
  res.json({{ status: 'healthy', service: '{project_name}' }});
}});

app.listen(PORT, () => {{
  console.log(`Server running on port ${{PORT}}`);
}});

module.exports = app;
""",
                type="text"
            ),
        ]
        
        structure = {
            "src": ["index.js"],
            "files": ["package.json"]
        }
        
        instructions = """
# Setup Instructions

1. Ensure you have Node.js 16+ and npm installed
2. Navigate to the project directory
3. Run: `npm install`
4. Run: `npm run dev`
5. Visit: http://localhost:3000

The application will start with nodemon for auto-reloading.
"""
        
        return files, structure, instructions
    
    def _generate_nextjs_fallback(self, prompt: str, project_name: str) -> tuple:
        """Generate basic Next.js project"""
        files = [
            FileContent(
                name="package.json",
                content=f"""{{
  "name": "{project_name}",
  "version": "0.1.0",
  "private": true,
  "scripts": {{
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  }},
  "dependencies": {{
    "next": "14.0.4",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }},
  "devDependencies": {{
    "@types/node": "^20.10.0",
    "@types/react": "^18.2.45",
    "@types/react-dom": "^18.2.18",
    "typescript": "^5.3.3"
  }}
}}""",
                type="text"
            ),
            FileContent(
                name="src/app/layout.tsx",
                content=f"""import type {{ Metadata }} from 'next'

export const metadata: Metadata = {{
  title: '{project_name}',
  description: 'Generated by DocuGen AI',
}}

export default function RootLayout({{
  children,
}}: {{
  children: React.ReactNode
}}) {{
  return (
    <html lang="en">
      <body>{{children}}</body>
    </html>
  )
}}
""",
                type="text"
            ),
            FileContent(
                name="src/app/page.tsx",
                content=f"""export default function Home() {{
  return (
    <main style={{{{ padding: '2rem', fontFamily: 'system-ui, sans-serif' }}}}>
      <h1>Welcome to {project_name}</h1>
      <p>This is a Next.js application generated by DocuGen AI.</p>
    </main>
  )
}}
""",
                type="text"
            ),
        ]
        
        structure = {
            "src": {
                "app": ["layout.tsx", "page.tsx"],
            },
            "files": ["package.json"]
        }
        
        instructions = """
# Setup Instructions

1. Ensure you have Node.js 18+ and npm installed
2. Navigate to the project directory
3. Run: `npm install`
4. Run: `npm run dev`
5. Visit: http://localhost:3000

The application will start in development mode with hot reloading.
"""
        
        return files, structure, instructions
    
    def _generate_generic_fallback(self, prompt: str, project_name: str) -> tuple:
        """Generate generic project structure"""
        files = [
            FileContent(
                name="README.md",
                content=f"""# {project_name}

Generated project based on: {prompt}

## Description
This is a basic project structure generated by DocuGen AI.

## Setup
1. Review the generated files
2. Install any required dependencies
3. Follow technology-specific setup instructions

## Notes
- This is a basic template
- Customize according to your needs
- Add proper error handling and testing
""",
                type="text"
            )
        ]
        
        structure = {"files": ["README.md"]}
        instructions = "Please review the README.md file for basic project information."
        
        return files, structure, instructions
    
    async def get_project_zip(self, project_id: str) -> bytes:
        """Get generated project as ZIP file"""
        try:
            if project_id not in self.generated_projects:
                raise ValueError("Project not found")
            
            project = self.generated_projects[project_id]
            files = project["files"]
            
            # Create ZIP file in memory
            zip_buffer = io.BytesIO()
            
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for file_content in files:
                    zip_file.writestr(file_content.name, file_content.content)
            
            zip_buffer.seek(0)
            return zip_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Error creating project ZIP: {str(e)}")
            raise