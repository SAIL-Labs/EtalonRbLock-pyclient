# -*- mode: python -*-

block_cipher = None


a = Analysis(['RbMoniter.py'],
             pathex=['/Users/chrisbetters/Dropbox/github/postdoc_code/UDPreceiverRedpitaya/python'],
             binaries=None,
             datas=None,
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
          console=False )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='RbMoniter')
app = BUNDLE(coll,
             name='RbMoniter.app',
             icon=None,
             bundle_identifier=None)
