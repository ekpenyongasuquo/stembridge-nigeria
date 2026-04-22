"""
RAG Pipeline — ChromaDB vector store over WAEC knowledge base
Loads questions from data/knowledge_base.json and enables semantic retrieval
"""
import json
import os
import chromadb
from chromadb.utils import embedding_functions

_client = None
_collections = {}


def _get_client():
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path="data/chroma_db")
    return _client


def _get_embedding_fn():
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )


def build_vector_store(knowledge_base: dict) -> bool:
    """Index all WAEC questions into ChromaDB"""
    client = _get_client()
    ef = _get_embedding_fn()

    for subject, questions in knowledge_base.items():
        collection_name = f"waec_{subject.lower()}"

        # Drop and recreate for fresh indexing
        try:
            client.delete_collection(collection_name)
        except Exception:
            pass

        collection = client.create_collection(
            name=collection_name,
            embedding_function=ef,
            metadata={"subject": subject}
        )

        documents, metadatas, ids = [], [], []
        for i, q in enumerate(questions):
            doc = f"Question: {q['question']}\nAnswer: {q['answer']}"
            documents.append(doc)
            metadatas.append({
                "topic": q.get("topic", subject),
                "year": q.get("year", "N/A"),
                "subject": subject,
                "question": q["question"],
                "answer": q["answer"],
            })
            ids.append(f"{subject}_{i}")

        if documents:
            collection.add(documents=documents, metadatas=metadatas, ids=ids)
            _collections[subject.lower()] = collection

    return True


def load_collections():
    """Load existing ChromaDB collections"""
    client = _get_client()
    ef = _get_embedding_fn()
    subjects = ["mathematics", "physics", "chemistry", "biology"]

    for subject in subjects:
        collection_name = f"waec_{subject}"
        try:
            col = client.get_collection(name=collection_name, embedding_function=ef)
            _collections[subject] = col
        except Exception:
            pass

    return len(_collections) > 0


def retrieve(query: str, subject: str, n_results: int = 4) -> list:
    """Retrieve relevant Q&A pairs for a query"""
    subject_key = subject.lower()
    if subject_key not in _collections:
        return []

    collection = _collections[subject_key]
    try:
        results = collection.query(
            query_texts=[query],
            n_results=min(n_results, collection.count())
        )
        context_items = []
        if results and results["metadatas"]:
            for meta in results["metadatas"][0]:
                context_items.append(
                    f"[{meta.get('topic', subject)} - WAEC {meta.get('year', '')}]\n"
                    f"Q: {meta.get('question', '')}\n"
                    f"A: {meta.get('answer', '')}"
                )
        return context_items
    except Exception:
        return []


def is_ready() -> bool:
    return len(_collections) > 0


def init_rag() -> bool:
    """Initialize RAG — load existing or build from knowledge base"""
    # Try loading existing
    if load_collections():
        return True

    # Build from knowledge base JSON
    kb_path = "data/knowledge_base.json"
    if os.path.exists(kb_path):
        with open(kb_path) as f:
            kb = json.load(f)
        return build_vector_store(kb)

    return False