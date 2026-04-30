"""
全域快捷鍵：GetAsyncKeyState 輪詢，不需管理員，不需訊息迴圈。
test_key.py 已確認 right ctrl (0xA3) 可被偵測。
"""
import ctypes
import ctypes.wintypes
import threading
import time

_user32 = ctypes.windll.user32

_VK_MAP = {
    "right ctrl":  0xA3, "left ctrl":  0xA2,
    "right alt":   0xA5, "left alt":   0xA4,
    "right shift": 0xA1, "left shift": 0xA0,
    "insert": 0x2D, "delete": 0x2E, "pause": 0x13,
    "f1":  0x70, "f2":  0x71, "f3":  0x72, "f4":  0x73,
    "f5":  0x74, "f6":  0x75, "f7":  0x76, "f8":  0x77,
    "f9":  0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B,
}

_press_cb   = None
_release_cb = None
_stop_flag  = threading.Event()
_thread     = None


def _vk(name: str) -> int:
    return _VK_MAP.get(name.strip().lower(), 0xA3)


def _poll(vk: int):
    pressed = False
    print(f"[hotkey] 輪詢執行中 vk=0x{vk:02X}，請按 Right Ctrl 測試")
    while not _stop_flag.is_set():
        down = bool(_user32.GetAsyncKeyState(vk) & 0x8000)
        if down and not pressed:
            pressed = True
            print("[hotkey] 偵測到按下")
            if _press_cb:
                threading.Thread(target=_press_cb, daemon=True).start()
        elif not down and pressed:
            pressed = False
            print("[hotkey] 偵測到放開")
            if _release_cb:
                threading.Thread(target=_release_cb, daemon=True).start()
        time.sleep(0.02)
    print("[hotkey] 輪詢結束")


def register(hotkey_name: str, on_press, on_release) -> bool:
    global _press_cb, _release_cb, _thread
    _press_cb   = on_press
    _release_cb = on_release
    _stop_flag.clear()
    vk = _vk(hotkey_name)
    _thread = threading.Thread(target=_poll, args=(vk,), daemon=True, name="hotkey-poll")
    _thread.start()
    time.sleep(0.1)  # 確保執行緒已啟動
    print(f"[hotkey] 已綁定：{hotkey_name}")
    return True


def unregister():
    _stop_flag.set()
