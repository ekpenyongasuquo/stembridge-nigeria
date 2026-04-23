"""
STEMBridge Nigeria — Main App
AI-powered WAEC/NECO tutor for Nigerian SS1-SS3 students
"""
import streamlit as st
import os
import json
from dotenv import load_dotenv

load_dotenv()

# Page config — must be first Streamlit call
st.set_page_config(
    page_title="STEMBridge Nigeria",
    page_icon="🌉",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.session_state import init_session
from core import rag_pipeline
from utils.scraper import FALLBACK_CONTENT, build_knowledge_base

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --green: #00A86B;
    --green-light: #E8F8F1;
    --gold: #F5A623;
    --dark: #0D1117;
    --card-bg: #F8FFFE;
}

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
}

.main-header {
    background: linear-gradient(135deg, #006644 0%, #00A86B 50%, #00C47A 100%);
    border-radius: 20px;
    padding: 2.5rem 2rem;
    color: white;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}

.main-header::before {
    content: '🇳🇬';
    position: absolute;
    right: 2rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 5rem;
    opacity: 0.15;
}

.main-header h1 {
    font-family: 'Syne', sans-serif;
    font-size: 2.5rem;
    font-weight: 800;
    margin: 0 0 0.25rem;
    letter-spacing: -1px;
}

.main-header p {
    font-size: 1rem;
    opacity: 0.85;
    margin: 0;
}

.subject-card {
    background: white;
    border: 2px solid #E8F8F1;
    border-radius: 16px;
    padding: 1.25rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s ease;
}

.subject-card:hover {
    border-color: #00A86B;
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,168,107,0.15);
}

.subject-card.active {
    border-color: #00A86B;
    background: #E8F8F1;
}

.subject-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.subject-name { font-weight: 600; color: #0D1117; font-size: 0.95rem; }

.stat-box {
    background: white;
    border: 1.5px solid #E8F8F1;
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}

.stat-val {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    color: #00A86B;
    line-height: 1;
}

.stat-label {
    font-size: 0.75rem;
    color: #666;
    margin-top: 0.25rem;
}

.chat-bubble-user {
    background: #00A86B;
    color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 0.85rem 1.1rem;
    margin: 0.4rem 0;
    max-width: 80%;
    margin-left: auto;
    font-size: 0.9rem;
}

.chat-bubble-ai {
    background: white;
    border: 1.5px solid #E8F8F1;
    color: #0D1117;
    border-radius: 18px 18px 18px 4px;
    padding: 0.85rem 1.1rem;
    margin: 0.4rem 0;
    max-width: 85%;
    font-size: 0.9rem;
    line-height: 1.6;
}

.rag-badge {
    display: inline-block;
    background: #E8F8F1;
    color: #00A86B;
    font-size: 0.7rem;
    padding: 2px 8px;
    border-radius: 20px;
    margin-bottom: 0.5rem;
    font-weight: 600;
}

.setup-card {
    background: linear-gradient(135deg, #FFF9E6, #FFF3CC);
    border: 1.5px solid #F5A623;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

/* Sidebar */
.css-1d391kg { background: #F8FFFE !important; }

/* Hide Streamlit footer */
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Init ────────────────────────────────────────────────────────────────────
init_session()

# ── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0;">
        <div style="font-family:'Syne',sans-serif; font-size:1.4rem; font-weight:800; color:#00A86B;">
            🌉 STEMBridge
        </div>
        <div style="font-size:0.75rem; color:#666;">Nigeria WAEC/NECO AI Tutor</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # Subject selector
    st.markdown("**📚 Select Subject**")
    subject_icons = {"Mathematics": "🔢", "Physics": "⚡", "Chemistry": "🧪", "Biology": "🧬"}
    for subj, icon in subject_icons.items():
        if st.button(f"{icon} {subj}", key=f"subj_{subj}",
                     use_container_width=True,
                     type="primary" if st.session_state.subject == subj else "secondary"):
            st.session_state.subject = subj
            st.session_state.messages = []
            st.rerun()

    st.divider()

    # Progress snapshot
    st.markdown("**📊 Your Progress**")
    for subj in ["Mathematics", "Physics", "Chemistry", "Biology"]:
        p = st.session_state.progress[subj]
        answered = p["questions_answered"]
        correct = p["correct"]
        acc = round(correct / answered * 100) if answered > 0 else 0
        if answered > 0:
            st.markdown(f"**{subject_icons[subj]} {subj}**: {acc}% accuracy")
            st.progress(acc / 100)




# ── RAG Initialization ───────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def initialize_rag():
    """Build knowledge base and RAG pipeline — cached"""
    kb_path = "data/knowledge_base.json"
    if not os.path.exists(kb_path):
        os.makedirs("data", exist_ok=True)
        kb = build_knowledge_base()
    else:
        with open(kb_path) as f:
            kb = json.load(f)

    from core.rag_pipeline import build_vector_store
    build_vector_store(kb)
    return True


# ── Main Page ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🌉 STEMBridge Nigeria</h1>
    <p>Your AI WAEC/NECO tutor — powered by real past questions | Mathematics • Physics • Chemistry • Biology</p>
</div>
""", unsafe_allow_html=True)

# Stats row
col1, col2, col3, col4 = st.columns(4)
total_answered = sum(st.session_state.progress[s]["questions_answered"] for s in ["Mathematics","Physics","Chemistry","Biology"])
total_correct = sum(st.session_state.progress[s]["correct"] for s in ["Mathematics","Physics","Chemistry","Biology"])
overall_acc = round(total_correct/total_answered*100) if total_answered > 0 else 0

with col1:
    st.markdown(f'<div class="stat-box"><div class="stat-val">{total_answered}</div><div class="stat-label">Questions Answered</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="stat-box"><div class="stat-val">{overall_acc}%</div><div class="stat-label">Overall Accuracy</div></div>', unsafe_allow_html=True)
with col3:
    topics_covered = sum(len(st.session_state.progress[s]["topics_covered"]) for s in ["Mathematics","Physics","Chemistry","Biology"])
    st.markdown(f'<div class="stat-box"><div class="stat-val">{topics_covered}</div><div class="stat-label">Topics Covered</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="stat-box"><div class="stat-val">4</div><div class="stat-label">Subjects Available</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Initialize RAG
with st.spinner("🔄 Loading WAEC knowledge base..."):
    try:
        rag_ready = initialize_rag()
        st.session_state.rag_ready = True
    except Exception as e:
        st.warning(f"Knowledge base loading issue: {e}. Tutor will still work without RAG.")

# Quick nav cards
st.markdown("### 🚀 Start Learning")
c1, c2, c3 = st.columns(3)

with c1:
    st.info("### 💬 Chat Tutor\nAsk any WAEC topic — get step-by-step explanations with Nigerian examples.\n\n👉 **Go to Tutor page in sidebar**")

with c2:
    st.success("### 📝 Practice Quiz\nTest yourself with auto-generated WAEC-style MCQ questions.\n\n👉 **Go to Quiz page in sidebar**")

with c3:
    st.warning("### 📈 Track Progress\nSee your accuracy per subject and identify weak areas.\n\n👉 **Go to Progress page in sidebar**")

# Current subject highlight
st.markdown(f"""
<div style="background:#E8F8F1; border-left: 4px solid #00A86B; border-radius: 8px; padding: 0.85rem 1.25rem; margin-top: 1rem;">
    <strong>Currently selected:</strong> {subject_icons.get(st.session_state.subject, '📚')} {st.session_state.subject} &nbsp;|&nbsp;
    <span style="color:#666;">Switch subjects in the sidebar</span>
</div>
""", unsafe_allow_html=True)