import PyInstaller.__main__

PyInstaller.__main__.run([
    'jarvis.py',
    '--onefile',
    '--name=Jarvis',
    '--icon=NONE',
    '--noconsole'
])
