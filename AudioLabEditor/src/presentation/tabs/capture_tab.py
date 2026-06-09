from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from application.capture_media_use_case import (
    CAPTURE_MODE_AUDIO_ONLY,
    CAPTURE_MODE_VIDEO_COMPRESSED,
    CAPTURE_MODE_VIDEO_ORIGINAL,
    CaptureMediaRequest,
    CaptureMediaUseCase,
)
from application.output_organizer import OutputOrganizer
from infrastructure.path_config import PathConfig
from presentation.widgets import LogBox


class CaptureTab:
    MODE_LABELS = {
        "Video original": CAPTURE_MODE_VIDEO_ORIGINAL,
        "Video comprimido": CAPTURE_MODE_VIDEO_COMPRESSED,
        "Somente audio": CAPTURE_MODE_AUDIO_ONLY,
    }
    AUDIO_FORMATS = ["mp3", "m4a", "wav", "flac", "ogg", "aac"]

    def __init__(self, parent, app, use_case: CaptureMediaUseCase):
        self._app = app
        self._use_case = use_case
        self._output_organizer = OutputOrganizer()
        self._path_config = PathConfig()
        self._last_output_path: Path | None = None

        self.url_var = ctk.StringVar()
        self.output_dir_var = ctk.StringVar(value=self._path_config.get_dest_dir())
        self.mode_var = ctk.StringVar(value="Video original")
        self.quality_var = ctk.StringVar(value="Alta")
        self.audio_format_var = ctk.StringVar(value="mp3")
        self.audio_bitrate_var = ctk.StringVar(value="192")

        self.root = ctk.CTkScrollableFrame(parent, corner_radius=14)
        self.root.pack(fill="both", expand=True, padx=10, pady=10)
        self._build()

    def _build(self):
        ctk.CTkLabel(self.root, text="Captura de Midia", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", padx=14, pady=(12, 4))
        self.note = ctk.CTkLabel(
            self.root,
            text="Baixe videos, preserve o original, comprima com qualidade ou extraia audio em um fluxo unico.",
        )
        self.note.pack(anchor="w", padx=14, pady=(0, 12))

        self.url_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.url_frame.pack(fill="x", padx=14, pady=(0, 8))
        self.url_entry = ctk.CTkEntry(self.url_frame, textvariable=self.url_var, placeholder_text="Cole a URL do video aqui")
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.analyze_btn = ctk.CTkButton(self.url_frame, text="Analisar", width=120, command=self.analyze)
        self.analyze_btn.pack(side="left", padx=(0, 8))
        self.start_btn = ctk.CTkButton(self.url_frame, text="Iniciar", width=120, command=self.start_capture)
        self.start_btn.pack(side="left")

        self.output_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.output_frame.pack(fill="x", padx=14, pady=(0, 8))
        self.output_label = ctk.CTkLabel(self.output_frame, text="Pasta de saida:", width=110)
        self.output_label.pack(side="left")
        self.output_entry = ctk.CTkEntry(self.output_frame, textvariable=self.output_dir_var)
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.output_btn = ctk.CTkButton(self.output_frame, text="Escolher", width=120, command=self.choose_output)
        self.output_btn.pack(side="left")

        self.options_frame = ctk.CTkFrame(self.root, corner_radius=16)
        self.options_frame.pack(fill="x", padx=14, pady=(0, 12))
        self.options_frame.grid_columnconfigure(1, weight=1)
        self.options_frame.grid_columnconfigure(3, weight=1)
        ctk.CTkLabel(self.options_frame, text="Modo").grid(row=0, column=0, padx=(12, 8), pady=12, sticky="w")
        self.mode_menu = ctk.CTkOptionMenu(
            self.options_frame,
            values=list(self.MODE_LABELS.keys()),
            variable=self.mode_var,
            command=self._on_mode_changed,
            width=180,
        )
        self.mode_menu.grid(row=0, column=1, padx=(0, 16), pady=12, sticky="w")
        ctk.CTkLabel(self.options_frame, text="Qualidade").grid(row=0, column=2, padx=(0, 8), pady=12, sticky="w")
        self.quality_menu = ctk.CTkOptionMenu(
            self.options_frame,
            values=["Alta", "Balanceada", "Compacta"],
            variable=self.quality_var,
            width=150,
        )
        self.quality_menu.grid(row=0, column=3, padx=(0, 12), pady=12, sticky="w")

        self.audio_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.audio_frame.pack(fill="x", padx=14, pady=(0, 12))
        ctk.CTkLabel(self.audio_frame, text="Formato de audio", width=130).pack(side="left")
        self.audio_format_menu = ctk.CTkOptionMenu(self.audio_frame, values=self.AUDIO_FORMATS, variable=self.audio_format_var, width=120)
        self.audio_format_menu.pack(side="left", padx=(0, 12))
        ctk.CTkLabel(self.audio_frame, text="Bitrate").pack(side="left", padx=(0, 8))
        self.audio_bitrate_entry = ctk.CTkEntry(self.audio_frame, textvariable=self.audio_bitrate_var, width=90)
        self.audio_bitrate_entry.pack(side="left")

        self.info_box = ctk.CTkTextbox(self.root, height=160)
        self.info_box.pack(fill="x", padx=14, pady=(0, 12))
        self.info_box.insert("end", "Analise uma URL para ver metadados antes de iniciar.")

        self.status_label = ctk.CTkLabel(self.root, text="Aguardando captura...")
        self.status_label.pack(anchor="w", padx=14)
        self.progress = ctk.CTkProgressBar(self.root)
        self.progress.set(0)
        self.progress.pack(fill="x", padx=14, pady=(8, 12))

        self.logs = LogBox(self.root, height=220)
        self.logs.pack(fill="x", padx=14, pady=(0, 12))

        self.actions = ctk.CTkFrame(self.root, fg_color="transparent")
        self.actions.pack(fill="x", padx=14, pady=(0, 14))
        self.open_dir_btn = ctk.CTkButton(
            self.actions,
            text="Abrir pasta de destino",
            width=180,
            command=lambda: self._reveal_file(),
        )
        self.open_dir_btn.pack(side="left", padx=(0, 8))
        self.open_dir_btn.pack_forget()
        self.clear_btn = ctk.CTkButton(self.actions, text="Limpar logs", width=150, command=lambda: self.logs.delete("1.0", "end"))
        self.clear_btn.pack(side="left")
        self._on_mode_changed()

    def _reveal_file(self):
        import subprocess
        import sys
        path = self._last_output_path
        if not path:
            return
        if sys.platform == "win32":
            subprocess.Popen(["explorer", "/select,", str(path)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", "-R", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path.parent)])

    def choose_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir_var.set(folder)
            self._path_config.set_dest_dir(folder)

    def _on_mode_changed(self, _value=None):
        if self.MODE_LABELS.get(self.mode_var.get()) == CAPTURE_MODE_AUDIO_ONLY:
            if not self.audio_frame.winfo_manager():
                self.audio_frame.pack(fill="x", padx=14, pady=(0, 12), before=self.info_box)
            self.quality_menu.configure(state="disabled")
        else:
            if self.audio_frame.winfo_manager():
                self.audio_frame.pack_forget()
            self.quality_menu.configure(state="normal")

    def _set_progress(self, percent, message):
        self.progress.set(max(0.0, min(1.0, percent / 100.0)))
        self.status_label.configure(text=message)
        self.logs.append(message)

    def analyze(self):
        url = self.url_var.get().strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            messagebox.showerror("URL invalida", "Informe uma URL valida (http/https).")
            return
        self.logs.append("Analisando URL...")

        def task():
            try:
                info = self._use_case.get_info(url)
                title = info.title or "-"
                duration = str(info.duration) + " segundos" if info.duration else "-"
                uploader = info.uploader or "-"
                webpage = info.webpage_url or url

                def _show():
                    self.info_box.delete("1.0", "end")
                    self.info_box.insert(
                        "end",
                        "\n".join([
                            f"Titulo: {title}",
                            f"Duracao: {duration}",
                            f"Canal/Uploader: {uploader}",
                            f"Link: {webpage}",
                        ]),
                    )
                    self.logs.append("Metadados carregados. Escolha o modo e inicie a captura.")
                    self.status_label.configure(text="URL analisada.")
                self.root.after(0, _show)
            except Exception as exc:
                error = str(exc)
                self.root.after(0, lambda: messagebox.showerror("Erro ao analisar", error))

        import threading
        threading.Thread(target=task, daemon=True).start()

    def start_capture(self):
        url = self.url_var.get().strip()
        output_dir = self.output_dir_var.get().strip()
        if not url.startswith("http://") and not url.startswith("https://"):
            messagebox.showerror("URL invalida", "Informe uma URL valida (http/https).")
            return
        if not output_dir:
            messagebox.showerror("Saida invalida", "Escolha uma pasta de saida.")
            return
        try:
            audio_bitrate = int(self.audio_bitrate_var.get().strip() or "192")
        except Exception:
            messagebox.showerror("Bitrate invalido", "Informe um bitrate numerico.")
            return

        request = CaptureMediaRequest(
            url=url,
            output_dir=Path(output_dir),
            project_name="ALE",
            mode=self.MODE_LABELS[self.mode_var.get()],
            quality_preset=self.quality_var.get(),
            audio_format=self.audio_format_var.get(),
            audio_bitrate=audio_bitrate,
        )
        self.progress.set(0)
        self.logs.append("Iniciando captura...")

        def task():
            try:
                result = self._use_case.execute(request, progress_cb=self._set_progress)
                self._last_output_path = result.output_path
                self.root.after(0, self._show_open_dir_button)
                self.root.after(0, lambda: self.logs.append(f"Arquivo salvo em: {result.output_path}"))
            except Exception as exc:
                error = str(exc)
                self.root.after(0, lambda: messagebox.showerror("Erro na captura", error))

        import threading
        threading.Thread(target=task, daemon=True).start()

    def _show_open_dir_button(self):
        if not self.open_dir_btn.winfo_manager():
            self.open_dir_btn.pack(side="left", padx=(0, 8), before=self.clear_btn)
