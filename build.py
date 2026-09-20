"""Build and test on the target operating system: python build.py."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    if sys.version_info[:2] != (3, 14):
        raise SystemExit("Bu proje Python 3.14 x64 ile derlenir.")
    import tkinter
    import customtkinter
    from rembg.sessions.u2net import U2netSession
    models = ROOT / "models"
    models.mkdir(exist_ok=True)
    os.environ["U2NET_HOME"] = str(models)
    print("Model indiriliyor ve sağlama toplamı doğrulanıyor…", flush=True)
    U2netSession.download_models()
    subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", str(ROOT / "NexaEdit.spec")], cwd=ROOT, check=True)
    binary = ROOT / "dist" / "NexaEdit" / ("NexaEdit.exe" if os.name == "nt" else "NexaEdit")
    subprocess.run([str(binary), "--self-test"], cwd=ROOT, check=True)
    subprocess.run([str(binary), "--smoke-gui"], cwd=ROOT, check=True)
    archive = shutil.make_archive(str(ROOT / "dist" / f"NexaEdit-{sys.platform}"), "zip", ROOT / "dist", "NexaEdit")
    print(f"Hazır: {binary}\nDağıtım: {archive}")


if __name__ == "__main__":
    main()
