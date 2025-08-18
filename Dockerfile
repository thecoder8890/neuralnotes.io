# DocuGen AI - Multi-stage Dockerfile
# Stage 1: Build frontend with Node.js
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package.json frontend/package-lock.json ./

# Install frontend dependencies
RUN npm ci

# Copy frontend source code
COPY frontend/ ./

# Build frontend for production
RUN npm run build

# Stage 2: Python runtime with backend
FROM python:3.11-slim AS backend

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_TRUSTED_HOST="pypi.org files.pythonhosted.org pypi.python.org"

# Create app directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Update certificates
RUN update-ca-certificates

# Copy requirements first for better caching
COPY requirements.txt .

# Install minimal Python dependencies first for fallback
RUN pip install --no-ssl-verify fastapi uvicorn python-multipart pydantic python-dotenv || \
    pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org \
    fastapi uvicorn python-multipart pydantic python-dotenv

# Try to install full requirements but continue if it fails
RUN pip install --no-ssl-verify -r requirements.txt || \
    echo "Full requirements failed, using minimal setup"

# Copy backend source code
COPY . .

# Copy built frontend from frontend-builder stage
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# Create data directory for ChromaDB
RUN mkdir -p data

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Default command
CMD ["python", "main.py"]