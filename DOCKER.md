# Docker Deployment Guide for DocuGen AI

This guide covers Docker deployment options for DocuGen AI.

## Quick Start with Docker

### Option 1: Using Pre-built Image from Docker Hub

```bash
# Pull and run the latest image
docker run -d \
  --name neuralnotes-io \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  -v neuralnotes_data:/app/data \
  thecoder8890/neuralnotes-io:latest
```

### Option 2: Using Docker Compose (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/thecoder8890/neuralnotes.io.git
   cd neuralnotes.io
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and set your OPENAI_API_KEY
   ```

3. **Start with Docker Compose:**
   ```bash
   docker-compose up -d
   ```

4. **Access the application:**
   - Open http://localhost:8000 in your browser

### Option 3: Build from Source

```bash
# Clone repository
git clone https://github.com/thecoder8890/neuralnotes.io.git
cd neuralnotes.io

# Build the Docker image
docker build -t neuralnotes-io:local .

# Run the container
docker run -d \
  --name neuralnotes-io \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_openai_api_key_here \
  -v neuralnotes_data:/app/data \
  neuralnotes-io:local
```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key for full functionality | - | No* |
| `DEBUG` | Enable debug mode | `false` | No |
| `HOST` | Host to bind to | `0.0.0.0` | No |
| `PORT` | Port to listen on | `8000` | No |
| `CHROMA_DB_PATH` | Path to ChromaDB data | `/app/data/chroma_db` | No |

*Note: The application works in simplified mode without OpenAI API key.

## Volume Mounts

### Data Persistence
Mount `/app/data` to persist ChromaDB and generated projects:
```bash
-v neuralnotes_data:/app/data
```

### Custom Configuration
Mount a custom `.env` file:
```bash
-v /path/to/your/.env:/app/.env
```

## Production Deployment

### Docker Compose for Production

```yaml
version: '3.8'
services:
  neuralnotes:
    image: thecoder8890/neuralnotes-io:latest
    ports:
      - "8000:8000"
    environment:
      - DEBUG=false
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - neuralnotes_data:/app/data
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - neuralnotes
    restart: unless-stopped

volumes:
  neuralnotes_data:
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: neuralnotes-io
spec:
  replicas: 2
  selector:
    matchLabels:
      app: neuralnotes-io
  template:
    metadata:
      labels:
        app: neuralnotes-io
    spec:
      containers:
      - name: neuralnotes-io
        image: thecoder8890/neuralnotes-io:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: neuralnotes-secrets
              key: openai-api-key
        volumeMounts:
        - name: data-volume
          mountPath: /app/data
        resources:
          limits:
            memory: "1Gi"
            cpu: "500m"
          requests:
            memory: "512Mi"
            cpu: "250m"
      volumes:
      - name: data-volume
        persistentVolumeClaim:
          claimName: neuralnotes-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: neuralnotes-service
spec:
  selector:
    app: neuralnotes-io
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Health Checks and Monitoring

The Docker image includes built-in health checks:

```bash
# Check container health
docker inspect neuralnotes-io | grep -A 10 Health

# Manual health check
curl http://localhost:8000/api/health
```

## Troubleshooting

### Container Won't Start
1. Check logs:
   ```bash
   docker logs neuralnotes-io
   ```

2. Verify environment variables:
   ```bash
   docker exec neuralnotes-io env | grep -E "(OPENAI|DEBUG|PORT)"
   ```

### Frontend Not Loading
1. Verify frontend build was successful:
   ```bash
   docker exec neuralnotes-io ls -la /app/frontend/build
   ```

2. Check if the app is serving static files:
   ```bash
   curl -I http://localhost:8000/static/js/
   ```

### Performance Issues
1. Increase memory limits:
   ```bash
   docker run --memory=1g --cpus=1 neuralnotes-io:latest
   ```

2. Monitor resource usage:
   ```bash
   docker stats neuralnotes-io
   ```

## Development with Docker

### Development Environment
```bash
# Use docker-compose for development
docker-compose -f docker-compose.dev.yml up
```

### Debugging
```bash
# Run with debug mode
docker run -e DEBUG=true neuralnotes-io:latest

# Access container shell
docker exec -it neuralnotes-io bash
```

## Security Considerations

1. **Run as non-root user**: The image uses a non-root user `app`
2. **Environment variables**: Never include secrets in the image
3. **Network isolation**: Use Docker networks to isolate containers
4. **Volume security**: Properly configure volume permissions
5. **Image scanning**: Regularly scan images for vulnerabilities

## CI/CD Integration

The repository includes GitHub Actions for automated Docker builds:

1. **Automatic builds** on push to main branch
2. **Multi-platform images** (amd64, arm64)
3. **Docker Hub publishing** with version tags
4. **Security scanning** and vulnerability checks

### Setup GitHub Actions

1. Add Docker Hub credentials to GitHub Secrets:
   - `DOCKER_USERNAME`: Your Docker Hub username
   - `DOCKER_PASSWORD`: Your Docker Hub access token

2. Push to main branch to trigger automated build and publish