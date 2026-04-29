import sys
import threading
import config
import hotkey as hk
from recorder import Recorder
from transcriber import transcribe
from polisher import polish
from injector import inject
from tray import TrayApp
from web import server as web_server


def main():
    web_server.run_detached()

    recorder = Recorder()
    tray = TrayApp(
        on_quit=_on_quit,
        on_open_settings=web_server.open_browser,
    )

    def on_press():
        if not recorder._recording:
            tray.set_recording()
            recorder.start()

    def on_release():
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

    def register():
        hk.register(config.HOTKEY, on_press, on_release)
        print(f"[VoiceType] 已啟動 — 按住 [{config.HOTKEY}] 說話，放開後自動輸入")
        print("[VoiceType] 系統匣右鍵 → 開啟設定 | 結束")

    def on_settings_reload():
        hk.unregister()
        register()

    web_server.set_reload_callback(on_settings_reload)

    # 背景啟動快捷鍵（等 tray 就緒）
    threading.Thread(target=lambda: (__import__('time').sleep(0.5), register()), daemon=True).start()

    # pystray 在主執行緒執行
    tray.run()


def _on_quit():
    hk.unregister()
    sys.exit(0)


if __name__ == "__main__":
    main()
