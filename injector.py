import time
import pyperclip
import keyboard
from config import INJECT_METHOD


def inject(text: str):
    if not text:
        return

    if INJECT_METHOD == "clipboard":
        _inject_via_clipboard(text)
    else:
        keyboard.write(text, delay=0.01)


def _inject_via_clipboard(text: str):
    # 備份原有剪貼簿內容
    try:
        original = pyperclip.paste()
    except Exception:
        original = ""

    pyperclip.copy(text)
    time.sleep(0.05)
    keyboard.press_and_release("ctrl+v")
    time.sleep(0.1)

    # 還原剪貼簿
    pyperclip.copy(original)
