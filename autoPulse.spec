# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Collect matplotlib data (styles, fonts, etc.)
matplotlib_datas = collect_data_files('matplotlib')
datas = matplotlib_datas + [
    ('C:\\Users\\gslam\\Dropbox\\SlamaTech\\Consulting\\AUTO Programs Python\\AutoOutput\\Source\\autoOutput\\oscilloscope.ico', '.')
]

a = Analysis(
    ['autoPulse.py'],  # Your main script
    pathex=[],
    binaries=[
        ('C:\\Users\\gslam\\Dropbox\\SlamaTech\\Consulting\\AUTO Programs Python\\AutoOutput\\Source\\autoOutput\\.venv\\Lib\\site-packages\\pyodbc.pyd', '.'),
        ('C:\\Users\\gslam\\AppData\\Local\\Programs\\Python\\Python312\\python312.dll', '.')
    ],
    datas = datas,
    hiddenimports=[
        'pyodbc',
        'win32com',
        'win32com.client',
        'matplotlib',
        'matplotlib.pyplot',
        'matplotlib.backends.backend_tkagg'
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='autoOutput',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True  # Set to False if you're using a Tkinter GUI only
    # icon='C:\\Users\\gslam\\Dropbox\\SlamaTech\\Consulting\\AUTO Programs Python\\AutoPulseInductance\\Source\\oscilloscope.ico'
)

