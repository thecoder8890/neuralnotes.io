# 🐳 Docker Hub Setup Instructions

## Setting up Automated Docker Hub Publishing

To enable automated Docker image publishing to Docker Hub, follow these steps:

### 1. Create Docker Hub Account and Repository

1. **Sign up for Docker Hub**: https://hub.docker.com/
2. **Create a new repository**: 
   - Repository name: `neuralnotes-io`
   - Description: "DocuGen AI - Documentation-aware project scaffolding engine"
   - Visibility: Public

### 2. Generate Docker Hub Access Token

1. Go to **Account Settings** → **Security** → **New Access Token**
2. **Token description**: "GitHub Actions - neuralnotes.io"
3. **Access permissions**: Read, Write, Delete
4. **Copy the token** (you won't see it again)

### 3. Configure GitHub Repository Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Add the following secrets:

```
DOCKER_USERNAME: your_dockerhub_username
DOCKER_PASSWORD: your_dockerhub_access_token
```

### 4. Update GitHub Actions Workflow (if needed)

The workflow file `.github/workflows/docker-publish.yml` is already configured to use these secrets.

If you want to use a different Docker Hub username or repository name, update the `IMAGE_NAME` in the workflow:

```yaml
env:
  REGISTRY: docker.io
  IMAGE_NAME: your-custom-name  # Change this if needed
```

### 5. Trigger the First Build

**Option A: Push to main branch**
```bash
git checkout main
git merge your-feature-branch
git push origin main
```

**Option B: Create a tag**
```bash
git tag v1.0.0
git push origin v1.0.0
```

### 6. Verify the Build

1. Go to **Actions** tab in your GitHub repository
2. Watch the "Build and Publish Docker Image" workflow
3. Check Docker Hub for the published image

## 📋 Expected Docker Hub Tags

After successful CI/CD setup, you'll have:

- `latest` - Latest stable build from main branch
- `main` - Latest commit on main branch  
- `v1.0.0` - Specific version tags
- `pr-123` - Pull request builds (for testing)

## 🚀 Using Published Images

Once published, users can run:

```bash
# Latest stable version
docker run -p 8000:8000 your-username/neuralnotes-io:latest

# Specific version
docker run -p 8000:8000 your-username/neuralnotes-io:v1.0.0

# With environment variables
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=sk-... \
  -v neuralnotes_data:/app/data \
  your-username/neuralnotes-io:latest
```

## 🔍 Monitoring and Maintenance

### Check Build Status
- GitHub Actions tab shows build history
- Docker Hub shows image details and pull statistics

### Update Dependencies
- Dependabot can update Dockerfile dependencies
- Regular rebuilds ensure security patches

### Image Size Optimization
Current multi-stage build is optimized, but you can:
- Monitor image size in Docker Hub
- Use `docker images` to check local sizes
- Consider Alpine variants for smaller images

## 🛠️ Troubleshooting

### Build Fails
1. Check GitHub Actions logs
2. Verify secrets are set correctly
3. Test Dockerfile locally: `docker build .`

### Authentication Issues
1. Regenerate Docker Hub access token
2. Update GitHub secrets
3. Ensure token has correct permissions

### Image Not Found
1. Check if build completed successfully
2. Verify repository name matches
3. Check Docker Hub repository visibility

## 📞 Support

For issues with:
- **Docker Hub**: Check Docker Hub documentation
- **GitHub Actions**: Review workflow logs
- **Application**: See main README.md and DOCKER.md

---

✅ **Setup Complete!** Your neuralnotes.io project now has full Docker containerization with automated publishing to Docker Hub.