import faiss
import json
import os
import numpy as np
import pandas as pd
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Dict, Any
import logging

from src.config import settings

logger = logging.getLogger(__name__)

# --- Configuration and Paths ---
DATA_DIR = "data"
DATASET_PATH = os.path.join(DATA_DIR, "smart_support.xlsx")
FAISS_INDEX_PATH = os.path.join(DATA_DIR, "faiss_index_bge_m3.bin")
METADATA_PATH = os.path.join(DATA_DIR, "metadata.json")

class Hint(BaseModel):
    response: str
    confidence: str
    category: str = ""
    subcategory: str = ""
    template: str = ""

# --- Model and Data Loading ---

class SciboxEmbeddings:
    """Wrapper for Scibox embeddings API."""
    def __init__(self, client: OpenAI, model: str):
        self.client = client
        self.model = model
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query."""
        response = self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed multiple documents."""
        response = self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]


def load_rag_components():
    """Loads all necessary components for the RAG pipeline."""
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
    
    # Load or create FAISS index
    if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(METADATA_PATH):
        logger.info("Loading existing FAISS index...")
        index = faiss.read_index(FAISS_INDEX_PATH)
        with open(METADATA_PATH, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
    else:
        logger.info("Creating new FAISS index...")
        index, metadata = create_faiss_index(embedding_model)
    
    return client, embedding_model, index, metadata


def create_faiss_index(embedding_model: SciboxEmbeddings):
    """Creates a FAISS index from the dataset."""
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(
            f"Dataset not found at '{DATASET_PATH}'. "
            f"Please place smart_support.xlsx in the '{DATA_DIR}' directory."
        )
    
    # Load dataset
    df = pd.read_excel(DATASET_PATH)
    logger.info(f"Loaded dataset with {len(df)} rows")
    
    # Prepare texts and metadata
    texts = []
    metadata = []
    
    for idx, row in df.iterrows():
        # Combine question and context for better retrieval
        text = str(row.get('Вопрос клиента', row.get('question', '')))
        
        metadata.append({
            'index': idx,
            'question': text,
            'category': str(row.get('Категория', row.get('category', ''))),
            'subcategory': str(row.get('Подкатегория', row.get('subcategory', ''))),
            'template': str(row.get('Шаблон ответа', row.get('template', ''))),
            'keywords': str(row.get('Ключевые слова', row.get('keywords', '')))
        })
        texts.append(text)
    
    # Generate embeddings in batches
    batch_size = 32
    all_embeddings = []
    
    logger.info("Generating embeddings...")
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        embeddings = embedding_model.embed_documents(batch)
        all_embeddings.extend(embeddings)
        if (i // batch_size + 1) % 10 == 0:
            logger.info(f"Processed {i+len(batch)}/{len(texts)} texts")
    
    # Create FAISS index
    embeddings_array = np.array(all_embeddings).astype('float32')
    dimension = embeddings_array.shape[1]
    
    index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
    faiss.normalize_L2(embeddings_array)  # Normalize for cosine similarity
    index.add(embeddings_array)
    
    # Save index and metadata
    os.makedirs(DATA_DIR, exist_ok=True)
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(METADATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    logger.info(f"FAISS index created with {index.ntotal} vectors")
    return index, metadata


# Initialize components
try:
    client, embedding_model, faiss_index, dataset_metadata = load_rag_components()
    logger.info("RAG components loaded successfully")
except Exception as e:
    logger.error(f"Failed to load RAG components: {e}")
    client, embedding_model, faiss_index, dataset_metadata = None, None, None, None

# --- Hint Generation ---

def retrieve_relevant_contexts(question: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Retrieves relevant contexts from FAISS index."""
    if faiss_index is None or embedding_model is None or dataset_metadata is None:
        raise RuntimeError("RAG components not initialized")
    
    # Generate query embedding
    query_embedding = np.array([embedding_model.embed_query(question)]).astype('float32')
    faiss.normalize_L2(query_embedding)
    
    # Search in FAISS index
    distances, indices = faiss_index.search(query_embedding, top_k)
    
    # Retrieve metadata for top results
    results = []
    for idx, distance in zip(indices[0], distances[0]):
        if idx < len(dataset_metadata):
            result = dataset_metadata[idx].copy()
            result['similarity'] = float(distance)
            results.append(result)
    
    return results


def classify_and_extract(question: str, contexts: List[Dict[str, Any]]) -> Dict[str, str]:
    """Classifies the question and extracts category/subcategory."""
    if not contexts:
        return {'category': 'Общий вопрос', 'subcategory': 'Прочее'}
    
    # Use the most relevant context for classification
    best_match = contexts[0]
    return {
        'category': best_match.get('category', 'Общий вопрос'),
        'subcategory': best_match.get('subcategory', 'Прочее')
    }


def generate_hint(question: str) -> Hint:
    """Generates a hint based on the user's question using the RAG pipeline."""
    try:
        if client is None:
            return Hint(
                response="Система временно недоступна. Пожалуйста, попробуйте позже.",
                confidence="low",
                category="Ошибка",
                subcategory="Системная ошибка"
            )
        
        # Retrieve relevant contexts
        contexts = retrieve_relevant_contexts(question, top_k=3)
        
        if not contexts:
            return Hint(
                response="К сожалению, не удалось найти подходящий ответ. Пожалуйста, уточните ваш вопрос.",
                confidence="low",
                category="Неизвестно",
                subcategory="Неизвестно"
            )
        
        # Classify and extract entities
        classification = classify_and_extract(question, contexts)
        
        # Build context for LLM
        context_text = "\n\n".join([
            f"Пример {i+1} (релевантность: {ctx['similarity']:.2f}):\n"
            f"Вопрос: {ctx['question']}\n"
            f"Категория: {ctx['category']} / {ctx['subcategory']}\n"
            f"Шаблон ответа: {ctx['template']}"
            for i, ctx in enumerate(contexts)
        ])
        
        # Create prompt for LLM
        prompt = f"""Ты — ассистент службы поддержки клиентов. Твоя задача — предоставить оператору готовый шаблон ответа на вопрос клиента.

Вопрос клиента:
{question}

Категория: {classification['category']}
Подкатегория: {classification['subcategory']}

Похожие вопросы из базы знаний:
{context_text}

Инструкции:
1. Проанализируй вопрос клиента и похожие примеры
2. Создай профессиональный и вежливый ответ на русском языке
3. Используй шаблоны из похожих вопросов как основу
4. Адаптируй ответ под конкретный вопрос клиента
5. Будь конкретным и полезным
6. Если уверен в ответе, укажи confidence: "high", иначе "medium" или "low"

Верни ответ СТРОГО в формате JSON:
{{
  "response": "Ваш готовый ответ клиенту",
  "confidence": "high/medium/low",
  "template": "Краткое описание использованного шаблона"
}}

Важно: верни ТОЛЬКО JSON, без дополнительного текста."""
        
        # Call LLM
        response = client.chat.completions.create(
            model=settings.SCIBOX_LLM_MODEL,
            messages=[
                {"role": "system", "content": "Ты — профессиональный ассистент службы поддержки. Отвечай только в формате JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        
        # Parse response
        response_text = response.choices[0].message.content.strip()
        
        # Try to extract JSON from response
        try:
            # Remove markdown code blocks if present
            if '```json' in response_text:
                response_text = response_text.split('```json')[1].split('```')[0].strip()
            elif '```' in response_text:
                response_text = response_text.split('```')[1].split('```')[0].strip()
            
            hint_data = json.loads(response_text)
            
            return Hint(
                response=hint_data.get('response', response_text),
                confidence=hint_data.get('confidence', 'medium'),
                category=classification['category'],
                subcategory=classification['subcategory'],
                template=hint_data.get('template', contexts[0].get('template', ''))
            )
        except json.JSONDecodeError:
            # Fallback: use raw response
            logger.warning(f"Failed to parse JSON response: {response_text}")
            return Hint(
                response=response_text,
                confidence='medium',
                category=classification['category'],
                subcategory=classification['subcategory'],
                template=contexts[0].get('template', '')
            )
    
    except Exception as e:
        logger.error(f"Error generating hint: {e}", exc_info=True)
        return Hint(
            response=f"Произошла ошибка при обработке запроса: {str(e)}",
            confidence="low",
            category="Ошибка",
            subcategory="Системная ошибка",
            template=""
        )
