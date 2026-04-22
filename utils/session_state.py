"""Streamlit session state management for STEMBridge"""
import streamlit as st
from datetime import datetime


def init_session():
    """Initialize all session state variables"""
    defaults = {
        "messages": [],
        "subject": "Mathematics",
        "topic": None,
        "quiz_questions": [],
        "quiz_score": 0,
        "quiz_index": 0,
        "quiz_active": False,
        "progress": {
            "Mathematics": {"sessions": 0, "questions_answered": 0, "correct": 0, "topics_covered": []},
            "Physics": {"sessions": 0, "questions_answered": 0, "correct": 0, "topics_covered": []},
            "Chemistry": {"sessions": 0, "questions_answered": 0, "correct": 0, "topics_covered": []},
            "Biology": {"sessions": 0, "questions_answered": 0, "correct": 0, "topics_covered": []},
        },
        "session_start": datetime.now().isoformat(),
        "rag_ready": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def add_message(role: str, content: str):
    st.session_state.messages.append({
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    })


def update_progress(subject: str, correct: bool, topic: str = None):
    p = st.session_state.progress[subject]
    p["questions_answered"] += 1
    if correct:
        p["correct"] += 1
    if topic and topic not in p["topics_covered"]:
        p["topics_covered"].append(topic)


def get_accuracy(subject: str) -> float:
    p = st.session_state.progress[subject]
    if p["questions_answered"] == 0:
        return 0.0
    return round(p["correct"] / p["questions_answered"] * 100, 1)