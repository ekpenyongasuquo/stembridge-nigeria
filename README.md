# 🌉 STEMBridge Nigeria

> **AI-powered WAEC/NECO tutor for Nigerian SS1–SS3 students**  
> Built for DSH Hacks V1 | Theme: AI × STEM Education

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Render.com-00A86B?style=for-the-badge)]
(https://emfon-stembridge-nigeria.hf.space)
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?style=for-the-badge)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Gemini-2.0%20Flash-orange?style=for-the-badge)](https://aistudio.google.com)

---

## 🎯 The Problem

Nigeria has **over 1.5 million WAEC candidates** yearly. Most cannot afford private tutors (₦5,000–₦20,000/hour). Free online resources don't understand the WAEC syllabus or use Nigerian examples. Students memorize formulas without understanding concepts — leading to high failure rates (only ~50% pass 5+ subjects in WAEC annually).

## 💡 The Solution

STEMBridge is an adaptive AI tutor that:
- **Speaks Nigerian** — uses Naira, Lagos-Abuja distances, NNPC/Dangote references, local ecosystems
- **Knows WAEC** — RAG pipeline over real past questions (2016–2023)
- **Finds misconceptions** — doesn't just give answers, identifies *why* a student got it wrong
- **Adapts difficulty** — tracks performance per topic and personalizes the learning path

## 🚀 Features

| Feature | Description |
|---------|-------------|
| 💬 AI Tutor Chat | Conversational WAEC tutor with Nigerian context and step-by-step explanations |
| 📝 WAEC Quiz Generator | Auto-generated MCQ questions at WAEC difficulty level with instant feedback |
| 🔍 Misconception Detector | Analyzes wrong answers to pinpoint specific conceptual gaps |
| 📊 Progress Tracker | Accuracy per subject, topics covered, personalized study tips |
| 🔢 4 Subjects | Mathematics, Physics, Chemistry, Biology |
| 🌍 RAG Pipeline | ChromaDB vector store over scraped WAEC past questions |

## 🛠️ Tech Stack

```
Frontend:    Streamlit
AI Model:    Google Gemini 2.0 Flash (free tier)
Vector DB:   ChromaDB + Sentence Transformers (all-MiniLM-L6-v2)
Embeddings:  Local (no API cost)
Data:        Scraped WAEC past questions + curated Nigerian content
Deployment:  Render.com
```

## 📦 Local Setup

```bash
# 1. Clone
git clone https://github.com/YOUR_USERNAME/stembridge-nigeria
cd stembridge-nigeria

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up API key
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
# Get free key at: https://aistudio.google.com

# 5. Build knowledge base (run once)
python utils/scraper.py

# 6. Run
streamlit run app.py
```

## 🌐 Deploy to Render.com

1. Push repo to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Add environment variable: `GEMINI_API_KEY`
5. Deploy (render.yaml handles the rest)

## 📁 Project Structure

```
stembridge/
├── app.py                  # Main Streamlit app (landing page)
├── render.yaml             # Render deployment config
├── requirements.txt
├── .env.example
├── core/
│   ├── gemini_client.py    # Gemini 2.0 Flash API wrapper
│   ├── rag_pipeline.py     # ChromaDB vector store + retrieval
│   ├── tutor_engine.py     # Tutoring logic, Nigerian prompts
│   └── quiz_engine.py      # WAEC-style MCQ generator
├── data/
│   ├── knowledge_base.json # Scraped WAEC questions
│   └── chroma_db/          # Vector store (auto-created)
├── pages/
│   ├── 01_tutor.py         # AI chat tutor page
│   ├── 02_quiz.py          # Quiz practice page
│   └── 03_progress.py      # Progress tracking page
└── utils/
    ├── scraper.py          # WAEC past questions scraper
    └── session_state.py    # Streamlit state management
```

## 🎨 Design Philosophy

- **Mobile-first** — Nigerian students primarily use phones
- **Low-bandwidth friendly** — Streamlit is lightweight
- **Nigerian aesthetic** — Green/gold color scheme reflecting national identity
- **Encouraging tone** — Tutor uses Nigerian expressions ("Oya let's try", "No wahala")

## 👨‍💻 Built by

Ekpenyong — Nigeria 🇳🇬  
DSH Hacks V1 Submission | June 2026

---

*"Every Nigerian student deserves access to world-class STEM tutoring, regardless of family income."*