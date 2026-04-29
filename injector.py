import time
import ctypes
from ctypes import wintypes
import pyperclip
import config

# Windows SendInput 結構定義
PUL = ctypes.POINTER(ctypes.c_ulong)

class KeyBdInput(ctypes.Structure):
    _fields_ = [
        ("wVk",         wintypes.WORD),
        ("wScan",       wintypes.WORD),
        ("dwFlags",     wintypes.DWORD),
        ("time",        wintypes.DWORD),
        ("dwExtraInfo", PUL),
    ]

class HardwareInput(ctypes.Structure):
    _fields_ = [
        ("uMsg",    wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]

class MouseInput(ctypes.Structure):
    _fields_ = [
        ("dx",          wintypes.LONG),
        ("dy",          wintypes.LONG),
        ("mouseData",   wintypes.DWORD),
        ("dwFlags",     wintypes.DWORD),
        ("time",        wintypes.DWORD),
        ("dwExtraInfo", PUL),
    ]

class _InputUnion(ctypes.Union):
    _fields_ = [("ki", KeyBdInput), ("mi", MouseInput), ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("ii", _InputUnion)]

VK_CONTROL = 0x11
VK_V       = 0x56
KEYEVENTF_KEYUP = 0x0002
INPUT_KEYBOARD  = 1


def _send_ctrl_v():
    """用 SendInput 模擬 Ctrl+V，可穿透 UAC 層級限制。"""
    extra = ctypes.c_ulong(0)
    pExtra = ctypes.pointer(extra)

    inputs = (Input * 4)(
        # Ctrl 按下
        Input(type=INPUT_KEYBOARD, ii=_InputUnion(
            ki=KeyBdInput(wVk=VK_CONTROL, wScan=0, dwFlags=0, time=0, dwExtraInfo=pExtra))),
        # V 按下
        Input(type=INPUT_KEYBOARD, ii=_InputUnion(
            ki=KeyBdInput(wVk=VK_V, wScan=0, dwFlags=0, time=0, dwExtraInfo=pExtra))),
        # V 放開
        Input(type=INPUT_KEYBOARD, ii=_InputUnion(
            ki=KeyBdInput(wVk=VK_V, wScan=0, dwFlags=KEYEVENTF_KEYUP, time=0, dwExtraInfo=pExtra))),
        # Ctrl 放開
        Input(type=INPUT_KEYBOARD, ii=_InputUnion(
            ki=KeyBdInput(wVk=VK_CONTROL, wScan=0, dwFlags=KEYEVENTF_KEYUP, time=0, dwExtraInfo=pExtra))),
    )
    ctypes.windll.user32.SendInput(4, ctypes.pointer(inputs[0]), ctypes.sizeof(Input))


def inject(text: str):
    if not text:
        return

    if config.INJECT_METHOD == "clipboard":
        _inject_via_clipboard(text)
    else:
        # 逐字模式：改用 SendInput 逐字元輸入
        _inject_chars(text)


def _inject_via_clipboard(text: str):
    try:
        original = pyperclip.paste()
    except Exception:
        original = ""

    pyperclip.copy(text)
    time.sleep(0.08)   # 稍長的延遲，等 Word 等 app 處理剪貼簿
    _send_ctrl_v()
    time.sleep(0.15)

    pyperclip.copy(original)


def _inject_chars(text: str):
    """用 SendInput 逐字元輸入（Unicode）。"""
    KEYEVENTF_UNICODE = 0x0004
    extra = ctypes.c_ulong(0)
    pExtra = ctypes.pointer(extra)

    for ch in text:
        code = ord(ch)
        inputs = (Input * 2)(
            Input(type=INPUT_KEYBOARD, ii=_InputUnion(
                ki=KeyBdInput(wVk=0, wScan=code, dwFlags=KEYEVENTF_UNICODE, time=0, dwExtraInfo=pExtra))),
            Input(type=INPUT_KEYBOARD, ii=_InputUnion(
                ki=KeyBdInput(wVk=0, wScan=code, dwFlags=KEYEVENTF_UNICODE | KEYEVENTF_KEYUP, time=0, dwExtraInfo=pExtra))),
        )
        ctypes.windll.user32.SendInput(2, ctypes.pointer(inputs[0]), ctypes.sizeof(Input))
        time.sleep(0.005)
