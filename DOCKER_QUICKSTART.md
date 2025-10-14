# 🐳 Docker Quick Start - 2 Minutes to Running System

## ⚡ Super Fast Start

```bash
# 1. Make sure smart_support.xlsx is in fastapi-chat/data/
ls fastapi-chat/data/smart_support.xlsx

# 2. Run the start script
./docker-start.sh

# OR manually:
docker-compose up --build
```

**That's it!** 🎉

Wait 2-3 minutes for:
- Database initialization
- FAISS index creation
- Services to start

Then open: **http://localhost:3000**

---

## 📋 What Gets Started

| Service | Port | URL | Description |
|---------|------|-----|-------------|
| **Frontend** | 3000 | http://localhost:3000 | Vue.js chat interface |
| **Backend** | 8001 | http://localhost:8001/docs | FastAPI + RAG pipeline |
| **PostgreSQL** | 5442 | localhost:5442 | Database |
| **Redis** | 6379 | localhost:6379 | Cache |
| **PgAdmin** | 7070 | http://localhost:7070 | DB management (optional) |

---

## 🎯 First Time Setup

### Step 1: Ensure Dataset Exists
```bash
# Check if file exists
ls -lh fastapi-chat/data/smart_support.xlsx

# If missing, add your dataset file there
```

### Step 2: Start Everything
```bash
# Option A: Use the helper script
./docker-start.sh

# Option B: Manual start
docker-compose up --build
```

### Step 3: Wait for Initialization

Watch the logs for these messages:
```
✅ "Initializing FAISS index from smart_support.xlsx..."
✅ "FAISS index created with X vectors"
✅ "Running database migrations..."
✅ "Starting FastAPI server..."
✅ "Uvicorn running on http://0.0.0.0:8001"
✅ "VITE ready in XXXms"
```

### Step 4: Test the System

1. **Open frontend**: http://localhost:3000
2. **Register/Login**
3. **Open a chat**
4. **Type a question**: "Как восстановить пароль?"
5. **Click the 💡 button**
6. **See the AI hint appear!**

---

## 🔧 Common Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Just backend
docker-compose logs -f backend

# Just frontend
docker-compose logs -f frontend
```

### Stop Services
```bash
# Stop all (keeps data)
docker-compose down

# Stop and remove data
docker-compose down -v
```

### Restart a Service
```bash
docker-compose restart backend
docker-compose restart frontend
```

### Rebuild After Code Changes
```bash
# Rebuild everything
docker-compose up --build

# Rebuild specific service
docker-compose up --build backend
```

### Check Status
```bash
docker-compose ps
```

### Access Container Shell
```bash
# Backend
docker-compose exec backend sh

# Frontend
docker-compose exec frontend sh

# Database
docker-compose exec db psql -U postgres
```

---

## 🐛 Troubleshooting

### "Port already in use"
```bash
# Find what's using the port
lsof -i :8001  # or :3000

# Kill it or change port in docker-compose.yml
```

### "Dataset not found"
```bash
# Make sure file exists
ls fastapi-chat/data/smart_support.xlsx

# If missing, add it and restart
docker-compose restart backend
```

### "FAISS index failed"
```bash
# Check logs
docker-compose logs backend | grep -i faiss

# Manually initialize
docker-compose exec backend python scripts/init_faiss_index.py
```

### "Backend won't start"
```bash
# Check logs
docker-compose logs backend

# Common fixes:
# 1. Wait for database (30 seconds)
# 2. Rebuild: docker-compose up --build backend
# 3. Check .env file exists
```

### "Frontend can't connect"
```bash
# Check backend is running
docker-compose ps backend

# Check backend logs
docker-compose logs backend

# Restart both
docker-compose restart backend frontend
```

### Start Fresh
```bash
# Nuclear option - removes everything
docker-compose down -v
docker-compose up --build
```

---

## 📊 Verify Everything Works

### 1. Check Backend API
```bash
curl http://localhost:8001/docs
```
Should return Swagger UI HTML.

### 2. Test RAG Pipeline
```bash
docker-compose exec backend python scripts/test_rag.py
```
Should show test results with hints.

### 3. Test Hint Endpoint
```bash
curl -X POST "http://localhost:8001/chat/hint/?query=Как%20восстановить%20пароль"
```
Should return JSON with hint.

### 4. Check Frontend
Open http://localhost:3000 in browser.

### 5. Check FAISS Index
```bash
docker-compose exec backend ls -lh data/faiss_index_bge_m3.bin
```
Should show file size (e.g., 4.2M).

---

## 🚀 Production Deployment

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up --build -d

# Frontend will be on port 80
# Backend will use Gunicorn with 4 workers
```

---

## 📦 What's in Each Container?

### Backend Container
```
/opt/chat/
├── src/                    # FastAPI application
│   ├── chat/
│   │   └── rag.py         # RAG pipeline
│   ├── main.py
│   └── .env               # Configuration
├── data/
│   ├── smart_support.xlsx # Dataset
│   ├── faiss_index_bge_m3.bin  # Vector index
│   └── metadata.json      # Question metadata
├── scripts/
│   ├── init_faiss_index.py
│   └── test_rag.py
└── alembic/               # Database migrations
```

### Frontend Container
```
/app/
├── src/
│   ├── components/
│   │   └── chat/
│   │       ├── MainChat.vue
│   │       └── SelectedChatWindow.vue
│   └── store/
│       └── messageStore.js
└── package.json
```

---

## 🎯 Success Checklist

After running `docker-compose up --build`, verify:

- [ ] All 5 containers are running (`docker-compose ps`)
- [ ] Backend shows "Uvicorn running" in logs
- [ ] Frontend shows "VITE ready" in logs
- [ ] FAISS index file exists in backend
- [ ] http://localhost:3000 loads
- [ ] http://localhost:8001/docs loads
- [ ] Can register/login
- [ ] Can create a chat
- [ ] Lightbulb button returns hints

---

## 💡 Tips

1. **First run takes longer** - Docker needs to download images and build containers
2. **FAISS index creation** - Takes 1-2 minutes depending on dataset size
3. **Hot reload works** - Edit code and see changes without rebuilding
4. **Data persists** - Database and FAISS index survive container restarts
5. **Clean slate** - Use `docker-compose down -v` to start fresh

---

## 🆘 Getting Help

### Check Logs
```bash
docker-compose logs -f
```

### Check Container Health
```bash
docker-compose ps
docker inspect smart-support-backend
```

### Test Components
```bash
# Test backend
docker-compose exec backend python scripts/test_rag.py

# Test database
docker-compose exec db pg_isready -U postgres

# Test Redis
docker-compose exec redis redis-cli ping
```

### Full Documentation
- **DOCKER_GUIDE.md** - Complete Docker documentation
- **QUICKSTART.md** - Non-Docker setup guide
- **RAG_INTEGRATION.md** - Technical details

---

## 🎉 You're Ready!

Your Smart Support RAG system is now running in Docker!

**Next steps:**
1. Open http://localhost:3000
2. Register an account
3. Start a chat
4. Click the 💡 button
5. Watch the AI magic happen! ✨

**For detailed documentation, see DOCKER_GUIDE.md**
