import ctypes, time

user32 = ctypes.windll.user32

KEYS = {
    "Right Ctrl":  0xA3,
    "Right Alt":   0xA5,
    "Right Shift": 0xA1,
    "F8":          0x77,
}

print("=== 按鍵偵測測試 ===")
print("請在 10 秒內按以下任一鍵：Right Ctrl、Right Alt、Right Shift、F8")
print("（按完可以繼續按其他鍵）\n")

detected = set()
start = time.time()

while time.time() - start < 10:
    for name, vk in KEYS.items():
        if user32.GetAsyncKeyState(vk) & 0x8000:
            if name not in detected:
                detected.add(name)
                print(f"  ✓ 偵測到：{name}")
    time.sleep(0.02)

print()
if detected:
    print(f"成功偵測到：{', '.join(detected)}")
else:
    print("【沒有偵測到任何按鍵】— GetAsyncKeyState 可能受到限制")
