import sys
import threading
import ctypes
import config
import hotkey as hk
from recorder import Recorder
from transcriber import transcribe
from polisher import polish
from injector import inject
from tray import TrayApp
from web import server as web_server

# 防止重複啟動
_MUTEX_NAME = "VoiceType_SingleInstance"
_mutex = ctypes.windll.kernel32.CreateMutexW(None, True, _MUTEX_NAME)
if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
    print("[VoiceType] 已經在執行中，不允許重複啟動。")
    sys.exit(0)


def main():
    web_server.run_detached()

    recorder = Recorder()
    tray = TrayApp(
        on_quit=_on_quit,
        on_open_settings=web_server.open_browser,
    )

    def on_press():
        if not recorder._recording:
            print("[DEBUG] 偵測到按下，開始錄音...")
            tray.set_recording()
            recorder.start()

    def on_release():
        if recorder._recording:
            print("[DEBUG] 偵測到放開，停止錄音...")
            tray.set_processing()
            wav_path = recorder.stop()
            if wav_path:
                try:
                    print("[DEBUG] 送出辨識...")
                    text = transcribe(wav_path)
                    print(f"[DEBUG] 辨識結果：{text!r}")
                    if text:
                        text = polish(text)
                        print(f"[DEBUG] 潤飾結果：{text!r}")
                        print("[DEBUG] 注入文字中...")
                        inject(text)
                        print("[DEBUG] 注入完成")
                except Exception as e:
                    print(f"[VoiceType] 錯誤：{e}", file=sys.stderr)
                    import traceback; traceback.print_exc()
            else:
                print("[DEBUG] 錄音太短或無聲，略過")
            tray.set_idle()

    def register():
        ok = hk.register(config.HOTKEY, on_press, on_release)
        if ok:
            print(f"[VoiceType] 已啟動 — 按住 [{config.HOTKEY}] 說話，放開後自動輸入")
        else:
            print(f"[VoiceType] ⚠ 快捷鍵 [{config.HOTKEY}] 註冊失敗，可能被其他程式佔用")

    def on_settings_reload():
        hk.unregister()
        register()

    web_server.set_reload_callback(on_settings_reload)

    def _start_hotkey():
        import time
        time.sleep(0.5)
        register()

    threading.Thread(target=_start_hotkey, daemon=True, name="hotkey-init").start()

    tray.run()


def _on_quit():
    hk.unregister()
    sys.exit(0)


if __name__ == "__main__":
    main()
