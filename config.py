import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "whisper-large-v3-turbo"

# 錄音設定
SAMPLE_RATE = 16000
CHANNELS = 1

# 快捷鍵：按住錄音，放開辨識
HOTKEY = "right alt"

# 語言設定（留空讓 Whisper 自動偵測）
LANGUAGE = "zh"

# 注入方式：clipboard（貼上）或 type（逐字輸入）
INJECT_METHOD = "clipboard"
