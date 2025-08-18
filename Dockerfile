# DocuGen AI - Multi-stage Dockerfile
# Stage 1: Build frontend with Node.js
FROM node:18-alpine AS frontend-builder

# Set npm timeout and cache configuration for reliability
ENV NPM_CONFIG_TIMEOUT=60000
ENV NPM_CONFIG_FETCH_TIMEOUT=60000

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package.json frontend/package-lock.json ./

# Install frontend dependencies with timeout settings
RUN npm ci --only=production || npm install

# Copy frontend source code
COPY frontend/ ./

# Build frontend for production
RUN npm run build

# Stage 2: Python runtime with backend
FROM python:3.11-slim AS backend

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Create app directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies with fallback for minimal functionality
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org \
    fastapi uvicorn python-multipart pydantic python-dotenv requests beautifulsoup4 markdown || \
    pip install fastapi uvicorn python-multipart pydantic python-dotenv

# Try to install full requirements if possible
RUN pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org \
    -r requirements.txt 2>/dev/null || echo "Using minimal dependency setup"

# Copy backend source code
COPY . .

# Copy built frontend from frontend-builder stage
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Create data directory for database persistence
RUN mkdir -p data

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Default command
CMD ["python", "main.py"]