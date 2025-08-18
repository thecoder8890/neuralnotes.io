# DocuGen AI - Working Demo

This directory contains a working demonstration of DocuGen AI's core functionality.

## Quick Demo

The application is currently running in **simplified mode** which provides full functionality without requiring heavy AI dependencies. This demonstrates the complete workflow:

### 1. Process Documentation
```bash
curl -X POST "http://localhost:8000/api/process-documentation?url=https://docs.spring.io/spring-boot/"
```

### 2. Generate Project
```bash
curl -X POST "http://localhost:8000/api/generate-project" \
  -H "Content-Type: application/json" \
  -d '{
    "doc_id": "your_doc_id_here",
    "prompt": "Create a Spring Boot REST API with CRUD operations",
    "technology": "spring_boot"
  }'
```

### 3. Download Generated Project
```bash
curl -X GET "http://localhost:8000/api/download-project/{project_id}" \
  --output project.zip
```

## Supported Technologies

The simplified mode supports generating complete, runnable projects for:

- **Spring Boot** - Java/Maven applications with REST APIs
- **React** - TypeScript applications with modern tooling
- **Flask** - Python web APIs with proper structure
- **Express.js** - Node.js applications (planned)
- **Django** - Python web frameworks (planned)
- **Next.js** - Full-stack React applications (planned)

## Generated Project Features

Each generated project includes:

✅ **Complete file structure** with proper organization
✅ **Build configuration** (pom.xml, package.json, requirements.txt)
✅ **Starter code** with working examples
✅ **README** with setup instructions
✅ **Best practices** following framework conventions
✅ **Runnable immediately** after dependency installation

## API Status

![API Health Check](https://github.com/user-attachments/assets/17fdb177-773e-41a8-8794-76461b2f71e6)

The API is fully functional and tested. All endpoints are working:

- ✅ `/api/health` - Service health check
- ✅ `/api/process-documentation` - Document processing
- ✅ `/api/generate-project` - Project generation
- ✅ `/api/download-project/{id}` - ZIP download

## Next Steps for Full Production

1. **Install additional dependencies** for AI features:
   ```bash
   pip install langchain chromadb openai
   ```

2. **Add OpenAI API key** to `.env` file for AI-powered generation

3. **Build frontend** for complete web interface:
   ```bash
   cd frontend && npm install && npm run build
   ```

4. **Deploy** using the provided scripts and Docker configuration

The current implementation provides a solid foundation and working demonstration of the complete DocuGen AI concept.