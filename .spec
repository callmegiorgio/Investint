# -*- mode: python ; coding: utf-8 -*-
import os

def is_extension(filepath: str, ext: str) -> bool:
    """
    Returns whether `ext` is the extension of `filepath`.
    """

    return os.path.splitext(filepath)[1] == ext

def extension_count(dirpath: str, ext: str) -> int:
    """
    Checks whether the directory `dirpath` has at least one file with extension `ext`.

    Returns 0 if `dirpath` doesn't exist or there is no such file with that extension.
    Otherwise, returns the number of files with that extension.
    """

    try:
        return sum(1 for fp in os.listdir(dirpath) if is_extension(fp, ext))
    except FileNotFoundError:
        return 0

block_cipher = None

datas = []

qm_count = extension_count('data/translations', '.qm')

if qm_count != 0:
    datas.append(('data/translations/*.qm', 'translations'))

print('USER INFO: translations found ==', qm_count)

a = Analysis(
    ['build/lib/investint/__main__.py'],
    pathex=[],
    binaries=[],
    datas=datas,
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
