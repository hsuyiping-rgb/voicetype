import sys
import os
import threading
import webbrowser
from flask import Flask, render_template, request, jsonify
import config

WEB_PORT = 7777

# PyInstaller 打包後資源路徑
def _base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

_web_dir = _base_path() if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
_app = Flask(__name__,
             template_folder=os.path.join(_web_dir, "templates"),
             static_folder=os.path.join(_web_dir, "static"))
_reload_callback = None  # 設定儲存後通知 main.py 重載


def set_reload_callback(fn):
    global _reload_callback
    _reload_callback = fn


@_app.route("/")
def index():
    settings = config.load()
    return render_template("index.html", s=settings)


@_app.route("/api/settings", methods=["GET"])
def get_settings():
    return jsonify(config.load())


@_app.route("/api/settings", methods=["POST"])
def save_settings():
    data = request.get_json()
    allowed_keys = {
        "openai_api_key", "groq_api_key", "stt_provider", "llm_provider",
        "polish_mode", "hotkey", "language", "inject_method",
    }
    current = config.load()
    for k in allowed_keys:
        if k in data:
            current[k] = data[k]
    config.save(current)
    config.reload()
    if _reload_callback:
        _reload_callback()
    return jsonify({"status": "ok"})


@_app.route("/api/status", methods=["GET"])
def status():
    return jsonify({
        "stt_provider": config.STT_PROVIDER,
        "llm_provider": config.LLM_PROVIDER,
        "polish_mode": config.POLISH_MODE,
        "hotkey": config.HOTKEY,
        "groq_key_set": bool(config.GROQ_API_KEY),
        "openai_key_set": bool(config.OPENAI_API_KEY),
    })


def open_browser():
    webbrowser.open(f"http://localhost:{WEB_PORT}")


def run(debug=False):
    _app.run(host="127.0.0.1", port=WEB_PORT, debug=debug, use_reloader=False)


def run_detached():
    t = threading.Thread(target=run, daemon=True)
    t.start()
