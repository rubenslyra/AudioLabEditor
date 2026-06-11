import atexit
import signal
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image, ImageTk

from application.bootstrap import validate_startup
from infrastructure.ffmpeg_adapter import FFmpegAdapter
from presentation.splash import SplashScreen

_cleanup_hooks: list[callable] = []
_subprocesses: list[object] = []
_background_threads: list[threading.Thread] = []


def register_cleanup(fn: callable) -> callable:
    _cleanup_hooks.append(fn)
    return fn


def track_subprocess(proc: object) -> object:
    _subprocesses.append(proc)
    return proc


def track_thread(t: threading.Thread) -> threading.Thread:
    _background_threads.append(t)
    return t


def cleanup_resources():
    for fn in reversed(_cleanup_hooks):
        try:
            fn()
        except Exception:
            pass
    for proc in _subprocesses:
        try:
            if hasattr(proc, "poll") and proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=3)
        except Exception:
            pass
    for t in _background_threads:
        if t.is_alive():
            t.join(timeout=2)


atexit.register(cleanup_resources)


def _signal_handler(signum, frame):
    cleanup_resources()
    sys.exit(128 + signum)


signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)


def show_startup_error(message: str) -> None:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Dependencias ausentes", message)
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


_LIGHT_TABS = ["Captura", "Audio"]
_HEAVY_TABS = ["Stems", "Transcricao", "TTS", "Video"]


def build_window(app, splash=None):

    def step(value, msg):
        if splash:
            splash.set_progress(value, msg)

    _build_adapters(app, step)

    step(0.35, "Montando interface...")

    tab_values = _LIGHT_TABS + _HEAVY_TABS

    tab_switcher = ctk.CTkSegmentedButton(app, values=tab_values)
    tab_switcher.pack(fill="x", padx=10, pady=(10, 0))

    tab_container = ctk.CTkFrame(app)
    tab_container.pack(fill="both", expand=True, padx=10, pady=(5, 10))

    tab_frames: dict[str, ctk.CTkFrame] = {}
    tab_builders: dict[str, callable] = {}
    _tab_cache: dict[str, bool] = {}

    def show_tab(label):
        for f in tab_frames.values():
            f.pack_forget()

        if label in tab_frames:
            tab_frames[label].pack(fill="both", expand=True)
            return

        if label in _tab_cache:
            actual = ctk.CTkFrame(tab_container)
            try:
                tab_builders[label](actual)
            except Exception as exc:
                actual.destroy()
                error_frame = ctk.CTkFrame(tab_container)
                ctk.CTkLabel(
                    error_frame,
                    text=f"Erro ao carregar {label}: {exc}",
                    font=ctk.CTkFont(size=14),
                    text_color="red",
                ).pack(expand=True)
                tab_frames[label] = error_frame
                error_frame.pack(fill="both", expand=True)
                return
            tab_frames[label] = actual
            actual.pack(fill="both", expand=True)
            return

        placeholder = ctk.CTkFrame(tab_container)
        placeholder.pack(fill="both", expand=True)
        tab_frames[label] = placeholder

        ctk.CTkLabel(
            placeholder,
            text="Carregando...",
            font=ctk.CTkFont(size=18),
        ).pack(expand=True)
        spinner = ctk.CTkProgressBar(placeholder, mode="indeterminate", width=200)
        spinner.pack(pady=10)
        spinner.start()

        def load():
            try:
                actual = ctk.CTkFrame(tab_container)
                tab_builders[label](actual)
                tab_frames[label] = actual
                tab_frames[label + "._spawned"] = placeholder
                placeholder.after(0, lambda: _swap_placeholder(placeholder, actual))
            except Exception as exc:
                placeholder.after(0, lambda e=exc: _show_tab_error(placeholder, label, e))

        def _swap_placeholder(old, new):
            if old.winfo_exists():
                old.destroy()
            new.pack(fill="both", expand=True)

        def _show_tab_error(old, label, exc):
            if old.winfo_exists():
                old.destroy()
            error_frame = ctk.CTkFrame(tab_container)
            ctk.CTkLabel(
                error_frame,
                text=f"Erro ao carregar {label}: {exc}",
                font=ctk.CTkFont(size=14),
                text_color="red",
            ).pack(expand=True)
            tab_frames[label] = error_frame
            error_frame.pack(fill="both", expand=True)

        t = threading.Thread(target=load, daemon=True)
        _background_threads.append(t)
        t.start()

    tab_switcher.configure(command=show_tab)
    tab_builders["Captura"] = _make_capture_tab_builder(app)
    tab_builders["Audio"] = _make_trim_tab_builder(app)
    tab_builders["Stems"] = _make_stem_tab_builder(app)
    tab_builders["Transcricao"] = _make_transcription_tab_builder(app)
    tab_builders["TTS"] = _make_tts_tab_builder(app)
    tab_builders["Video"] = _make_video_tab_builder(app)

    show_tab("Captura")
    step(1.0, "Pronto!")

    def _preload():
        import time
        time.sleep(0.5)
        for label in _HEAVY_TABS:
            if label not in tab_frames:
                _tab_cache[label] = True

    t = threading.Thread(target=_preload, daemon=True)
    _background_threads.append(t)
    t.start()


def _make_capture_tab_builder(app):
    def build(parent):
        from application.capture_media_use_case import CaptureMediaUseCase
        from infrastructure.downloader_adapter import YtDlpAdapter
        from presentation.tabs.capture_tab import CaptureTab

        downloader = YtDlpAdapter()
        ffmpeg = FFmpegAdapter()
        use_case = CaptureMediaUseCase(downloader=downloader, ffmpeg=ffmpeg)
        CaptureTab(parent, app, use_case)

    return build


def _make_trim_tab_builder(app):
    def build(parent):
        from presentation.tabs.trim_tab import TrimTab
        TrimTab(parent, app)

    return build


def _make_stem_tab_builder(app):
    def build(parent):
        from presentation.tabs.stem_tab import StemTab
        StemTab(parent, app)

    return build


def _make_transcription_tab_builder(app):
    def build(parent):
        from presentation.tabs.transcription_tab import TranscriptionTab
        TranscriptionTab(parent, app)

    return build


def _make_tts_tab_builder(app):
    def build(parent):
        from presentation.tabs.tts_tab import TtsTab
        TtsTab(parent, app)

    return build


def _make_video_tab_builder(app):
    def build(parent):
        from presentation.tabs.video_editor_tab import VideoEditorTab
        VideoEditorTab(parent, app)

    return build


def _build_adapters(app, step):
    from infrastructure.downloader_adapter import YtDlpAdapter

    step(0.18, "Verificando dependencias de audio...")
    step(0.20, "Verificando dependencias de transcricao...")
    step(0.22, "Verificando dependencias de sintese de voz...")
    step(0.25, "Carregando modulos de captura de midia...")
    YtDlpAdapter()
    step(0.28, "Carregando modulos de processamento de audio...")
    FFmpegAdapter()
    step(0.32, "Finalizando carregamento...")


def main() -> int:
    error_message = validate_startup()
    if error_message:
        show_startup_error(error_message)
        return 2

    app = ctk.CTk()
    app.withdraw()
    app.title("AudioLabEditor")

    set_window_icon(app)

    app.geometry("1120x720")
    app.minsize(960, 640)

    app.protocol("WM_DELETE_WINDOW", lambda: _on_close(app))

    splash = SplashScreen(app)
    splash.set_progress(0.15, "Inicializando interface...")

    build_window(app, splash)

    splash.close()
    app.deiconify()
    app.update()
    app.mainloop()
    return 0


def _on_close(app):
    cleanup_resources()
    try:
        app.destroy()
    except Exception:
        pass


if __name__ == "__main__":
    raise SystemExit(main())
