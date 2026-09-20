from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

root = Path(SPECPATH)
model = root / 'models' / 'u2net.onnx'
if not model.is_file():
    raise SystemExit('Önce python build.py çalıştırın: model eksik.')
a = Analysis(
    [str(root / 'main.py')],
    pathex=[str(root)],
    datas=[(str(model), 'models'), (str(root / 'icon.svg'), '.'), (str(root / 'icon.png'), '.')] + collect_data_files('customtkinter') + copy_metadata('rembg'),
    hiddenimports=collect_submodules('rembg.sessions') + collect_submodules('scipy'),
    excludes=['kivy', 'torch', 'tensorflow', 'IPython', 'pytest'],
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='NexaEdit', icon=str(root / 'icon.ico'),
          console=False, debug=False, strip=False, upx=False)
coll = COLLECT(exe, a.binaries, a.datas, name='NexaEdit', strip=False, upx=False)
