import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tempfile, os, time

SAMPLE_RATE = 16000
DURATION = 4  # 秒

print("=== 麥克風測試 ===")
print(f"錄音 {DURATION} 秒，請開口說話...\n")

# 列出可用麥克風
print("【可用錄音裝置】")
devices = sd.query_devices()
for i, d in enumerate(devices):
    if d['max_input_channels'] > 0:
        print(f"  [{i}] {d['name']}")

print()
time.sleep(1)
print("開始錄音 ▶")
audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE,
               channels=1, dtype='int16')
for i in range(DURATION, 0, -1):
    print(f"  剩餘 {i} 秒...", end='\r')
    time.sleep(1)
sd.wait()
print("錄音完成 ✓          ")

# 檢查音量
volume = np.abs(audio).mean()
print(f"平均音量：{volume:.1f}  (>100 代表有收到聲音)")

if volume < 10:
    print("⚠ 音量太低，麥克風可能沒有正常收音")
else:
    print("✓ 麥克風正常收音！")

# 儲存並送 Groq 辨識
print("\n送出 Groq Whisper 辨識中...")
tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
wav.write(tmp.name, SAMPLE_RATE, audio)

try:
    import config
    from groq import Groq
    client = Groq(api_key=config.GROQ_API_KEY)
    with open(tmp.name, "rb") as f:
        result = client.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file=("audio.wav", f, "audio/wav"),
            language="zh",
            response_format="text",
        )
    text = result if isinstance(result, str) else result.text
    print(f"\n【辨識結果】\n  {text.strip() or '（無法辨識，請確認說話夠清晰）'}")
except Exception as e:
    print(f"辨識失敗：{e}")
finally:
    os.unlink(tmp.name)

print("\n測試完成。")
