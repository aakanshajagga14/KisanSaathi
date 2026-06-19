"""Text-to-speech via gTTS."""

import logging
import re
import tempfile

from gtts import gTTS

logger = logging.getLogger(__name__)


def _strip_markdown(text: str) -> str:
    """Remove markdown symbols before TTS."""
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    cleaned = re.sub(r"\*([^*]+)\*", r"\1", cleaned)
    cleaned = re.sub(r"#{1,6}\s*", "", cleaned)
    cleaned = re.sub(r"[_`~]", "", cleaned)
    return cleaned.strip()


def text_to_speech(text: str, lang: str = "hi") -> str:
    """Convert text to Hindi speech MP3. Returns filepath or None on failure."""
    if not text or not text.strip():
        return None

    try:
        cleaned_text = _strip_markdown(text)
        if not cleaned_text:
            return None

        tts = gTTS(text=cleaned_text, lang=lang, slow=False)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp.close()
        tts.save(tmp.name)
        return tmp.name
    except Exception as exc:
        logger.error("TTS conversion failed: %s", exc)
        return None
