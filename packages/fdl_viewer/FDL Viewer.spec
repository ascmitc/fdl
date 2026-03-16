# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src/fdl_viewer/main.py'],
    pathex=[],
    binaries=[],
    datas=[('src/fdl_viewer/resources', 'resources')],
    hiddenimports=['PySide6.QtCore', 'PySide6.QtGui', 'PySide6.QtWidgets', 'numpy', 'numpy.core._methods', 'numpy.lib.format', 'OpenImageIO'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FDL Viewer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['src/fdl_viewer/resources/icons/fdl_viewer.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FDL Viewer',
)
app = BUNDLE(
    coll,
    name='FDL Viewer.app',
    icon='src/fdl_viewer/resources/icons/fdl_viewer.icns',
    bundle_identifier=None,
)
