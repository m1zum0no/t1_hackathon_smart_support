#!/usr/bin/env python3
"""
Test script for RAG pipeline.
Tests the hint generation functionality.
"""
import sys
import os

# Add the parent directory to the path to import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.chat.rag import generate_hint
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_hint_generation():
    """Test hint generation with sample queries."""
    
    test_queries = [
        "Как восстановить пароль?",
        "Не могу войти в личный кабинет",
        "Как оформить возврат товара?",
        "Проблема с оплатой картой",
        "Где посмотреть историю заказов?"
    ]
    
    logger.info("Testing RAG pipeline with sample queries...\n")
    
    for i, query in enumerate(test_queries, 1):
        logger.info(f"Test {i}/{len(test_queries)}")
        logger.info(f"Query: {query}")
        
        try:
            hint = generate_hint(query)
            
            logger.info(f"✓ Response generated successfully!")
            logger.info(f"  Category: {hint.category}")
            logger.info(f"  Subcategory: {hint.subcategory}")
            logger.info(f"  Confidence: {hint.confidence}")
            logger.info(f"  Response: {hint.response[:100]}...")
            if hint.template:
                logger.info(f"  Template: {hint.template[:80]}...")
            logger.info("")
            
        except Exception as e:
            logger.error(f"✗ Failed to generate hint: {e}")
            logger.error("", exc_info=True)
            return 1
    
    logger.info("All tests completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(test_hint_generation())
