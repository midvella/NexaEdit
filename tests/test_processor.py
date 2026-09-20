import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from PIL import Image, UnidentifiedImageError
from processor import load_image, save_png


class ImageTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def test_png_preserves_pixels_and_alpha(self):
        image = Image.new("RGBA", (20, 12), (34, 56, 78, 90))
        path = self.root / "Türkçe görsel.png"
        save_png(image, path)
        result = load_image(path)
        self.assertEqual(result.tobytes(), image.tobytes())
        self.assertEqual(result.size, image.size)

    def test_failed_save_preserves_existing_file_and_cleans_temporary(self):
        path = self.root / "output.png"
        path.write_bytes(b"original")
        image = Image.new("RGBA", (2, 2))
        with patch.object(Image.Image, "save", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                save_png(image, path)
        self.assertEqual(path.read_bytes(), b"original")
        self.assertEqual(list(self.root.iterdir()), [path])

    def test_exif_orientation_is_applied(self):
        image = Image.new("RGB", (20, 10))
        exif = Image.Exif()
        exif[274] = 6
        path = self.root / "rotated.jpg"
        image.save(path, exif=exif)
        self.assertEqual(load_image(path).size, (10, 20))

    def test_bad_image_is_rejected(self):
        path = self.root / "bad.png"
        path.write_text("not an image")
        with self.assertRaises(UnidentifiedImageError):
            load_image(path)

    def test_non_png_destination_is_rejected(self):
        with self.assertRaises(ValueError):
            save_png(Image.new("RGBA", (2, 2)), self.root / "bad.jpg")

    def test_oversized_image_is_rejected(self):
        path = self.root / "big.png"
        Image.new("RGB", (11, 10)).save(path)
        with patch.object(Image, "MAX_IMAGE_PIXELS", 100):
            with self.assertRaises(Image.DecompressionBombWarning):
                load_image(path)


if __name__ == "__main__":
    unittest.main()
