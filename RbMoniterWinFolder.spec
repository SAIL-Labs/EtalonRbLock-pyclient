# -*- mode: python -*-

block_cipher = None

binfolder='C:\\Users\\cbetters\\Anaconda3\\envs\\qt5dev\\Library\\bin\\'

a = Analysis(['RbMoniter.py'],
             pathex=['C:\\Users\\cbetters\\Dropbox\\github\\postdoc_code\\UDPreceiverRedpitaya\\python'],
             binaries=[(binfolder+'mkl_avx2.dll','.'),(binfolder+'mkl_def.dll','.')],
             datas=[('RbMoniter.ui', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='RbMoniter',
          debug=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='RbMoniter')
