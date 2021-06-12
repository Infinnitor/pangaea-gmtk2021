# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['game.py'],
             pathex=['D:\\Librarys\\Documents\\Sketchbook\\Github\\question\\gamists-gmtk-2021'],
             binaries=[],
             datas=[('data/sprites/countries/*','data/sprites/countries'),('data/sprites/ICONS/*','data/sprites/ICONS '),('data/sprites/VNUI/*','data/sprites/VNUI ')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='game',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
