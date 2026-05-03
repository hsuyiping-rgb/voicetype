import sys
import os
import opencc
import config

# PyInstaller 打包後 opencc 資料檔路徑
if getattr(sys, 'frozen', False):
    _opencc_dir = os.path.join(sys._MEIPASS, 'opencc')
    os.environ.setdefault('OPENCC_DATA', _opencc_dir)

# 簡體 → 繁體轉換器（台灣用語）
_converter = opencc.OpenCC("s2twp")

_PROMPTS = {
    "light": (
        "請將以下口語文字中的贅詞（嗯、啊、那個、就是、對對對、um、uh、you know 等）刪除，"
        "只做最小必要的修改，保留原始語意、用詞與語言（中文保持繁體中文，英文保持英文，不可互相翻譯），"
        "直接輸出結果，不要加任何說明。\n\n"
        "{text}"
    ),
    "full": (
        "請將以下口語語音辨識文字整理成流暢、專業的書面文字：\n"
        "1. 刪除贅詞與口頭語（嗯、啊、那個、就是說、um、uh、you know 等）\n"
        "2. 修正文法與標點\n"
        "3. 保留原始語意，不要增加額外內容\n"
        "4. 保留原始語言：中文用繁體中文，英文保持英文，絕對不可互相翻譯\n"
        "直接輸出整理後的文字，不要加說明或前綴。\n\n"
        "{text}"
    ),
}

_SYSTEM = (
    "你是多語言文字編輯助手。"
    "核心規則：中文一律輸出繁體中文；英文保持英文原文；嚴禁將任何語言翻譯成另一種語言。"
)

# 快取 API client，避免每次重新建立連線
_groq_client = None
_openai_client = None


def _get_groq():
    global _groq_client
    if _groq_client is None or _groq_client.api_key != config.GROQ_API_KEY:
        from groq import Groq
        if not config.GROQ_API_KEY:
            raise ValueError("Groq API 金鑰未設定")
        _groq_client = Groq(api_key=config.GROQ_API_KEY)
    return _groq_client


def _get_openai():
    global _openai_client
    if _openai_client is None or _openai_client.api_key != config.OPENAI_API_KEY:
        from openai import OpenAI
        if not config.OPENAI_API_KEY:
            raise ValueError("OpenAI API 金鑰未設定")
        _openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
    return _openai_client


def polish(text: str) -> str:
    """根據 polish_mode 決定是否潤飾，回傳處理後的文字。"""
    mode = config.POLISH_MODE
    if mode == "off" or not text.strip():
        return text

    prompt = _PROMPTS.get(mode, _PROMPTS["full"]).format(text=text)
    provider = config.LLM_PROVIDER

    if provider == "openai":
        result = _polish_openai(prompt)
    elif provider == "groq":
        result = _polish_groq(prompt)
    else:
        return text

    # 確保中文輸出為繁體（不影響英文）
    return _converter.convert(result)


def _polish_groq(prompt: str) -> str:
    client = _get_groq()
    response = client.chat.completions.create(
        model=config.GROQ_LLM_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user",   "content": prompt},
        ],
        temperature=0.3,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()


def _polish_openai(prompt: str) -> str:
    client = _get_openai()
    response = client.chat.completions.create(
        model=config.OPENAI_LLM_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user",   "content": prompt},
        ],
        temperature=0.3,
        max_tokens=1024,
    )
    return response.choices[0].message.content.strip()
