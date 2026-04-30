"""
全域快捷鍵：RegisterHotKey（偵測按下）+ GetAsyncKeyState 輪詢（偵測放開）
不需要管理員權限。
"""
import ctypes
import ctypes.wintypes
import threading
import queue

user32 = ctypes.windll.user32

WM_HOTKEY    = 0x0312
MOD_NOREPEAT = 0x4000

# 常用鍵名 → Virtual Key Code
_VK_MAP = {
    "right ctrl":  0xA3, "left ctrl":  0xA2,
    "right alt":   0xA5, "left alt":   0xA4,
    "right shift": 0xA1, "left shift": 0xA0,
    "f1":  0x70, "f2":  0x71, "f3":  0x72,  "f4":  0x73,
    "f5":  0x74, "f6":  0x75, "f7":  0x76,  "f8":  0x77,
    "f9":  0x78, "f10": 0x79, "f11": 0x7A,  "f12": 0x7B,
    "caps lock": 0x14, "pause": 0x13,
}

HOTKEY_ID = 1

_press_cb   = None
_release_cb = None
_stop       = False
_thread     = None


def _vk_from_name(name: str) -> int:
    n = name.strip().lower()
    return _VK_MAP.get(n, 0xA3)  # 預設 right ctrl


def _loop(vk: int, ready: queue.Queue):
    global _stop
    _stop = False

    ok = user32.RegisterHotKey(None, HOTKEY_ID, MOD_NOREPEAT, vk)
    ready.put(bool(ok))
    if not ok:
        err = ctypes.windll.kernel32.GetLastError()
        print(f"[hotkey] RegisterHotKey 失敗 vk=0x{vk:02X} err={err}")
        return

    print(f"[hotkey] 已綁定 vk=0x{vk:02X}")
    msg   = ctypes.wintypes.MSG()
    pressed = False

    while not _stop:
        # 等待 WM_HOTKEY（按下）
        if user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
            if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                if not pressed:
                    pressed = True
                    if _press_cb:
                        threading.Thread(target=_press_cb, daemon=True).start()
        else:
            # 輪詢放開
            if pressed:
                state = user32.GetAsyncKeyState(vk)
                if not (state & 0x8000):
                    pressed = False
                    if _release_cb:
                        threading.Thread(target=_release_cb, daemon=True).start()
            ctypes.windll.kernel32.Sleep(10)

    user32.UnregisterHotKey(None, HOTKEY_ID)


def register(hotkey_name: str, on_press, on_release) -> bool:
    global _press_cb, _release_cb, _thread, _stop
    _press_cb   = on_press
    _release_cb = on_release
    vk = _vk_from_name(hotkey_name)
    _stop = False
    ready = queue.Queue()
    _thread = threading.Thread(target=_loop, args=(vk, ready), daemon=True)
    _thread.start()
    try:
        return ready.get(timeout=3)
    except queue.Empty:
        return False


def unregister():
    global _stop
    _stop = True
