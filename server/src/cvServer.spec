# -*- mode: python -*-

added_files = [ ('mainHelp.png', 'mainHelp.png', 'DATA'),
                ('startupHelp.png', 'startupHelp.png', 'DATA'),
                ('haarcascade_frontalface_alt.xml', 'haarcascade_frontalface_alt.xml', 'DATA')]

block_cipher = None


a = Analysis(['cvServer.py'],
             pathex=['C:\\Users\\Sarah\\Projects\\ihart\\server\\src'],
             binaries=None,
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

a.datas.append(added_files[0])
a.datas.append(added_files[1])
a.datas.append(added_files[2])

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='cvServer',
          debug=False,
          strip=False,
          upx=True,
          console=False )
