# 🐳 Docker Deployment Guide - Smart Support RAG System

## 🚀 Quick Start with Docker

### Prerequisites
- Docker installed (version 20.10+)
- Docker Compose installed (version 2.0+)
- At least 4GB RAM available
- `smart_support.xlsx` in `fastapi-chat/data/` directory

### One-Command Start (Development)

```bash
# From the project root directory
docker-compose up --build
```

That's it! The system will:
1. ✅ Build all containers
2. ✅ Start PostgreSQL and Redis
3. ✅ Run database migrations
4. ✅ Initialize FAISS index automatically
5. ✅ Start backend on http://localhost:8001
6. ✅ Start frontend on http://localhost:3000

**Wait for this message:**
```
smart-support-backend    | INFO:     Uvicorn running on http://0.0.0.0:8001
smart-support-frontend   | VITE ready in XXXms
```

Then open: **http://localhost:3000**

---

## 📋 Detailed Setup

### Step 1: Prepare the Dataset

Ensure `smart_support.xlsx` exists:
```bash
ls fastapi-chat/data/smart_support.xlsx
```

If missing, place your dataset file there.

### Step 2: Configure Environment

Check environment variables:
```bash
cat fastapi-chat/src/.env
```

Should contain:
```env
SCIBOX_API_KEY="sk-Crh_Ol2yEhe0c8tpELeTkQ"
SCIBOX_BASE_URL="https://llm.t1v.scibox.tech/v1"
SCIBOX_LLM_MODEL="Qwen2.5-72B-Instruct-AWQ"
SCIBOX_EMBEDDING_MODEL="bge-m3"
```

### Step 3: Build and Start Services

**Development Mode (with hot reload):**
```bash
docker-compose up --build
```

**Production Mode:**
```bash
docker-compose -f docker-compose.prod.yml up --build -d
```

**Background Mode:**
```bash
docker-compose up -d
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Docker Compose Stack                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Frontend Container (Port 3000)                    │    │
│  │  - Vue.js + Vuetify                                │    │
│  │  - Development: Vite dev server                    │    │
│  │  - Production: Nginx                               │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │                                          │
│  ┌────────────────▼───────────────────────────────────┐    │
│  │  Backend Container (Port 8001)                     │    │
│  │  - FastAPI + RAG Pipeline                          │    │
│  │  - Auto FAISS index initialization                 │    │
│  │  - Database migrations                             │    │
│  └────────────────┬───────────────────────────────────┘    │
│                   │                                          │
│  ┌────────────────▼───────────────────────────────────┐    │
│  │  PostgreSQL Container (Port 5442)                  │    │
│  │  - User data, chats, messages                      │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Redis Container (Port 6379)                        │   │
│  │  - Caching, WebSocket pub/sub                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  PgAdmin Container (Port 7070) [Optional]           │   │
│  │  - Database management UI                           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Volumes:
- postgres_data: Database persistence
- faiss_data: FAISS index persistence
- pgadmin_data: PgAdmin settings
```

---

## 🔧 Container Details

### Backend Container
- **Image**: Python 3.11.3-slim
- **Port**: 8001
- **Features**:
  - Auto-installs dependencies via Poetry
  - Runs database migrations on startup
  - Initializes FAISS index if not exists
  - Hot reload in development mode
  - Gunicorn with 4 workers in production

### Frontend Container
- **Development**:
  - Image: Node 18-alpine
  - Port: 3000
  - Hot reload enabled
  - Volume mounted for live updates
- **Production**:
  - Image: Nginx alpine
  - Port: 80
  - Optimized static assets
  - Gzip compression
  - API proxy to backend

### Database Container
- **Image**: PostgreSQL 15-alpine
- **Port**: 5442 (external), 5432 (internal)
- **Volume**: postgres_data
- **Health check**: Automatic

### Redis Container
- **Image**: Redis alpine
- **Port**: 6379
- **Health check**: Automatic

---

## 📝 Common Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Stop Services
```bash
# Stop all
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v
```

### Restart a Service
```bash
docker-compose restart backend
docker-compose restart frontend
```

### Rebuild a Service
```bash
docker-compose up --build backend
docker-compose up --build frontend
```

### Execute Commands in Container
```bash
# Backend shell
docker-compose exec backend sh

# Run Python script
docker-compose exec backend python scripts/test_rag.py

# Frontend shell
docker-compose exec frontend sh

# Database shell
docker-compose exec db psql -U postgres
```

### Check Service Status
```bash
docker-compose ps
```

### View Resource Usage
```bash
docker stats
```

---

## 🧪 Testing the System

### 1. Check Backend Health
```bash
curl http://localhost:8001/docs
```

### 2. Test RAG Pipeline
```bash
docker-compose exec backend python scripts/test_rag.py
```

### 3. Test Hint API
```bash
curl -X POST "http://localhost:8001/chat/hint/?query=Как%20восстановить%20пароль"
```

### 4. Access Frontend
Open browser: http://localhost:3000

### 5. Access PgAdmin
Open browser: http://localhost:7070
- Email: admin@admin.com
- Password: admin

---

## 🔍 Troubleshooting

### FAISS Index Not Initialized

**Symptom**: Backend starts but hints don't work

**Solution**:
```bash
# Manually initialize
docker-compose exec backend python scripts/init_faiss_index.py

# Check if file exists
docker-compose exec backend ls -lh data/faiss_index_bge_m3.bin
```

### Dataset Not Found

**Symptom**: "Dataset not found at 'data/smart_support.xlsx'"

**Solution**:
```bash
# Check if file exists in host
ls fastapi-chat/data/smart_support.xlsx

# Copy to container if needed
docker cp fastapi-chat/data/smart_support.xlsx smart-support-backend:/opt/chat/data/

# Reinitialize index
docker-compose exec backend python scripts/init_faiss_index.py
```

### Backend Won't Start

**Symptom**: Backend container exits immediately

**Solution**:
```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Database not ready - wait 30 seconds and retry
# 2. Port 8001 already in use - stop other services
# 3. Missing dependencies - rebuild: docker-compose up --build backend
```

### Frontend Can't Connect to Backend

**Symptom**: API errors in browser console

**Solution**:
```bash
# Check backend is running
docker-compose ps backend

# Check backend logs
docker-compose logs backend

# Verify network
docker-compose exec frontend ping backend

# Check API base URL
docker-compose exec frontend env | grep VITE_API_BASE_URL
```

### Database Connection Issues

**Symptom**: "could not connect to server"

**Solution**:
```bash
# Check database is running
docker-compose ps db

# Check database logs
docker-compose logs db

# Restart database
docker-compose restart db

# Wait for health check
docker-compose ps
```

### Port Already in Use

**Symptom**: "port is already allocated"

**Solution**:
```bash
# Find process using port
lsof -i :8001  # or :3000, :5442

# Kill process or change port in docker-compose.yml
# Example: "8002:8001" instead of "8001:8001"
```

### Out of Memory

**Symptom**: Container killed, OOM errors

**Solution**:
```bash
# Check Docker memory limit
docker info | grep Memory

# Increase Docker memory in Docker Desktop settings
# Or reduce workers in production:
# gunicorn --workers 2 instead of --workers 4
```

### FAISS Index Corrupted

**Symptom**: Errors when generating hints

**Solution**:
```bash
# Remove corrupted index
docker-compose exec backend rm data/faiss_index_bge_m3.bin
docker-compose exec backend rm data/metadata.json

# Reinitialize
docker-compose exec backend python scripts/init_faiss_index.py

# Restart backend
docker-compose restart backend
```

---

## 🔄 Updating the System

### Update Code
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose up --build
```

### Update Dataset
```bash
# Replace dataset file
cp new_smart_support.xlsx fastapi-chat/data/smart_support.xlsx

# Remove old index
docker-compose exec backend rm data/faiss_index_bge_m3.bin

# Reinitialize
docker-compose exec backend python scripts/init_faiss_index.py

# Restart backend
docker-compose restart backend
```

### Update Dependencies
```bash
# Backend
cd fastapi-chat
# Edit pyproject.toml
docker-compose up --build backend

# Frontend
cd vuetify-chat
# Edit package.json
docker-compose up --build frontend
```

---

## 🚀 Production Deployment

### Using Production Compose File
```bash
# Build and start
docker-compose -f docker-compose.prod.yml up --build -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Production Checklist
- [ ] Update environment variables in `.env`
- [ ] Set strong database passwords
- [ ] Configure proper CORS origins
- [ ] Enable HTTPS (use reverse proxy like Nginx/Traefik)
- [ ] Set up monitoring (Sentry, Prometheus)
- [ ] Configure backup for volumes
- [ ] Set resource limits in docker-compose
- [ ] Use Docker secrets for sensitive data
- [ ] Enable log rotation

### Resource Limits (Add to docker-compose.prod.yml)
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

---

## 📊 Monitoring

### Health Checks
```bash
# Backend health
curl http://localhost:8001/docs

# Database health
docker-compose exec db pg_isready -U postgres

# Redis health
docker-compose exec redis redis-cli ping
```

### Resource Usage
```bash
# Real-time stats
docker stats

# Disk usage
docker system df

# Volume sizes
docker volume ls
du -sh /var/lib/docker/volumes/*
```

### Logs
```bash
# Follow all logs
docker-compose logs -f

# Export logs
docker-compose logs > logs.txt

# Filter by time
docker-compose logs --since 30m backend
```

---

## 🧹 Cleanup

### Remove Stopped Containers
```bash
docker-compose down
```

### Remove Volumes (⚠️ Deletes Data)
```bash
docker-compose down -v
```

### Clean Docker System
```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove everything unused
docker system prune -a --volumes
```

---

## 📦 Backup & Restore

### Backup Database
```bash
# Create backup
docker-compose exec -T db pg_dump -U postgres postgres > backup.sql

# With timestamp
docker-compose exec -T db pg_dump -U postgres postgres > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore Database
```bash
# Restore from backup
docker-compose exec -T db psql -U postgres postgres < backup.sql
```

### Backup FAISS Index
```bash
# Copy from container
docker cp smart-support-backend:/opt/chat/data/faiss_index_bge_m3.bin ./backup/
docker cp smart-support-backend:/opt/chat/data/metadata.json ./backup/
```

### Restore FAISS Index
```bash
# Copy to container
docker cp ./backup/faiss_index_bge_m3.bin smart-support-backend:/opt/chat/data/
docker cp ./backup/metadata.json smart-support-backend:/opt/chat/data/
```

---

## 🎯 Performance Optimization

### Backend
- Use Gunicorn with multiple workers (production)
- Enable Redis caching
- Optimize FAISS index (use IndexIVFFlat for large datasets)
- Use connection pooling for database

### Frontend
- Enable Nginx gzip compression
- Use CDN for static assets
- Implement lazy loading
- Optimize bundle size

### Database
- Regular VACUUM and ANALYZE
- Add appropriate indexes
- Configure connection pooling
- Monitor slow queries

---

## 📞 Support

### Check Logs First
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Common Issues
1. **Port conflicts**: Change ports in docker-compose.yml
2. **Memory issues**: Increase Docker memory limit
3. **Network issues**: Check firewall settings
4. **Permission issues**: Run with sudo or fix Docker permissions

### Useful Commands
```bash
# Restart everything
docker-compose restart

# Rebuild from scratch
docker-compose down -v
docker-compose up --build

# Check container health
docker-compose ps
docker inspect smart-support-backend
```

---

## ✅ Success Indicators

You know it's working when:
- ✅ All containers show "healthy" status
- ✅ Backend accessible at http://localhost:8001/docs
- ✅ Frontend accessible at http://localhost:3000
- ✅ FAISS index file exists in backend container
- ✅ Lightbulb button returns AI hints
- ✅ No errors in logs

**Enjoy your containerized Smart Support RAG System! 🎉**
