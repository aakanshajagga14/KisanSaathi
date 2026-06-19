"""LLM farming advice via Groq API."""

import logging
import os

from groq import Groq

logger = logging.getLogger(__name__)

FALLBACK_MESSAGE = "Maaf kijiye, abhi jawab nahi de paaya. Dobara koshish karein."
INVALID_KEY_MESSAGE = (
    "GROQ API key galat ya set nahi hai. `.env` file mein sahi key daalein "
    "(console.groq.com se free key lein), phir app restart karein."
)


def _is_valid_key(api_key: str) -> bool:
    if not api_key or not api_key.strip():
        return False
    if api_key.strip() in {"your_groq_api_key_here", "gsk_your_actual_key_here"}:
        return False
    return api_key.startswith("gsk_")


def get_farming_advice(user_text: str, system_prompt: str) -> str:
    """Get farming advice from Groq LLaMA model."""
    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not _is_valid_key(api_key):
        logger.error("GROQ_API_KEY missing or placeholder")
        return INVALID_KEY_MESSAGE

    try:
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=400,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text},
            ],
        )
        content = response.choices[0].message.content
        return content.strip() if content else FALLBACK_MESSAGE
    except Exception as exc:
        logger.error("LLM request failed: %s", exc)
        err = str(exc).lower()
        if "401" in err or "invalid_api_key" in err or "invalid api key" in err:
            return INVALID_KEY_MESSAGE
        return FALLBACK_MESSAGE
