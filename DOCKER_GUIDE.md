# 🐳 Docker Deployment Guide

Complete guide for deploying the Semantic Book Recommender using Docker.

---

## 📋 Prerequisites

Before you begin, ensure you have:

- **Docker** installed (version 20.10+)
- **Docker Compose** installed (version 2.0+)
- **OpenAI API key** ([Get one here](https://platform.openai.com/api-keys))
- **Port 7860** available on your machine

### Verify Installation

```bash
# Check Docker
docker --version
# Should show: Docker version 20.10.x or higher

# Check Docker Compose
docker-compose --version
# Should show: Docker Compose version 2.x.x or higher
```

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd llm_semantic_book_recommender
```

### 2. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your OpenAI API key
nano .env  # or use your preferred editor
```

Add this line to `.env`:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Start Application

```bash
# Build and start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f
```

### 4. Access Application

Open your browser and navigate to:
```
http://localhost:7860
```

---

## 📦 What Gets Built

### Docker Image

The Dockerfile creates an image that includes:

- **Base**: Python 3.13 slim image
- **Package Manager**: UV for fast dependency installation
- **Application Code**: All source files
- **Dependencies**: All Python packages from `pyproject.toml`
- **Directories**: Pre-created data, vector_store, and logs directories

### Container Configuration

The container runs with:

- **Port Mapping**: 7860 (host) → 7860 (container)
- **Volume Mounts**: Data persistence for database, vector store, and logs
- **Environment Variables**: From `.env` file
- **Restart Policy**: Automatically restarts unless stopped
- **Health Check**: Monitors application availability

---

## 🔧 Docker Compose Configuration

### Services

#### App Service

```yaml
services:
  app:
    build: .
    container_name: book-recommender
    ports:
      - "7860:7860"
    volumes:
      - ./data:/app/data
      - ./vector_store:/app/vector_store
      - ./logs:/app/logs
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    restart: unless-stopped
```

### Volume Mounts

Data is persisted through volume mounts:

| Host Path | Container Path | Purpose |
|-----------|---------------|---------|
| `./data` | `/app/data` | User database (SQLite) |
| `./vector_store` | `/app/vector_store` | ChromaDB vector store |
| `./logs` | `/app/logs` | Application logs |

---

## 🛠️ Common Commands

### Starting & Stopping

```bash
# Start application
docker-compose up -d

# Start with build (if code changed)
docker-compose up -d --build

# Stop application
docker-compose down

# Stop and remove volumes (CAUTION: deletes data)
docker-compose down -v

# Restart application
docker-compose restart
```

### Logs & Monitoring

```bash
# View logs (follow mode)
docker-compose logs -f

# View logs for last hour
docker-compose logs --since 1h

# View last 100 lines
docker-compose logs --tail=100

# Check container status
docker-compose ps

# View resource usage
docker stats book-recommender
```

### Shell Access

```bash
# Access container shell
docker-compose exec app /bin/bash

# Run one-off command
docker-compose exec app python scripts/check_vector_store.py

# View environment variables
docker-compose exec app env
```

### Database Management

```bash
# Reinitialize database
docker-compose exec app python scripts/setup_db.py

# Backup database
docker cp book-recommender:/app/data/app.db ./backup/app_$(date +%Y%m%d).db

# Restore database
docker cp ./backup/app_20240115.db book-recommender:/app/data/app.db
docker-compose restart
```

---

## 🔍 Troubleshooting

### Container Won't Start

**Check logs:**
```bash
docker-compose logs app
```

**Common issues:**

1. **Port already in use**
   ```bash
   # Find process using port 7860
   lsof -i :7860
   
   # Kill the process or change port in docker-compose.yml
   ```

2. **Missing API key**
   ```bash
   # Verify .env file
   cat .env | grep OPENAI_API_KEY
   
   # Check environment in container
   docker-compose exec app env | grep OPENAI
   ```

3. **Permission issues**
   ```bash
   # Fix directory permissions
   chmod -R 755 data vector_store logs
   ```

### Application Errors

**View detailed logs:**
```bash
# Application logs
docker-compose logs -f app

# Check log files
docker-compose exec app cat /app/logs/app.log
```

**Restart with fresh state:**
```bash
docker-compose down
docker-compose up -d --build
```

### Database Issues

**Reset database:**
```bash
# Stop application
docker-compose down

# Remove database
rm -rf data/app.db

# Start and reinitialize
docker-compose up -d
docker-compose exec app python scripts/setup_db.py
```

### Vector Store Issues

**Validate vector store:**
```bash
docker-compose exec app python scripts/check_vector_store.py
```

**Check vector store files:**
```bash
docker-compose exec app ls -la /app/vector_store
```

---

## 🌐 Production Deployment

### Environment Variables for Production

Create a `.env.production` file:

```bash
# Required
OPENAI_API_KEY=sk-your-production-key

# Production settings
DEBUG=false
LOG_LEVEL=WARNING

# Database
DATABASE_PATH=/app/data/app.db
VECTOR_STORE_PATH=/app/vector_store
LOG_FILE=/app/logs/app.log

# Performance
CACHE_TTL=3600
OPENAI_MAX_RPM=3000

# Server
GRADIO_SERVER_NAME=0.0.0.0
GRADIO_SERVER_PORT=7860
GRADIO_SHARE=false
```

### Use Production Config

```bash
# Specify environment file
docker-compose --env-file .env.production up -d
```

### Resource Limits

Add resource limits to `docker-compose.yml`:

```yaml
services:
  app:
    # ... other config ...
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

### Reverse Proxy (Nginx)

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name books.example.com;

    location / {
        proxy_pass http://localhost:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support for Gradio
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

---

## 📊 Monitoring

### Health Checks

The container includes a health check:

```bash
# Check health status
docker inspect --format='{{.State.Health.Status}}' book-recommender

# View health check logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' book-recommender
```

### Resource Monitoring

```bash
# Real-time stats
docker stats book-recommender

# Detailed container info
docker inspect book-recommender
```

### Log Rotation

Configure log rotation in `docker-compose.yml`:

```yaml
services:
  app:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 🔄 Updates & Maintenance

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

### Update Dependencies

```bash
# Update UV lock file
uv lock

# Rebuild image
docker-compose build --no-cache
docker-compose up -d
```

### Backup Strategy

**Automated backup script:**

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups/$DATE"

mkdir -p $BACKUP_DIR

# Backup database
docker cp book-recommender:/app/data/app.db $BACKUP_DIR/

# Backup vector store
docker cp book-recommender:/app/vector_store $BACKUP_DIR/

# Backup logs
docker cp book-recommender:/app/logs $BACKUP_DIR/

echo "Backup completed: $BACKUP_DIR"
```

**Run backup:**
```bash
chmod +x backup.sh
./backup.sh
```

---

## 🔐 Security Best Practices

### 1. API Key Security

```bash
# Never commit .env files
echo ".env" >> .gitignore
echo ".env.production" >> .gitignore

# Use secrets for production
docker swarm init
echo "sk-your-key" | docker secret create openai_key -
```

### 2. Network Security

```bash
# Create custom network
docker network create book-recommender-net

# Update docker-compose.yml
services:
  app:
    networks:
      - book-recommender-net

networks:
  book-recommender-net:
    driver: bridge
```

### 3. File Permissions

```bash
# Secure data directories
chmod 700 data vector_store logs

# Run container as non-root user
# Add to Dockerfile:
USER nobody:nogroup
```

---

## 📈 Performance Optimization

### Build Optimization

```bash
# Use BuildKit for faster builds
DOCKER_BUILDKIT=1 docker-compose build

# Multi-stage build (if needed)
# Reduce final image size
```

### Runtime Optimization

```yaml
services:
  app:
    # Enable GPU support (if available)
    runtime: nvidia
    
    # Optimize shared memory
    shm_size: '2gb'
    
    # Set resource limits
    mem_limit: 2g
    memswap_limit: 2g
```

---

## 🆘 Getting Help

### Check Status

```bash
# Container status
docker-compose ps

# Service logs
docker-compose logs -f app

# System resources
docker system df
```

### Clean Up

```bash
# Remove stopped containers
docker-compose down

# Clean up unused images
docker image prune -a

# Full system cleanup (CAUTION)
docker system prune -a --volumes
```

---

## ✅ Deployment Checklist

Before deploying to production:

- [ ] OpenAI API key configured in `.env.production`
- [ ] Resource limits set in `docker-compose.yml`
- [ ] Log rotation configured
- [ ] Backup strategy implemented
- [ ] Health checks working
- [ ] Firewall rules configured
- [ ] Reverse proxy set up (if needed)
- [ ] SSL/TLS certificate installed (if needed)
- [ ] Monitoring set up
- [ ] Tested failover scenarios

---

## 🎯 Next Steps

1. **Monitor logs** for the first few days
2. **Set up alerts** for errors
3. **Configure backups** to run daily
4. **Document** any custom changes
5. **Test recovery** procedures

---

**Your Semantic Book Recommender is now running in Docker!** 🐳🚀