import config

_PROMPTS = {
    "light": (
        "請將以下口語文字中的贅詞（嗯、啊、那個、就是、對對對 等）刪除，"
        "只做最小必要的修改，保留原始語意與用詞，必須使用繁體中文輸出，直接輸出結果，不要加任何說明。\n\n"
        "{text}"
    ),
    "full": (
        "請將以下口語語音辨識文字整理成流暢、專業的書面文字：\n"
        "1. 刪除贅詞與口頭語（嗯、啊、那個、就是說 等）\n"
        "2. 修正文法與標點\n"
        "3. 保留原始語意，不要增加額外內容\n"
        "4. 必須使用繁體中文輸出，不可使用簡體中文\n"
        "直接輸出整理後的文字，不要加說明或前綴。\n\n"
        "{text}"
    ),
}


def polish(text: str) -> str:
    """根據 polish_mode 決定是否潤飾，回傳處理後的文字。"""
    mode = config.POLISH_MODE
    if mode == "off" or not text.strip():
        return text

    prompt = _PROMPTS.get(mode, _PROMPTS["full"]).format(text=text)
    provider = config.LLM_PROVIDER

    if provider == "openai":
        return _polish_openai(prompt)
    elif provider == "groq":
        return _polish_groq(prompt)
    else:
        return text


_SYSTEM = "你是繁體中文文字編輯助手。所有輸出必須使用繁體中文，嚴禁使用簡體中文。"


def _polish_groq(prompt: str) -> str:
    from groq import Groq
    if not config.GROQ_API_KEY:
        raise ValueError("Groq API 金鑰未設定")
    client = Groq(api_key=config.GROQ_API_KEY)
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
    from openai import OpenAI
    if not config.OPENAI_API_KEY:
        raise ValueError("OpenAI API 金鑰未設定")
    client = OpenAI(api_key=config.OPENAI_API_KEY)
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
