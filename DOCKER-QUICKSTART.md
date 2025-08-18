# DocuGen AI - Docker Quick Start

## 🐳 Docker Files Overview

This repository now includes complete Docker support with the following files:

### Core Docker Files
- **`Dockerfile`** - Multi-stage production-ready container
- **`docker-compose.yml`** - Easy local development setup
- **`.dockerignore`** - Optimized build context
- **`docker-run.sh`** - Helper script for common Docker operations

### CI/CD
- **`.github/workflows/docker-publish.yml`** - Automated Docker Hub publishing

### Documentation
- **`DOCKER.md`** - Complete Docker deployment guide
- **`README.md`** - Updated with Docker quick start

## 🚀 Quick Commands

### Using Docker Compose (Recommended)
```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Using Helper Script
```bash
# Make executable (first time only)
chmod +x docker-run.sh

# Build and run
./docker-run.sh run

# View logs
./docker-run.sh logs

# Check status
./docker-run.sh status

# Stop
./docker-run.sh stop
```

### Using Docker Directly
```bash
# Build image
docker build -t neuralnotes-io:local .

# Run container
docker run -d \
  --name neuralnotes-io \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key_here \
  -v neuralnotes_data:/app/data \
  neuralnotes-io:local
```

### Using Pre-built Image (Coming Soon)
```bash
# Pull and run from Docker Hub
docker run -d \
  --name neuralnotes-io \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key_here \
  -v neuralnotes_data:/app/data \
  thecoder8890/neuralnotes-io:latest
```

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY` - Your OpenAI API key (optional for demo mode)
- `DEBUG=false` - Production mode
- `HOST=0.0.0.0` - Listen on all interfaces
- `PORT=8000` - Application port

### Volume Mounts
- `/app/data` - Persistent data storage (ChromaDB, generated projects)

## 🌐 Access Points

After starting the container:
- **Main Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## 📖 Next Steps

1. **Read the full guide**: [DOCKER.md](DOCKER.md)
2. **Set up CI/CD**: Configure GitHub secrets for Docker Hub publishing
3. **Deploy to cloud**: Use provided Kubernetes/cloud deployment examples
4. **Monitor**: Set up health checks and logging

## 🆘 Troubleshooting

### Container won't start
```bash
# Check logs
docker logs neuralnotes-io

# Check if port is in use
lsof -i :8000
```

### Build issues
```bash
# Clear Docker cache
docker system prune -a

# Rebuild without cache
docker build --no-cache -t neuralnotes-io:local .
```

### Frontend not loading
```bash
# Verify frontend build
docker exec neuralnotes-io ls -la /app/frontend/build

# Check static file serving
curl -I http://localhost:8000/static/js/
```

For more detailed troubleshooting, see [DOCKER.md](DOCKER.md).