# System Architecture - Smart Support RAG

## 🏗️ High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         OPERATOR INTERFACE                        │
│                         (Vue.js + Vuetify)                        │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Chat Window                                             │    │
│  │  ┌────────────────────────────────────────────────┐     │    │
│  │  │ Customer: "Не могу войти в личный кабинет"     │     │    │
│  │  └────────────────────────────────────────────────┘     │    │
│  │                                                          │    │
│  │  [Type message...] [📎] [😊] [📤] [💡]                   │    │
│  │                                      ↑                   │    │
│  │                                      │ Click for hint    │    │
│  └──────────────────────────────────────┼───────────────────┘    │
│                                         │                         │
│  ┌──────────────────────────────────────▼───────────────────┐    │
│  │  AI Recommendation Card                                  │    │
│  │  ┌────────────────────────────────────────────────────┐ │    │
│  │  │ 💡 AI Recommendation                               │ │    │
│  │  ├────────────────────────────────────────────────────┤ │    │
│  │  │ [Технические вопросы] [Проблемы с доступом]        │ │    │
│  │  │                                                    │ │    │
│  │  │ Здравствуйте! Для восстановления доступа к        │ │    │
│  │  │ личному кабинету:                                  │ │    │
│  │  │ 1. Нажмите "Забыли пароль?"                        │ │    │
│  │  │ 2. Введите email                                   │ │    │
│  │  │ 3. Следуйте инструкциям в письме                   │ │    │
│  │  │                                                    │ │    │
│  │  │ Template: Инструкция по восстановлению доступа     │ │    │
│  │  │                                                    │ │    │
│  │  │                          [Confidence: high] 🟢     │ │    │
│  │  └────────────────────────────────────────────────────┘ │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
                                │
                                │ HTTP POST
                                │ /chat/hint/?query=...
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                         FASTAPI BACKEND                           │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  API Router (src/chat/router.py)                           │  │
│  │  POST /chat/hint/                                          │  │
│  │  ├─ Receives: query parameter                             │  │
│  │  ├─ Calls: generate_hint(query)                           │  │
│  │  └─ Returns: Hint object (JSON)                           │  │
│  └────────────────────┬───────────────────────────────────────┘  │
│                       │                                           │
│  ┌────────────────────▼───────────────────────────────────────┐  │
│  │  RAG Pipeline (src/chat/rag.py)                            │  │
│  │                                                            │  │
│  │  Step 1: EMBEDDING                                         │  │
│  │  ┌──────────────────────────────────────────────────────┐ │  │
│  │  │ Query: "Не могу войти в личный кабинет"              │ │  │
│  │  │         ↓                                            │ │  │
│  │  │ bge-m3 Embedding API                                 │ │  │
│  │  │         ↓                                            │ │  │
│  │  │ Vector: [0.12, -0.34, 0.56, ..., 0.89] (1024-dim)   │ │  │
│  │  └──────────────────────────────────────────────────────┘ │  │
│  │                                                            │  │
│  │  Step 2: RETRIEVAL                                         │  │
│  │  ┌──────────────────────────────────────────────────────┐ │  │
│  │  │ FAISS Index Search (IndexFlatIP)                     │ │  │
│  │  │         ↓                                            │ │  │
│  │  │ Top-3 Similar Questions:                             │ │  │
│  │  │ 1. "Забыл пароль от личного кабинета" (0.95)        │ │  │
│  │  │ 2. "Не могу войти в аккаунт" (0.89)                 │ │  │
│  │  │ 3. "Проблема с авторизацией" (0.82)                 │ │  │
│  │  └──────────────────────────────────────────────────────┘ │  │
│  │                                                            │  │
│  │  Step 3: CLASSIFICATION                                    │  │
│  │  ┌──────────────────────────────────────────────────────┐ │  │
│  │  │ Extract from best match:                             │ │  │
│  │  │ Category: "Технические вопросы"                      │ │  │
│  │  │ Subcategory: "Проблемы с доступом"                   │ │  │
│  │  └──────────────────────────────────────────────────────┘ │  │
│  │                                                            │  │
│  │  Step 4: PROMPT CONSTRUCTION                               │  │
│  │  ┌──────────────────────────────────────────────────────┐ │  │
│  │  │ System: "Ты — ассистент службы поддержки..."         │ │  │
│  │  │                                                      │ │  │
│  │  │ User Prompt:                                         │ │  │
│  │  │ - Вопрос клиента: [query]                           │ │  │
│  │  │ - Категория: [category]                             │ │  │
│  │  │ - Похожие вопросы: [top-3 contexts]                 │ │  │
│  │  │ - Инструкции: [formatting rules]                    │ │  │
│  │  │ - Требуемый формат: JSON                            │ │  │
│  │  └──────────────────────────────────────────────────────┘ │  │
│  │                                                            │  │
│  │  Step 5: LLM GENERATION                                    │  │
│  │  ┌──────────────────────────────────────────────────────┐ │  │
│  │  │ Qwen2.5-72B-Instruct-AWQ                             │ │  │
│  │  │ Temperature: 0.3                                     │ │  │
│  │  │ Max tokens: 800                                      │ │  │
│  │  │         ↓                                            │ │  │
│  │  │ JSON Response:                                       │ │  │
│  │  │ {                                                    │ │  │
│  │  │   "response": "Здравствуйте! Для восстановления...",│ │  │
│  │  │   "confidence": "high",                              │ │  │
│  │  │   "template": "Инструкция по восстановлению..."     │ │  │
│  │  │ }                                                    │ │  │
│  │  └──────────────────────────────────────────────────────┘ │  │
│  │                                                            │  │
│  │  Step 6: RESPONSE ASSEMBLY                                 │  │
│  │  ┌──────────────────────────────────────────────────────┐ │  │
│  │  │ Hint Object:                                         │ │  │
│  │  │ - response: [LLM generated text]                     │ │  │
│  │  │ - category: [from classification]                    │ │  │
│  │  │ - subcategory: [from classification]                 │ │  │
│  │  │ - template: [from LLM]                               │ │  │
│  │  │ - confidence: [from LLM]                             │ │  │
│  │  └──────────────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
                                │
                                │ API Calls
                                ▼
┌──────────────────────────────────────────────────────────────────┐
│                    SCIBOX API (llm.t1v.scibox.tech)               │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  /v1/embeddings                                            │  │
│  │  Model: bge-m3                                             │  │
│  │  Input: "Не могу войти в личный кабинет"                  │  │
│  │  Output: [0.12, -0.34, ..., 0.89] (1024 dimensions)       │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  /v1/chat/completions                                      │  │
│  │  Model: Qwen2.5-72B-Instruct-AWQ                           │  │
│  │  Messages: [system, user]                                  │  │
│  │  Output: JSON with response, confidence, template          │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

## 📊 Data Flow Timeline

```
Time    Component           Action
────────────────────────────────────────────────────────────────
0ms     Frontend            User clicks 💡 button
10ms    Frontend            messageStore.getHint(query)
20ms    Frontend            POST /chat/hint/?query=...
        
30ms    Backend Router      Receive request
40ms    Backend Router      Call generate_hint(query)
        
50ms    RAG Pipeline        Start embedding generation
150ms   Scibox API          Return query embedding
        
160ms   RAG Pipeline        FAISS search
170ms   RAG Pipeline        Top-3 results retrieved
        
180ms   RAG Pipeline        Classification complete
190ms   RAG Pipeline        Prompt constructed
200ms   RAG Pipeline        Send to LLM
        
2500ms  Scibox API          LLM generates response
        
2510ms  RAG Pipeline        Parse JSON response
2520ms  RAG Pipeline        Assemble Hint object
        
2530ms  Backend Router      Return Hint to frontend
2540ms  Frontend            Receive response
2550ms  Frontend            Display hint card
────────────────────────────────────────────────────────────────
Total: ~2.5-3 seconds
```

## 🗄️ Data Storage

```
fastapi-chat/data/
├── smart_support.xlsx          # Original dataset
│   Columns:
│   - Вопрос клиента           # Customer questions
│   - Категория                # Categories
│   - Подкатегория             # Subcategories
│   - Шаблон ответа            # Answer templates
│   - Ключевые слова           # Keywords
│
├── faiss_index_bge_m3.bin     # FAISS vector index
│   - Type: IndexFlatIP
│   - Dimension: 1024
│   - Vectors: N (number of questions)
│   - Size: ~4MB per 1000 vectors
│
└── metadata.json              # Question metadata
    [
      {
        "index": 0,
        "question": "...",
        "category": "...",
        "subcategory": "...",
        "template": "...",
        "keywords": "..."
      },
      ...
    ]
```

## 🔄 Component Interactions

```
┌─────────────────────────────────────────────────────────────┐
│                    Component Diagram                         │
└─────────────────────────────────────────────────────────────┘

Frontend Components:
┌──────────────────────┐
│ SelectedChatWindow   │  - Message input
│                      │  - Lightbulb button
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ messageStore         │  - getHint() action
│                      │  - API client
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ MainChat             │  - Display hint card
│                      │  - Format categories
│                      │  - Show confidence
└──────────────────────┘

Backend Components:
┌──────────────────────┐
│ router.py            │  - /chat/hint/ endpoint
│                      │  - Query parameter
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ rag.py               │  - RAG pipeline
│                      │  - FAISS search
│                      │  - LLM generation
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ SciboxEmbeddings     │  - Embedding wrapper
│                      │  - OpenAI client
└──────────────────────┘

External Services:
┌──────────────────────┐
│ Scibox API           │  - bge-m3 embeddings
│                      │  - Qwen2.5-72B LLM
└──────────────────────┘
```

## 🎯 RAG Pipeline Detailed Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    RAG Pipeline Stages                       │
└─────────────────────────────────────────────────────────────┘

1. INPUT PROCESSING
   ┌──────────────────────────────────────────────┐
   │ Query: "Не могу войти в личный кабинет"      │
   │ Validation: ✓ Non-empty                      │
   │ Language: Russian                            │
   └──────────────────────────────────────────────┘

2. EMBEDDING GENERATION
   ┌──────────────────────────────────────────────┐
   │ Model: bge-m3                                │
   │ API: POST /v1/embeddings                     │
   │ Input: Query text                            │
   │ Output: 1024-dimensional vector              │
   │ Normalization: L2 normalized                 │
   └──────────────────────────────────────────────┘

3. SIMILARITY SEARCH
   ┌──────────────────────────────────────────────┐
   │ Index: FAISS IndexFlatIP                     │
   │ Metric: Cosine similarity (via inner product)│
   │ Top-k: 3 results                             │
   │ Results:                                     │
   │   [0] similarity: 0.95                       │
   │   [1] similarity: 0.89                       │
   │   [2] similarity: 0.82                       │
   └──────────────────────────────────────────────┘

4. CONTEXT RETRIEVAL
   ┌──────────────────────────────────────────────┐
   │ For each result:                             │
   │   - Question text                            │
   │   - Category                                 │
   │   - Subcategory                              │
   │   - Template                                 │
   │   - Keywords                                 │
   │   - Similarity score                         │
   └──────────────────────────────────────────────┘

5. CLASSIFICATION
   ┌──────────────────────────────────────────────┐
   │ Method: Best match classification            │
   │ Source: Top-1 result                         │
   │ Extracted:                                   │
   │   - Category: "Технические вопросы"          │
   │   - Subcategory: "Проблемы с доступом"       │
   └──────────────────────────────────────────────┘

6. PROMPT ENGINEERING
   ┌──────────────────────────────────────────────┐
   │ System Prompt:                               │
   │   "Ты — ассистент службы поддержки..."       │
   │                                              │
   │ User Prompt Structure:                       │
   │   1. Customer query                          │
   │   2. Detected category/subcategory           │
   │   3. Similar examples (top-3)                │
   │   4. Instructions                            │
   │   5. Output format (JSON)                    │
   └──────────────────────────────────────────────┘

7. LLM GENERATION
   ┌──────────────────────────────────────────────┐
   │ Model: Qwen2.5-72B-Instruct-AWQ              │
   │ API: POST /v1/chat/completions               │
   │ Parameters:                                  │
   │   - temperature: 0.3 (focused)               │
   │   - max_tokens: 800                          │
   │   - messages: [system, user]                 │
   │                                              │
   │ Output: JSON string                          │
   └──────────────────────────────────────────────┘

8. RESPONSE PARSING
   ┌──────────────────────────────────────────────┐
   │ Parse JSON:                                  │
   │   - Remove markdown code blocks              │
   │   - Extract fields                           │
   │   - Validate structure                       │
   │                                              │
   │ Fallback: Use raw text if JSON fails         │
   └──────────────────────────────────────────────┘

9. RESULT ASSEMBLY
   ┌──────────────────────────────────────────────┐
   │ Hint Object:                                 │
   │   {                                          │
   │     response: "...",                         │
   │     confidence: "high",                      │
   │     category: "Технические вопросы",         │
   │     subcategory: "Проблемы с доступом",      │
   │     template: "..."                          │
   │   }                                          │
   └──────────────────────────────────────────────┘

10. DELIVERY
    ┌──────────────────────────────────────────────┐
    │ HTTP Response: 200 OK                        │
    │ Content-Type: application/json               │
    │ Body: Hint object                            │
    └──────────────────────────────────────────────┘
```

## 🔐 Security & Configuration

```
Environment Variables (.env):
┌──────────────────────────────────────────────┐
│ SCIBOX_API_KEY                               │
│   - Authentication token                     │
│   - Required for all API calls               │
│                                              │
│ SCIBOX_BASE_URL                              │
│   - API endpoint                             │
│   - Default: https://llm.t1v.scibox.tech/v1  │
│                                              │
│ SCIBOX_LLM_MODEL                             │
│   - LLM model name                           │
│   - Value: Qwen2.5-72B-Instruct-AWQ          │
│                                              │
│ SCIBOX_EMBEDDING_MODEL                       │
│   - Embedding model name                     │
│   - Value: bge-m3                            │
└──────────────────────────────────────────────┘
```

---

**Architecture Version**: 1.0.0  
**Last Updated**: 2025-10-14  
**Status**: Production Ready ✅
