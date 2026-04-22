"""
STEMBridge — Quiz Page
WAEC-style MCQ practice with instant feedback and misconception detection
"""
import streamlit as st
from utils.session_state import init_session, update_progress
from core.quiz_engine import generate_quiz
from core.tutor_engine import detect_misconception, WAEC_TOPICS

st.set_page_config(page_title="STEMBridge — Quiz", page_icon="📝", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }

.quiz-header {
    background: linear-gradient(135deg, #1A1A2E, #16213E);
    border-radius: 16px;
    padding: 1.25rem 1.5rem;
    color: white;
    margin-bottom: 1.5rem;
}

.question-card {
    background: white;
    border: 2px solid #DCF5EC;
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.question-text {
    font-size: 1.05rem;
    font-weight: 500;
    color: #0D1117;
    margin-bottom: 1.25rem;
    line-height: 1.6;
}

.option-btn {
    width: 100%;
    text-align: left;
    padding: 0.75rem 1rem;
    border: 1.5px solid #E0E0E0;
    border-radius: 10px;
    background: white;
    cursor: pointer;
    margin: 0.3rem 0;
    font-size: 0.9rem;
    transition: all 0.15s;
}

.option-correct {
    border-color: #00A86B !important;
    background: #E8F8F1 !important;
    color: #006644 !important;
    font-weight: 600;
}

.option-wrong {
    border-color: #E74C3C !important;
    background: #FDECEA !important;
    color: #C0392B !important;
}

.score-display {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    color: #00A86B;
    text-align: center;
}

.progress-bar-wrap {
    background: #E8F8F1;
    border-radius: 20px;
    height: 8px;
    margin: 0.5rem 0 1.25rem;
}

.progress-bar-fill {
    background: linear-gradient(90deg, #00A86B, #00C47A);
    border-radius: 20px;
    height: 100%;
    transition: width 0.3s;
}

.feedback-correct {
    background: #E8F8F1;
    border-left: 4px solid #00A86B;
    border-radius: 8px;
    padding: 0.85rem 1rem;
    color: #006644;
    font-size: 0.9rem;
    margin-top: 0.75rem;
}

.feedback-wrong {
    background: #FDECEA;
    border-left: 4px solid #E74C3C;
    border-radius: 8px;
    padding: 0.85rem 1rem;
    color: #922B21;
    font-size: 0.9rem;
    margin-top: 0.75rem;
}
</style>
""", unsafe_allow_html=True)

init_session()
subject = st.session_state.get("subject", "Mathematics")
icons = {"Mathematics": "🔢", "Physics": "⚡", "Chemistry": "🧪", "Biology": "🧬"}

st.markdown(f"""
<div class="quiz-header">
    <div style="font-family:'Syne',sans-serif;font-size:1.4rem;font-weight:800">
        📝 {subject} Quiz
    </div>
    <div style="opacity:0.75;font-size:0.85rem;margin-top:0.25rem">
        WAEC-style practice questions • Instant feedback • Misconception analysis
    </div>
</div>
""", unsafe_allow_html=True)

# ── Quiz Setup ──────────────────────────────────────────────────────────────
if not st.session_state.quiz_active:
    st.markdown("### ⚙️ Configure Your Quiz")

    col1, col2 = st.columns(2)
    with col1:
        topic_options = ["Any topic"] + WAEC_TOPICS.get(subject, [])
        selected_topic = st.selectbox("📌 Topic", topic_options)
        if selected_topic == "Any topic":
            selected_topic = None

    with col2:
        num_q = st.slider("Number of Questions", 3, 10, 5)

    if st.button("🚀 Start Quiz", type="primary", use_container_width=True):
        with st.spinner("Generating WAEC-style questions..."):
            questions = generate_quiz(subject, topic=selected_topic, num_questions=num_q)

        if questions:
            st.session_state.quiz_questions = questions
            st.session_state.quiz_index = 0
            st.session_state.quiz_score = 0
            st.session_state.quiz_active = True
            st.session_state.quiz_answered = {}  # {index: {"selected": "A", "correct": True}}
            st.rerun()
        else:
            st.error("Could not generate questions. Check your API key.")

# ── Active Quiz ──────────────────────────────────────────────────────────────
elif st.session_state.quiz_active:
    questions = st.session_state.quiz_questions
    idx = st.session_state.quiz_index
    total = len(questions)

    # Progress
    progress_pct = idx / total
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;font-size:0.85rem;color:#666;">
        <span>Question {idx+1} of {total}</span>
        <span>Score: {st.session_state.quiz_score}/{idx}</span>
    </div>
    <div class="progress-bar-wrap">
        <div class="progress-bar-fill" style="width:{int(progress_pct*100)}%"></div>
    </div>
    """, unsafe_allow_html=True)

    if idx < total:
        q = questions[idx]
        answered_data = st.session_state.get("quiz_answered", {})
        already_answered = idx in answered_data

        st.markdown(f"""
        <div class="question-card">
            <div style="font-size:0.75rem;color:#00A86B;font-weight:600;margin-bottom:0.5rem;">
                📌 {q.get('topic', subject)} • WAEC Level
            </div>
            <div class="question-text">{q['question']}</div>
        </div>
        """, unsafe_allow_html=True)

        # Options
        selected = answered_data.get(idx, {}).get("selected") if already_answered else None
        correct_letter = q["correct"]

        for opt in q["options"]:
            opt_letter = opt[0]
            if already_answered:
                if opt_letter == correct_letter:
                    st.success(f"✅ {opt}")
                elif opt_letter == selected and selected != correct_letter:
                    st.error(f"❌ {opt}")
                else:
                    st.markdown(f"<div style='padding:0.5rem;color:#888;'>{opt}</div>", unsafe_allow_html=True)
            else:
                if st.button(opt, key=f"opt_{idx}_{opt_letter}", use_container_width=True):
                    is_correct = opt_letter == correct_letter
                    if "quiz_answered" not in st.session_state:
                        st.session_state.quiz_answered = {}
                    st.session_state.quiz_answered[idx] = {"selected": opt_letter, "correct": is_correct}
                    if is_correct:
                        st.session_state.quiz_score += 1
                    update_progress(subject, is_correct, q.get("topic"))
                    st.rerun()

        # Feedback after answering
        if already_answered:
            ans_data = answered_data[idx]
            if ans_data["correct"]:
                st.markdown(f"""
                <div class="feedback-correct">
                    🎉 <strong>Correct! Well done!</strong><br><br>
                    {q.get('explanation', '')}
                </div>
                """, unsafe_allow_html=True)
            else:
                # ── Misconception Detector ──────────────────────────────────
                selected_opt = next((o for o in q["options"] if o[0] == ans_data["selected"]), ans_data["selected"])
                correct_opt  = next((o for o in q["options"] if o[0] == q["correct"]), q["correct"])

                # Cache misconception analysis so it doesn't re-run on every rerun
                cache_key = f"misconception_{idx}"
                if cache_key not in st.session_state:
                    with st.spinner("🔍 Analysing your mistake..."):
                        analysis = detect_misconception(
                            student_answer=selected_opt,
                            correct_answer=correct_opt,
                            subject=subject
                        )
                    st.session_state[cache_key] = analysis
                else:
                    analysis = st.session_state[cache_key]

                st.markdown(f"""
                <div class="feedback-wrong">
                    ❌ <strong>Not quite — you chose:</strong> {selected_opt}<br>
                    ✅ <strong>Correct answer:</strong> {correct_opt}<br><br>
                    <strong>📖 Explanation:</strong> {q.get('explanation', '')}<br>
                </div>
                """, unsafe_allow_html=True)

                # Misconception analysis block
                st.markdown(f"""
                <div style="background:#FFF8E1;border-left:4px solid #F5A623;border-radius:8px;
                            padding:0.85rem 1rem;margin-top:0.75rem;font-size:0.9rem;color:#5D4037;">
                    <strong>🧠 Misconception Analysis:</strong><br><br>
                    {analysis}
                </div>
                """, unsafe_allow_html=True)

                # "Ask the tutor" shortcut — pre-fills tutor with this question
                if st.button("💬 Ask Tutor to Explain This Further", use_container_width=True):
                    from utils.session_state import add_message
                    followup = f"I got this WAEC {subject} question wrong: '{q['question']}'. I chose '{selected_opt}' but the correct answer is '{correct_opt}'. Can you explain this concept clearly with a Nigerian example?"
                    add_message("user", followup)
                    st.switch_page("pages/01_tutor.py")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Next Question ➡️", type="primary", use_container_width=True):
                st.session_state.quiz_index += 1
                st.rerun()

    else:
        # ── Results ──────────────────────────────────────────────────────────
        score = st.session_state.quiz_score
        total_q = len(questions)
        pct = round(score / total_q * 100)

        grade = "🏆 Excellent!" if pct >= 80 else "👍 Good effort!" if pct >= 60 else "📖 Keep studying!"

        st.markdown(f"""
        <div style="text-align:center;padding:2rem 1rem;">
            <div style="font-size:3.5rem">{"🎉" if pct >= 80 else "💪" if pct >= 60 else "📚"}</div>
            <div class="score-display">{pct}%</div>
            <div style="font-size:1.1rem;color:#333;font-weight:600;margin:0.5rem 0">{grade}</div>
            <div style="color:#666;">You scored {score} out of {total_q} questions on {subject}</div>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Try Again", use_container_width=True):
                st.session_state.quiz_active = False
                st.session_state.quiz_answered = {}
                st.rerun()
        with col2:
            if st.button("💬 Study with Tutor", use_container_width=True):
                st.switch_page("pages/01_tutor.py")
        with col3:
            if st.button("📊 View Progress", use_container_width=True):
                st.switch_page("pages/03_progress.py")