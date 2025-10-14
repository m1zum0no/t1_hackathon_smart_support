#!/usr/bin/env python3
"""
Script to initialize FAISS index from smart_support.xlsx dataset.
This script should be run once before starting the FastAPI server.
"""
import sys
import os

# Add the parent directory to the path to import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.chat.rag import create_faiss_index, SciboxEmbeddings, DATASET_PATH, FAISS_INDEX_PATH, METADATA_PATH
from src.config import settings
from openai import OpenAI
import logging
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Initialize FAISS index from dataset."""
    parser = argparse.ArgumentParser(description="Initialize FAISS index.")
    parser.add_argument("--recreate", action="store_true", help="Recreate the index if it already exists.")
    args = parser.parse_args()

    logger.info("Starting FAISS index initialization...")
    
    # Check if dataset exists
    if not os.path.exists(DATASET_PATH):
        logger.error(f"Dataset not found at {DATASET_PATH}")
        logger.error("Please ensure smart_support.xlsx is in the data/ directory")
        return 1
    
    # Check if index already exists
    if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(METADATA_PATH):
        if not args.recreate:
            logger.info("FAISS index already exists. Skipping creation. Use --recreate to overwrite.")
            return 0
        logger.info("Recreating FAISS index as requested.")
    
    try:
        # Initialize OpenAI client for Scibox API
        client = OpenAI(
            api_key=settings.SCIBOX_API_KEY,
            base_url=settings.SCIBOX_BASE_URL
        )
        
        # Initialize embedding model
        embedding_model = SciboxEmbeddings(
            client=client,
            model=settings.SCIBOX_EMBEDDING_MODEL
        )
        
        logger.info("Creating FAISS index...")
        index, metadata = create_faiss_index(embedding_model)
        
        logger.info(f"✓ FAISS index created successfully!")
        logger.info(f"  - Index file: {FAISS_INDEX_PATH}")
        logger.info(f"  - Metadata file: {METADATA_PATH}")
        logger.info(f"  - Total vectors: {index.ntotal}")
        logger.info(f"  - Dimension: {index.d}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Failed to create FAISS index: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
