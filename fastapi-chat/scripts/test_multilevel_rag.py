#!/usr/bin/env python3
"""
Test script for multi-level RAG implementation.
Tests L1 (exact match), L2 (semantic search), and L3 (LLM rerank) routing.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.chat.rag import generate_hint

def test_rag_system():
    """Test the multi-level RAG system with various queries."""
    
    test_cases = [
        {
            "name": "Test 1: Exact match (should hit L1 cache)",
            "question": "Как сбросить пароль?",
            "expected_route": "L1"
        },
        {
            "name": "Test 2: Similar question (should hit L2 or L3)",
            "question": "Не могу войти в систему, забыл пароль",
            "expected_route": "L2 or L3"
        },
        {
            "name": "Test 3: Semantic search (should hit L2 or L3)",
            "question": "Проблема с доступом к аккаунту",
            "expected_route": "L2 or L3"
        }
    ]
    
    print("=" * 80)
    print("TESTING MULTI-LEVEL RAG SYSTEM")
    print("=" * 80)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{test_case['name']}")
        print("-" * 80)
        print(f"Question: {test_case['question']}")
        
        try:
            hint = generate_hint(test_case['question'])
            
            print(f"\n✓ Route: {hint.route}")
            print(f"✓ Confidence: {hint.confidence}")
            print(f"✓ Processing time: {hint.processing_time_ms}ms")
            print(f"✓ Candidates found: {hint.candidates_found}")
            print(f"✓ Category: {hint.category}")
            print(f"✓ Subcategory: {hint.subcategory}")
            print(f"\nResponse:\n{hint.response[:200]}{'...' if len(hint.response) > 200 else ''}")
            
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_rag_system()
