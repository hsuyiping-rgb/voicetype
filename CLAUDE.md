# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案簡介

Windows 桌面語音輸入工具，對標 Typeless。按住快捷鍵錄音，放開後自動語音辨識 + LLM 潤飾，結果貼入當前游標位置。設定介面為本地 web 頁面（`localhost:7777`）。

## 環境設定

```bash
pip install -r requirements.txt
python main.py   # 需以系統管理員身份執行
```

首次啟動後，右鍵系統匣圖示 → **開啟設定**，在瀏覽器填入 API 金鑰。

## 架構總覽

```
main.py          進入點：組裝模組、掛載快捷鍵、監聽 stop_event
config.py        讀寫 settings.json；reload() 供設定變更後熱重載
recorder.py      sounddevice 錄音；stop() 回傳暫存 WAV 路徑
transcriber.py   STT：依 config.STT_PROVIDER 呼叫 Groq 或 OpenAI Whisper
polisher.py      LLM 潤飾：依 config.LLM_PROVIDER / POLISH_MODE 決定行為
injector.py      剪貼簿貼上（預設）或逐字注入游標
tray.py          pystray 系統匣；三色圖示 + 右鍵選單（開啟設定 / 結束）
web/server.py    Flask（port 7777）：GET / 設定頁、POST /api/settings 儲存
web/templates/   Jinja2 HTML 設定頁面
web/static/      CSS（深色主題）+ JS（表單送出、密碼顯示切換）
settings.json    本地設定檔（gitignore），存 API 金鑰與所有選項
```

### 狀態流程

```
待機（藍）→ [按下 HOTKEY] → 錄音（紅）→ [放開] → STT + LLM（橘）→ 注入 → 待機（藍）
```

### 設定熱重載

`web/server.py` 儲存設定後呼叫 `config.reload()`，再觸發 `main.py` 中的 `on_settings_reload()`，重新掛載快捷鍵（因為 HOTKEY 可能改變）。

### 關鍵設定（settings.json）

| 欄位 | 選項 | 說明 |
|------|------|------|
| `stt_provider` | `groq` / `openai` | 語音辨識引擎 |
| `llm_provider` | `groq` / `openai` / `off` | 文字潤飾引擎 |
| `polish_mode` | `light` / `full` | 輕度去贅詞 / 完整整理 |
| `hotkey` | 任意鍵名 | 按住錄音的快捷鍵 |
| `language` | `zh` / `en` / `` | 空字串 = 自動偵測 |
| `inject_method` | `clipboard` / `type` | 文字注入方式 |

### LLM 模型

| 提供者 | STT | LLM |
|--------|-----|-----|
| Groq | `whisper-large-v3-turbo` | `llama-3.3-70b-versatile` |
| OpenAI | `whisper-1` | `gpt-4o-mini` |
