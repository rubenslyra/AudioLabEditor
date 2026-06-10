import importlib
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image, ImageTk

from application.bootstrap import validate_startup
from application.capture_media_use_case import CaptureMediaUseCase
from application.separate_audio_use_case import SeparateAudioUseCase
from infrastructure.demucs_adapter import DemucsSubprocessAdapter
from infrastructure.downloader_adapter import YtDlpAdapter
from infrastructure.ffmpeg_adapter import FFmpegAdapter
from presentation.splash import SplashScreen
from presentation.tabs.capture_tab import CaptureTab
from presentation.tabs.stem_tab import StemTab
from presentation.tabs.trim_tab import TrimTab
from presentation.tabs.video_editor_tab import VideoEditorTab


def show_startup_error(message: str) -> None:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Dependencias ausentes", message)
    root.destroy()


def show_startup_warning(message: str) -> None:
    root = tk.Tk()
    root.withdraw()
    messagebox.showwarning("Dependencias opcionais ausentes", message)
    root.destroy()


def set_window_icon(app):
    icon_png = Path(__file__).resolve().parent / "assets" / "logo.png"
    if not icon_png.exists():
        return
    try:
        img = Image.open(icon_png)
        photos = []
        for size in [16, 22, 32, 48, 64, 128]:
            photos.append(ImageTk.PhotoImage(img.resize((size, size), Image.LANCZOS)))
        app._icon_photos = photos
        app.iconphoto(True, *photos)
    except Exception:
        pass


def build_window(app, splash=None):

    def step(value, msg):
        if splash:
            splash.set_progress(value, msg)

    step(0.20, "Criando adaptadores...")
    downloader = YtDlpAdapter()
    ffmpeg = FFmpegAdapter()
    demucs_available = importlib.util.find_spec("demucs") is not None
    demucs = DemucsSubprocessAdapter() if demucs_available else None

    capture_use_case = CaptureMediaUseCase(downloader=downloader, ffmpeg=ffmpeg)
    separate_use_case = SeparateAudioUseCase(demucs=demucs) if demucs_available else None

    step(0.35, "Montando interface...")

    if separate_use_case is not None:
        tab_values = ["Captura", "Audio", "Stems", "Video"]
        tab_builders = {
            "Captura": lambda parent: CaptureTab(parent, app, capture_use_case),
            "Audio": lambda parent: TrimTab(parent, app),
            "Stems": lambda parent: StemTab(parent, app, separate_use_case),
            "Video": lambda parent: VideoEditorTab(parent, app),
        }
    else:
        tab_values = ["Captura", "Audio", "Video"]
        tab_builders = {
            "Captura": lambda parent: CaptureTab(parent, app, capture_use_case),
            "Audio": lambda parent: TrimTab(parent, app),
            "Video": lambda parent: VideoEditorTab(parent, app),
        }

    tab_switcher = ctk.CTkSegmentedButton(app, values=tab_values)
    tab_switcher.pack(fill="x", padx=10, pady=(10, 0))

    tab_container = ctk.CTkFrame(app)
    tab_container.pack(fill="both", expand=True, padx=10, pady=(5, 10))

    tab_frames: dict[str, ctk.CTkFrame] = {}

    def build_tab(label):
        frame = ctk.CTkFrame(tab_container)
        tab_builders[label](frame)
        tab_frames[label] = frame
        return frame

    def show_tab(label):
        for f in tab_frames.values():
            f.pack_forget()
        if label not in tab_frames:
            step(0.99, f"Carregando aba {label}...")
            build_tab(label)
        tab_frames[label].pack(fill="both", expand=True)

    tab_switcher.configure(command=show_tab)
    build_tab("Captura")
    show_tab("Captura")
    step(1.0, "Pronto!")


def main() -> int:
    app = ctk.CTk()
    app.title("AudioLabEditor")

    # suppress Tcl errors from after-callbacks that reference destroyed widgets
    app.tk.call("proc", "bgerror", "msg", "return")

    set_window_icon(app)

    error_message, warning_message = validate_startup()
    if error_message:
        app.destroy()
        show_startup_error(error_message)
        return 2
    if warning_message:
        show_startup_warning(warning_message)

    app.deiconify()
    app.geometry("1120x720")
    app.minsize(960, 640)
    app.update()

    splash = SplashScreen(app)
    splash.set_progress(0.15, "Iniciando...")

    build_window(app, splash)

    splash.close()
    try:
        app.tk.call("wm", "wmclass", app._w, "AudioLabEditor", "AudioLabEditor")
    except Exception:
        pass
    app.update()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
