"""Speech-to-text via Groq Whisper API."""

import logging
import os

from groq import Groq

logger = logging.getLogger(__name__)


def transcribe_audio(audio_filepath: str) -> str:
    """Transcribe audio file using Groq Whisper. Returns empty string on failure."""
    if audio_filepath is None:
        return None

    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key or api_key in {"your_groq_api_key_here", "gsk_your_actual_key_here"}:
        logger.error("GROQ_API_KEY not set or still placeholder")
        return ""

    try:
        client = Groq(api_key=api_key)
        with open(audio_filepath, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=audio_file,
                model="whisper-large-v3-turbo",
            )
        return transcription.text.strip() if transcription.text else ""
    except Exception as exc:
        logger.error("STT transcription failed: %s", exc)
        return ""
