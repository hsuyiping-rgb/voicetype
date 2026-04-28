# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案簡介

Windows 桌面語音輸入工具，按住快捷鍵錄音、放開後自動將語音辨識結果貼入當前游標位置，行為類似輸入法。

## 環境設定

```bash
pip install -r requirements.txt
```

複製 `.env.example` 為 `.env` 並填入 Groq API 金鑰：
```
GROQ_API_KEY=your_groq_api_key_here
```

## 執行

```bash
python main.py
```

> 需要以**系統管理員身份**執行，`keyboard` 套件監聽全域快捷鍵需要管理員權限。

## 架構說明

```
main.py          進入點：組裝各模組、掛載快捷鍵事件
config.py        所有設定集中在此（熱鍵、語言、注入方式、API key）
recorder.py      sounddevice 麥克風錄音，stop() 回傳暫存 WAV 路徑
transcriber.py   將 WAV 送至 Groq Whisper API，回傳純文字
injector.py      透過剪貼簿 + Ctrl+V 將文字注入當前視窗
tray.py          pystray 系統匣圖示，顏色反映目前狀態
```

### 狀態流程

```
待機（藍） → [按下 HOTKEY] → 錄音中（紅） → [放開] → 辨識中（橘） → 注入文字 → 待機（藍）
```

### 關鍵設定（config.py）

| 變數 | 預設值 | 說明 |
|------|--------|------|
| `HOTKEY` | `right alt` | 按住錄音的快捷鍵 |
| `LANGUAGE` | `zh` | Whisper 語言代碼，留空自動偵測 |
| `INJECT_METHOD` | `clipboard` | `clipboard`（貼上）或 `type`（逐字） |
| `GROQ_MODEL` | `whisper-large-v3-turbo` | Groq 語音辨識模型 |

### 文字注入方式

- `clipboard`（預設）：將文字寫入剪貼簿後模擬 Ctrl+V，速度快、支援中文，操作完成後會還原原始剪貼簿內容。
- `type`：用 `keyboard.write()` 逐字輸入，對部分應用程式相容性較差，不建議用於中文。
