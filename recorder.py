import threading
import numpy as np
import sounddevice as sd
import scipy.io.wavfile as wav
import tempfile
import os
from config import SAMPLE_RATE, CHANNELS


class Recorder:
    def __init__(self):
        self._frames = []
        self._recording = False
        self._lock = threading.Lock()

    def start(self):
        with self._lock:
            self._frames = []
            self._recording = True

        def callback(indata, frames, time, status):
            if self._recording:
                self._frames.append(indata.copy())

        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype="int16",
            callback=callback,
        )
        self._stream.start()

    def stop(self) -> str | None:
        with self._lock:
            self._recording = False

        self._stream.stop()
        self._stream.close()

        if not self._frames:
            return None

        audio = np.concatenate(self._frames, axis=0)

        # 太短的錄音（< 0.3 秒）忽略
        if len(audio) < SAMPLE_RATE * 0.3:
            return None

        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        wav.write(tmp.name, SAMPLE_RATE, audio)
        return tmp.name
