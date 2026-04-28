import threading
from PIL import Image, ImageDraw
import pystray


def _make_icon(color: str) -> Image.Image:
    img = Image.new("RGB", (64, 64), color="white")
    draw = ImageDraw.Draw(img)
    draw.ellipse([8, 8, 56, 56], fill=color)
    return img


ICON_IDLE = _make_icon("#4A90D9")
ICON_RECORDING = _make_icon("#E74C3C")
ICON_PROCESSING = _make_icon("#F39C12")


class TrayApp:
    def __init__(self, on_quit):
        self._on_quit = on_quit
        self._icon = pystray.Icon(
            name="voicetype",
            icon=ICON_IDLE,
            title="VoiceType — 待機中",
            menu=pystray.Menu(
                pystray.MenuItem("VoiceType", None, enabled=False),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("結束", self._quit),
            ),
        )

    def run(self):
        self._icon.run()

    def run_detached(self):
        t = threading.Thread(target=self.run, daemon=True)
        t.start()

    def set_idle(self):
        self._icon.icon = ICON_IDLE
        self._icon.title = "VoiceType — 待機中"

    def set_recording(self):
        self._icon.icon = ICON_RECORDING
        self._icon.title = "VoiceType — 錄音中..."

    def set_processing(self):
        self._icon.icon = ICON_PROCESSING
        self._icon.title = "VoiceType — 辨識中..."

    def _quit(self, icon, item):
        icon.stop()
        self._on_quit()
