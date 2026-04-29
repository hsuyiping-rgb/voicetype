import json
import os

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), "settings.json")

_DEFAULTS = {
    "openai_api_key": "",
    "groq_api_key": "",
    "stt_provider": "groq",       # "groq" | "openai"
    "llm_provider": "groq",       # "groq" | "openai" | "off"
    "polish_mode": "full",        # "off" | "light" | "full"
    "hotkey": "right alt",
    "language": "zh",             # "" = 自動偵測
    "inject_method": "clipboard", # "clipboard" | "type"
}

# 錄音參數（不對外開放設定）
SAMPLE_RATE = 16000
CHANNELS = 1

# Groq STT 模型
GROQ_STT_MODEL = "whisper-large-v3-turbo"

# OpenAI STT 模型
OPENAI_STT_MODEL = "whisper-1"

# LLM 模型
GROQ_LLM_MODEL = "llama-3.3-70b-versatile"
OPENAI_LLM_MODEL = "gpt-4o-mini"


def load() -> dict:
    if not os.path.exists(SETTINGS_PATH):
        save(_DEFAULTS.copy())
        return _DEFAULTS.copy()
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    # 補上缺少的預設值
    for k, v in _DEFAULTS.items():
        data.setdefault(k, v)
    return data


def save(settings: dict):
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


# 讀取一次供各模組 import 使用
_s = load()

OPENAI_API_KEY: str = _s["openai_api_key"]
GROQ_API_KEY: str = _s["groq_api_key"]
STT_PROVIDER: str = _s["stt_provider"]
LLM_PROVIDER: str = _s["llm_provider"]
POLISH_MODE: str = _s["polish_mode"]
HOTKEY: str = _s["hotkey"]
LANGUAGE: str = _s["language"]
INJECT_METHOD: str = _s["inject_method"]


def reload():
    """設定頁儲存後呼叫，重新載入所有設定到全域變數。"""
    global OPENAI_API_KEY, GROQ_API_KEY, STT_PROVIDER, LLM_PROVIDER
    global POLISH_MODE, HOTKEY, LANGUAGE, INJECT_METHOD
    s = load()
    OPENAI_API_KEY = s["openai_api_key"]
    GROQ_API_KEY = s["groq_api_key"]
    STT_PROVIDER = s["stt_provider"]
    LLM_PROVIDER = s["llm_provider"]
    POLISH_MODE = s["polish_mode"]
    HOTKEY = s["hotkey"]
    LANGUAGE = s["language"]
    INJECT_METHOD = s["inject_method"]
