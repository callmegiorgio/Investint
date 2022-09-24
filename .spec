# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['build/lib/investint/__main__.py'],
    pathex=[],
    binaries=[],
    datas=[('data/translations/*.qm', 'translations')],
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='Investint',
    debug=bool(__debug__),
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=bool(__debug__),
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

if bool(__debug__):
    dist_dir = 'debug'
else:
    dist_dir = 'release'

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=dist_dir,
)
