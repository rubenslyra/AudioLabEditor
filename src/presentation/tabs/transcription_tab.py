from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from application.transcribe_audio_use_case import TranscribeAudioUseCase
from domain.interfaces import TranscriptionRequest
from infrastructure.ai_runtime_manager import (
    TRANSCRIPTION_PACKAGES,
    AiRuntimeStatus,
    check_transcription_runtime,
)
from infrastructure.path_config import PathConfig
from infrastructure.runtime_paths import IS_FROZEN
from infrastructure.whisper_adapter import (
    WHISPER_LANGUAGES,
    WHISPER_MODELS,
    WhisperSubprocessAdapter,
)
from presentation.widgets import LogBox


class TranscriptionTab:
    def __init__(self, parent, app, use_case: TranscribeAudioUseCase | None = None):
        self._app = app
        self._use_case = use_case
        self._path_config = PathConfig()
        self._last_output_dir: Path | None = None
        self._ai_status: AiRuntimeStatus | None = None

        self.source_var = ctk.StringVar(value="")
        self.dest_var = ctk.StringVar(value="")
        self.project_var = ctk.StringVar(value="")
        self.lang_var = ctk.StringVar(value=list(WHISPER_LANGUAGES.keys())[0])
        self.model_var = ctk.StringVar(value=WHISPER_MODELS[1])

        self.root = ctk.CTkScrollableFrame(parent, corner_radius=14)
        self.root.pack(fill="both", expand=True, padx=10, pady=10)
        self._stack: list[ctk.CTkFrame] = []
        self._show_checking()

    def _clear(self):
        for f in self._stack:
            f.destroy()
        self._stack.clear()

    def _push(self, title: str, subtitle: str) -> ctk.CTkFrame:
        self._clear()
        header = ctk.CTkFrame(self.root, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(12, 0))
        ctk.CTkLabel(header, text=title, font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(header, text=subtitle).pack(anchor="w", pady=(2, 12))
        self._stack.append(header)
        return header

    def _show_checking(self):
        frame = self._push("Transcricao de Audio", "Verificando dependencias...")
        self._spinner = ctk.CTkProgressBar(frame, mode="indeterminate", width=400)
        self._spinner.pack(pady=20)
        self._spinner.start()
        self._status_msg = ctk.CTkLabel(frame, text="Verificando pacotes de transcricao...")
        self._status_msg.pack()
        self.root.after(50, self._do_check)

    def _do_check(self):
        try:
            self._ai_status = check_transcription_runtime()
        except Exception:
            self._ai_status = AiRuntimeStatus(available=False, missing=TRANSCRIPTION_PACKAGES)
        if self._spinner:
            self._spinner.stop()
        if self._ai_status and self._ai_status.available:
            try:
                self._show_ready()
            except Exception:
                self._show_missing()
        else:
            self._show_missing()

    def _show_missing(self):
        self._push("Transcricao de Audio", "Dependencias de transcricao necessarias")

        container = ctk.CTkFrame(self.root, corner_radius=16)
        container.pack(fill="x", padx=14, pady=(0, 20))
        self._stack.append(container)

        ctk.CTkLabel(
            container,
            text="Pacotes necessarios para transcricao:",
            font=ctk.CTkFont(size=14),
        ).pack(anchor="w", padx=20, pady=(16, 8))

        pkg_box = ctk.CTkTextbox(container, height=120, width=520)
        pkg_box.pack(padx=20, pady=(0, 12))
        lines = []
        for pkg in TRANSCRIPTION_PACKAGES:
            status = "\u2713" if pkg not in self._ai_status.missing else "\u2717"
            lines.append(f"  {status} {pkg['import']} ({pkg['pip']})")
        pkg_box.insert("1.0", "\n".join(lines))
        pkg_box.configure(state="disabled")

        if not IS_FROZEN:
            ctk.CTkLabel(
                container,
                text=(
                    "Modo desenvolvimento: instale as dependencias manualmente:\n"
                    "  pip install -e \".[ai]\""
                ),
                font=ctk.CTkFont(size=12),
                justify="left",
                anchor="w",
                text_color="orange",
            ).pack(anchor="w", padx=20, pady=(8, 16))
        else:
            ctk.CTkLabel(
                container,
                text=(
                    "Erro interno: dependencias de IA nao encontradas no pacote.\n"
                    "Reinstale o aplicativo ou reporte o bug."
                ),
                font=ctk.CTkFont(size=12),
                justify="left",
                anchor="w",
                text_color="red",
            ).pack(anchor="w", padx=20, pady=(8, 16))

    def _show_ready(self):
        if self._use_case is None:
            self._use_case = TranscribeAudioUseCase(transcriber=WhisperSubprocessAdapter())

        self._clear()

        self._push(
            "Transcricao de Audio",
            "Transcreva audio para texto usando IA (faster-whisper). Gera SRT e TXT.",
        )
        sep_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        sep_frame.pack(fill="x", padx=14, pady=(0, 12))
        for i in range(3):
            sep_frame.grid_columnconfigure(1, weight=1)
        self._stack.append(sep_frame)

        row = 0
        ctk.CTkLabel(sep_frame, text="Arquivo de origem:", width=140).grid(row=row, column=0, sticky="w", pady=4)
        self.source_entry = ctk.CTkEntry(
            sep_frame, textvariable=self.source_var, placeholder_text="Selecione o arquivo de audio/video..."
        )
        self.source_entry.grid(row=row, column=1, sticky="ew", padx=(0, 8), pady=4)
        self.source_btn = ctk.CTkButton(sep_frame, text="Procurar", width=110, command=self._choose_source)
        self.source_btn.grid(row=row, column=2, pady=4)

        row += 1
        ctk.CTkLabel(sep_frame, text="Pasta de destino:", width=140).grid(row=row, column=0, sticky="w", pady=4)
        self.dest_entry = ctk.CTkEntry(
            sep_frame, textvariable=self.dest_var, placeholder_text="Escolha onde salvar a transcricao..."
        )
        self.dest_entry.grid(row=row, column=1, sticky="ew", padx=(0, 8), pady=4)
        self.dest_btn = ctk.CTkButton(sep_frame, text="Procurar", width=110, command=self._choose_dest)
        self.dest_btn.grid(row=row, column=2, pady=4)

        row += 1
        ctk.CTkLabel(sep_frame, text="Nome do projeto:", width=140).grid(row=row, column=0, sticky="w", pady=4)
        self.project_entry = ctk.CTkEntry(
            sep_frame, textvariable=self.project_var, placeholder_text="Deixe em branco para usar 'ALE'"
        )
        self.project_entry.grid(row=row, column=1, sticky="ew", padx=(0, 8), pady=4)

        options_frame = ctk.CTkFrame(self.root, corner_radius=16)
        options_frame.pack(fill="x", padx=14, pady=(0, 12))
        options_frame.grid_columnconfigure(1, weight=1)
        options_frame.grid_columnconfigure(3, weight=1)
        self._stack.append(options_frame)

        ctk.CTkLabel(options_frame, text="Idioma").grid(row=0, column=0, padx=(12, 8), pady=12, sticky="w")
        self.lang_menu = ctk.CTkOptionMenu(
            options_frame,
            values=list(WHISPER_LANGUAGES.keys()),
            variable=self.lang_var,
            width=200,
        )
        self.lang_menu.grid(row=0, column=1, padx=(0, 16), pady=12, sticky="w")

        ctk.CTkLabel(options_frame, text="Modelo").grid(row=0, column=2, padx=(0, 8), pady=12, sticky="w")
        self.model_menu = ctk.CTkOptionMenu(
            options_frame,
            values=WHISPER_MODELS,
            variable=self.model_var,
            width=140,
        )
        self.model_menu.grid(row=0, column=3, padx=(0, 12), pady=12, sticky="w")

        ctk.CTkLabel(options_frame, text="Recomendado: base (rapido) / large-v3 (preciso)").grid(
            row=1, column=0, columnspan=4, padx=12, pady=(0, 12), sticky="w"
        )

        self.start_btn = ctk.CTkButton(
            self.root, text="Iniciar transcricao", height=44, command=self._start_transcription
        )
        self.start_btn.pack(fill="x", padx=14, pady=(0, 12))
        self._stack.append(self.start_btn)

        self.status_label = ctk.CTkLabel(self.root, text="Configure os caminhos e clique em Iniciar.")
        self.status_label.pack(anchor="w", padx=14)
        self._stack.append(self.status_label)

        self.progress = ctk.CTkProgressBar(self.root)
        self.progress.set(0)
        self.progress.pack(fill="x", padx=14, pady=(8, 12))
        self._stack.append(self.progress)

        self.logs = LogBox(self.root, height=220)
        self.logs.pack(fill="x", padx=14, pady=(0, 12))
        self._stack.append(self.logs)

        actions = ctk.CTkFrame(self.root, fg_color="transparent")
        actions.pack(fill="x", padx=14, pady=(0, 14))
        self._stack.append(actions)

        self.open_dir_btn = ctk.CTkButton(
            actions, text="Abrir pasta de destino", width=180, command=self._reveal_output_dir
        )
        self.open_dir_btn.pack(side="left", padx=(0, 8))
        self.open_dir_btn.pack_forget()
        ctk.CTkButton(
            actions, text="Limpar logs", width=150, command=lambda: self.logs.delete("1.0", "end")
        ).pack(side="left")

        if self._path_config.get_dest_dir():
            self.dest_var.set(self._path_config.get_dest_dir())

    def _reveal_output_dir(self):
        import subprocess
        import sys
        path = self._last_output_dir
        if not path:
            return
        if sys.platform == "win32":
            subprocess.Popen(["explorer", str(path)])
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])

    def _choose_source(self):
        folder = filedialog.askopenfilename(
            title="Selecionar arquivo de audio ou video",
            filetypes=[
                ("Audio/Video", "*.mp3 *.wav *.flac *.ogg *.m4a *.mp4 *.avi *.mkv *.mov *.webm"),
                ("Todos", "*.*"),
            ],
        )
        if folder:
            self.source_var.set(folder)

    def _choose_dest(self):
        folder = filedialog.askdirectory(title="Selecionar pasta de destino da transcricao")
        if folder:
            self.dest_var.set(folder)
            self._path_config.set_dest_dir(folder)

    def _set_progress(self, percent, message):
        self.progress.set(max(0.0, min(1.0, percent / 100.0)) if percent is not None else 0.0)
        self.status_label.configure(text=message)
        self.logs.append(message)

    def _start_transcription(self):
        source = self.source_var.get().strip()
        dest = self.dest_var.get().strip()

        if not source:
            messagebox.showerror("Origem ausente", "Selecione um arquivo de audio ou video de origem.")
            return
        if not Path(source).exists():
            messagebox.showerror("Arquivo nao encontrado", f"O arquivo informado nao existe:\n{source}")
            return
        if not dest:
            messagebox.showerror("Destino ausente", "Escolha uma pasta de destino para a transcricao.")
            return

        self.progress.set(0)
        self.logs.append("Preparando transcricao...")

        request = TranscriptionRequest(
            source_path=Path(source),
            language=WHISPER_LANGUAGES[self.lang_var.get()],
            model_size=self.model_var.get(),
            dest_dir=dest,
            project_name=self.project_var.get().strip(),
        )

        def task():
            try:
                result = self._use_case.execute(request, progress_cb=self._set_progress)
                self._last_output_dir = result.output_dir

                def _done():
                    self._show_open_dir_button()
                    self.logs.append(f"Transcricao gerada em: {result.output_dir}")
                    self.logs.append(f"Idioma detectado: {result.language}")
                    self.logs.append(f"Segmentos: {result.segments_count}")

                self.root.after(0, _done)
            except Exception as exc:
                error = str(exc)

                def _error():
                    messagebox.showerror("Erro na transcricao", error)
                    self.logs.append(f"ERRO: {error}")

                self.root.after(0, _error)

        import threading

        threading.Thread(target=task, daemon=True).start()

    def _show_open_dir_button(self):
        if not self.open_dir_btn.winfo_manager():
            self.open_dir_btn.pack(side="left", padx=(0, 8))
