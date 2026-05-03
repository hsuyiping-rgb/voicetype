import sys
import os
import threading
import ctypes

# 最早期錯誤捕捉：用 MessageBox 顯示，因為 console 可能不可用
def _fatal(msg):
    ctypes.windll.user32.MessageBoxW(None, str(msg), "VoiceType 啟動錯誤", 0x10)
    sys.exit(1)

# exe 模式下將所有輸出寫入日誌檔
if getattr(sys, 'frozen', False):
    try:
        _log_path = os.path.join(os.path.dirname(sys.executable), "voicetype.log")
        _log = open(_log_path, "w", encoding="utf-8", buffering=1)
        sys.stdout = _log
        sys.stderr = _log
    except Exception as e:
        _fatal(f"無法建立日誌：{e}")

try:
    import config
    import hotkey as hk
    from recorder import Recorder
    from transcriber import transcribe
    from polisher import polish
    from injector import inject
    from tray import TrayApp
    from web import server as web_server
except Exception as e:
    import traceback
    _fatal(f"匯入模組失敗：\n{e}\n\n{traceback.format_exc()}")

# 防止重複啟動
_MUTEX_NAME = "VoiceType_SingleInstance"
_mutex = ctypes.windll.kernel32.CreateMutexW(None, True, _MUTEX_NAME)
if ctypes.windll.kernel32.GetLastError() == 183:
    ctypes.windll.user32.MessageBoxW(None, "VoiceType 已經在執行中。", "VoiceType", 0x40)
    sys.exit(0)


def main():
    try:
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
                audio_bytes = recorder.stop()
                if audio_bytes:
                    try:
                        print("[DEBUG] 送出辨識...")
                        text = transcribe(audio_bytes)
                        print(f"[DEBUG] 辨識結果：{text!r}")
                        if text:
                            text = polish(text)
                            print(f"[DEBUG] 潤飾結果：{text!r}")
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
                print(f"[VoiceType] ⚠ 快捷鍵 [{config.HOTKEY}] 註冊失敗")

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

    except Exception as e:
        import traceback
        _fatal(f"執行錯誤：\n{e}\n\n{traceback.format_exc()}")


def _on_quit():
    hk.unregister()
    sys.exit(0)


if __name__ == "__main__":
    main()
