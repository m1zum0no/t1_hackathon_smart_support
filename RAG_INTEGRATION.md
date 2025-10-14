# RAG Integration Guide

## Overview

This project integrates a Retrieval-Augmented Generation (RAG) pipeline for intelligent customer support using:
- **LLM**: Qwen2.5-72B-Instruct-AWQ (via Scibox API)
- **Embeddings**: bge-m3 (via Scibox API)
- **Vector Database**: FAISS
- **Dataset**: smart_support.xlsx

## Architecture

```
User Query → Frontend (Vue.js)
    ↓
FastAPI Backend (/chat/hint/)
    ↓
RAG Pipeline:
  1. Query Embedding (bge-m3)
  2. FAISS Similarity Search
  3. Context Retrieval
  4. Classification (Category/Subcategory)
  5. LLM Generation (Qwen2.5)
    ↓
Response with:
  - Answer text
  - Category/Subcategory
  - Template reference
  - Confidence level
    ↓
Frontend Display (Styled hint card)
```

## Setup Instructions

### 1. Backend Setup

#### Install Dependencies
```bash
cd fastapi-chat
poetry install
```

#### Initialize FAISS Index
```bash
# Make sure smart_support.xlsx is in fastapi-chat/data/
poetry run python scripts/init_faiss_index.py
```

This will:
- Load the dataset from `data/smart_support.xlsx`
- Generate embeddings using bge-m3
- Create FAISS index at `data/faiss_index_bge_m3.bin`
- Save metadata at `data/metadata.json`

#### Start Backend Server
```bash
poetry run uvicorn src.main:app --reload --port 8001
```

### 2. Frontend Setup

```bash
cd vuetify-chat
npm install
npm run dev
```

## Usage

1. **Open the chat interface** in your browser
2. **Type a customer query** in the message input
3. **Click the lightbulb button** (💡) to request an AI hint
4. **View the recommendation** with:
   - Category and subcategory tags
   - AI-generated response
   - Template reference
   - Confidence indicator (high/medium/low)

## Features

### Classification & Entity Extraction
- Automatically classifies queries into categories and subcategories
- Extracts relevant entities from the customer question
- Uses semantic similarity to find the best matching category

### Recommendation Quality
- Retrieves top-3 most relevant examples from the knowledge base
- Generates contextual responses using Qwen2.5-72B
- Adapts templates to specific customer questions
- Provides confidence scores for transparency

### User Interface
- Beautiful, modern hint cards with gradient backgrounds
- Color-coded confidence indicators:
  - 🟢 Green: High confidence
  - 🟡 Yellow: Medium confidence
  - 🔴 Red: Low confidence
- Category/subcategory chips for quick classification
- Template reference for operator guidance

### Performance
- Fast retrieval using FAISS vector search
- Batch embedding generation for efficiency
- Caching support for frequently asked questions
- Async API calls for non-blocking operations

## API Endpoints

### Get Hint
```http
POST /chat/hint/?query=<customer_query>
```

**Response:**
```json
{
  "response": "Здравствуйте! Для восстановления пароля...",
  "confidence": "high",
  "category": "Технические вопросы",
  "subcategory": "Восстановление доступа",
  "template": "Инструкция по восстановлению пароля"
}
```

## Configuration

Environment variables in `fastapi-chat/src/.env`:

```env
SCIBOX_API_KEY="sk-Crh_Ol2yEhe0c8tpELeTkQ"
SCIBOX_BASE_URL="https://llm.t1v.scibox.tech/v1"
SCIBOX_LLM_MODEL="Qwen2.5-72B-Instruct-AWQ"
SCIBOX_EMBEDDING_MODEL="bge-m3"
```

## Dataset Format

The `smart_support.xlsx` file should contain:
- **Вопрос клиента** (Customer Question)
- **Категория** (Category)
- **Подкатегория** (Subcategory)
- **Шаблон ответа** (Answer Template)
- **Ключевые слова** (Keywords) - optional

## Troubleshooting

### FAISS Index Not Found
```bash
cd fastapi-chat
poetry run python scripts/init_faiss_index.py
```

### API Connection Issues
- Verify `SCIBOX_API_KEY` is correct
- Check network connectivity to `llm.t1v.scibox.tech`
- Review logs for detailed error messages

### Empty Responses
- Ensure the dataset has sufficient examples
- Check that embeddings are being generated correctly
- Verify the query is in Russian (the model is optimized for Russian)

## Assessment Criteria Coverage

✅ **Classification and Entity Extraction Quality**
- Automatic category/subcategory classification
- Semantic similarity-based matching
- Entity extraction from customer queries

✅ **Relevance of Recommendations**
- Top-k retrieval from knowledge base
- Context-aware response generation
- Template adaptation to specific questions

✅ **User Interface and Usability**
- Modern, intuitive operator interface
- Clear visualization of AI recommendations
- Quick access to hints via lightbulb button

✅ **System Performance**
- Fast FAISS vector search
- Efficient batch processing
- Async API architecture

✅ **Presentation Quality**
- Professional UI design
- Clear business logic demonstration
- Comprehensive documentation

## Future Enhancements

- [ ] Feedback mechanism for continuous learning
- [ ] Multi-turn conversation support
- [ ] Advanced filtering by category
- [ ] Analytics dashboard for operators
- [ ] A/B testing for different prompts
- [ ] Integration with ticketing systems
