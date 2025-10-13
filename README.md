# Запуск веб-сервиса:

## Backend:
### Запуск:
``` bash
cd fastapi-chat
docker network create chat-net
docker-compose up --build -d
docker exec chat-backend poetry run alembic upgrade head
```

### Остановка:
```bash
docker-compose down
docker-compose rm -f
```

## Frontend:

### Запуск:
```bash
cd vuetify-chat
npm install
npm run dev
```

### Остановка:
```Ctrl-C```

# Тестирование rag-customer-support-using-gigachat-and-faiss.ipynb
1. Перейти на https://developers.sber.ru/docs/ru/gigachat/tariffs/individual-tariffs , последовать инструкции получения Freemium
2. Получить GigaChat API Token
3. Зарегистрироваться на Kaggle, открыть ноутбук в нем
4. Через `Add-ons > Secrets` добавить GigaChat API Token в переменную с именем `GIGACHAT_CLIENT_SECRET`
5. Запускать ячейки   

# Алгоритм решения задачи от Grok3

Классическая RAG-архитектуру (Retrieval-Augmented Generation), Scibox: OpenAI-совместимый провайдер: его API может быть использован для embeddings (векторизации) и LLM (генерации ответов). Формат решения - веб-приложение, где оператор видит чат клиента, а ИИ в реальном времени предлагает рекомендации на основе базы знаний (документы, FAQ, инструкции).

## Предлагаемый стек технологий

Для хакатона выбираем простой, быстрый в реализации стек, чтобы уложиться во время. Всё можно собрать за 1-2 дня, без сложного обучения (RAG не требует fine-tuning).

| Компонент | Рекомендация | Почему? |
|-----------|--------------|---------|
| Язык/Фреймворк | Python + LangChain (для RAG-пайплайна) | LangChain упрощает интеграцию embeddings, retrieval и LLM. Легко добавить стриминг и chaining (классификация + NER). |
| Embeddings (векторизация) | Scibox API (модель: text-embedding-3-small или аналогичная OpenAI-compatible) | Низкая latency, хорошая семантика. Размер embedding: 1536 dims. Альтернатива: HuggingFaceSentenceTransformers, если Scibox недоступен локально. |
| Разбивка текста (chunking) | RecursiveCharacterTextSplitter (из LangChain) | Разбивает документы на чанки по 500-1000 токенов с overlap 20%, чтобы сохранить контекст. Поддерживает метаданные (e.g., источник документа). |
| Векторная БД | FAISS (Facebook AI Similarity Search) | Локальная, быстрая, не требует облака. Индексация по cosine similarity. Для scale-up: Pinecone (облачная, с API). Хранит ~10k чанков легко. |
| LLM для генерации/классификации/NER | Scibox API (модель: GPT-4o-mini или Grok-аналог) | OpenAI-compatible, поддерживает стриминг. Для NER и классификации: chain из LangChain (e.g., create_extraction_chain). |
| Веб-интерфейс | FastAPI + Vue.js | Быстрое прототипирование чата с real-time обновлениями. WebSocket для стриминга подсказок. |
| Дополнительно | Pydantic (для валидации), Celery (если нужен background ingestion) | Для обработки больших баз знаний. |

## Шаговый алгоритм (RAG-пайплайн с классификацией и NER)

Алгоритм разделён на этапы: подготовка (ingestion, один раз), обработка запроса (real-time). Добавляем классификацию (e.g., тип тикета: "техническая проблема", "возврат") и NER (извлечение сущностей: имя продукта, версия, email) для точного retrieval. Всё в реальном времени (<2 сек на ответ).

### 1. Подготовка базы знаний (Ingestion Pipeline)

- Загрузите документы (PDF, TXT, FAQ) из папки или URL
- Разбейте на чанки: `splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)`
- Векторизуйте: `embeddings = SciboxEmbeddings(model="text-embedding-3-small")`; получите векторы для каждого чанка
- Добавьте метаданные (e.g., `{"source": "FAQ_v1", "category": "billing"}`)
- Сохраните в FAISS: `vectorstore = FAISS.from_documents(chunks, embeddings)`. Индекс готов к поиску

### 2. Обработка входящего запроса (Real-time Query Pipeline)

**Вход**: Текст запроса клиента (e.g., "Мой iPhone 14 не заряжается после обновления iOS 17")

**Шаг 2.1: Классификация и NER (используя LLM-chain)**

- Prompt для LLM: "Классифицируй запрос: [query]. Категории: technical, billing, return. Извлеки сущности: product, version, issue."
- Выход: JSON `{"category": "technical", "entities": {"product": "iPhone 14", "version": "iOS 17", "issue": "charging"}}`
- Это фильтрует retrieval (e.g., искать только в категории "technical")

**Шаг 2.2: Retrieval**

- Векторизуйте запрос: `query_embedding = embeddings.embed_query(query)`
- Поиск top-k (k=3-5) похожих чанков: `docs = vectorstore.similarity_search(query, k=5, filter={"category": classification['category']})`
- Метрика: Cosine similarity (>0.8 для релевантности)

**Шаг 2.3: Генерация рекомендации**

- Prompt для LLM: "На основе этих документов: {docs}. И сущностей: {entities}. Сгенерируй краткую рекомендацию для оператора: шаг за шагом, с цитатами из базы. Формат: 'Подсказка: [text]. Источник: [doc]'."
- Стриминг: `response = llm.stream(prompt)` — выводите по токенам для real-time (оператор видит подсказку "на лету")
- Добавьте fallback: Если релевантность низкая, предложите эскалацию к человеку

**Выход**: Подсказка для оператора (e.g., "Шаг 1: Проверьте кабель. Из FAQ: 'Для iOS 17 сбросьте настройки'"). Показать в UI рядом с чатом клиента.

### 3. Деплой и фичи

- Real-time: WebSocket для обновлений
- Цитирование: Добавьте ссылки на источники в ответе (метаданные из docs)
- Тестирование: Симулируйте запросы, измерьте latency (цель: <1 сек на retrieval)

Этот алгоритм масштабируем: для больших баз — батчинг ingestion. Продуктовая ценность: Снижает время ответа оператора на 50%, минимизирует ошибки, интегрируется в существующие CRM (e.g., Zendesk API).

# Recommended RAG Framework: LangChain

## OpenAI Compatibility
Scibox's endpoints (`/v1/chat/completions` and `/v1/embeddings`) are drop-in replacements for OpenAI. LangChain's `ChatOpenAI` and `OpenAIEmbeddings` classes work out-of-the-box—simply set:
- `base_url="https://llm.t1v.scibox.tech/v1"`
- `api_key=your_token`

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

## Примеры продуктов, решивших похожую задачу

- **DoorDash (DashPass Support Chatbot)**: RAG-чатбот для поддержки курьеров (Dashers). Система сжимает разговоры, ищет релевантные статьи/кейсы в базе, генерирует ответы с guardrails (проверка точности). Результат: Быстрее разрешения тикетов, меньше эскалаций.
- **LinkedIn (Customer Service Q&A)**: RAG с knowledge graph на основе исторических тикетов. Для запроса строит подграф, retrieves релевантные узлы, генерирует ответы. Сократило время разрешения на 28.6%.
- **Thomson Reuters (Support Executive Assistant)**: RAG для поиска в внутренних доках, refinement через seq-to-seq модель для структурированных ответов. Чат-интерфейс с цитатами, снижает галлюцинации, ускоряет поддержку.
- **BotPenguin (RAG-Ready AI Agents)**: Платформа для чатботов поддержки, подключает RAG к докам/FAQ. Генерирует персонализированные ответы в реальном времени по каналам (WhatsApp, web). Идеально для SMB, без обучения.
- **Commercient (RAG Chat Assistant)**: Специализированный ассистент для B2B-поддержки, retrieves из CRM/доков для точных ответов. Пример: Аналогично Amazon AI, где боты трекают заказы/возвраты из базы без человека.

Ссылки:
- https://www.evidentlyai.com/blog/rag-examples
- https://botpenguin.com/blogs/most-useful-rag-application-and-use-cases
- https://www.commercient.com/transforming-customer-support-with-commercient-rag-chat-assistant/?srsltid=AfmBOoo8SVit7GlYRbvztwPyUpzdHGm0owgSefASaWF-XR-gh82TAqmH

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
