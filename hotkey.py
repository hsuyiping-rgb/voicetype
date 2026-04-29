"""
用 Windows RegisterHotKey API 註冊全域快捷鍵。
這個方法不需要管理員權限，也不會被 UAC 層級阻擋。
"""
import ctypes
import threading
import queue

WM_HOTKEY   = 0x0312
MOD_NONE    = 0x0000
MOD_ALT     = 0x0001
MOD_CTRL    = 0x0002
MOD_SHIFT   = 0x0004
MOD_WIN     = 0x0008
MOD_NOREPEAT = 0x4000

# 常用鍵名 → Virtual Key Code
_VK_MAP = {
    "right alt": 0xA5,  "left alt": 0xA4,
    "right ctrl": 0xA3, "left ctrl": 0xA2,
    "right shift": 0xA1,"left shift": 0xA0,
    "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73,
    "f5": 0x74, "f6": 0x75, "f7": 0x76, "f8": 0x77,
    "f9": 0x78, "f10": 0x79,"f11": 0x7A,"f12": 0x7B,
    "caps lock": 0x14, "scroll lock": 0x91, "pause": 0x13,
}

HOTKEY_ID_PRESS   = 1
HOTKEY_ID_RELEASE = 2  # 放開無法用 RegisterHotKey，用輪詢

_press_cb   = None
_release_cb = None
_thread     = None
_stop       = False
_vk         = 0xA5  # 預設 Right Alt


def _vk_from_name(name: str) -> int:
    name = name.strip().lower()
    if name in _VK_MAP:
        return _VK_MAP[name]
    if len(name) == 1:
        return ctypes.windll.user32.VkKeyScanW(ord(name)) & 0xFF
    return 0xA5  # fallback: Right Alt


def _message_loop(vk):
    """主訊息迴圈，監聽 WM_HOTKEY 與按鍵放開。"""
    global _stop
    user32 = ctypes.windll.user32

    # 註冊按下事件
    user32.RegisterHotKey(None, HOTKEY_ID_PRESS, MOD_NOREPEAT, vk)

    msg = ctypes.wintypes.MSG()
    pressed = False

    while not _stop:
        # PeekMessage 非阻塞
        if user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 1):
            if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID_PRESS:
                if not pressed:
                    pressed = True
                    if _press_cb:
                        threading.Thread(target=_press_cb, daemon=True).start()
        else:
            # 偵測放開（輪詢 GetAsyncKeyState）
            state = user32.GetAsyncKeyState(vk)
            if pressed and not (state & 0x8000):
                pressed = False
                if _release_cb:
                    threading.Thread(target=_release_cb, daemon=True).start()
            ctypes.windll.kernel32.Sleep(10)

    user32.UnregisterHotKey(None, HOTKEY_ID_PRESS)


def register(hotkey_name: str, on_press, on_release):
    global _press_cb, _release_cb, _vk, _thread, _stop
    _press_cb   = on_press
    _release_cb = on_release
    _vk = _vk_from_name(hotkey_name)
    _stop = False
    _thread = threading.Thread(target=_message_loop, args=(_vk,), daemon=True)
    _thread.start()


def unregister():
    global _stop
    _stop = True
