# Multi-Level RAG Implementation

## Overview

This implementation provides a **3-level routing system** for AI-powered customer support recommendations, as specified in `algo_rag.txt`. The system ensures that responses are **exact matches from the knowledge base** rather than generated text, minimizing the risk of errors in a financial organization context.

## Architecture

### Level 1 (L1): Exact Match Cache
- **Purpose**: Instant responses for exact question matches
- **Technology**: Hash-based lookup using MD5 of normalized text
- **Confidence**: High (100%)
- **Processing Time**: < 10ms typically
- **Use Case**: Questions that exactly match entries in the knowledge base

### Level 2 (L2): Semantic Search
- **Purpose**: Find similar questions using vector similarity
- **Technology**: 
  - Embeddings: `bge-m3` model via Scibox API
  - Vector Store: FAISS with cosine similarity (IndexFlatIP)
- **Confidence**: High if similarity ≥ 0.95, otherwise proceeds to L3
- **Processing Time**: 50-200ms typically
- **Use Case**: Questions semantically similar to knowledge base entries

### Level 3 (L3): LLM Rerank
- **Purpose**: Select the best answer from multiple candidates using LLM reasoning
- **Technology**: `Qwen2.5-72B-Instruct-AWQ` via Scibox API
- **Confidence**: Based on LLM's confidence score (0-100)
  - High: ≥ 80%
  - Medium: 50-79%
  - Low: < 50%
- **Processing Time**: 1000-3500ms typically
- **Use Case**: Ambiguous questions requiring intelligent selection

## Key Features

### 1. **No Text Generation**
- System returns **exact templates** from the knowledge base
- Complies with the requirement: "Ответ должен дословно соответствовать тому, что в есть в базе знаний"
- Eliminates risk of hallucinations or incorrect information

### 2. **Progressive Routing**
```
Question → L1 Exact Match → Found? → Return (High Confidence)
                ↓ Not Found
           L2 Semantic Search → Similarity ≥ 0.95? → Return (High Confidence)
                ↓ Similarity < 0.95
           L3 LLM Rerank → Select Best → Return (Variable Confidence)
```

### 3. **Confidence Scoring**
- **High**: Exact match (L1) or very high semantic similarity (L2 ≥ 0.95) or LLM confidence ≥ 80%
- **Medium**: LLM confidence 50-79%
- **Low**: LLM confidence < 50% or no suitable answer found

### 4. **Performance Tracking**
Each response includes:
- `route`: Which level processed the request (L1/L2/L3)
- `processing_time_ms`: Time taken in milliseconds
- `candidates_found`: Number of candidates retrieved
- `confidence`: Confidence level (high/medium/low)

## Implementation Details

### Data Flow

1. **Initialization**:
   ```python
   # Load dataset from smart_support.xlsx
   # Create FAISS index with bge-m3 embeddings
   # Build L1 cache from questions
   ```

2. **Query Processing**:
   ```python
   def generate_hint(question: str) -> Hint:
       # L1: Check exact match cache
       if exact_match_found:
           return template with high confidence
       
       # L2: Semantic search
       candidates = semantic_search(question, top_k=5)
       if top_similarity >= 0.95:
           return template with high confidence
       
       # L3: LLM rerank
       best_candidate = llm_rerank(question, top_3_candidates)
       return template with variable confidence
   ```

### File Structure

```
fastapi-chat/
├── src/chat/rag.py          # Main implementation
├── data/
│   ├── smart_support.xlsx   # Knowledge base dataset
│   ├── faiss_index_bge_m3.bin  # FAISS vector index
│   ├── metadata.json        # Question metadata
│   └── l1_cache.json        # L1 exact match cache
└── scripts/
    ├── init_faiss_index.py  # Initialize FAISS index
    └── test_multilevel_rag.py  # Test the system
```

### Configuration (src/config.py)

```python
SCIBOX_API_KEY = "sk-Crh_Ol2yEhe0c8tpELeTkQ"
SCIBOX_BASE_URL = "https://llm.t1v.scibox.tech/v1"
SCIBOX_LLM_MODEL = "Qwen2.5-72B-Instruct-AWQ"
SCIBOX_EMBEDDING_MODEL = "bge-m3"
```

## Usage

### Initialize the System

```bash
cd fastapi-chat
python scripts/init_faiss_index.py
```

This will:
- Load `data/smart_support.xlsx`
- Generate embeddings using `bge-m3`
- Create FAISS index
- Build L1 cache

### Query the System

```python
from src.chat.rag import generate_hint

# Ask a question
hint = generate_hint("Как сбросить пароль?")

print(f"Route: {hint.route}")
print(f"Confidence: {hint.confidence}")
print(f"Response: {hint.response}")
print(f"Time: {hint.processing_time_ms}ms")
```

### Test the System

```bash
cd fastapi-chat
python scripts/test_multilevel_rag.py
```

## Statistics (from algo_rag.txt)

- **Knowledge Base**: 201 answers, 6 categories, 35 subcategories
- **L1 Cache**: ~1197 exact matches for instant responses
- **L2 Vector Index**: ~1200 vector features for semantic search
- **L3 Candidates**: Typically 3 candidates for LLM reranking

## Performance Characteristics

| Level | Avg Time | Confidence | Use Case |
|-------|----------|------------|----------|
| L1 | < 10ms | High | Exact matches |
| L2 | 50-200ms | High (if sim ≥ 0.95) | Similar questions |
| L3 | 1000-3500ms | Variable | Ambiguous questions |

## Error Handling

- **No candidates found**: Returns low confidence message asking for clarification
- **LLM failure**: Falls back to highest similarity candidate
- **System unavailable**: Returns error message with low confidence

## Compliance with Requirements

✅ **Exact match requirement**: Returns only templates from knowledge base  
✅ **No generation**: System selects, never generates responses  
✅ **Multi-level routing**: L1 → L2 → L3 cascade  
✅ **Confidence scoring**: Based on routing level and LLM confidence  
✅ **Performance tracking**: Processing time and route information  
✅ **Scibox integration**: Uses bge-m3 and Qwen2.5-72B-Instruct-AWQ  

## Future Enhancements

1. **Synthetic Data Generation**: Generate ~2000 variations from 200 base questions to improve embeddings
2. **L3.5 Manual Correction**: Add human-in-the-loop for low confidence answers
3. **L4 Manual Review**: Queue for human review
4. **Cache Warming**: Pre-compute common question variations
5. **A/B Testing**: Compare L2 vs L3 performance for optimization

## References

- Task specification: `algo_rag.txt`
- Scibox API documentation: `SciboxInstruction.md`
- Dataset: `fastapi-chat/data/smart_support.xlsx`
