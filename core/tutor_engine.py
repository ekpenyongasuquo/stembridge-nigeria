"""
STEMBridge Tutor Engine
Adaptive tutoring with WAEC context, misconception detection,
and Nigerian-specific examples
"""
from core.gemini_client import chat_generate, generate
from core import rag_pipeline

NIGERIAN_CONTEXT = {
    "Mathematics": "Use Nigerian Naira (₦) for money problems. Reference Nigerian markets, NNPC fuel prices, Dangote cement, or Lagos-Abuja distances for word problems.",
    "Physics": "Use Nigerian examples: NEPA/PHCN electricity supply, Dangote refinery processes, Lagos Third Mainland Bridge (stress/load), Kano harmattan (humidity/temperature).",
    "Chemistry": "Use Nigerian contexts: crude oil refining at Port Harcourt, sachet water (pure water) purification, Nigerian food chemistry (ogbono, palm oil, pepper), NNPC petroleum products.",
    "Biology": "Use Nigerian examples: malaria and Anopheles mosquito in Nigeria, cassava/yam photosynthesis, Lagos lagoon ecosystem, common Nigerian diseases (typhoid, cholera), NAFDAC drug regulation.",
}

WAEC_TOPICS = {
    "Mathematics": ["Number & Numeration", "Algebraic Processes", "Mensuration", "Plane Geometry", "Trigonometry", "Statistics & Probability", "Coordinate Geometry", "Logarithms"],
    "Physics": ["Mechanics", "Thermal Physics", "Waves & Sound", "Light & Optics", "Electricity & Magnetism", "Modern Physics", "Atomic Physics"],
    "Chemistry": ["Atomic Structure", "Chemical Bonding", "Mole Concept", "Acids/Bases/Salts", "Electrochemistry", "Organic Chemistry", "Equilibrium", "Periodic Table"],
    "Biology": ["Cell Biology", "Nutrition", "Transport Systems", "Respiration", "Excretion", "Reproduction", "Genetics & Evolution", "Ecology", "Coordination"],
}


def build_system_prompt(subject: str, context_docs: list) -> str:
    nigerian_hint = NIGERIAN_CONTEXT.get(subject, "")
    context_str = "\n\n".join(context_docs) if context_docs else "No specific past questions retrieved — use your general WAEC knowledge."

    return f"""You are STEMBridge, an expert WAEC/NECO {subject} tutor for Nigerian SS1-SS3 students.

YOUR PERSONALITY:
- Warm, encouraging, and patient like a good Nigerian teacher
- Use phrases like "Very good!", "Oya let's try this", "No wahala, let me explain again"
- Never make students feel bad for wrong answers
- Celebrate progress genuinely

YOUR TEACHING APPROACH:
1. Always explain concepts in simple English first, then give the formula/rule
2. {nigerian_hint}
3. If a student makes a mistake, identify the SPECIFIC misconception before correcting
4. Always end explanations by asking a follow-up question to check understanding
5. For calculations, show ALL steps clearly — never skip

FORMULA FORMATTING RULES — VERY IMPORTANT:
- NEVER use LaTeX notation. No square brackets, no backslashes, no \Delta, no \frac, no [ ] around formulas
- Write all formulas in plain readable text like this:
  GOOD: Q = mcΔT  where Q = heat energy (J), m = mass (kg), c = specific heat capacity (J/kg°C), ΔT = temperature change (°C)
  GOOD: F = ma  where F = force (N), m = mass (kg), a = acceleration (m/s²)
  GOOD: v = u + at
  BAD: [ Q = mc\\Delta T ]
  BAD: \\frac{{a}}{{b}}
- Use the actual Unicode symbols directly: Δ for delta, ² for squared, ³ for cubed, ° for degrees, × for multiply, ÷ for divide, π for pi
- Write fractions as: a/b — never use LaTeX frac
- Always put formulas on their own line for clarity

WAEC PAST QUESTIONS CONTEXT:
{context_str}

RULES:
- Stay focused on {subject} and WAEC/NECO syllabus
- When solving problems, write: "Step 1:", "Step 2:" etc.
- If asked something outside {subject}, politely redirect
- Always recommend the student attempts the problem first before you solve it
- Keep responses concise but complete — students read on mobile"""


def tutor_respond(user_message: str, subject: str, history: list) -> str:
    """Generate a tutor response with RAG context"""
    # Retrieve relevant WAEC content
    context_docs = []
    if rag_pipeline.is_ready():
        context_docs = rag_pipeline.retrieve(user_message, subject, n_results=3)

    system = build_system_prompt(subject, context_docs)

    try:
        response = chat_generate(history, user_message, system=system)
        return response
    except Exception as e:
        return f"⚠️ Connection issue: {str(e)}. Please check your OPENAI_API_KEY."


def detect_misconception(student_answer: str, correct_answer: str, subject: str) -> str:
    """Analyze a student's wrong answer to find the specific misconception"""
    prompt = f"""A Nigerian SS student gave a wrong answer on a WAEC {subject} question.

Correct answer: {correct_answer}
Student's answer: {student_answer}

In 2-3 sentences:
1. Name the specific misconception
2. Explain WHY they might have thought that
3. Give the clearest one-line correction

Be gentle and encouraging. Use simple language."""

    try:
        return generate(prompt, temperature=0.5)
    except Exception:
        return f"The correct answer is: {correct_answer}"


def get_study_tip(subject: str, weak_topics: list) -> str:
    """Generate a personalized study tip based on weak areas"""
    if not weak_topics:
        return ""

    prompt = f"""A Nigerian SS3 student preparing for WAEC {subject} is struggling with: {', '.join(weak_topics)}.

Give ONE practical, specific study tip for the weakest topic. 
Include a Nigerian real-world connection.
Keep it to 3 sentences max. Be motivating."""

    try:
        return generate(prompt, temperature=0.8)
    except Exception:
        return ""