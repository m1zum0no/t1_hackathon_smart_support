# RAG System Initialization Guide

## Problem

You're seeing empty responses because the RAG system hasn't been initialized yet. The logs show:
- `L1 cache is empty`
- Candidates have empty questions and templates
- Response field is empty

## Solution

You need to initialize the FAISS index and L1 cache. Here are the methods:

---

## Method 1: Initialize Inside Docker Container (Recommended)

### Step 1: Access the backend container

```bash
docker exec -it smart-support-backend bash
```

### Step 2: Run the initialization script

```bash
cd /opt/chat
python scripts/init_faiss_index.py --recreate
```

This will:
1. Load `data/smart_support.xlsx`
2. Drop "Приоритет" and "Целевая аудитория" columns
3. Generate embeddings using `bge-m3` (takes 2-5 minutes)
4. Create FAISS index
5. Build L1 cache automatically
6. Save all files to `data/` directory

### Step 3: Restart the backend (optional, but recommended)

```bash
exit  # Exit the container
docker-compose restart smart-support-backend
```

---

## Method 2: Quick Initialization Script

If you have the script available:

```bash
docker exec -it smart-support-backend bash -c "cd /opt/chat && python scripts/init_faiss_index.py --recreate"
```

---

## Method 3: Initialize Before Starting Docker

If you prefer to initialize before running Docker:

### Step 1: Set up local environment

```bash
cd fastapi-chat

# Install dependencies (if using poetry)
poetry install

# Or if using pip
pip install -r requirements.txt  # if you have one
```

### Step 2: Run initialization

```bash
python scripts/init_faiss_index.py
```

### Step 3: Start Docker

The initialized files will be available in the `data/` directory and will be mounted into the container.

---

## Verification

After initialization, you should see these files created:

```bash
ls -lh fastapi-chat/data/
```

Expected output:
```
smart_support.xlsx          # Original dataset
faiss_index_bge_m3.bin     # FAISS vector index
metadata.json              # Question metadata
l1_cache.json              # L1 exact match cache
```

### Check the logs

After restarting, you should see:
```
RAG components loaded successfully. L1 cache: 201 entries
```

Instead of:
```
L1 cache is empty
```

---

## Expected Initialization Output

```
================================================================================
FAISS INDEX INITIALIZATION
================================================================================
✓ Dataset found: data/smart_support.xlsx
Connecting to Scibox API: https://llm.t1v.scibox.tech/v1
Using embedding model: bge-m3
Creating FAISS index and L1 cache...
--------------------------------------------------------------------------------
Loaded dataset with 201 rows
Columns: ['Вопрос клиента', 'Категория', 'Подкатегория', ...]
Dropped column: Приоритет
Dropped column: Целевая аудитория
Generating embeddings for 201 questions...
Processed 32/201 texts
Processed 64/201 texts
...
Processed 201/201 texts
Creating FAISS index with dimension 1024...
FAISS index created with 201 vectors
Saved to: data/faiss_index_bge_m3.bin
Metadata saved to: data/metadata.json
Building L1 cache...
Built L1 cache with 201 entries (skipped 0 invalid entries)
--------------------------------------------------------------------------------
✓ INITIALIZATION COMPLETE!
  - Index file: data/faiss_index_bge_m3.bin
  - Metadata file: data/metadata.json
  - L1 cache file: data/l1_cache.json
  - Total vectors: 201
  - Dimension: 1024
  - Metadata entries: 201
================================================================================
```

---

## Testing After Initialization

### Test 1: Quick Test Script

```bash
docker exec -it smart-support-backend bash -c "cd /opt/chat && python scripts/quick_test.py"
```

This will:
- Show sample questions from L1 cache
- Test exact match (should hit L1)
- Test modified question (should hit L2 or L3)

### Test 2: Via UI

1. Open the chat application
2. Click the lightbulb icon to open AI Recommendations
3. Type a question like: "Как оформить карту more"
4. Click the lightbulb button

You should now see:
- ✅ Category and subcategory chips
- ✅ Confidence percentage (e.g., "50-79%")
- ✅ Route information (e.g., "L3 LLM rerank")
- ✅ Processing time (e.g., "3495ms")
- ✅ Actual recommendation text (not empty)

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'pandas'"

**Solution**: The dependencies aren't installed. This shouldn't happen in Docker, but if it does:

```bash
docker exec -it smart-support-backend bash -c "cd /opt/chat && pip install pandas openpyxl"
```

### Issue: "Dataset not found"

**Solution**: Make sure `smart_support.xlsx` is in the `fastapi-chat/data/` directory and is mounted correctly in Docker.

Check docker-compose.yml:
```yaml
volumes:
  - ./fastapi-chat:/opt/chat
```

### Issue: "Connection error to Scibox API"

**Solution**: Check your network connection and API key in `src/config.py`:
```python
SCIBOX_API_KEY = "sk-Crh_Ol2yEhe0c8tpELeTkQ"
SCIBOX_BASE_URL = "https://llm.t1v.scibox.tech/v1"
```

### Issue: Still seeing empty responses after initialization

**Solution**: 
1. Check that files were created: `ls -lh fastapi-chat/data/`
2. Restart the backend: `docker-compose restart smart-support-backend`
3. Check logs: `docker-compose logs smart-support-backend | grep "RAG components"`
4. Should see: "RAG components loaded successfully. L1 cache: 201 entries"

---

## Performance Notes

- **Initialization time**: 2-5 minutes (depends on network speed to Scibox API)
- **L1 cache hits**: < 10ms (instant)
- **L2 semantic search**: 50-200ms
- **L3 LLM rerank**: 1000-3500ms

---

## What Changed in the UI

After the fixes, the AI Recommendation panel now shows:

1. **Category chip** (blue) - e.g., "Карты"
2. **Subcategory chip** (purple) - e.g., "Регистрация и онбординг"
3. **Confidence chip** (color-coded) - Shows percentage range:
   - Green (high): 80-100%
   - Orange (medium): 50-79%
   - Red (low): 0-49%
4. **Route chip** (blue) - Shows which level processed the request:
   - "L1 Точное совпадение" (exact match)
   - "L2 Семантический поиск" (semantic search)
   - "L3 LLM rerank" (LLM reranking)
5. **Processing time chip** (grey) - Shows time in milliseconds

---

## Next Steps

After successful initialization:

1. **Test with various questions** to see different routing levels
2. **Monitor L1 hit rate** in logs to see cache effectiveness
3. **Adjust similarity threshold** (currently 0.95) if needed in `src/chat/rag.py`
4. **Generate synthetic data** to improve embeddings (optional)

---

## Quick Reference Commands

```bash
# Initialize inside Docker
docker exec -it smart-support-backend python /opt/chat/scripts/init_faiss_index.py --recreate

# Check if initialized
docker exec -it smart-support-backend ls -lh /opt/chat/data/

# View logs
docker-compose logs -f smart-support-backend

# Restart backend
docker-compose restart smart-support-backend

# Run quick test
docker exec -it smart-support-backend python /opt/chat/scripts/quick_test.py
```
