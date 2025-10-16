#!/bin/bash
set -e

echo "=========================================="
echo "Smart Support Backend - Starting..."
echo "=========================================="

# Wait for database
echo "Waiting for database..."
sleep 5

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Check if FAISS index exists
if [ ! -f /opt/chat/data/faiss_index_bge_m3.bin ]; then
    echo "=========================================="
    echo "FAISS index not found. Initializing..."
    echo "=========================================="
    python scripts/init_faiss_index.py || {
        echo "ERROR: FAISS index initialization failed!"
        echo "The system will start but RAG features may not work."
        echo "You can manually initialize later with:"
        echo "  docker exec -it smart-support-backend python /opt/chat/scripts/init_faiss_index.py --recreate"
    }
else
    echo "✓ FAISS index found at /opt/chat/data/faiss_index_bge_m3.bin"
    
    # Check if L1 cache exists
    if [ ! -f /opt/chat/data/l1_cache.json ]; then
        echo "L1 cache not found. Rebuilding from metadata..."
        python -c "
import sys
sys.path.insert(0, '/opt/chat')
from src.chat.rag import dataset_metadata, build_l1_cache_from_dataset, load_rag_components
try:
    _, _, _, metadata, _ = load_rag_components()
    if metadata:
        build_l1_cache_from_dataset(metadata)
        print('✓ L1 cache rebuilt successfully')
    else:
        print('WARNING: No metadata found, skipping L1 cache rebuild')
except Exception as e:
    print(f'ERROR: Failed to rebuild L1 cache: {e}')
"
    else
        echo "✓ L1 cache found at /opt/chat/data/l1_cache.json"
    fi
fi

echo "=========================================="
echo "Starting FastAPI server..."
echo "=========================================="

# Start the FastAPI server
exec uvicorn src.main:app --host=0.0.0.0 --port=8001 --reload
