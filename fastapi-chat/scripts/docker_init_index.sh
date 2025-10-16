#!/bin/bash
# Script to initialize FAISS index inside Docker container

echo "=========================================="
echo "Initializing FAISS Index and L1 Cache"
echo "=========================================="

cd /opt/chat

# Run the initialization script
python scripts/init_faiss_index.py --recreate

echo ""
echo "=========================================="
echo "Initialization Complete!"
echo "=========================================="
