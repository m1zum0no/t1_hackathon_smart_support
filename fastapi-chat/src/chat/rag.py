import faiss
import json
import os
import numpy as np
import pandas as pd
from openai import OpenAI
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Tuple
import logging
import hashlib
import re

from src.config import settings

logger = logging.getLogger(__name__)

# --- Configuration and Paths ---
DATA_DIR = "data"
DATASET_PATH = os.path.join(DATA_DIR, "smart_support.xlsx")
FAISS_INDEX_PATH = os.path.join(DATA_DIR, "faiss_index_bge_m3.bin")
METADATA_PATH = os.path.join(DATA_DIR, "metadata.json")
L1_CACHE_PATH = os.path.join(DATA_DIR, "l1_cache.json")

class Hint(BaseModel):
    response: str
    confidence: str
    category: str = ""
    subcategory: str = ""
    template: str = ""
    route: str = ""  # L1, L2, L3, etc.
    processing_time_ms: int = 0
    candidates_found: int = 0

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
    
    # Load or create L1 cache
    l1_cache = load_l1_cache()
    
    return client, embedding_model, index, metadata, l1_cache


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
    logger.info(f"Columns: {list(df.columns)}")
    
    # Drop unnecessary columns as preprocessing
    columns_to_drop = ['Приоритет', 'Целевая аудитория']
    for col in columns_to_drop:
        if col in df.columns:
            df = df.drop(columns=[col])
            logger.info(f"Dropped column: {col}")
    
    # Prepare texts and metadata
    texts = []
    metadata = []
    
    for idx, row in df.iterrows():
        # Get question - try different possible column names
        question = ''
        for col_name in ['Пример вопроса', 'Вопрос клиента', 'question', 'Вопрос']:
            if col_name in df.columns:
                question = str(row.get(col_name, '')).strip()
                if question and question != 'nan':
                    break
        
        # Get template - try different possible column names
        template = ''
        for col_name in ['Шаблонный ответ', 'Шаблон ответа', 'template', 'Ответ', 'ответ']:
            if col_name in df.columns:
                template = str(row.get(col_name, '')).strip()
                if template and template != 'nan':
                    break
        
        # Skip rows without question or template
        if not question or not template or question == 'nan' or template == 'nan':
            logger.warning(f"Skipping row {idx}: missing question or template")
            continue
        
        # Get category
        category = ''
        for col_name in ['Основная категория', 'Категория', 'category']:
            if col_name in df.columns:
                category = str(row.get(col_name, '')).strip()
                if category and category != 'nan':
                    break
        
        # Get subcategory
        subcategory = ''
        for col_name in ['Подкатегория', 'subcategory']:
            if col_name in df.columns:
                subcategory = str(row.get(col_name, '')).strip()
                if subcategory and subcategory != 'nan':
                    break
        
        # Get keywords
        keywords = ''
        for col_name in ['Ключевые слова', 'keywords']:
            if col_name in df.columns:
                keywords = str(row.get(col_name, '')).strip()
                if keywords and keywords != 'nan':
                    break
        
        metadata.append({
            'index': int(idx),
            'question': question,
            'category': category,
            'subcategory': subcategory,
            'template': template,
            'keywords': keywords
        })
        texts.append(question)
    
    # Generate embeddings in batches
    batch_size = 32
    all_embeddings = []
    
    logger.info(f"Generating embeddings for {len(texts)} questions...")
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        try:
            embeddings = embedding_model.embed_documents(batch)
            all_embeddings.extend(embeddings)
            if (i // batch_size + 1) % 5 == 0 or i + batch_size >= len(texts):
                logger.info(f"Processed {min(i+batch_size, len(texts))}/{len(texts)} texts")
        except Exception as e:
            logger.error(f"Error generating embeddings for batch {i//batch_size}: {e}")
            raise
    
    # Create FAISS index
    embeddings_array = np.array(all_embeddings).astype('float32')
    dimension = embeddings_array.shape[1]
    
    logger.info(f"Creating FAISS index with dimension {dimension}...")
    index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
    faiss.normalize_L2(embeddings_array)  # Normalize for cosine similarity
    index.add(embeddings_array)
    
    # Save index and metadata
    os.makedirs(DATA_DIR, exist_ok=True)
    faiss.write_index(index, FAISS_INDEX_PATH)
    with open(METADATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    logger.info(f"FAISS index created with {index.ntotal} vectors")
    logger.info(f"Saved to: {FAISS_INDEX_PATH}")
    logger.info(f"Metadata saved to: {METADATA_PATH}")
    
    # Build L1 cache immediately after creating index
    logger.info("Building L1 cache...")
    l1_cache = build_l1_cache_from_dataset(metadata)
    
    return index, metadata


# --- L1 Cache Management ---

def normalize_text(text: str) -> str:
    """Normalize text for exact matching."""
    # Convert to lowercase
    text = text.lower()
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove common punctuation but keep essential characters
    text = re.sub(r'[?.!,;:\-—–]+$', '', text)  # Remove trailing punctuation
    text = re.sub(r'^[?.!,;:\-—–]+', '', text)  # Remove leading punctuation
    # Strip whitespace
    text = text.strip()
    return text

def get_text_hash(text: str) -> str:
    """Generate hash for text."""
    normalized = normalize_text(text)
    return hashlib.md5(normalized.encode('utf-8')).hexdigest()

def load_l1_cache() -> Dict[str, Dict[str, Any]]:
    """Load L1 exact match cache."""
    if os.path.exists(L1_CACHE_PATH):
        with open(L1_CACHE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_l1_cache(cache: Dict[str, Dict[str, Any]]):
    """Save L1 cache to disk."""
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(L1_CACHE_PATH, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def build_l1_cache_from_dataset(metadata: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Build L1 cache from dataset metadata."""
    cache = {}
    skipped = 0
    for item in metadata:
        question = item.get('question', '')
        template = item.get('template', '')
        
        if question and template:
            text_hash = get_text_hash(question)
            normalized = normalize_text(question)
            cache[text_hash] = {
                'question': question,
                'normalized_question': normalized,
                'template': template,
                'category': item.get('category', ''),
                'subcategory': item.get('subcategory', ''),
                'keywords': item.get('keywords', '')
            }
        else:
            skipped += 1
    
    save_l1_cache(cache)
    logger.info(f"Built L1 cache with {len(cache)} entries (skipped {skipped} invalid entries)")
    if len(cache) > 0:
        # Log first few entries for debugging
        sample_keys = list(cache.keys())[:3]
        for key in sample_keys:
            logger.debug(f"L1 cache sample - Hash: {key[:8]}... Question: {cache[key]['normalized_question'][:50]}...")
    return cache

# Initialize components
try:
    client, embedding_model, faiss_index, dataset_metadata, l1_cache = load_rag_components()
    # Build L1 cache if empty
    if not l1_cache and dataset_metadata:
        l1_cache = build_l1_cache_from_dataset(dataset_metadata)
    logger.info(f"RAG components loaded successfully. L1 cache: {len(l1_cache)} entries")
except Exception as e:
    logger.error(f"Failed to load RAG components: {e}")
    client, embedding_model, faiss_index, dataset_metadata, l1_cache = None, None, None, None, {}

# --- Hint Generation ---

def l1_exact_match(question: str) -> Optional[Dict[str, Any]]:
    """L1: Exact match lookup in cache."""
    if not l1_cache:
        logger.debug("L1 cache is empty")
        return None
    
    text_hash = get_text_hash(question)
    normalized = normalize_text(question)
    result = l1_cache.get(text_hash)
    
    if result:
        logger.info(f"L1 HIT - Normalized query: '{normalized[:50]}...'")
    else:
        logger.debug(f"L1 MISS - Hash: {text_hash[:8]}... Normalized: '{normalized[:50]}...'")
    
    return result

def l2_semantic_search(question: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """L2: Semantic search using FAISS index."""
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


def l3_llm_rerank(question: str, candidates: List[Dict[str, Any]]) -> Tuple[Dict[str, Any], float]:
    """L3: LLM-based reranking to select the best answer."""
    if not candidates:
        raise ValueError("No candidates provided for reranking")
    
    if client is None:
        raise RuntimeError("LLM client not initialized")
    
    # Build prompt for reranking
    candidates_text = ""
    for i, candidate in enumerate(candidates):
        candidates_text += f"\n\nКандидат {i+1}:\n"
        candidates_text += f"Вопрос из базы: {candidate['question']}\n"
        candidates_text += f"Ответ: {candidate['template']}\n"
        candidates_text += f"Категория: {candidate['category']} / {candidate['subcategory']}\n"
        candidates_text += f"Релевантность (семантическая): {candidate.get('similarity', 0):.2f}"
    
    prompt = f"""Ты — эксперт по подбору наиболее релевантного ответа из базы знаний.

Вопрос клиента:
{question}

Кандидаты из базы знаний:{candidates_text}

Твоя задача:
1. Проанализируй вопрос клиента и все кандидаты
2. Выбери ОДИН наиболее подходящий кандидат, который лучше всего отвечает на вопрос
3. Оцени уверенность в выборе от 0 до 100

ВАЖНО:
- Ответ должен ТОЧНО соответствовать вопросу клиента
- Если ни один кандидат не подходит идеально, выбери наиболее близкий
- Не генерируй новый ответ, выбери из предложенных кандидатов

Верни ответ СТРОГО в формате JSON:
{{
  "selected_candidate": <номер кандидата 1-{len(candidates)}>,
  "confidence": <число от 0 до 100>,
  "reasoning": "Краткое объяснение выбора"
}}

Верни ТОЛЬКО JSON, без дополнительного текста."""
    
    try:
        response = client.chat.completions.create(
            model=settings.SCIBOX_LLM_MODEL,
            messages=[
                {"role": "system", "content": "Ты — эксперт по анализу релевантности. Отвечай только в формате JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Low temperature for consistent selection
            max_tokens=300
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Parse JSON response
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        result = json.loads(response_text)
        selected_idx = result['selected_candidate'] - 1  # Convert to 0-based index
        confidence = result['confidence'] / 100.0  # Convert to 0-1 range
        
        if 0 <= selected_idx < len(candidates):
            logger.info(f"LLM rerank selected candidate {selected_idx + 1} with confidence {confidence:.2f}")
            return candidates[selected_idx], confidence
        else:
            logger.warning(f"Invalid candidate index {selected_idx}, using first candidate")
            return candidates[0], 0.5
    
    except Exception as e:
        logger.error(f"Error in LLM reranking: {e}", exc_info=True)
        # Fallback to highest similarity
        return candidates[0], 0.5


def generate_hint(question: str) -> Hint:
    """Generates a hint based on the user's question using multi-level RAG pipeline."""
    import time
    start_time = time.time()
    
    try:
        if client is None:
            return Hint(
                response="Система временно недоступна. Пожалуйста, попробуйте позже.",
                confidence="low",
                category="Ошибка",
                subcategory="Системная ошибка",
                route="Error",
                processing_time_ms=0,
                candidates_found=0
            )
        
        # --- L1: Exact Match ---
        l1_result = l1_exact_match(question)
        if l1_result:
            processing_time = int((time.time() - start_time) * 1000)
            logger.info(f"L1 exact match found for question: {question[:50]}...")
            return Hint(
                response=l1_result['template'],
                confidence="high",
                category=l1_result.get('category', ''),
                subcategory=l1_result.get('subcategory', ''),
                template=l1_result['template'],
                route="L1 Точное совпадение",
                processing_time_ms=processing_time,
                candidates_found=1
            )
        
        # --- L2: Semantic Search ---
        candidates = l2_semantic_search(question, top_k=5)
        
        if not candidates:
            processing_time = int((time.time() - start_time) * 1000)
            return Hint(
                response="К сожалению, не удалось найти подходящий ответ. Пожалуйста, уточните ваш вопрос.",
                confidence="low",
                category="Неизвестно",
                subcategory="Неизвестно",
                route="L2 Семантический поиск",
                processing_time_ms=processing_time,
                candidates_found=0
            )
        
        # Check if top candidate has very high similarity (threshold for L2)
        top_similarity = candidates[0].get('similarity', 0)
        if top_similarity >= 0.95:  # Very high confidence threshold
            processing_time = int((time.time() - start_time) * 1000)
            logger.info(f"L2 high confidence match (similarity: {top_similarity:.3f})")
            return Hint(
                response=candidates[0]['template'],
                confidence="high",
                category=candidates[0].get('category', ''),
                subcategory=candidates[0].get('subcategory', ''),
                template=candidates[0]['template'],
                route="L2 Семантический поиск",
                processing_time_ms=processing_time,
                candidates_found=len(candidates)
            )
        
        # --- L3: LLM Rerank ---
        # Use top 3 candidates for reranking
        top_candidates = candidates[:3]
        selected_candidate, llm_confidence = l3_llm_rerank(question, top_candidates)
        
        processing_time = int((time.time() - start_time) * 1000)
        
        # Determine confidence level based on LLM confidence and similarity
        if llm_confidence >= 0.8:
            confidence_level = "high"
        elif llm_confidence >= 0.5:
            confidence_level = "medium"
        else:
            confidence_level = "low"
        
        logger.info(f"L3 LLM rerank completed (confidence: {llm_confidence:.2f}, time: {processing_time}ms)")
        
        return Hint(
            response=selected_candidate['template'],
            confidence=confidence_level,
            category=selected_candidate.get('category', ''),
            subcategory=selected_candidate.get('subcategory', ''),
            template=selected_candidate['template'],
            route="L3 LLM rerank",
            processing_time_ms=processing_time,
            candidates_found=len(candidates)
        )
    
    except Exception as e:
        processing_time = int((time.time() - start_time) * 1000)
        logger.error(f"Error generating hint: {e}", exc_info=True)
        return Hint(
            response=f"Произошла ошибка при обработке запроса: {str(e)}",
            confidence="low",
            category="Ошибка",
            subcategory="Системная ошибка",
            template="",
            route="Error",
            processing_time_ms=processing_time,
            candidates_found=0
        )
