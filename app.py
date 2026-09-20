"""Minimal CustomTkinter desktop interface."""
import queue
import threading
import subprocess
import shutil
import sys
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk
from processor import Processor, load_image, save_png


class App(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        super().__init__()
        self.title("NexaEdit")
        icon_path = Path(__file__).resolve().parent / "icon.png"
        if icon_path.is_file():
            self.iconphoto(True, ImageTk.PhotoImage(Image.open(icon_path)))
        self.geometry("940x660")
        self.minsize(700, 500)
        self.configure(fg_color="#101114")
        self.processor = Processor()
        self.events = queue.Queue()
        self.source = self.result = self.source_path = None
        self.busy = False
        self.preview_images = []
        self.resize_timer = None
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=28, pady=(24, 18))
        ctk.CTkLabel(header, text="NexaEdit", font=ctk.CTkFont(size=28, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(header, text="Arka planı kaldır. Sadece görselin kalsın.", text_color="#9ca3af").pack(anchor="w")
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=1, column=0, sticky="ew", padx=28)
        self.open_button = ctk.CTkButton(toolbar, text="Görsel seç", command=self.open_image, height=38)
        self.remove_button = ctk.CTkButton(toolbar, text="Arka planı kaldır", command=self.remove_background, height=38)
        self.save_button = ctk.CTkButton(toolbar, text="PNG kaydet", command=self.save_image, height=38, fg_color="#30343d", hover_color="#424854")
        self.clear_button = ctk.CTkButton(toolbar, text="Temizle", command=self.clear_image, height=38, fg_color="#30343d", hover_color="#424854")
        for button in (self.open_button, self.remove_button, self.save_button, self.clear_button):
            button.pack(side="left", padx=(0, 10))
        self.previews = ctk.CTkFrame(self, fg_color="transparent")
        self.previews.grid(row=2, column=0, sticky="nsew", padx=28, pady=22)
        self.previews.grid_columnconfigure((0, 1), weight=1, uniform="preview")
        self.previews.grid_rowconfigure(0, weight=1)
        self.panels = []
        for column, title in enumerate(("ORİJİNAL", "SONUÇ")):
            box = ctk.CTkFrame(self.previews, fg_color="#1b1d22", corner_radius=12)
            box.grid(row=0, column=column, sticky="nsew", padx=(0, 7) if column == 0 else (7, 0))
            box.grid_columnconfigure(0, weight=1)
            box.grid_rowconfigure(1, weight=1)
            box.grid_propagate(False)
            ctk.CTkLabel(box, text=title, font=ctk.CTkFont(size=11, weight="bold"), text_color="#9ca3af").grid(row=0, column=0, sticky="w", padx=16, pady=(12, 0))
            panel = ctk.CTkLabel(box, text="Henüz görsel yok", text_color="#727985")
            panel.grid(row=1, column=0, sticky="nsew", padx=12, pady=12)
            self.panels.append(panel)
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", padx=28, pady=(0, 22))
        self.progress = ctk.CTkProgressBar(footer, height=3, mode="indeterminate")
        self.progress.pack(fill="x", pady=(0, 10))
        self.progress.set(0)
        self.status = ctk.CTkLabel(footer, text="Bir görsel seçerek başlayın. Görselleriniz bilgisayarınızda kalır.", anchor="w", text_color="#9ca3af", wraplength=820)
        self.status.pack(fill="x")
        self.previews.bind("<Configure>", self.schedule_redraw)
        self.refresh()
        self.poll_timer = self.after(100, self.poll)

    def refresh(self):
        self.open_button.configure(state="disabled" if self.busy else "normal")
        self.remove_button.configure(state="normal" if not self.busy and self.source is not None else "disabled")
        self.save_button.configure(state="normal" if not self.busy and self.result is not None else "disabled")
        self.clear_button.configure(state="disabled" if self.busy or (self.source is None and self.result is None) else "normal")
        if self.busy:
            self.progress.start()
        else:
            self.progress.stop()
            self.progress.set(0)

    def start_job(self, kind, operation):
        if self.busy:
            return
        self.busy = True
        self.refresh()
        def worker():
            try:
                self.events.put((kind, operation()))
            except Exception as error:
                self.events.put(("error", str(error) or type(error).__name__))
        threading.Thread(target=worker, daemon=True).start()

    def open_image(self):
        path = self.system_file_picker()
        if path:
            self.status.configure(text="Görsel açılıyor…")
            self.start_job("loaded", lambda: (Path(path), load_image(path)))

    def system_file_picker(self):
        """Use the desktop's modern GTK/KDE picker before Tk's legacy fallback."""
        if sys.platform.startswith("linux"):
            image_filter = "*.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff"
            if shutil.which("zenity"):
                result = subprocess.run(
                    ["zenity", "--file-selection", "--title=Görsel seç", "--file-filter=Görseller | " + image_filter],
                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
                )
                return result.stdout.strip() if result.returncode == 0 else ""
            if shutil.which("kdialog"):
                result = subprocess.run(
                    ["kdialog", "--getopenfilename", str(Path.home()), image_filter, "Görsel seç"],
                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True,
                )
                return result.stdout.strip() if result.returncode == 0 else ""
        return filedialog.askopenfilename(
            parent=self,
            title="Görsel seç",
            filetypes=[("Görseller", "*.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff"), ("Tüm dosyalar", "*")],
        )

    def remove_background(self):
        if self.processor.session is None:
            self.status.configure(text="Model hazırlanıyor; ilk kullanımda U²-Net indiriliyor, ardından CPU işlemesi başlayacak…")
        else:
            self.status.configure(text="CPU üzerinde arka plan kaldırılıyor…")
        self.start_job("removed", lambda: self.processor.remove(self.source))

    def clear_image(self):
        if self.busy:
            return
        self.source = None
        self.result = None
        self.source_path = None
        self.status.configure(text="Ekran temizlendi. Yeni bir görsel seçebilirsiniz.")
        self.refresh()
        self.redraw()

    def save_image(self):
        path = self.system_save_picker(self.source_path.stem + "_nexa.png")
        if path:
            path = str(self.next_available_path(Path(path)))
            if Path(path).resolve() == self.source_path.resolve():
                self.show_error("Farklı dosya seçin", "Orijinal görselin üzerine kaydedemezsiniz.")
                return
            self.status.configure(text="Kaydediliyor…")
            self.start_job("saved", lambda: (save_png(self.result, path), path)[1])

    @staticmethod
    def next_available_path(path):
        """Return path, or path with a numbered suffix when it already exists."""
        if not path.exists():
            return path
        number = 1
        while True:
            candidate = path.with_name(f"{path.stem} ({number}){path.suffix}")
            if not candidate.exists():
                return candidate
            number += 1

    def system_save_picker(self, filename):
        if sys.platform.startswith("linux"):
            if shutil.which("zenity"):
                result = subprocess.run(["zenity", "--file-selection", "--save", "--confirm-overwrite", "--title=Şeffaf PNG kaydet", f"--filename={filename}", "--file-filter=PNG | *.png"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
                return result.stdout.strip() if result.returncode == 0 else ""
            if shutil.which("kdialog"):
                result = subprocess.run(["kdialog", "--getsavefilename", str(Path.home() / filename), "*.png", "Şeffaf PNG kaydet"], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
                return result.stdout.strip() if result.returncode == 0 else ""
        return filedialog.asksaveasfilename(parent=self, title="Şeffaf PNG kaydet", initialfile=filename, defaultextension=".png", filetypes=[("PNG", "*.png")])

    def poll(self):
        try:
            kind, value = self.events.get_nowait()
        except queue.Empty:
            pass
        else:
            self.busy = False
            if kind == "error":
                self.status.configure(text="İşlem başarısız oldu. Ayrıntı için hata penceresini kontrol edin.")
                self.show_error("İşlem tamamlanamadı", value)
            elif kind == "loaded":
                self.source_path, self.source = value
                self.result = None
                self.status.configure(text=f"{self.source_path.name} · {self.source.width} × {self.source.height}")
            elif kind == "removed":
                self.result = value
                self.status.configure(text="Hazır. Sonucu şeffaf PNG olarak kaydedebilirsiniz.")
            elif kind == "saved":
                self.status.configure(text=f"Kaydedildi: {value}")
            self.refresh()
            self.redraw()
        self.poll_timer = self.after(100, self.poll)

    def schedule_redraw(self, event=None):
        if self.resize_timer is not None:
            self.after_cancel(self.resize_timer)
        self.resize_timer = self.after(100, self.redraw)

    def redraw(self):
        self.resize_timer = None
        images = []
        for panel, source in zip(self.panels, (self.source, self.result)):
            if source is None:
                panel.configure(image=None, text="Henüz görsel yok")
                continue
            preview = source.copy()
            preview.thumbnail((max(1, panel.winfo_width() - 8), max(1, panel.winfo_height() - 8)), Image.Resampling.LANCZOS)
            background = Image.new("RGBA", preview.size, "#292c33")
            draw = ImageDraw.Draw(background)
            for y in range(0, preview.height, 12):
                for x in range(0, preview.width, 12):
                    if (x // 12 + y // 12) % 2:
                        draw.rectangle((x, y, x + 11, y + 11), fill="#363a43")
            background.alpha_composite(preview)
            image = ctk.CTkImage(light_image=background, dark_image=background, size=preview.size)
            images.append(image)
            panel.configure(image=image, text="")
        self.preview_images = images

    def show_error(self, title, message):
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("430x220")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        ctk.CTkLabel(dialog, text="!", text_color="#ff6b6b", font=ctk.CTkFont(size=34, weight="bold")).pack(pady=(22, 0))
        ctk.CTkLabel(dialog, text=title, font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(2, 6))
        ctk.CTkLabel(dialog, text=message, text_color="#b9bec8", wraplength=370).pack(padx=24)
        ctk.CTkButton(dialog, text="Tamam", width=110, command=dialog.destroy).pack(pady=20)

    def destroy(self):
        if self.resize_timer is not None:
            self.after_cancel(self.resize_timer)
        self.after_cancel(self.poll_timer)
        self.progress.stop()
        super().destroy()
