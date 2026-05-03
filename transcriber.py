import config

# 快取 API client，避免每次重新建立連線
_groq_client = None
_openai_client = None


def _get_groq():
    global _groq_client
    if _groq_client is None or _groq_client.api_key != config.GROQ_API_KEY:
        from groq import Groq
        if not config.GROQ_API_KEY:
            raise ValueError("Groq API 金鑰未設定，請開啟設定頁填入")
        _groq_client = Groq(api_key=config.GROQ_API_KEY)
    return _groq_client


def _get_openai():
    global _openai_client
    if _openai_client is None or _openai_client.api_key != config.OPENAI_API_KEY:
        from openai import OpenAI
        if not config.OPENAI_API_KEY:
            raise ValueError("OpenAI API 金鑰未設定，請開啟設定頁填入")
        _openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
    return _openai_client


def transcribe(audio_bytes: bytes) -> str:
    """根據 STT_PROVIDER 設定選擇辨識引擎，回傳純文字。"""
    provider = config.STT_PROVIDER
    if provider == "openai":
        return _transcribe_openai(audio_bytes)
    else:
        return _transcribe_groq(audio_bytes)


def _transcribe_groq(audio_bytes: bytes) -> str:
    client = _get_groq()
    response = client.audio.transcriptions.create(
        model=config.GROQ_STT_MODEL,
        file=("audio.wav", audio_bytes, "audio/wav"),
        language=config.LANGUAGE or None,
        response_format="text",
    )
    result = response if isinstance(response, str) else response.text
    return result.strip()


def _transcribe_openai(audio_bytes: bytes) -> str:
    import io
    client = _get_openai()
    response = client.audio.transcriptions.create(
        model=config.OPENAI_STT_MODEL,
        file=("audio.wav", io.BytesIO(audio_bytes), "audio/wav"),
        language=config.LANGUAGE or None,
        response_format="text",
    )
    return response.strip()
