"""
RAG Pipeline — Lightweight keyword retrieval over WAEC knowledge base
No heavy ML models. Works within Render free tier (512MB RAM).
Uses TF-IDF style scoring for relevant question retrieval.
"""
import json
import os
import re
from collections import defaultdict

_knowledge_base = {}  # {subject: [{"question":..,"answer":..,"topic":..,"year":..}]}


def build_vector_store(knowledge_base: dict) -> bool:
    """Load knowledge base into memory"""
    global _knowledge_base
    _knowledge_base = knowledge_base
    return True


def load_collections() -> bool:
    """Load from saved JSON"""
    global _knowledge_base
    kb_path = "data/knowledge_base.json"
    if os.path.exists(kb_path):
        with open(kb_path) as f:
            _knowledge_base = json.load(f)
        return True
    return False


def _score(query: str, question: dict) -> float:
    """Score a question's relevance to a query using keyword overlap"""
    query_words = set(re.findall(r'\w+', query.lower()))
    # Remove common stop words
    stops = {"what","is","the","a","an","of","in","how","do","does","find",
             "calculate","state","define","give","name","explain","difference",
             "between","and","or","to","for","with","can","i","me","my","why"}
    query_words -= stops

    q_text = (question.get("question","") + " " +
              question.get("answer","") + " " +
              question.get("topic","")).lower()
    q_words = set(re.findall(r'\w+', q_text))

    if not query_words:
        return 0.0

    overlap = query_words & q_words
    score = len(overlap) / len(query_words)

    # Boost if topic words match
    topic_words = set(re.findall(r'\w+', question.get("topic","").lower()))
    if query_words & topic_words:
        score += 0.3

    return score


def retrieve(query: str, subject: str, n_results: int = 4) -> list:
    """Retrieve top-k relevant WAEC questions for a query"""
    subject_key = subject.lower()
    questions = _knowledge_base.get(subject_key, [])

    if not questions:
        return []

    # Score all questions
    scored = [(q, _score(query, q)) for q in questions]
    scored.sort(key=lambda x: x[1], reverse=True)

    results = []
    for q, score in scored[:n_results]:
        if score > 0:
            results.append(
                f"[{q.get('topic', subject)} - WAEC {q.get('year', '')}]\n"
                f"Q: {q.get('question', '')}\n"
                f"A: {q.get('answer', '')}"
            )

    return results


def is_ready() -> bool:
    return len(_knowledge_base) > 0


def init_rag() -> bool:
    """Initialize RAG pipeline"""
    if is_ready():
        return True
    if load_collections():
        return True
    kb_path = "data/knowledge_base.json"
    if os.path.exists(kb_path):
        with open(kb_path) as f:
            kb = json.load(f)
        return build_vector_store(kb)
    return False
