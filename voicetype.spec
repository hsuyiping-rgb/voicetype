# -*- mode: python ; coding: utf-8 -*-
import os

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('web/templates', 'web/templates'),
        ('web/static',    'web/static'),
        (r'C:\Users\vm\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\opencc\config',     'opencc/config'),
        (r'C:\Users\vm\AppData\Local\Python\pythoncore-3.14-64\Lib\site-packages\opencc\dictionary', 'opencc/dictionary'),
    ],
    hiddenimports=[
        'groq', 'openai', 'flask', 'sounddevice', 'scipy',
        'scipy.io.wavfile', 'pystray', 'PIL', 'PIL.Image', 'PIL.ImageDraw',
        'keyboard', 'pyperclip', 'engineio', 'pkg_resources.py2_warn',
        'pystray._win32', 'opencc',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VoiceType',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
