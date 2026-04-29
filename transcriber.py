import os
import config


def transcribe(wav_path: str) -> str:
    """根據 STT_PROVIDER 設定選擇辨識引擎，回傳純文字。"""
    try:
        provider = config.STT_PROVIDER
        if provider == "openai":
            return _transcribe_openai(wav_path)
        else:
            return _transcribe_groq(wav_path)
    finally:
        try:
            os.unlink(wav_path)
        except OSError:
            pass


def _transcribe_groq(wav_path: str) -> str:
    from groq import Groq
    if not config.GROQ_API_KEY:
        raise ValueError("Groq API 金鑰未設定，請開啟設定頁填入")
    client = Groq(api_key=config.GROQ_API_KEY)
    with open(wav_path, "rb") as f:
        response = client.audio.transcriptions.create(
            model=config.GROQ_STT_MODEL,
            file=("audio.wav", f, "audio/wav"),
            language=config.LANGUAGE or None,
            response_format="text",
        )
    result = response if isinstance(response, str) else response.text
    return result.strip()


def _transcribe_openai(wav_path: str) -> str:
    from openai import OpenAI
    if not config.OPENAI_API_KEY:
        raise ValueError("OpenAI API 金鑰未設定，請開啟設定頁填入")
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    with open(wav_path, "rb") as f:
        response = client.audio.transcriptions.create(
            model=config.OPENAI_STT_MODEL,
            file=f,
            language=config.LANGUAGE or None,
            response_format="text",
        )
    return response.strip()
