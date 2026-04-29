import sys
import threading
import keyboard
import config
from recorder import Recorder
from transcriber import transcribe
from polisher import polish
from injector import inject
from tray import TrayApp
from web import server as web_server


def main():
    # 啟動 Flask 設定 server（背景）
    web_server.run_detached()

    recorder = Recorder()
    stop_event = threading.Event()
    _hotkey_handle = []  # 用 list 以便在 closure 中替換

    def open_settings():
        web_server.open_browser()

    tray = TrayApp(
        on_quit=lambda: stop_event.set(),
        on_open_settings=open_settings,
    )
    tray.run_detached()

    def on_press(_):
        if not recorder._recording:
            tray.set_recording()
            recorder.start()

    def on_release(_):
        if recorder._recording:
            tray.set_processing()
            wav_path = recorder.stop()
            if wav_path:
                try:
                    text = transcribe(wav_path)
                    if text:
                        text = polish(text)
                        inject(text)
                except Exception as e:
                    print(f"[VoiceType] 錯誤：{e}", file=sys.stderr)
            tray.set_idle()

    def register_hotkey():
        hk = config.HOTKEY
        keyboard.on_press_key(hk, on_press)
        keyboard.on_release_key(hk, on_release)
        print(f"[VoiceType] 已啟動 — 按住 [{hk}] 說話，放開後自動輸入")
        print("[VoiceType] 系統匣右鍵 → 開啟設定 | 結束")

    def on_settings_reload():
        """設定儲存後重新掛載快捷鍵。"""
        keyboard.unhook_all()
        register_hotkey()

    web_server.set_reload_callback(on_settings_reload)
    register_hotkey()

    stop_event.wait()
    keyboard.unhook_all()
    sys.exit(0)


if __name__ == "__main__":
    main()
