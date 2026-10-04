"""CPU background removal; independent of the UI."""
import os
import sys
import tempfile
from pathlib import Path
from PIL import Image, ImageOps

MODEL = "u2net"


def load_image(path):
    with Image.open(path) as image:
        return ImageOps.exif_transpose(image).convert("RGBA")


def save_png(image, destination):
    """Replace only after the complete PNG is written successfully."""
    destination = Path(destination)
    if destination.suffix.lower() != ".png":
        raise ValueError("Çıktı dosyasının uzantısı .png olmalı.")
    fd, temporary = tempfile.mkstemp(suffix=".png", dir=destination.parent)
    os.close(fd)
    try:
        image.save(temporary, format="PNG")
        os.replace(temporary, destination)
    finally:
        Path(temporary).unlink(missing_ok=True)


class Processor:
    def __init__(self):
        self.session = None

    def prepare(self):
        if self.session is None:
            os.environ.setdefault("OMP_NUM_THREADS", str(min(os.cpu_count() or 1, 4)))
            if getattr(sys, "frozen", False):
                model_path = Path(sys._MEIPASS) / "models" / f"{MODEL}.onnx"
                if not model_path.is_file():
                    raise FileNotFoundError("Model eksik. NexaEdit klasörünün tamamını kopyalayın.")
                # Bypass rembg's download_models() — it uses pooch+tqdm which
                # crash when sys.stderr is None (PyInstaller console=False).
                # Load the bundled ONNX model directly via onnxruntime instead.
                import onnxruntime as ort
                from rembg.sessions.u2net import U2netSession
                providers = ["CPUExecutionProvider"]
                sess_opts = ort.SessionOptions()
                session = object.__new__(U2netSession)
                session.model_name = MODEL
                session.inner_session = ort.InferenceSession(
                    str(model_path), sess_options=sess_opts, providers=providers
                )
                self.session = session
            else:
                directory = Path(__file__).resolve().parent / "models"
                if (directory / f"{MODEL}.onnx").is_file():
                    os.environ["U2NET_HOME"] = str(directory)
                from rembg import new_session
                self.session = new_session(MODEL, providers=["CPUExecutionProvider"])
        return self.session

    def remove(self, image):
        from rembg import remove
        return remove(image, session=self.prepare()).convert("RGBA")
