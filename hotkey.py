"""
全域快捷鍵：使用 keyboard 庫的低階 hook。
"""
import threading
import keyboard

_press_cb    = None
_release_cb  = None
_current_key = None
_pressed     = False
_lock        = threading.Lock()


def register(hotkey_name: str, on_press, on_release) -> bool:
    global _press_cb, _release_cb, _current_key, _pressed
    _press_cb    = on_press
    _release_cb  = on_release
    _current_key = hotkey_name.strip().lower()
    _pressed     = False

    try:
        keyboard.on_press_key(_current_key,   _handle_press,   suppress=False)
        keyboard.on_release_key(_current_key, _handle_release, suppress=False)
        print(f"[hotkey] 已綁定：{_current_key}")
        return True
    except Exception as e:
        print(f"[hotkey] 綁定失敗：{e}")
        return False


def _handle_press(e):
    global _pressed
    with _lock:
        if _pressed:
            return
        _pressed = True
    if _press_cb:
        threading.Thread(target=_press_cb, daemon=True).start()


def _handle_release(e):
    global _pressed
    with _lock:
        if not _pressed:
            return
        _pressed = False
    if _release_cb:
        threading.Thread(target=_release_cb, daemon=True).start()


def unregister():
    global _pressed
    _pressed = False
    try:
        keyboard.unhook_all()
    except Exception:
        pass
