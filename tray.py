import threading
from PIL import Image, ImageDraw
import pystray


def _make_icon(color: str) -> Image.Image:
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # 底色圓形
    draw.ellipse([4, 4, 60, 60], fill=color)
    # 麥克風主體（白色圓角矩形）
    draw.rounded_rectangle([24, 10, 40, 36], radius=8, fill="white")
    # 麥克風弧形外殼
    draw.arc([17, 22, 47, 46], start=0, end=180, fill="white", width=4)
    # 麥克風支架（直線）
    draw.line([32, 46, 32, 54], fill="white", width=4)
    # 底座橫線
    draw.line([24, 54, 40, 54], fill="white", width=4)
    return img


ICON_IDLE       = _make_icon("#4A90D9")
ICON_RECORDING  = _make_icon("#E74C3C")
ICON_PROCESSING = _make_icon("#F39C12")


class TrayApp:
    def __init__(self, on_quit, on_open_settings):
        self._on_quit = on_quit
        self._on_open_settings = on_open_settings
        self._icon = pystray.Icon(
            name="voicetype",
            icon=ICON_IDLE,
            title="VoiceType — 待機中",
            menu=pystray.Menu(
                pystray.MenuItem("VoiceType", None, enabled=False),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("⚙ 開啟設定", self._open_settings),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("結束", self._quit),
            ),
        )

    def run(self):
        """主執行緒呼叫，blocking。"""
        self._icon.run()

    def run_detached(self):
        t = threading.Thread(target=self._icon.run, daemon=True)
        t.start()

    def set_idle(self):
        self._icon.icon = ICON_IDLE
        self._icon.title = "VoiceType — 待機中"

    def set_recording(self):
        self._icon.icon = ICON_RECORDING
        self._icon.title = "VoiceType — 錄音中…"

    def set_processing(self):
        self._icon.icon = ICON_PROCESSING
        self._icon.title = "VoiceType — 辨識中…"

    def _open_settings(self, icon, item):
        self._on_open_settings()

    def _quit(self, icon, item):
        icon.stop()
        self._on_quit()
