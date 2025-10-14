import json
import os
import pandas as pd
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_gigachat import GigaChat
from langchain_huggingface import HuggingFaceEmbeddings
from pydantic import BaseModel

from src.config import settings

# --- Configuration and Paths ---
# IMPORTANT: Make sure to download the following files into the `fastapi-chat/data` directory:
# 1. faqs_dataset.csv - from https://www.kaggle.com/datasets/kamilm/russian-bank-faq-2024
# 2. faiss_index.bin - The pre-computed FAISS index from your notebook.

DATA_DIR = "data"
DATASET_PATH = os.path.join(DATA_DIR, "faqs_dataset.csv")
FAISS_INDEX_PATH = os.path.join(DATA_DIR, "faiss_index.bin")

class Hint(BaseModel):
    response: str
    confidence: str

# --- Model and Data Loading ---

def load_rag_components():
    """Loads all necessary components for the RAG pipeline."""
    if not os.path.exists(DATASET_PATH) or not os.path.exists(FAISS_INDEX_PATH):
        raise FileNotFoundError(
            f"Please make sure '{DATASET_PATH}' and '{FAISS_INDEX_PATH}' exist. "
            f"Download them from Kaggle and place them in the '{DATA_DIR}' directory."
        )

    # Load embedding model
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/paraphrase-multilingual-mpnet-base-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': False}
    )

    # Load the dataset to provide context metadata
    df = pd.read_csv(DATASET_PATH)
    documents = [Document(page_content=row['prompt'], metadata={'response': row['response']}) for _, row in df.iterrows()]

    # Load the pre-computed FAISS index
    vectorstore = FAISS.load_local(
        folder_path=DATA_DIR, 
        embeddings=embedding_model, 
        index_name="faiss_index",
        allow_dangerous_deserialization=True
    )
    retriever = vectorstore.as_retriever()

    # Load GigaChat model
    llm = GigaChat(
        credentials=settings.GIGACHAT_CLIENT_SECRET,
        scope="GIGACHAT_API_PERS",
        verify_ssl_certs=False,
    )

    return retriever, llm

retriever, model = load_rag_components()

# --- Hint Generation ---

def generate_hint(question: str) -> Hint:
    """Generates a hint based on the user's question using the RAG pipeline."""
    context_docs = retriever.get_relevant_documents(question)
    context = "\n".join([doc.page_content for doc in context_docs])

    prompt = f"""**Customer Support Response Guidelines**

    Context Information:
    {context}

    Current Query:
    {question}

    Response Requirements:
    1. Provide clear, step-by-step instructions.
    2. Use markdown formatting for lists.
    3. Keep the response concise (max 3 sentences).
    4. If uncertain, offer to escalate to a human agent.

    Required JSON Format:
    {{"response": "Your answer here.", "confidence": "high"}}
    """

    response = model.invoke(prompt)
    try:
        # Assuming the response content is a JSON string
        hint_data = json.loads(response.content)
        return Hint(**hint_data)
    except (json.JSONDecodeError, TypeError):
        # Fallback if the model does not return valid JSON
        return Hint(response=response.content, confidence='low')
