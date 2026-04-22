"""
RAG Pipeline — FAISS vector store over WAEC knowledge base
"""
import json
import os
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

_model = None
_index = None
_metadata = []

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def build_vector_store(knowledge_base: dict) -> bool:
    global _index, _metadata
    model = _get_model()
    documents = []
    _metadata = []

    for subject, questions in knowledge_base.items():
        for q in questions:
            doc = f"Question: {q['question']}\nAnswer: {q['answer']}"
            documents.append(doc)
            _metadata.append({
                "subject": subject,
                "topic": q.get("topic", subject),
                "year": q.get("year", "N/A"),
                "question": q["question"],
                "answer": q["answer"],
            })

    if not documents:
        return False

    embeddings = model.encode(documents, show_progress_bar=False)
    embeddings = np.array(embeddings).astype("float32")
    faiss.normalize_L2(embeddings)

    _index = faiss.IndexFlatIP(embeddings.shape[1])
    _index.add(embeddings)

    os.makedirs("data", exist_ok=True)
    faiss.write_index(_index, "data/faiss.index")
    with open("data/metadata.json", "w") as f:
        json.dump(_metadata, f)

    return True

def load_collections() -> bool:
    global _index, _metadata
    if os.path.exists("data/faiss.index") and os.path.exists("data/metadata.json"):
        _index = faiss.read_index("data/faiss.index")
        with open("data/metadata.json") as f:
            _metadata = json.load(f)
        return True
    return False

def retrieve(query: str, subject: str, n_results: int = 4) -> list:
    global _index, _metadata
    if _index is None or not _metadata:
        return []

    model = _get_model()
    query_vec = model.encode([query], show_progress_bar=False)
    query_vec = np.array(query_vec).astype("float32")
    faiss.normalize_L2(query_vec)

    n = min(n_results * 3, _index.ntotal)
    _, indices = _index.search(query_vec, n)

    results = []
    for idx in indices[0]:
        if idx < 0 or idx >= len(_metadata):
            continue
        meta = _metadata[idx]
        if meta["subject"].lower() == subject.lower():
            results.append(
                f"[{meta['topic']} - WAEC {meta['year']}]\n"
                f"Q: {meta['question']}\nA: {meta['answer']}"
            )
        if len(results) >= n_results:
            break

    return results

def is_ready() -> bool:
    return _index is not None and len(_metadata) > 0

def init_rag() -> bool:
    if load_collections():
        return True
    kb_path = "data/knowledge_base.json"
    if os.path.exists(kb_path):
        with open(kb_path) as f:
            kb = json.load(f)
        return build_vector_store(kb)
    return False