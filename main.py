"""NexaEdit entry point. Heavy inference imports stay off the UI thread."""
import multiprocessing
import sys


def self_test():
    import tempfile
    from pathlib import Path
    from PIL import Image, ImageDraw
    from processor import Processor, load_image, save_png
    processor = Processor()
    source = Image.new("RGB", (128, 128), "white")
    ImageDraw.Draw(source).ellipse((24, 16, 104, 120), fill="red")
    result = processor.remove(source)
    assert result.mode == "RGBA" and result.size == source.size
    assert result.getchannel("A").getextrema()[0] < 255
    assert processor.session.inner_session.get_providers() == ["CPUExecutionProvider"]
    with tempfile.TemporaryDirectory() as directory:
        destination = Path(directory) / "sonuç.png"
        save_png(result, destination)
        assert load_image(destination).tobytes() == result.tobytes()
    if sys.stdout is not None:
        print("NexaEdit self-test OK: CPU model, inference, PNG")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    if "--self-test" in sys.argv:
        self_test()
    else:
        from app import App
        app = App()
        if "--smoke-gui" in sys.argv:
            app.after(1200, app.destroy)
        app.mainloop()
