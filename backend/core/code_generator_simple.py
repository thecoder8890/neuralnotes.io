import os
import json
import uuid
import logging
import zipfile
import io
from typing import Dict, List, Any, Optional
from datetime import datetime
from backend.models.schemas import GenerationResponse, FileContent, Technology

logger = logging.getLogger(__name__)

class CodeGenerator:
    """Simplified code generator for demonstration"""
    
    def __init__(self):
        self.generated_projects = {}  # In-memory storage for generated projects
        logger.info("CodeGenerator initialized (simplified mode)")
    
    async def generate_project(self, doc_id: str, prompt: str, technology: Optional[Technology] = None) -> GenerationResponse:
        """Generate a complete project based on documentation and user prompt"""
        try:
            project_id = str(uuid.uuid4())
            
            logger.info(f"Generating project for prompt: {prompt}")
            
            # Determine technology from prompt if not specified
            if not technology:
                technology = self._detect_technology(prompt)
            
            # Generate project structure and files
            files, structure, instructions = self._generate_project_files(prompt, technology)
            
            # Store generated project
            self.generated_projects[project_id] = {
                "files": files,
                "structure": structure,
                "instructions": instructions,
                "generated_at": datetime.now().isoformat(),
                "prompt": prompt,
                "technology": technology
            }
            
            logger.info(f"Project {project_id} generated successfully")
            
            return GenerationResponse(
                project_id=project_id,
                files=files,
                structure=structure,
                instructions=instructions
            )
            
        except Exception as e:
            logger.error(f"Error generating project: {str(e)}")
            raise
    
    def _detect_technology(self, prompt: str) -> Optional[Technology]:
        """Detect technology from prompt"""
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['spring', 'java', 'maven', 'gradle']):
            return Technology.SPRING_BOOT
        elif any(word in prompt_lower for word in ['react', 'jsx', 'tsx']):
            return Technology.REACT
        elif any(word in prompt_lower for word in ['django', 'python web']):
            return Technology.DJANGO
        elif any(word in prompt_lower for word in ['flask', 'python api', 'python rest']):
            return Technology.FLASK
        elif any(word in prompt_lower for word in ['express', 'node', 'nodejs']):
            return Technology.EXPRESS
        elif any(word in prompt_lower for word in ['next', 'nextjs']):
            return Technology.NEXTJS
        
        return None
    
    def _generate_project_files(self, prompt: str, technology: Optional[Technology]) -> tuple:
        """Generate project files based on technology"""
        
        if technology == Technology.SPRING_BOOT:
            return self._generate_spring_boot_project(prompt)
        elif technology == Technology.REACT:
            return self._generate_react_project(prompt)
        elif technology == Technology.FLASK:
            return self._generate_flask_project(prompt)
        elif technology == Technology.DJANGO:
            return self._generate_django_project(prompt)
        elif technology == Technology.EXPRESS:
            return self._generate_express_project(prompt)
        elif technology == Technology.NEXTJS:
            return self._generate_nextjs_project(prompt)
        else:
            return self._generate_generic_project(prompt)
    
    def _generate_spring_boot_project(self, prompt: str) -> tuple:
        """Generate Spring Boot project"""
        project_name = "demo-app"
        
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
        {'<dependency><groupId>org.springframework.boot</groupId><artifactId>spring-boot-starter-data-jpa</artifactId></dependency>' if 'jpa' in prompt.lower() or 'database' in prompt.lower() else ''}
        {'<dependency><groupId>org.postgresql</groupId><artifactId>postgresql</artifactId><scope>runtime</scope></dependency>' if 'postgres' in prompt.lower() else ''}
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
                name="src/main/java/com/example/controller/HomeController.java",
                content="""package com.example.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class HomeController {
    
    @GetMapping("/hello")
    public String hello() {
        return "Hello from Spring Boot!";
    }
}""",
                type="text"
            ),
            FileContent(
                name="src/main/resources/application.properties",
                content="""# Application configuration
server.port=8080

# Database configuration (if using JPA)
# spring.datasource.url=jdbc:postgresql://localhost:5432/mydb
# spring.datasource.username=user
# spring.datasource.password=password
# spring.jpa.hibernate.ddl-auto=update""",
                type="text"
            ),
            FileContent(
                name="README.md",
                content=f"""# {project_name}

Spring Boot application generated based on: {prompt}

## Getting Started

### Prerequisites
- Java 17+
- Maven 3.6+

### Running the Application

1. Build the project:
   ```bash
   mvn clean compile
   ```

2. Run the application:
   ```bash
   mvn spring-boot:run
   ```

3. Access the application:
   - API: http://localhost:8080/api/hello

## Project Structure

- `src/main/java/com/example/` - Main application code
- `src/main/resources/` - Configuration files
- `pom.xml` - Maven dependencies and build configuration

## Features

- Spring Boot web application
- REST API endpoints
- Auto-configuration
{'- JPA/Database integration' if 'jpa' in prompt.lower() or 'database' in prompt.lower() else ''}
{'- PostgreSQL support' if 'postgres' in prompt.lower() else ''}
""",
                type="text"
            )
        ]
        
        structure = {
            "src": {
                "main": {
                    "java": {
                        "com": {
                            "example": ["Application.java"],
                            "controller": ["HomeController.java"]
                        }
                    },
                    "resources": ["application.properties"]
                }
            },
            "files": ["pom.xml", "README.md"]
        }
        
        instructions = """# Setup Instructions

1. Prerequisites:
   - Install Java 17 or later
   - Install Maven 3.6 or later

2. Build and run:
   ```bash
   mvn clean compile
   mvn spring-boot:run
   ```

3. Access the application:
   - API endpoint: http://localhost:8080/api/hello
   - API docs (if Swagger added): http://localhost:8080/swagger-ui.html

4. Development:
   - The application will auto-reload when you make changes
   - Add new controllers in the controller package
   - Configure database settings in application.properties

5. Testing:
   ```bash
   mvn test
   ```

The application includes a basic REST endpoint and is ready for further development."""
        
        return files, structure, instructions
    
    def _generate_react_project(self, prompt: str) -> tuple:
        """Generate React project"""
        project_name = "react-app"
        
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
    "react-scripts": "5.0.1",
    {"\"axios\": \"^1.6.0\"," if 'api' in prompt.lower() or 'fetch' in prompt.lower() else ""}
    {"\"react-router-dom\": \"^6.8.0\"," if 'router' in prompt.lower() or 'navigation' in prompt.lower() else ""}
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "typescript": "^4.9.0"
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
                name="src/index.tsx",
                content="""import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(
  document.getElementById('root') as HTMLElement
);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);""",
                type="text"
            ),
            FileContent(
                name="src/App.tsx",
                content=f"""import React from 'react';
import './App.css';

function App() {{
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to {project_name}</h1>
        <p>Generated based on: {prompt}</p>
        {'<p>Ready for API integration!</p>' if 'api' in prompt.lower() else ''}
        {'<p>Ready for routing and navigation!</p>' if 'router' in prompt.lower() else ''}
      </header>
    </div>
  );
}}

export default App;""",
                type="text"
            ),
            FileContent(
                name="src/App.css",
                content=""".App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.App-header h1 {
  margin-bottom: 16px;
}

.App-header p {
  margin: 8px 0;
}""",
                type="text"
            ),
            FileContent(
                name="src/index.css",
                content="""body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}""",
                type="text"
            ),
            FileContent(
                name="tsconfig.json",
                content="""{
  "compilerOptions": {
    "target": "es5",
    "lib": [
      "dom",
      "dom.iterable",
      "es6"
    ],
    "allowJs": true,
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true,
    "module": "esnext",
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": [
    "src"
  ]
}""",
                type="text"
            ),
            FileContent(
                name="README.md",
                content=f"""# {project_name}

React TypeScript application generated based on: {prompt}

## Getting Started

### Prerequisites
- Node.js 16+
- npm or yarn

### Running the Application

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start development server:
   ```bash
   npm start
   ```

3. Access the application:
   - App: http://localhost:3000

## Project Structure

- `src/` - React components and TypeScript code
- `public/` - Static assets
- `package.json` - Dependencies and scripts

## Features

- React 18 with TypeScript
- Modern development setup
- Hot reloading
{'- API integration ready (axios included)' if 'api' in prompt.lower() else ''}
{'- Routing ready (react-router-dom included)' if 'router' in prompt.lower() else ''}

## Available Scripts

- `npm start` - Development server
- `npm run build` - Production build
- `npm test` - Run tests
""",
                type="text"
            )
        ]
        
        structure = {
            "public": ["index.html"],
            "src": ["index.tsx", "App.tsx", "App.css", "index.css"],
            "files": ["package.json", "tsconfig.json", "README.md"]
        }
        
        instructions = """# Setup Instructions

1. Prerequisites:
   - Install Node.js 16 or later
   - npm comes with Node.js

2. Install and run:
   ```bash
   npm install
   npm start
   ```

3. Access the application:
   - Development server: http://localhost:3000
   - Hot reloading is enabled for development

4. Build for production:
   ```bash
   npm run build
   ```

5. Testing:
   ```bash
   npm test
   ```

The application is set up with TypeScript for type safety and includes modern React patterns."""
        
        return files, structure, instructions
    
    def _generate_flask_project(self, prompt: str) -> tuple:
        """Generate Flask project"""
        project_name = "flask-app"
        
        files = [
            FileContent(
                name="requirements.txt",
                content="""Flask==3.0.0
Werkzeug==3.0.1
python-dotenv==1.0.0
Flask-CORS==4.0.0""" + ("""
SQLAlchemy==2.0.23
Flask-SQLAlchemy==3.1.1""" if 'database' in prompt.lower() or 'sql' in prompt.lower() else "") + ("""
Flask-JWT-Extended==4.6.0""" if 'auth' in prompt.lower() or 'jwt' in prompt.lower() else ""),
                type="text"
            ),
            FileContent(
                name="app.py",
                content=f"""from flask import Flask, jsonify, request
from flask_cors import CORS
{"from flask_sqlalchemy import SQLAlchemy" if 'database' in prompt.lower() else ""}
{"from flask_jwt_extended import JWTManager" if 'auth' in prompt.lower() else ""}
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
{"app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')" if 'database' in prompt.lower() else ""}
{"app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key')" if 'auth' in prompt.lower() else ""}

# Initialize extensions
{"db = SQLAlchemy(app)" if 'database' in prompt.lower() else ""}
{"jwt = JWTManager(app)" if 'auth' in prompt.lower() else ""}

@app.route('/')
def hello():
    return jsonify({{"message": "Hello from Flask!", "project": "{project_name}"}})

@app.route('/api/status')
def status():
    return jsonify({{"status": "running", "message": "Flask API is working"}})

{"@app.route('/api/health')" if 'health' in prompt.lower() or 'api' in prompt.lower() else ""}
{"def health():" if 'health' in prompt.lower() or 'api' in prompt.lower() else ""}
{"    return jsonify({'status': 'healthy', 'service': 'flask-app'})" if 'health' in prompt.lower() or 'api' in prompt.lower() else ""}

# Database models (if using database)
{"class User(db.Model):" if 'database' in prompt.lower() else ""}
{"    id = db.Column(db.Integer, primary_key=True)" if 'database' in prompt.lower() else ""}
{"    name = db.Column(db.String(100), nullable=False)" if 'database' in prompt.lower() else ""}
{"    email = db.Column(db.String(100), unique=True, nullable=False)" if 'database' in prompt.lower() else ""}

{"@app.before_first_request" if 'database' in prompt.lower() else ""}
{"def create_tables():" if 'database' in prompt.lower() else ""}
{"    db.create_all()" if 'database' in prompt.lower() else ""}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)""",
                type="text"
            ),
            FileContent(
                name=".env.example",
                content="""SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
DATABASE_URL=sqlite:///app.db
FLASK_ENV=development""",
                type="text"
            ),
            FileContent(
                name="README.md",
                content=f"""# {project_name}

Flask application generated based on: {prompt}

## Getting Started

### Prerequisites
- Python 3.8+
- pip

### Running the Application

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Access the application:
   - API: http://localhost:5000
   - Status: http://localhost:5000/api/status

## Project Structure

- `app.py` - Main Flask application
- `requirements.txt` - Python dependencies
- `.env` - Environment configuration

## Features

- Flask web framework
- CORS enabled for frontend integration
- Environment configuration
{'- Database integration with SQLAlchemy' if 'database' in prompt.lower() else ''}
{'- JWT authentication support' if 'auth' in prompt.lower() else ''}
- Development server with auto-reload

## API Endpoints

- `GET /` - Welcome message
- `GET /api/status` - Service status
{'- `GET /api/health` - Health check' if 'health' in prompt.lower() else ''}
""",
                type="text"
            )
        ]
        
        structure = {
            "files": ["app.py", "requirements.txt", ".env.example", "README.md"]
        }
        
        instructions = """# Setup Instructions

1. Prerequisites:
   - Install Python 3.8 or later
   - pip comes with Python

2. Setup and run:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   python app.py
   ```

3. Access the application:
   - API server: http://localhost:5000
   - Development mode includes auto-reload

4. For production:
   - Use a proper WSGI server like Gunicorn
   - Set environment variables properly
   - Configure a production database

The Flask application is ready for API development and includes CORS for frontend integration."""
        
        return files, structure, instructions
    
    def _generate_django_project(self, prompt: str) -> tuple:
        """Generate Django project"""
        project_name = "django_app"

        has_api = 'api' in prompt.lower() or 'rest' in prompt.lower()
        has_auth = 'auth' in prompt.lower() or 'login' in prompt.lower()
        has_db = 'database' in prompt.lower() or 'model' in prompt.lower() or 'sql' in prompt.lower()

        requirements = """Django==4.2.8
python-dotenv==1.0.0""" + ("""
djangorestframework==3.14.0""" if has_api else "") + ("""
django-cors-headers==4.3.1""" if has_api else "")

        files = [
            FileContent(
                name="requirements.txt",
                content=requirements,
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
    {'"rest_framework",' if has_api else ''}
    {'"corsheaders",' if has_api else ''}
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    {'"corsheaders.middleware.CorsMiddleware",' if has_api else ''}
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

{f"CORS_ALLOW_ALL_ORIGINS = DEBUG" if has_api else ""}
{f"REST_FRAMEWORK = {{'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny']}}" if has_api else ""}
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
                content=f"""from django.http import JsonResponse
{"from rest_framework.decorators import api_view" if has_api else ""}
{"from rest_framework.response import Response" if has_api else ""}
from .models import Item


{"@api_view(['GET'])" if has_api else ""}
def hello(request):
    {"return Response({'message': 'Hello from Django REST API!', 'status': 'running'})" if has_api else "return JsonResponse({'message': 'Hello from Django!', 'status': 'running'})"}


{"@api_view(['GET'])" if has_api else ""}
def items_list(request):
    items = list(Item.objects.values('id', 'name', 'description', 'created_at'))
    {"return Response({'items': items})" if has_api else "return JsonResponse({'items': items})"}
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
            FileContent(
                name=".env.example",
                content="""SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
""",
                type="text"
            ),
            FileContent(
                name="README.md",
                content=f"""# {project_name}

Django application generated based on: {prompt}

## Getting Started

### Prerequisites
- Python 3.8+
- pip

### Running the Application

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment:
   ```bash
   cp .env.example .env
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Run the development server:
   ```bash
   python manage.py runserver
   ```

6. Access the application:
   - App: http://localhost:8000
   - Admin: http://localhost:8000/admin

## Features

- Django web framework
- SQLite database (configurable)
{f'- Django REST Framework for API endpoints' if has_api else ''}
{f'- CORS support for frontend integration' if has_api else ''}
{f'- Authentication support' if has_auth else ''}
""",
                type="text"
            ),
        ]

        structure = {
            project_name: ["settings.py", "urls.py", "wsgi.py"],
            "core": ["__init__.py", "models.py", "views.py", "urls.py"],
            "files": ["manage.py", "requirements.txt", ".env.example", "README.md"]
        }

        instructions = f"""# Setup Instructions

1. Prerequisites:
   - Install Python 3.8 or later

2. Setup and run:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   cp .env.example .env
   python manage.py migrate
   python manage.py runserver
   ```

3. Access the application:
   - Development server: http://localhost:8000
   - Admin panel: http://localhost:8000/admin (create superuser first)

4. Create admin superuser:
   ```bash
   python manage.py createsuperuser
   ```

5. API endpoints:
   - GET / - Hello message
   - GET /api/items/ - List items

The Django application includes a core app with models, views, and URL routing."""

        return files, structure, instructions

    def _generate_express_project(self, prompt: str) -> tuple:
        """Generate Express.js project"""
        project_name = "express-app"

        has_db = 'database' in prompt.lower() or 'mongo' in prompt.lower() or 'sql' in prompt.lower()
        has_auth = 'auth' in prompt.lower() or 'jwt' in prompt.lower() or 'login' in prompt.lower()
        has_mongo = 'mongo' in prompt.lower()

        dependencies: dict = {
            "express": "^4.18.2",
            "dotenv": "^16.3.1",
            "cors": "^2.8.5",
        }
        if has_auth:
            dependencies["jsonwebtoken"] = "^9.0.2"
            dependencies["bcryptjs"] = "^2.4.3"
        if has_mongo:
            dependencies["mongoose"] = "^8.0.3"

        dev_dependencies: dict = {
            "nodemon": "^3.0.2"
        }

        deps_json = ',\n    '.join(f'"{k}": "{v}"' for k, v in dependencies.items())
        dev_deps_json = ',\n    '.join(f'"{k}": "{v}"' for k, v in dev_dependencies.items())

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
    {deps_json}
  }},
  "devDependencies": {{
    {dev_deps_json}
  }}
}}""",
                type="text"
            ),
            FileContent(
                name="src/index.js",
                content=f"""const express = require('express');
const cors = require('cors');
require('dotenv').config();
{"const mongoose = require('mongoose');" if has_mongo else ""}

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.use('/api', require('./routes/api'));

// Health check
app.get('/health', (req, res) => {{
  res.json({{ status: 'healthy', service: '{project_name}' }});
}});

{"// MongoDB connection" if has_mongo else ""}
{f"mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/{project_name}').then(() => console.log('MongoDB connected')).catch(err => console.error('MongoDB error:', err));" if has_mongo else ""}

app.listen(PORT, () => {{
  console.log(`Server running on port ${{PORT}}`);
}});

module.exports = app;
""",
                type="text"
            ),
            FileContent(
                name="src/routes/api.js",
                content=f"""const express = require('express');
const router = express.Router();
{"const jwt = require('jsonwebtoken');" if has_auth else ""}

// Welcome route
router.get('/', (req, res) => {{
  res.json({{ message: 'Hello from Express.js API!', version: '1.0.0' }});
}});

// Example items endpoint
const items = [
  {{ id: 1, name: 'Item 1', description: 'First item' }},
  {{ id: 2, name: 'Item 2', description: 'Second item' }},
];

router.get('/items', (req, res) => {{
  res.json({{ items, total: items.length }});
}});

router.get('/items/:id', (req, res) => {{
  const item = items.find(i => i.id === parseInt(req.params.id));
  if (!item) return res.status(404).json({{ error: 'Item not found' }});
  res.json(item);
}});

router.post('/items', (req, res) => {{
  const {{ name, description }} = req.body;
  if (!name) return res.status(400).json({{ error: 'Name is required' }});
  const newItem = {{ id: items.length + 1, name, description: description || '' }};
  items.push(newItem);
  res.status(201).json(newItem);
}});

{"// Auth routes" if has_auth else ""}
{f"""router.post('/auth/login', (req, res) => {{
  const {{ username, password }} = req.body;
  // TODO: validate credentials against your user store
  if (username === 'admin' && password === 'password') {{
    const token = jwt.sign({{ username }}, process.env.JWT_SECRET || 'secret', {{ expiresIn: '1h' }});
    res.json({{ token }});
  }} else {{
    res.status(401).json({{ error: 'Invalid credentials' }});
  }}
}});""" if has_auth else ""}

module.exports = router;
""",
                type="text"
            ),
            FileContent(
                name=".env.example",
                content=f"""PORT=3000
NODE_ENV=development
{"JWT_SECRET=your-jwt-secret-here" if has_auth else ""}
{"MONGODB_URI=mongodb://localhost:27017/" + project_name if has_mongo else ""}
""",
                type="text"
            ),
            FileContent(
                name=".gitignore",
                content="""node_modules/
.env
*.log
""",
                type="text"
            ),
            FileContent(
                name="README.md",
                content=f"""# {project_name}

Express.js application generated based on: {prompt}

## Getting Started

### Prerequisites
- Node.js 16+
- npm

### Running the Application

1. Install dependencies:
   ```bash
   npm install
   ```

2. Set up environment:
   ```bash
   cp .env.example .env
   ```

3. Run development server:
   ```bash
   npm run dev
   ```

4. Access the application:
   - API: http://localhost:3000/api
   - Health: http://localhost:3000/health

## API Endpoints

- `GET /health` - Health check
- `GET /api` - Welcome message
- `GET /api/items` - List all items
- `GET /api/items/:id` - Get item by ID
- `POST /api/items` - Create new item
{f'- `POST /api/auth/login` - Authenticate user' if has_auth else ''}

## Features

- Express.js web framework
- CORS enabled
- Environment configuration
{f'- JWT authentication' if has_auth else ''}
{f'- MongoDB/Mongoose integration' if has_mongo else ''}
""",
                type="text"
            ),
        ]

        structure = {
            "src": {
                "routes": ["api.js"],
            },
            "files": ["package.json", ".env.example", ".gitignore", "README.md"]
        }

        instructions = f"""# Setup Instructions

1. Prerequisites:
   - Install Node.js 16 or later

2. Install and run:
   ```bash
   npm install
   cp .env.example .env
   npm run dev
   ```

3. Access the application:
   - API server: http://localhost:3000
   - Development mode includes auto-reload via nodemon

4. For production:
   ```bash
   npm start
   ```

The Express.js application includes CORS support, structured routing, and example CRUD endpoints."""

        return files, structure, instructions

    def _generate_nextjs_project(self, prompt: str) -> tuple:
        """Generate Next.js project"""
        project_name = "nextjs-app"

        has_api = 'api' in prompt.lower() or 'backend' in prompt.lower()
        has_auth = 'auth' in prompt.lower() or 'login' in prompt.lower()

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
    "typescript": "^5.3.3",
    "eslint": "^8.56.0",
    "eslint-config-next": "14.0.4"
  }}
}}""",
                type="text"
            ),
            FileContent(
                name="tsconfig.json",
                content="""{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{"name": "next"}],
    "paths": {"@/*": ["./src/*"]}
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}""",
                type="text"
            ),
            FileContent(
                name="next.config.js",
                content="""/** @type {import('next').NextConfig} */
const nextConfig = {}

module.exports = nextConfig
""",
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
      <p>Generated based on: {prompt}</p>
      <p>
        Get started by editing{' '}
        <code>src/app/page.tsx</code>
      </p>
      {f'<p><a href="/api/hello">View API example</a></p>' if has_api else ''}
    </main>
  )
}}
""",
                type="text"
            ),
            FileContent(
                name="src/app/globals.css",
                content="""* {
  box-sizing: border-box;
  padding: 0;
  margin: 0;
}

body {
  max-width: 1200px;
  margin: 0 auto;
  font-family: system-ui, -apple-system, sans-serif;
}

a {
  color: inherit;
  text-decoration: none;
}
""",
                type="text"
            ),
        ]

        if has_api:
            files.append(FileContent(
                name="src/app/api/hello/route.ts",
                content="""import { NextResponse } from 'next/server'

export async function GET() {
  return NextResponse.json({
    message: 'Hello from Next.js API!',
    timestamp: new Date().toISOString(),
  })
}
""",
                type="text"
            ))

        files.extend([
            FileContent(
                name=".env.example",
                content=f"""NEXTAUTH_SECRET=your-secret-here
NEXTAUTH_URL=http://localhost:3000
{"# Add your API keys below" if has_auth else ""}
""",
                type="text"
            ),
            FileContent(
                name=".gitignore",
                content="""node_modules/
.next/
.env
*.log
""",
                type="text"
            ),
            FileContent(
                name="README.md",
                content=f"""# {project_name}

Next.js application generated based on: {prompt}

## Getting Started

### Prerequisites
- Node.js 18+
- npm

### Running the Application

1. Install dependencies:
   ```bash
   npm install
   ```

2. Run the development server:
   ```bash
   npm run dev
   ```

3. Access the application:
   - App: http://localhost:3000
   {f'- API: http://localhost:3000/api/hello' if has_api else ''}

## Project Structure

- `src/app/` - App Router pages and layouts
- `src/app/api/` - API route handlers
- `public/` - Static assets

## Features

- Next.js 14 with App Router
- TypeScript for type safety
- Server and client components
{f'- API route handlers' if has_api else ''}
{f'- Authentication ready' if has_auth else ''}

## Available Scripts

- `npm run dev` - Development server
- `npm run build` - Production build
- `npm start` - Production server
- `npm run lint` - Lint code
""",
                type="text"
            ),
        ])

        structure = {
            "src": {
                "app": (["layout.tsx", "page.tsx", "globals.css", "api/hello/route.ts"]
                        if has_api else ["layout.tsx", "page.tsx", "globals.css"]),
            },
            "files": ["package.json", "tsconfig.json", "next.config.js", ".env.example", ".gitignore", "README.md"]
        }

        instructions = f"""# Setup Instructions

1. Prerequisites:
   - Install Node.js 18 or later

2. Install and run:
   ```bash
   npm install
   npm run dev
   ```

3. Access the application:
   - Development server: http://localhost:3000
   - Hot reloading is enabled

4. Build for production:
   ```bash
   npm run build
   npm start
   ```

The Next.js application uses the App Router with TypeScript and includes server-side rendering support."""

        return files, structure, instructions

    def _generate_generic_project(self, prompt: str) -> tuple:
        """Generate generic project"""
        files = [
            FileContent(
                name="README.md",
                content=f"""# Generated Project

Project generated based on: {prompt}

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
- Consider security best practices

## Next Steps
1. Set up your development environment
2. Install dependencies for your chosen technology
3. Implement the core functionality
4. Add tests and documentation
5. Deploy to your preferred platform
""",
                type="text"
            )
        ]
        
        structure = {"files": ["README.md"]}
        instructions = "Please review the README.md file for basic project information and next steps."
        
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