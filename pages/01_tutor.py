"""
STEMBridge — AI Tutor Chat Page
"""
import re

def clean_latex(text: str) -> str:
    """Remove LaTeX notation and replace with clean readable text"""
    # Remove [ ] wrapping around formulas
    text = re.sub(r'\\\[|\\\]', '', text)
    text = re.sub(r'\$\$.*?\$\$', '', text, flags=re.DOTALL)
    text = re.sub(r'\$.*?\$', '', text)
    # Replace LaTeX symbols with Unicode
    text = text.replace(r'\Delta', 'Δ')
    text = text.replace(r'\delta', 'δ')
    text = text.replace(r'\alpha', 'α')
    text = text.replace(r'\beta', 'β')
    text = text.replace(r'\gamma', 'γ')
    text = text.replace(r'\lambda', 'λ')
    text = text.replace(r'\mu', 'μ')
    text = text.replace(r'\pi', 'π')
    text = text.replace(r'\theta', 'θ')
    text = text.replace(r'\omega', 'ω')
    text = text.replace(r'\times', '×')
    text = text.replace(r'\div', '÷')
    text = text.replace(r'\approx', '≈')
    text = text.replace(r'\neq', '≠')
    text = text.replace(r'\geq', '≥')
    text = text.replace(r'\leq', '≤')
    text = text.replace(r'\infty', '∞')
    text = text.replace(r'\cdot', '·')
    text = text.replace(r'\pm', '±')
    # Replace \frac{a}{b} with a/b
    text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\1/\2', text)
    # Replace ^{2} with ²
    text = re.sub(r'\^\{2\}', '²', text)
    text = re.sub(r'\^\{3\}', '³', text)
    text = re.sub(r'\^2\b', '²', text)
    text = re.sub(r'\^3\b', '³', text)
    # Remove remaining { } braces from LaTeX
    text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)
    text = text.replace('{', '').replace('}', '')
    # Remove remaining backslashes
    text = re.sub(r'\\(?=[a-zA-Z])', '', text)
    # Clean up extra whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


st.set_page_config(page_title="STEMBridge — Tutor", page_icon="💬", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }

.tutor-header {
    background: linear-gradient(135deg, #006644, #00A86B);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    color: white;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.chat-area {
    background: #F8FFFE;
    border: 1.5px solid #DCF5EC;
    border-radius: 16px;
    padding: 1.25rem;
    min-height: 400px;
    max-height: 500px;
    overflow-y: auto;
    margin-bottom: 1rem;
}

.msg-user {
    display: flex;
    justify-content: flex-end;
    margin: 0.6rem 0;
}

.bubble-user {
    background: #00A86B;
    color: white;
    border-radius: 18px 18px 4px 18px;
    padding: 0.75rem 1rem;
    max-width: 75%;
    font-size: 0.9rem;
    line-height: 1.5;
}

.msg-ai {
    display: flex;
    justify-content: flex-start;
    margin: 0.6rem 0;
    gap: 0.6rem;
    align-items: flex-start;
}

.ai-avatar {
    background: #00A86B;
    color: white;
    border-radius: 50%;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
    margin-top: 2px;
}

.bubble-ai {
    background: white;
    border: 1.5px solid #DCF5EC;
    color: #0D1117;
    border-radius: 18px 18px 18px 4px;
    padding: 0.75rem 1rem;
    max-width: 80%;
    font-size: 0.9rem;
    line-height: 1.65;
    white-space: pre-wrap;
}

.rag-tag {
    font-size: 0.68rem;
    background: #E8F8F1;
    color: #00A86B;
    padding: 1px 7px;
    border-radius: 20px;
    font-weight: 600;
    margin-bottom: 4px;
    display: inline-block;
}

.topic-chip {
    display: inline-block;
    background: #E8F8F1;
    color: #006644;
    font-size: 0.75rem;
    padding: 3px 10px;
    border-radius: 20px;
    margin: 2px;
    cursor: pointer;
    border: 1px solid #B8E8D4;
    font-weight: 500;
}

.empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #888;
}
</style>
""", unsafe_allow_html=True)

init_session()

subject = st.session_state.get("subject", "Mathematics")
icons = {"Mathematics": "🔢", "Physics": "⚡", "Chemistry": "🧪", "Biology": "🧬"}
icon = icons.get(subject, "📚")

# Header
st.markdown(f"""
<div class="tutor-header">
    <span style="font-size:2rem">{icon}</span>
    <div>
        <div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800">{subject} Tutor</div>
        <div style="opacity:0.85;font-size:0.85rem">WAEC/NECO Level • Nigerian Context • Real Past Questions</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Topic quick-pick
st.markdown("**Jump to a topic:**")
topics = WAEC_TOPICS.get(subject, [])
topic_cols = st.columns(min(len(topics), 4))
for i, topic in enumerate(topics):
    with topic_cols[i % 4]:
        if st.button(topic, key=f"topic_{topic}", use_container_width=True):
            starter = f"Please teach me about {topic} in {subject} for WAEC"
            add_message("user", starter)
            with st.spinner("STEMBridge is thinking..."):
                reply = tutor_respond(starter, subject, st.session_state.messages[:-1])
                reply = clean_latex(reply)
            add_message("assistant", reply)
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# RAG status
if st.session_state.get("rag_ready"):
    st.markdown('<span class="rag-tag">✅ WAEC past questions loaded</span>', unsafe_allow_html=True)
else:
    st.markdown('<span class="rag-tag">⚠️ Knowledge base loading...</span>', unsafe_allow_html=True)

# Chat display
chat_html = '<div class="chat-area">'

if not st.session_state.messages:
    chat_html += f"""
    <div class="empty-state">
        <div style="font-size:3rem">👋</div>
        <div style="font-size:1rem;font-weight:600;color:#333;margin:0.5rem 0">Welcome to STEMBridge!</div>
        <div style="font-size:0.85rem">Ask me anything about {subject} for WAEC.<br>
        Pick a topic above or type your question below.</div>
        <div style="margin-top:1rem;font-size:0.8rem;color:#00A86B">
            Try: "Explain the Mole Concept" • "Solve this WAEC question" • "What topics should I focus on?"
        </div>
    </div>"""
else:
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            chat_html += f'<div class="msg-user"><div class="bubble-user">{msg["content"]}</div></div>'
        else:
            raw = clean_latex(msg["content"])
            content = raw.replace("<", "&lt;").replace(">", "&gt;")
            chat_html += f'''
            <div class="msg-ai">
                <div class="ai-avatar">🌉</div>
                <div>
                    <div class="rag-tag">STEMBridge AI</div>
                    <div class="bubble-ai">{content}</div>
                </div>
            </div>'''

chat_html += '</div>'
st.markdown(chat_html, unsafe_allow_html=True)

# Input
col_input, col_send = st.columns([5, 1])
with col_input:
    user_input = st.chat_input(f"Ask about {subject}... (e.g. 'How do I solve quadratic equations?')")

if user_input:
    if not st.session_state.get("rag_ready"):
        st.warning("Knowledge base still loading. Please wait a moment.")
        st.stop()

    add_message("user", user_input)

    with st.spinner(f"STEMBridge is thinking about your {subject} question..."):
        reply = tutor_respond(user_input, subject, st.session_state.messages[:-1])
        reply = clean_latex(reply)

    add_message("assistant", reply)
    update_progress(subject, correct=True)  # Count participation
    st.rerun()

# Action buttons
col_a, col_b, col_c = st.columns(3)
with col_a:
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
with col_b:
    if st.button("📝 Take a Quiz", use_container_width=True):
        st.switch_page("pages/02_quiz.py")
with col_c:
    if st.button("📊 View Progress", use_container_width=True):
        st.switch_page("pages/03_progress.py")