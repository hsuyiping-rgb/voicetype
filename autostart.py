import sys
import os
import winreg

_KEY_PATH   = r"Software\Microsoft\Windows\CurrentVersion\Run"
_VALUE_NAME = "VoiceType"


def _exe_command() -> str:
    """回傳要寫入登錄的啟動指令。"""
    if getattr(sys, 'frozen', False):
        # 打包模式：直接執行 exe
        return f'"{sys.executable}"'
    else:
        # 開發模式：python main.py
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")
        return f'"{sys.executable}" "{script}"'


def is_enabled() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _KEY_PATH) as key:
            val, _ = winreg.QueryValueEx(key, _VALUE_NAME)
            return bool(val)
    except FileNotFoundError:
        return False


def enable():
    with winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, _KEY_PATH, 0, winreg.KEY_SET_VALUE
    ) as key:
        winreg.SetValueEx(key, _VALUE_NAME, 0, winreg.REG_SZ, _exe_command())


def disable():
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _KEY_PATH, 0, winreg.KEY_SET_VALUE
        ) as key:
            winreg.DeleteValue(key, _VALUE_NAME)
    except FileNotFoundError:
        pass
