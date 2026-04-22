"""Quiz engine — generates WAEC-style MCQ questions via Gemini"""
import json
from core.gemini_client import generate
from core import rag_pipeline


def generate_quiz(subject: str, topic: str = None, num_questions: int = 5) -> list:
    """Generate WAEC-style MCQ questions"""
    # Get context from RAG
    query = topic or f"{subject} WAEC past questions"
    context_docs = []
    if rag_pipeline.is_ready():
        context_docs = rag_pipeline.retrieve(query, subject, n_results=5)

    context_str = "\n".join(context_docs[:3]) if context_docs else ""
    topic_str = f"specifically on {topic}" if topic else "covering key WAEC topics"

    prompt = f"""Generate {num_questions} WAEC-style multiple choice questions for Nigerian SS students on {subject}, {topic_str}.

{f"Use this context as inspiration: {context_str}" if context_str else ""}

Return ONLY a JSON array. Each object must have exactly these fields:
- "question": the question text (include numbers/formulas where relevant)
- "options": array of exactly 4 strings ["A. ...", "B. ...", "C. ...", "D. ..."]
- "correct": the correct option letter, e.g. "A"
- "explanation": brief explanation of why the answer is correct (2 sentences max)
- "topic": the specific subtopic

Make questions at WAEC difficulty level. Include calculation questions.
Return ONLY the JSON array, no markdown, no extra text."""

    try:
        raw = generate(prompt, temperature=0.6)
        # Clean up any markdown fences
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip().rstrip("```")

        questions = json.loads(raw)
        # Validate structure
        validated = []
        for q in questions:
            if all(k in q for k in ["question", "options", "correct", "explanation"]):
                validated.append(q)
        return validated

    except Exception as e:
        # Fallback hardcoded questions
        return _fallback_questions(subject)


def _fallback_questions(subject: str) -> list:
    fallbacks = {
        "Mathematics": [
            {
                "question": "If 3x - 6 = 9, find x",
                "options": ["A. 3", "B. 4", "C. 5", "D. 6"],
                "correct": "C",
                "explanation": "3x = 15, so x = 5. We add 6 to both sides first.",
                "topic": "Linear Equations"
            },
            {
                "question": "What is the area of a rectangle with length 8cm and width 5cm?",
                "options": ["A. 13 cm²", "B. 26 cm²", "C. 40 cm²", "D. 45 cm²"],
                "correct": "C",
                "explanation": "Area = length × width = 8 × 5 = 40 cm²",
                "topic": "Mensuration"
            }
        ],
        "Physics": [
            {
                "question": "A force of 30N acts on a body of mass 6kg. What is the acceleration?",
                "options": ["A. 2 m/s²", "B. 5 m/s²", "C. 6 m/s²", "D. 180 m/s²"],
                "correct": "B",
                "explanation": "Using F = ma: a = F/m = 30/6 = 5 m/s²",
                "topic": "Newton's Laws"
            }
        ],
        "Chemistry": [
            {
                "question": "Which of the following is an example of a physical change?",
                "options": ["A. Burning wood", "B. Rusting iron", "C. Melting ice", "D. Cooking food"],
                "correct": "C",
                "explanation": "Melting ice is a physical change — only state changes, no new substance formed.",
                "topic": "Physical and Chemical Changes"
            }
        ],
        "Biology": [
            {
                "question": "Which organelle is responsible for protein synthesis?",
                "options": ["A. Mitochondria", "B. Ribosome", "C. Nucleus", "D. Vacuole"],
                "correct": "B",
                "explanation": "Ribosomes are the site of protein synthesis where mRNA is translated.",
                "topic": "Cell Biology"
            }
        ]
    }
    return fallbacks.get(subject, fallbacks["Mathematics"])