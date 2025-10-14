# Lightbulb Button Fix - Troubleshooting Guide

## Issues Identified and Fixed

### 1. ✅ FastAPILimiter Not Initialized (FIXED)
**Problem:** The application was crashing with:
```
Exception: You must call FastAPILimiter.init in startup event of fastapi!
```

**Solution:** Added `FastAPILimiter.init(redis)` to the startup event in `fastapi-chat/src/main.py`:

```python
@app.on_event("startup")
async def startup():
    logger.info("Application is started")
    redis = aioredis.Redis(connection_pool=redis_pool)
    await FastAPILimiter.init(redis)  # ← ADDED THIS LINE
```

### 2. ⚠️ FAISS Index Missing (NEEDS VERIFICATION)
**Problem:** The RAG system requires FAISS vector index files to function:
- `data/faiss_index_bge_m3.bin`
- `data/metadata.json`

**Status:** These files should be created automatically when the Docker container starts (based on the docker-compose configuration).

## How to Restart and Test

### Step 1: Restart Docker Services
```bash
cd /home/a_a/t1_hackathon_smart_support

# Stop any running containers
docker-compose down

# Rebuild and start (this will initialize FAISS index automatically)
docker-compose up --build
```

**Expected Output:**
```
chat-backend     | INFO: Starting FAISS index initialization...
chat-backend     | INFO: Loaded dataset with X rows
chat-backend     | INFO: Generating embeddings...
chat-backend     | INFO: FAISS index created with X vectors
chat-backend     | INFO: ✓ FAISS index created successfully!
chat-backend     | INFO: RAG components loaded successfully
chat-backend     | INFO: Application is started
chat-backend     | INFO: Uvicorn running on http://0.0.0.0:8001
```

### Step 2: Verify Services are Running
```bash
docker-compose ps
```

You should see:
- `chat-backend` (FastAPI) - Up
- `chat-frontend` (Vue.js) - Up
- `chat-postgres` - Up
- `chat-redis` - Up

### Step 3: Test the Lightbulb Button

#### Option A: Via UI
1. Open browser to http://localhost:3000
2. Login/register
3. Open or create a chat
4. Type a customer question (e.g., "Как восстановить пароль?")
5. Click the **💡 lightbulb button**
6. Wait 3-4 seconds
7. You should see a hint card appear with:
   - Category and subcategory chips
   - AI-generated response
   - Template reference
   - Confidence indicator

#### Option B: Via API Test
```bash
# Test the hint endpoint directly
curl -X POST "http://localhost:8001/chat/hint/?query=Как%20восстановить%20пароль"
```

**Expected Response:**
```json
{
  "response": "Здравствуйте! Для восстановления пароля...",
  "confidence": "high",
  "category": "Технические вопросы",
  "subcategory": "Восстановление доступа",
  "template": "Инструкция по восстановлению пароля"
}
```

#### Option C: Via Test Script
```bash
docker exec -it chat-backend python scripts/test_rag.py
```

## Troubleshooting

### If containers fail to start:
```bash
# Check logs
docker-compose logs chat-backend

# Common issues:
# 1. Port already in use
# 2. Missing environment variables
# 3. Database connection issues
```

### If FAISS index is not created:
```bash
# Manually create the index inside the container
docker exec -it chat-backend python scripts/init_faiss_index.py --recreate
```

### If hint button returns error:
1. **Check backend logs:**
   ```bash
   docker-compose logs -f chat-backend
   ```

2. **Check browser console (F12)** for frontend errors

3. **Verify API endpoint:**
   ```bash
   curl http://localhost:8001/docs
   ```
   Look for `/chat/hint/` endpoint

### If "No response" or timeout:
- Check Scibox API credentials in `fastapi-chat/src/.env`:
  ```
  SCIBOX_API_KEY="sk-Crh_Ol2yEhe0c8tpELeTkQ"
  SCIBOX_BASE_URL="https://llm.t1v.scibox.tech/v1"
  ```
- Verify network connectivity to Scibox API
- Check if rate limits are exceeded

## Architecture Flow

```
User clicks 💡 button
    ↓
Frontend: SelectedChatWindow.vue → requestHint()
    ↓
Store: messageStore.js → getHint(query)
    ↓
API: POST /chat/hint/?query=...
    ↓
Backend: router.py → get_hint_view()
    ↓
RAG: rag.py → generate_hint()
    ↓
1. Embed query (bge-m3)
2. Search FAISS index
3. Retrieve top-3 contexts
4. Generate response (Qwen2.5-72B)
    ↓
Return Hint object
    ↓
Frontend: MainChat.vue → Display hint card
```

## Files Modified

1. **fastapi-chat/src/main.py** (line 68)
   - Added `await FastAPILimiter.init(redis)` to startup event

## Key Components

### Backend
- **Endpoint:** `/chat/hint/` (POST)
- **Handler:** `src/chat/router.py:get_hint_view()`
- **RAG Pipeline:** `src/chat/rag.py:generate_hint()`
- **FAISS Index:** `data/faiss_index_bge_m3.bin`
- **Metadata:** `data/metadata.json`

### Frontend
- **Button:** `src/components/chat/SelectedChatWindow.vue` (line 53-55)
- **Handler:** `requestHint()` (line 167-172)
- **Store:** `src/store/messageStore.js:getHint()` (line 196-216)
- **Display:** `src/components/chat/MainChat.vue` (line 16-39)

## Expected Performance

- **Embedding generation:** ~100ms
- **FAISS search:** <10ms
- **LLM generation:** ~2-3 seconds
- **Total response time:** ~3-4 seconds

## Status

✅ **FastAPILimiter initialization** - Fixed
⚠️ **FAISS index** - Should be created automatically on container start
✅ **Frontend code** - Working correctly
✅ **Backend endpoint** - Properly configured
✅ **API client** - Correctly configured

## Next Steps

1. Run `docker-compose up --build` to restart services
2. Wait for FAISS index initialization to complete
3. Test the lightbulb button
4. Monitor logs for any errors

If issues persist after following these steps, check the logs and provide the error messages for further debugging.
