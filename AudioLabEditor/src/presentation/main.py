import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk
from application.capture_media_use_case import CaptureMediaUseCase
from application.separate_audio_use_case import SeparateAudioUseCase
from infrastructure.demucs_adapter import DemucsSubprocessAdapter
from infrastructure.downloader_adapter import YtDlpAdapter
from infrastructure.ffmpeg_adapter import FFmpegAdapter

from application.bootstrap import validate_startup
from presentation.tabs.capture_tab import CaptureTab
from presentation.tabs.stem_tab import StemTab
from presentation.tabs.trim_tab import TrimTab
from presentation.tabs.video_editor_tab import VideoEditorTab


def show_startup_error(message: str) -> None:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Dependencias ausentes", message)
    root.destroy()


def build_window():
    app = ctk.CTk()
    app.title("AudioLabEditor")
    app.geometry("1120x720")
    app.minsize(960, 640)

    tab_view = ctk.CTkTabview(app, corner_radius=14)
    tab_view.pack(fill="both", expand=True, padx=10, pady=10)

    downloader = YtDlpAdapter()
    ffmpeg = FFmpegAdapter()
    demucs = DemucsSubprocessAdapter()

    capture_use_case = CaptureMediaUseCase(downloader=downloader, ffmpeg=ffmpeg)
    separate_use_case = SeparateAudioUseCase(demucs=demucs)

    tabs = {
        "Captura": lambda parent: CaptureTab(parent, app, capture_use_case),
        "Audio": lambda parent: TrimTab(parent, app),
        "Stems": lambda parent: StemTab(parent, app, separate_use_case),
        "Video": lambda parent: VideoEditorTab(parent, app),
    }

    for label, build in tabs.items():
        tab = tab_view.add(label)
        build(tab)

    return app


def main() -> int:
    error_message = validate_startup()
    if error_message:
        show_startup_error(error_message)
        return 2
    app = build_window()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
