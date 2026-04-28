import sys
import threading
import keyboard
from config import HOTKEY, GROQ_API_KEY
from recorder import Recorder
from transcriber import transcribe
from injector import inject
from tray import TrayApp


def main():
    if not GROQ_API_KEY:
        print("錯誤：請先在 .env 檔案中設定 GROQ_API_KEY")
        sys.exit(1)

    recorder = Recorder()
    stop_event = threading.Event()

    tray = TrayApp(on_quit=lambda: stop_event.set())
    tray.run_detached()

    def on_hotkey_press():
        if not recorder._recording:
            tray.set_recording()
            recorder.start()

    def on_hotkey_release():
        if recorder._recording:
            tray.set_processing()
            wav_path = recorder.stop()
            if wav_path:
                try:
                    text = transcribe(wav_path)
                    if text:
                        inject(text)
                except Exception as e:
                    print(f"辨識失敗：{e}")
            tray.set_idle()

    keyboard.on_press_key(HOTKEY, lambda _: on_hotkey_press())
    keyboard.on_release_key(HOTKEY, lambda _: on_hotkey_release())

    print(f"VoiceType 已啟動，按住 [{HOTKEY}] 說話，放開後自動輸入文字")
    print("關閉請點選系統匣圖示 → 結束")

    stop_event.wait()
    keyboard.unhook_all()
    sys.exit(0)


if __name__ == "__main__":
    main()
