# Docker Setup Guide - Fully Automated RAG System

## Overview

The system is now fully dockerized with automatic FAISS index initialization. No manual commands needed!

---

## Quick Start

### First Time Setup

```bash
# Build and start all services
docker-compose up --build
```

That's it! The system will:
1. ✅ Build all containers
2. ✅ Start PostgreSQL and Redis
3. ✅ Run database migrations
4. ✅ **Automatically initialize FAISS index** (if not exists)
5. ✅ **Build L1 cache** (if not exists)
6. ✅ Start the FastAPI backend
7. ✅ Start the Vue.js frontend

### Subsequent Runs

```bash
# Just start the services (no rebuild needed)
docker-compose up
```

The FAISS index and L1 cache are stored in a Docker volume (`faiss_data`), so they persist between runs!

---

## What Changed

### 1. **Automatic Initialization**

The backend now has a smart entrypoint script (`docker-entrypoint.sh`) that:
- Checks if FAISS index exists
- If not, automatically runs initialization
- Rebuilds L1 cache if missing
- Provides helpful error messages if initialization fails

### 2. **Persistent Storage**

FAISS index and cache are stored in a named Docker volume:
```yaml
volumes:
  faiss_data:
```

This means:
- ✅ Data persists between container restarts
- ✅ No need to reinitialize on every `docker-compose up`
- ✅ Can be backed up using Docker volume commands

### 3. **Exact Confidence Values**

The system now returns exact confidence scores (0-100) instead of "high/medium/low":
- **L1 (Exact Match)**: 100%
- **L2 (Semantic Search)**: Based on similarity score (e.g., 95%, 97%)
- **L3 (LLM Rerank)**: Based on LLM confidence (e.g., 70%, 85%)

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│ docker-compose up --build                               │
└─────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
   ┌─────────┐    ┌──────────┐    ┌──────────┐
   │   DB    │    │  Redis   │    │ Backend  │
   │ (Postgres)│  │  (Cache) │    │ (FastAPI)│
   └─────────┘    └──────────┘    └──────────┘
                                        │
                    ┌───────────────────┴───────────────────┐
                    │ docker-entrypoint.sh                  │
                    │                                       │
                    │ 1. Wait for DB                        │
                    │ 2. Run migrations                     │
                    │ 3. Check FAISS index                  │
                    │    ├─ Not found? → Initialize         │
                    │    └─ Found? → Skip                   │
                    │ 4. Check L1 cache                     │
                    │    ├─ Not found? → Rebuild            │
                    │    └─ Found? → Skip                   │
                    │ 5. Start FastAPI server               │
                    └───────────────────────────────────────┘
                                        │
                                        ▼
                              ┌──────────────────┐
                              │  faiss_data      │
                              │  (Docker Volume) │
                              │                  │
                              │  • faiss_index   │
                              │  • metadata.json │
                              │  • l1_cache.json │
                              └──────────────────┘
```

---

## Expected Output

### First Run (with initialization)

```bash
$ docker-compose up --build

[... building images ...]

smart-support-backend | ==========================================
smart-support-backend | Smart Support Backend - Starting...
smart-support-backend | ==========================================
smart-support-backend | Waiting for database...
smart-support-backend | Running database migrations...
smart-support-backend | INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
smart-support-backend | INFO  [alembic.runtime.migration] Will assume transactional DDL.
smart-support-backend | ==========================================
smart-support-backend | FAISS index not found. Initializing...
smart-support-backend | ==========================================
smart-support-backend | ================================================================================
smart-support-backend | FAISS INDEX INITIALIZATION
smart-support-backend | ================================================================================
smart-support-backend | ✓ Dataset found: data/smart_support.xlsx
smart-support-backend | Connecting to Scibox API: https://llm.t1v.scibox.tech/v1
smart-support-backend | Using embedding model: bge-m3
smart-support-backend | Creating FAISS index and L1 cache...
smart-support-backend | --------------------------------------------------------------------------------
smart-support-backend | Loaded dataset with 201 rows
smart-support-backend | Columns: ['Основная категория', 'Подкатегория', 'Пример вопроса', ...]
smart-support-backend | Dropped column: Приоритет
smart-support-backend | Dropped column: Целевая аудитория
smart-support-backend | Generating embeddings for 201 questions...
smart-support-backend | Processed 160/201 texts
smart-support-backend | Processed 201/201 texts
smart-support-backend | Creating FAISS index with dimension 1024...
smart-support-backend | FAISS index created with 201 vectors
smart-support-backend | Saved to: data/faiss_index_bge_m3.bin
smart-support-backend | Metadata saved to: data/metadata.json
smart-support-backend | Building L1 cache...
smart-support-backend | Built L1 cache with 200 entries (skipped 0 invalid entries)
smart-support-backend | --------------------------------------------------------------------------------
smart-support-backend | ✓ INITIALIZATION COMPLETE!
smart-support-backend |   - Index file: data/faiss_index_bge_m3.bin
smart-support-backend |   - Metadata file: data/metadata.json
smart-support-backend |   - L1 cache file: data/l1_cache.json
smart-support-backend |   - Total vectors: 201
smart-support-backend |   - Dimension: 1024
smart-support-backend |   - Metadata entries: 201
smart-support-backend | ================================================================================
smart-support-backend | ==========================================
smart-support-backend | Starting FastAPI server...
smart-support-backend | ==========================================
smart-support-backend | INFO:     Will watch for changes in these directories: ['/opt/chat']
smart-support-backend | INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
smart-support-backend | INFO:     Started reloader process [XX] using StatReload
smart-support-backend | Application is started
```

### Subsequent Runs (no initialization needed)

```bash
$ docker-compose up

smart-support-backend | ==========================================
smart-support-backend | Smart Support Backend - Starting...
smart-support-backend | ==========================================
smart-support-backend | Waiting for database...
smart-support-backend | Running database migrations...
smart-support-backend | INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
smart-support-backend | INFO  [alembic.runtime.migration] Will assume transactional DDL.
smart-support-backend | ✓ FAISS index found at /opt/chat/data/faiss_index_bge_m3.bin
smart-support-backend | ✓ L1 cache found at /opt/chat/data/l1_cache.json
smart-support-backend | ==========================================
smart-support-backend | Starting FastAPI server...
smart-support-backend | ==========================================
smart-support-backend | INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
smart-support-backend | Application is started
```

---

## Volume Management

### View Volume Data

```bash
# List all volumes
docker volume ls

# Inspect the faiss_data volume
docker volume inspect t1_hackathon_smart_support_faiss_data
```

### Backup Volume

```bash
# Create a backup
docker run --rm -v t1_hackathon_smart_support_faiss_data:/data -v $(pwd):/backup alpine tar czf /backup/faiss_data_backup.tar.gz -C /data .
```

### Restore Volume

```bash
# Restore from backup
docker run --rm -v t1_hackathon_smart_support_faiss_data:/data -v $(pwd):/backup alpine tar xzf /backup/faiss_data_backup.tar.gz -C /data
```

### Force Reinitialization

If you want to rebuild the FAISS index from scratch:

```bash
# Method 1: Delete the volume and restart
docker-compose down -v
docker-compose up --build

# Method 2: Delete files inside the container
docker exec -it smart-support-backend rm -f /opt/chat/data/faiss_index_bge_m3.bin /opt/chat/data/l1_cache.json /opt/chat/data/metadata.json
docker-compose restart backend
```

---

## Confidence Display

The UI now shows **exact confidence percentages**:

| Confidence | Color | Example |
|------------|-------|---------|
| 80-100% | Green | 100%, 95%, 87% |
| 50-79% | Orange | 70%, 65%, 55% |
| 0-49% | Red | 45%, 30%, 15% |

### Examples

**L1 Exact Match:**
```
[📊 100%] - Green chip
```

**L2 High Similarity:**
```
[📊 97%] - Green chip
```

**L3 LLM Rerank:**
```
[📊 70%] - Orange chip
```

---

## Troubleshooting

### Issue: Initialization fails during first run

**Symptoms:**
```
ERROR: FAISS index initialization failed!
The system will start but RAG features may not work.
```

**Solution:**
1. Check if `smart_support.xlsx` exists in `fastapi-chat/data/`
2. Check network connectivity to Scibox API
3. Check logs for specific error:
   ```bash
   docker-compose logs backend | grep ERROR
   ```
4. Manually reinitialize:
   ```bash
   docker exec -it smart-support-backend python /opt/chat/scripts/init_faiss_index.py --recreate
   docker-compose restart backend
   ```

### Issue: Volume permissions error

**Symptoms:**
```
Permission denied: '/opt/chat/data/faiss_index_bge_m3.bin'
```

**Solution:**
```bash
# Fix permissions
docker exec -it smart-support-backend chown -R root:root /opt/chat/data
docker-compose restart backend
```

### Issue: Old data persists after code changes

**Solution:**
```bash
# Rebuild containers and reinitialize
docker-compose down
docker volume rm t1_hackathon_smart_support_faiss_data
docker-compose up --build
```

---

## Development Workflow

### Making Changes to RAG Code

1. Edit `fastapi-chat/src/chat/rag.py`
2. The server will auto-reload (no restart needed)
3. If you change the data structure, reinitialize:
   ```bash
   docker exec -it smart-support-backend rm /opt/chat/data/*.bin /opt/chat/data/*.json
   docker-compose restart backend
   ```

### Updating the Dataset

1. Replace `fastapi-chat/data/smart_support.xlsx`
2. Reinitialize:
   ```bash
   docker exec -it smart-support-backend python /opt/chat/scripts/init_faiss_index.py --recreate
   docker-compose restart backend
   ```

---

## Production Deployment

For production, consider:

1. **Use a production-ready entrypoint** (remove `--reload` flag)
2. **Set proper environment variables**:
   ```yaml
   environment:
     - ENVIRONMENT=production
     - LOG_LEVEL=INFO
   ```
3. **Use external volume for backups**:
   ```yaml
   volumes:
     - ./backups:/backups
   ```
4. **Add health checks** (already configured in docker-compose.yml)
5. **Use docker-compose.prod.yml** for production settings

---

## Summary

✅ **Fully automated** - No manual initialization needed  
✅ **Persistent storage** - Data survives container restarts  
✅ **Exact confidence values** - Shows precise percentages (0-100)  
✅ **Smart entrypoint** - Handles initialization automatically  
✅ **Easy to use** - Just `docker-compose up --build`  
✅ **Production ready** - Includes health checks and proper error handling  

**Just run `docker-compose up --build` and everything works!** 🎉
