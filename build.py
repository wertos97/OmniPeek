import PyInstaller.__main__
import os

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

PyInstaller.__main__.run([
    os.path.join(current_dir, 'main.py'),
    '--name=OmniPeek',
    '--onefile',
    '--windowed',
    '--clean',
    '--noconfirm',
    f'--icon={os.path.join(current_dir, "icon.ico")}',
])