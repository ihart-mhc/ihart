# -*- mode: python -*-

# Example: added_files = [ ('foo.jpg', 'foo.jpg', 'DATA') ]
added_files = []

block_cipher = None

a = Analysis(['sample_app.py'],
             pathex=['.', '../../library/python/'],
             binaries=None,
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

for entry in added_files:
    a.datas.append(entry)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='sample_app',
          debug=False,
          strip=False,
          upx=True,
          console=False)

app = BUNDLE(exe,
             name='sample_app.app',
             icon=None,
             bundle_identifier=None)
