"""CPU background removal; independent of the UI."""
import os
import sys
import tempfile
import warnings
from pathlib import Path
from PIL import Image, ImageOps

MODEL = "u2net"
MAX_WIDTH, MAX_HEIGHT = 3840, 2160
Image.MAX_IMAGE_PIXELS = MAX_WIDTH * MAX_HEIGHT


def load_image(path):
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(path) as image:
            if image.width > MAX_WIDTH or image.height > MAX_HEIGHT:
                raise ValueError("Görsel en fazla 3840 × 2160 piksel (4K UHD) olabilir.")
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
            if getattr(sys, "frozen", False):
                directory = Path(sys._MEIPASS) / "models"
                if not (directory / f"{MODEL}.onnx").is_file():
                    raise FileNotFoundError("Model eksik. NexaEdit klasörünün tamamını kopyalayın.")
                os.environ["U2NET_HOME"] = str(directory)
            else:
                directory = Path(__file__).resolve().parent / "models"
                if (directory / f"{MODEL}.onnx").is_file():
                    os.environ["U2NET_HOME"] = str(directory)
            os.environ.setdefault("OMP_NUM_THREADS", str(min(os.cpu_count() or 1, 4)))
            from rembg import new_session
            self.session = new_session(MODEL, providers=["CPUExecutionProvider"])
        return self.session

    def remove(self, image):
        from rembg import remove
        return remove(image, session=self.prepare()).convert("RGBA")
