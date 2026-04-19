# Docker Deployment Guide

## Prerequisites
- Docker installed and running
- Docker Compose (optional, but recommended)

## Build and Run Options

### Option 1: Using Docker Compose (Recommended)

1. **Build and start the container:**
   ```bash
   docker-compose up --build
   ```

2. **Run in detached mode:**
   ```bash
   docker-compose up --build -d
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Stop the container:**
   ```bash
   docker-compose down
   ```

### Option 2: Using Docker Directly

1. **Build the image:**
   ```bash
   docker build -t texttosqlagent .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name texttosqlagent \
     -p 8000:8000 \
     -e PYTHONPATH=/app \
     -e PYTHONUNBUFFERED=1 \
     texttosqlagent
   ```

3. **View logs:**
   ```bash
   docker logs -f texttosqlagent
   ```

4. **Stop the container:**
   ```bash
   docker stop texttosqlagent
   docker rm texttosqlagent
   ```

## Access the Application

Once the container is running, you can access:
- **API Documentation**: http://localhost:8000/docs
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **API Endpoints**: http://localhost:8000/api/

## Troubleshooting

### Build Issues
- **Network timeouts**: The Dockerfile now includes retry logic and extended timeouts
- **Docker daemon issues**: Restart Docker daemon if you encounter RPC errors
- **Permission issues**: Ensure Docker has proper permissions

### Runtime Issues
- **Port conflicts**: Change the port mapping if 8000 is already in use
- **Environment variables**: Check that required environment variables are set
- **Health checks**: The container includes health checks for monitoring

### Debug Mode
For debugging, you can run with more verbose logging:
```bash
docker run -d \
  --name texttosqlagent-debug \
  -p 8000:8000 \
  -e PYTHONPATH=/app \
  -e PYTHONUNBUFFERED=1 \
  texttosqlagent \
  uvicorn api.main:app --host 0.0.0.0 --port 8000 --log-level debug
```

## Production Considerations

1. **Environment Variables**: Set appropriate production environment variables
2. **Database**: Uncomment and configure the PostgreSQL service in docker-compose.yml if needed
3. **Volumes**: Mount persistent volumes for logs and data
4. **Security**: Configure proper authentication and CORS settings
5. **Monitoring**: Set up proper logging and monitoring

## Multi-stage Build Benefits

The Dockerfile uses a multi-stage build that:
- Reduces final image size
- Improves security by excluding build tools
- Provides better caching
- Enables faster rebuilds
