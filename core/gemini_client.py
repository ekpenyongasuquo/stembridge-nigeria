"""Gemini 2.0 Flash API client for STEMBridge"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

_model = None


def get_model():
    global _model
    if _model is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        genai.configure(api_key=api_key)
        _model = genai.GenerativeModel("gemini-2.0-flash")
    return _model


def generate(prompt: str, system: str = None, temperature: float = 0.7) -> str:
    """Single-turn generation"""
    model = get_model()
    config = genai.GenerationConfig(temperature=temperature, max_output_tokens=1500)

    if system:
        full_prompt = f"{system}\n\n{prompt}"
    else:
        full_prompt = prompt

    response = model.generate_content(full_prompt, generation_config=config)
    return response.text


def chat_generate(history: list, new_message: str, system: str = None) -> str:
    """Multi-turn chat generation"""
    model = get_model()
    config = genai.GenerationConfig(temperature=0.7, max_output_tokens=1500)

    # Build full prompt from history
    conversation = ""
    if system:
        conversation += f"[System Instructions]\n{system}\n\n"

    for msg in history[-10:]:  # Keep last 10 turns for context
        role = "Student" if msg["role"] == "user" else "STEMBridge Tutor"
        conversation += f"{role}: {msg['content']}\n\n"

    conversation += f"Student: {new_message}\n\nSTEMBridge Tutor:"

    response = model.generate_content(conversation, generation_config=config)
    return response.text