#!/usr/bin/env python3
"""
Quick test script to verify RAG system is working.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')

from src.chat.rag import generate_hint, l1_cache, dataset_metadata

def main():
    print("=" * 80)
    print("QUICK RAG SYSTEM TEST")
    print("=" * 80)
    
    # Check if components are loaded
    print(f"\n✓ L1 Cache entries: {len(l1_cache) if l1_cache else 0}")
    print(f"✓ Dataset metadata entries: {len(dataset_metadata) if dataset_metadata else 0}")
    
    if not l1_cache:
        print("\n⚠ WARNING: L1 cache is empty. Run 'python scripts/init_faiss_index.py' first.")
        return 1
    
    if not dataset_metadata:
        print("\n⚠ WARNING: Dataset metadata is empty. Run 'python scripts/init_faiss_index.py' first.")
        return 1
    
    # Show some sample questions from L1 cache
    print("\n" + "-" * 80)
    print("SAMPLE QUESTIONS FROM L1 CACHE (first 5):")
    print("-" * 80)
    for i, (hash_key, entry) in enumerate(list(l1_cache.items())[:5]):
        print(f"\n{i+1}. Question: {entry['question'][:80]}...")
        print(f"   Normalized: {entry.get('normalized_question', 'N/A')[:80]}...")
        print(f"   Category: {entry['category']} / {entry['subcategory']}")
    
    # Test with exact question from cache
    print("\n" + "=" * 80)
    print("TEST 1: Exact match from cache")
    print("=" * 80)
    
    # Get first question from cache
    first_entry = list(l1_cache.values())[0]
    test_question = first_entry['question']
    
    print(f"\nTest Question: {test_question}")
    print("\nGenerating hint...")
    
    try:
        hint = generate_hint(test_question)
        
        print(f"\n✓ Route: {hint.route}")
        print(f"✓ Confidence: {hint.confidence}")
        print(f"✓ Processing time: {hint.processing_time_ms}ms")
        print(f"✓ Candidates found: {hint.candidates_found}")
        print(f"✓ Category: {hint.category} / {hint.subcategory}")
        print(f"\nResponse:\n{hint.response[:200]}{'...' if len(hint.response) > 200 else ''}")
        
        if hint.route.startswith("L1"):
            print("\n✓✓✓ SUCCESS: L1 exact match working!")
        else:
            print(f"\n⚠ WARNING: Expected L1 route but got {hint.route}")
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Test with slightly modified question
    print("\n" + "=" * 80)
    print("TEST 2: Slightly modified question (should hit L2 or L3)")
    print("=" * 80)
    
    modified_question = test_question.replace("?", "").strip() + " пожалуйста?"
    print(f"\nTest Question: {modified_question}")
    print("\nGenerating hint...")
    
    try:
        hint = generate_hint(modified_question)
        
        print(f"\n✓ Route: {hint.route}")
        print(f"✓ Confidence: {hint.confidence}")
        print(f"✓ Processing time: {hint.processing_time_ms}ms")
        print(f"✓ Candidates found: {hint.candidates_found}")
        print(f"\nResponse:\n{hint.response[:200]}{'...' if len(hint.response) > 200 else ''}")
        
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
