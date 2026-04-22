"""
STEMBridge — Progress Tracking Page
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from utils.session_state import init_session, get_accuracy
from core.tutor_engine import get_study_tip

st.set_page_config(page_title="STEMBridge — Progress", page_icon="📊", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }

.progress-header {
    background: linear-gradient(135deg, #1A1A2E, #0F3460);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    color: white;
    margin-bottom: 1.5rem;
}

.subject-progress-card {
    background: white;
    border: 1.5px solid #E8F8F1;
    border-radius: 14px;
    padding: 1.25rem;
    margin-bottom: 0.75rem;
}

.tip-card {
    background: linear-gradient(135deg, #FFF9E6, #FFFAE8);
    border: 1.5px solid #F5A623;
    border-radius: 14px;
    padding: 1.25rem;
    margin-bottom: 0.75rem;
}
</style>
""", unsafe_allow_html=True)

init_session()

st.markdown("""
<div class="progress-header">
    <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800">📊 My WAEC Progress</div>
    <div style="opacity:0.75;font-size:0.85rem;margin-top:0.25rem">Track your performance across all subjects</div>
</div>
""", unsafe_allow_html=True)

subjects = ["Mathematics", "Physics", "Chemistry", "Biology"]
icons = {"Mathematics": "🔢", "Physics": "⚡", "Chemistry": "🧪", "Biology": "🧬"}
colors = {"Mathematics": "#00A86B", "Physics": "#3498DB", "Chemistry": "#9B59B6", "Biology": "#E74C3C"}

progress = st.session_state.progress
any_data = any(progress[s]["questions_answered"] > 0 for s in subjects)

if not any_data:
    st.info("📚 No progress yet! Start with the Tutor or Quiz to track your performance.")
    if st.button("Go to Tutor →", type="primary"):
        st.switch_page("pages/01_tutor.py")
    st.stop()

# ── Overview Chart ────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("### Accuracy by Subject")
    acc_data = {s: get_accuracy(s) for s in subjects}
    answered = {s: progress[s]["questions_answered"] for s in subjects}

    fig = go.Figure()
    for s in subjects:
        if answered[s] > 0:
            fig.add_trace(go.Bar(
                name=s,
                x=[s],
                y=[acc_data[s]],
                marker_color=colors[s],
                text=[f"{acc_data[s]}%"],
                textposition='outside',
            ))

    fig.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(range=[0, 110], title="Accuracy (%)", gridcolor='#F0F0F0'),
        height=300,
        margin=dict(t=20, b=20, l=20, r=20),
        font=dict(family="Space Grotesk"),
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### Questions Answered")
    total_answered = sum(progress[s]["questions_answered"] for s in subjects)
    total_correct = sum(progress[s]["correct"] for s in subjects)

    st.markdown(f"""
    <div style="text-align:center;padding:1rem;">
        <div style="font-family:'Syne',sans-serif;font-size:3rem;font-weight:800;color:#00A86B">{total_answered}</div>
        <div style="color:#666;font-size:0.85rem">Total Questions</div>
        <div style="margin-top:1rem;font-size:1.5rem;font-weight:700;color:#0D1117">{total_correct}</div>
        <div style="color:#666;font-size:0.85rem">Correct Answers</div>
        <div style="margin-top:1rem;font-size:1.5rem;font-weight:700;color:#00A86B">
            {round(total_correct/total_answered*100) if total_answered else 0}%
        </div>
        <div style="color:#666;font-size:0.85rem">Overall Accuracy</div>
    </div>
    """, unsafe_allow_html=True)

# ── Subject Breakdown ─────────────────────────────────────────────────────
st.markdown("### Subject Breakdown")
for s in subjects:
    p = progress[s]
    if p["questions_answered"] == 0:
        continue
    acc = get_accuracy(s)

    st.markdown(f"""
    <div class="subject-progress-card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.75rem;">
            <div style="font-weight:600;font-size:1rem">{icons[s]} {s}</div>
            <div style="font-size:1.25rem;font-weight:700;color:{colors[s]}">{acc}%</div>
        </div>
        <div style="background:#F0F0F0;border-radius:20px;height:6px;margin-bottom:0.75rem;">
            <div style="background:{colors[s]};width:{acc}%;border-radius:20px;height:100%;"></div>
        </div>
        <div style="display:flex;gap:1.5rem;font-size:0.8rem;color:#666;">
            <span>✅ {p['correct']} correct</span>
            <span>❌ {p['questions_answered'] - p['correct']} wrong</span>
            <span>📌 {len(p['topics_covered'])} topics covered</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── Study Tips ────────────────────────────────────────────────────────────
st.markdown("### 💡 Personalized Study Tips")
weak_subjects = [s for s in subjects if progress[s]["questions_answered"] > 0 and get_accuracy(s) < 70]

if weak_subjects:
    for s in weak_subjects[:2]:
        weak_topics = [t for t in progress[s]["topics_covered"]] if progress[s]["topics_covered"] else [s]
        with st.spinner(f"Getting tip for {s}..."):
            tip = get_study_tip(s, weak_topics)
        if tip:
            st.markdown(f"""
            <div class="tip-card">
                <div style="font-weight:600;color:#F5A623;margin-bottom:0.4rem">💡 {icons[s]} {s} Tip</div>
                <div style="font-size:0.9rem;color:#333;line-height:1.6">{tip}</div>
            </div>
            """, unsafe_allow_html=True)
else:
    st.success("🎉 You're performing well across all subjects! Keep it up!")

col1, col2 = st.columns(2)
with col1:
    if st.button("💬 Go to Tutor", use_container_width=True, type="primary"):
        st.switch_page("pages/01_tutor.py")
with col2:
    if st.button("📝 Take a Quiz", use_container_width=True):
        st.switch_page("pages/02_quiz.py")