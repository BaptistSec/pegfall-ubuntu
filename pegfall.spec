import glob
import os
block_cipher = None
a = Analysis(['run_pegfall.py'], pathex=[], binaries=[], datas=[('pegfall/assets', 'pegfall/assets')], hiddenimports=[], hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=[], win_no_prefer_redirects=False, cipher=block_cipher, noarchive=False)
a.datas = [d for d in a.datas if 'freesansbold' not in d[0].lower()]
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz, a.scripts, a.binaries, a.zipfiles, a.datas, [], name='pegfall', bootloader_ignore_signals=False, strip=False, upx=False, upx_exclude=[], runtime_tmpdir=None, console=False, disable_windowed_traceback=False, argv_emulation=False, target_arch=None, codesign_identity=None, entitlements_file=None)
