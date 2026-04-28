import os
from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, LANGUAGE


_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY 未設定，請在 .env 檔案中填入 API 金鑰")
        _client = Groq(api_key=GROQ_API_KEY)
    return _client


def transcribe(wav_path: str) -> str:
    client = _get_client()
    try:
        with open(wav_path, "rb") as f:
            response = client.audio.transcriptions.create(
                model=GROQ_MODEL,
                file=("audio.wav", f, "audio/wav"),
                language=LANGUAGE or None,
                response_format="text",
            )
        return response.strip() if isinstance(response, str) else response.text.strip()
    finally:
        os.unlink(wav_path)
