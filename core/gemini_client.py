"""OpenAI GPT-4o-mini client for STEMBridge"""
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = None


def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        _client = OpenAI(api_key=api_key)
    return _client


def generate(prompt: str, system: str = None, temperature: float = 0.7) -> str:
    """Single-turn generation"""
    client = get_client()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=temperature,
        max_tokens=1500,
    )
    return response.choices[0].message.content


def chat_generate(history: list, new_message: str, system: str = None) -> str:
    """Multi-turn chat generation"""
    client = get_client()
    messages = []

    if system:
        messages.append({"role": "system", "content": system})

    # Keep last 10 turns for context
    for msg in history[-10:]:
        role = "user" if msg["role"] == "user" else "assistant"
        messages.append({"role": role, "content": msg["content"]})

    messages.append({"role": "user", "content": new_message})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7,
        max_tokens=1500,
    )
    return response.choices[0].message.content