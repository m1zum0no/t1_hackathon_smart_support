# How to run web-service 

## Backend:
### Run:
``` bash
cd fastapi-chat
docker network create chat-net
docker-compose up --build -d
docker exec chat-backend poetry run alembic upgrade head
```

### Stop:
```bash
docker-compose down
docker-compose rm -f
```

## Frontend:

### Run:
```bash
cd vuetify-chat
npm install
npm run dev
```

### Stop:
```Ctrl-C```

## Stack

For hackathon we choose simple, fast stack to implement, to fit in time. Everything can be built in 1-2 days, without complex training (RAG does not require fine-tuning).

| Component | Recommendation | Why? |
|-----------|--------------|---------|
| Language/Framework | Python + LangChain (for RAG pipeline) | LangChain simplifies embeddings, retrieval and LLM integration. Easy to add streaming and chaining (classification + NER). |
| Embeddings (vectorization) | Scibox API (models: text-embedding-3-small or OpenAI-compatible) | Low latency, good semantics. Embedding size: 1536 dims. Alternative: HuggingFaceSentenceTransformers if Scibox is not available locally. |
| Text chunking | RecursiveCharacterTextSplitter (from LangChain) | Splits documents into chunks of 500-1000 tokens with 20% overlap to preserve context. Supports metadata (e.g., document source). |
| Vector database | FAISS (Facebook AI Similarity Search) | Local, fast, no cloud dependency. Cosine similarity indexing. For scale-up: Pinecone (cloud, with API). Stores ~10k chunks easily. |
| LLM for generation/classification/NER | Scibox API (models: GPT-4o-mini or Grok analog) | OpenAI-compatible, supports streaming. For NER and classification: LangChain chain (e.g., create_extraction_chain). |
| Web interface | FastAPI + Vue.js | Quick chat prototyping with real-time updates. WebSocket for streaming suggestions. |
| Дополнительно | Pydantic (для валидации), Celery (если нужен background ingestion) | Для обработки больших баз знаний. |


## Step-by-step algorithm (RAG pipeline with classification and NER)

### 1. Ingestion Pipeline

- Load documents (PDF, TXT, FAQ) from folder or URL
- Split into chunks: `splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)`
- Vectorize: `embeddings = SciboxEmbeddings(model="text-embedding-3-small")`; get vector for each chunk
- Add metadata (e.g., `{"source": "FAQ_v1", "category": "billing"}`)
- Save to FAISS: `vectorstore = FAISS.from_documents(chunks, embeddings)`. Index ready to search

### 2. Real-time Query Pipeline

**Input**: Text client query (e.g., "My iPhone 14 doesn't charge after iOS 17 update")

**Step 2.1: Classification and NER (using LLM-chain)**

- Prompt for LLM: "Classify query: [query]. Categories: technical, billing, return. Extract entities: product, version, issue."
- Output: JSON `{"category": "technical", "entities": {"product": "iPhone 14", "version": "iOS 17", "issue": "charging"}}`
- This filters retrieval (e.g., search only in "technical" category)

**Step 2.2: Retrieval**

- Vectorize query: `query_embedding = embeddings.embed_query(query)`
- Search top-k (k=3-5) similar chunks: `docs = vectorstore.similarity_search(query, k=5, filter={"category": classification['category']})`
- Metric: Cosine similarity (>0.8 for relevance)

**Step 2.3: Generation of recommendation**

- Prompt for LLM: "Based on these documents: {docs}. And entities: {entities}. Generate a short recommendation for the operator: step by step, with citations from the base. Format: 'Suggestion: [text]. Source: [doc]'."
- Streaming: `response = llm.stream(prompt)` — output tokens for real-time (operator sees suggestion "on the fly")
- Add fallback: If relevance is low, suggest escalation to a human

**Output**: Operator suggestion (e.g., "Step 1: Check the cable. From FAQ: 'For iOS 17 reset settings'"). Show in UI next to client chat.

### 3. Deployment and features

- Real-time: WebSocket for updates
- Citation: Add links to sources in response (metadata from docs)
- Testing: Simulate queries, measure latency (goal: <1 sec for retrieval)

This algorithm is scalable: for large knowledge bases — batch ingestion. Product value: Reduces operator response time by 50%, minimizes errors, integrates into existing CRM (e.g., Zendesk API).

## RAG Pipeline Essentials

### Ingestion/ETL
- Load documents (PDFs, Markdown, etc.)
- Split into chunks using `RecursiveCharacterTextSplitter`
- Embed with `bge-m3`
- Store in a vector database

### Query Processing
- Embed incoming support queries
- Retrieve top-k chunks
- Classify/extract entities via LLM prompts
- Generate response suggestions

### Real-Time Support
- Handles streaming responses from Scibox's Qwen model
- Provides live operator suggestions

## FastAPI Integration
LangChain's components (chains, retrievers) are callable functions or async, making them ideal for FastAPI endpoints. Use for a `/suggest` endpoint that:
- Takes a query
- Returns formatted recommendations

## Extensibility

### Classification & Entity Extraction
- Use LangChain's `LLMChain` or `create_extraction_chain` with Qwen
- Classify queries (e.g., "billing", "technical issue")
- Extract entities (e.g., product names, user IDs) before retrieval

### Knowledge Base
- Assume your KB is a folder of documents
- LangChain's `DocumentLoader` handles ingestion
- Run a one-time ETL script to populate the vector store on startup or via separate endpoint

### Product Polish
- Add citations using `with_sources=True` in retrievers to show source KB sections
- For "escalate to operator" feature: implement simple threshold (e.g., low confidence score → flag)

# Retrieval Metrics

## Context Precision: 
Measures if retrieved chunks rank relevant info highly (e.g., top-k docs match ground truth). Formula: Average precision @k. Aim for >0.8.
## Context Recall: 
Fraction of ground-truth relevant docs retrieved. Formula: TP / (TP + FN). High recall ensures no missed instructions.
## Context Relevance: 
Semantic similarity (e.g., cosine via embeddings) between query and retrieved chunks. Use to filter noisy retrievals.

# Generation Metrics

## Faithfulness: 
Checks if generated recommendations are grounded in retrieved contexts (no hallucinations). RAGAS computes this via LLM-judged entailment; score 0-1.
## Answer Relevance: 
How well the output matches the query intent. Computed as embedding similarity between query and answer.
## Answer Similarity: 
Compares generated answer to ground-truth (from dataset). Use ROUGE (n-gram overlap) or BERTScore (semantic match); target ROUGE-1 >0.5.

# Overall/End-to-End Metrics

## RAGAS Score: 
Composite from faithfulness, relevance, etc. (via ragas.evaluate()). Provides a holistic 0-1 score.
## BLEU/ROUGE: 
For lexical similarity in conversations; useful for multi-turn testing.
## Human-like Metrics: 
Perplexity (for fluency) or LLM-as-judge (e.g., GPT-4 scoring coherence on 1-5 scale).
## Custom for Support: 
Resolution Rate (does it suggest correct steps?); Latency (real-time <2s); Escalation Accuracy (when to hand off to operator).

Test on holdout data from your datasets: Run queries, retrieve from vector DB, generate via Scibox, then score. Tools like RAGAS integrate with LangChain for easy setup. If metrics are low, iterate on chunking or prompts.
