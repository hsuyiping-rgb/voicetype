"""
全域快捷鍵：用 GetAsyncKeyState 輪詢偵測按下與放開。
不需管理員權限，不依賴訊息迴圈。
"""
import ctypes
import ctypes.wintypes
import threading
import time

user32 = ctypes.windll.user32

_VK_MAP = {
    "right ctrl":  0xA3, "left ctrl":  0xA2,
    "right alt":   0xA5, "left alt":   0xA4,
    "right shift": 0xA1, "left shift": 0xA0,
    "f1":  0x70, "f2":  0x71, "f3":  0x72, "f4":  0x73,
    "f5":  0x74, "f6":  0x75, "f7":  0x76, "f8":  0x77,
    "f9":  0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B,
    "caps lock": 0x14, "pause": 0x13,
}

_press_cb   = None
_release_cb = None
_stop       = False
_thread     = None


def _vk_from_name(name: str) -> int:
    return _VK_MAP.get(name.strip().lower(), 0xA3)


def _poll(vk: int):
    pressed = False
    while not _stop:
        down = bool(user32.GetAsyncKeyState(vk) & 0x8000)
        if down and not pressed:
            pressed = True
            if _press_cb:
                threading.Thread(target=_press_cb, daemon=True).start()
        elif not down and pressed:
            pressed = False
            if _release_cb:
                threading.Thread(target=_release_cb, daemon=True).start()
        time.sleep(0.02)  # 20ms 輪詢


def register(hotkey_name: str, on_press, on_release) -> bool:
    global _press_cb, _release_cb, _stop, _thread
    _press_cb   = on_press
    _release_cb = on_release
    _stop = False
    vk = _vk_from_name(hotkey_name)
    _thread = threading.Thread(target=_poll, args=(vk,), daemon=True)
    _thread.start()
    print(f"[hotkey] 已綁定：{hotkey_name} (vk=0x{vk:02X})")
    return True


def unregister():
    global _stop
    _stop = True
