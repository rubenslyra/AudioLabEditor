import shutil
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from application.batch_separate_audio_use_case import BatchSeparateAudioUseCase
from application.separate_audio_use_case import SeparateAudioUseCase
from domain.interfaces import StemRequest
from infrastructure.ai_runtime_manager import (
    STEM_PACKAGES,
    AiRuntimeStatus,
    check_stem_runtime,
)
from infrastructure.demucs_adapter import DemucsSubprocessAdapter
from infrastructure.path_config import PathConfig
from presentation.widgets import LogBox


class StemTab:
    MODE_LABELS = {
        "Apenas vocais": "vocals",
        "4 stems (bass/drums/other/vocals)": "full4",
        "6 stems (piano/guitar + full4)": "extended6",
    }
    FORMAT_LABELS = {
        "WAV (qualidade maxima)": "wav",
        "MP3 320kbps": "mp3",
        "FLAC (compactado sem perda)": "flac",
    }

    def __init__(self, parent, app, use_case: SeparateAudioUseCase | None = None):
        self._app = app
        self._use_case = use_case
        self._path_config = PathConfig()
        self._last_output_dir: Path | None = None
        self._ai_status: AiRuntimeStatus | None = None
        self._source_paths: list[Path] = []

        self.source_var = ctk.StringVar(value="")
        self.dest_var = ctk.StringVar(value="")
        self.project_var = ctk.StringVar(value="")
        self.mode_var = ctk.StringVar(value=list(self.MODE_LABELS.keys())[0])
        self.format_var = ctk.StringVar(value=list(self.FORMAT_LABELS.keys())[0])

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
        frame = self._push("Separador de Stems", "Verificando dependencias...")
        self._spinner = ctk.CTkProgressBar(frame, mode="indeterminate", width=400)
        self._spinner.pack(pady=20)
        self._spinner.start()
        self._status_msg = ctk.CTkLabel(frame, text="Verificando pacotes de IA...")
        self._status_msg.pack()
        self.root.after(50, self._do_check)

    def _do_check(self):
        try:
            self._ai_status = check_stem_runtime()
        except Exception:
            self._ai_status = AiRuntimeStatus(available=False, missing=STEM_PACKAGES)
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
        self._push("Separador de Stems", "Dependencias de IA necessarias")

        container = ctk.CTkFrame(self.root, corner_radius=16)
        container.pack(fill="x", padx=14, pady=(0, 20))
        self._stack.append(container)

        ctk.CTkLabel(
            container,
            text="Pacotes necessarios para separacao de stems:",
            font=ctk.CTkFont(size=14),
        ).pack(anchor="w", padx=20, pady=(16, 8))

        pkg_box = ctk.CTkTextbox(container, height=200, width=520)
        pkg_box.pack(padx=20, pady=(0, 12))
        lines = []
        for pkg in STEM_PACKAGES:
            status = "\u2713" if pkg not in self._ai_status.missing else "\u2717"
            lines.append(f"  {status} {pkg['import']} ({pkg['pip']})")
        pkg_box.insert("1.0", "\n".join(lines))
        pkg_box.configure(state="disabled")

        ctk.CTkLabel(
            container,
            text="Recursos de IA nao encontrados. Clique abaixo para baixar e instalar automaticamente.",
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="w",
        ).pack(anchor="w", padx=20, pady=(8, 4))

        self._dl_progress = ctk.CTkProgressBar(container)
        self._dl_status = ctk.CTkLabel(container, text="", anchor="w", font=ctk.CTkFont(size=11))

        self._dl_btn = ctk.CTkButton(
            container,
            text="Baixar runtime de IA (~1.5 GB)",
            height=40,
            command=self._start_download,
        )
        self._dl_btn.pack(padx=20, pady=(4, 16))

    def _start_download(self):
        self._dl_btn.configure(state="disabled", text="Baixando...")
        self._dl_progress.pack(fill="x", padx=20, pady=(0, 4))
        self._dl_status.pack(fill="x", padx=20)
        self._dl_progress.set(0)

        import threading

        from infrastructure.runtime_downloader import ensure_runtime

        def progress(value, msg):
            self.root.after(0, lambda: self._update_dl_progress(value, msg))

        def task():
            ok = ensure_runtime(progress_cb=progress)

            def done():
                if ok:
                    self._dl_status.configure(text="Runtime instalado! Verificando...")
                    self._dl_progress.set(1)
                    self._ai_status = check_stem_runtime()
                    if self._ai_status.available:
                        self._show_ready()
                    else:
                        self._dl_btn.configure(state="normal", text="Tentar novamente")
                        self._dl_status.configure(text="Alguns componentes nao puderam ser instalados.")
                else:
                    self._dl_btn.configure(state="normal", text="Tentar novamente")
                    self._dl_status.configure(text="Falha no download. Verifique sua conexao.")

            self.root.after(0, done)

        threading.Thread(target=task, daemon=True).start()

    def _update_dl_progress(self, value, msg):
        if value is not None and isinstance(value, (int, float)):
            self._dl_progress.set(min(1.0, value / 100.0))
        if msg:
            self._dl_status.configure(text=msg)

    def _show_ready(self):
        if self._use_case is None:
            self._use_case = SeparateAudioUseCase(demucs=DemucsSubprocessAdapter())

        self._clear()

        self._push(
            "Separador de Stems",
            "Separe instrumentos e vocais de arquivos de audio usando IA (Demucs). Selecione um ou mais arquivos.",
        )
        self._validate_environment()
        sep_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        sep_frame.pack(fill="x", padx=14, pady=(0, 12))
        for i in range(3):
            sep_frame.grid_columnconfigure(1, weight=1)
        self._stack.append(sep_frame)

        row = 0
        ctk.CTkLabel(sep_frame, text="Arquivos de origem:", width=140).grid(row=row, column=0, sticky="w", pady=4)
        self.source_entry = ctk.CTkEntry(
            sep_frame, textvariable=self.source_var, placeholder_text="Selecione um ou mais arquivos..."
        )
        self.source_entry.grid(row=row, column=1, sticky="ew", padx=(0, 8), pady=4)
        self.source_btn = ctk.CTkButton(sep_frame, text="Procurar", width=110, command=self._choose_source)
        self.source_btn.grid(row=row, column=2, pady=4)
        self.clear_btn = ctk.CTkButton(sep_frame, text="Limpar", width=80, command=self._clear_sources)
        self.clear_btn.grid(row=row, column=3, padx=(4, 0), pady=4)

        row += 1
        self.file_list_label = ctk.CTkLabel(sep_frame, text="", anchor="w", justify="left")
        self.file_list_label.grid(row=row, column=0, columnspan=4, sticky="w", padx=140, pady=(0, 4))

        row += 1
        ctk.CTkLabel(sep_frame, text="Pasta de destino:", width=140).grid(row=row, column=0, sticky="w", pady=4)
        self.dest_entry = ctk.CTkEntry(
            sep_frame, textvariable=self.dest_var, placeholder_text="Escolha onde salvar os stems..."
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

        ctk.CTkLabel(options_frame, text="Modo de separacao").grid(row=0, column=0, padx=(12, 8), pady=12, sticky="w")
        self.mode_menu = ctk.CTkOptionMenu(
            options_frame,
            values=list(self.MODE_LABELS.keys()),
            variable=self.mode_var,
            width=280,
        )
        self.mode_menu.grid(row=0, column=1, padx=(0, 16), pady=12, sticky="w")

        ctk.CTkLabel(options_frame, text="Formato de saida").grid(row=0, column=2, padx=(0, 8), pady=12, sticky="w")
        self.format_menu = ctk.CTkOptionMenu(
            options_frame,
            values=list(self.FORMAT_LABELS.keys()),
            variable=self.format_var,
            width=260,
        )
        self.format_menu.grid(row=0, column=3, padx=(0, 12), pady=12, sticky="w")

        self.start_btn = ctk.CTkButton(self.root, text="Iniciar separacao", height=44, command=self._start_separation)
        self.start_btn.pack(fill="x", padx=14, pady=(0, 12))
        self._stack.append(self.start_btn)

        self._env_status_label = ctk.CTkLabel(self.root, text="", anchor="w")
        self._env_status_label.pack(anchor="w", padx=14, pady=(0, 4))
        self._stack.append(self._env_status_label)

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

    def _validate_environment(self):
        issues = []
        if shutil.which("ffmpeg") is None:
            issues.append("ffmpeg nao encontrado no PATH")

        try:
            free = shutil.disk_usage("/").free
            if free < 1_000_000_000:
                issues.append("espaco em disco insuficiente (min 1GB)")
        except Exception:
            pass

        if issues:
            self._env_status_label.configure(
                text="Atencao: " + "; ".join(issues),
                text_color="orange",
            )
            self.start_btn.configure(state="disabled")
        else:
            self._env_status_label.configure(
                text="Ambiente OK. Recursos de IA disponiveis.",
                text_color="green",
            )
            self.start_btn.configure(state="normal")

    def _update_file_list_display(self):
        count = len(self._source_paths)
        if count == 0:
            self.source_var.set("")
            self.file_list_label.configure(text="")
        elif count == 1:
            self.source_var.set(str(self._source_paths[0]))
            self.file_list_label.configure(text="")
        else:
            self.source_var.set(f"{count} arquivos selecionados")
            names = "\n".join(f"  \u2022 {p.name}" for p in self._source_paths[:5])
            if count > 5:
                names += f"\n  ... e mais {count - 5}"
            self.file_list_label.configure(text=f"Arquivos:\n{names}")

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
        files = filedialog.askopenfilenames(
            title="Selecionar arquivos de audio ou video",
            filetypes=[
                ("Audio/Video", "*.mp3 *.wav *.flac *.ogg *.m4a *.mp4 *.avi *.mkv *.mov *.webm"),
                ("Todos", "*.*"),
            ],
        )
        if files:
            self._source_paths = [Path(f) for f in files]
            self._update_file_list_display()

    def _clear_sources(self):
        self._source_paths.clear()
        self._update_file_list_display()

    def _choose_dest(self):
        folder = filedialog.askdirectory(title="Selecionar pasta de destino dos stems")
        if folder:
            self.dest_var.set(folder)
            self._path_config.set_dest_dir(folder)

    def _set_progress(self, percent, message):
        self.progress.set(max(0.0, min(1.0, percent / 100.0)) if percent is not None else 0.0)
        self.status_label.configure(text=message)
        self.logs.append(message)

    def _start_separation(self):
        dest = self.dest_var.get().strip()

        if not self._source_paths:
            messagebox.showerror("Origem ausente", "Selecione um ou mais arquivos de audio ou video.")
            return
        if not dest:
            messagebox.showerror("Destino ausente", "Escolha uma pasta de destino para os stems.")
            return

        self.progress.set(0)
        self.logs.append("Preparando separacao de stems...")

        mode = self.MODE_LABELS[self.mode_var.get()]
        output_format = self.FORMAT_LABELS[self.format_var.get()]
        project_name = self.project_var.get().strip()

        if len(self._source_paths) == 1:
            self._start_single(dest, mode, output_format, project_name)
        else:
            self._start_batch(dest, mode, output_format, project_name)

    def _start_single(self, dest: str, mode: str, output_format: str, project_name: str):
        request = StemRequest(
            source_path=self._source_paths[0],
            mode=mode,
            output_format=output_format,
            dest_dir=dest,
            project_name=project_name,
        )

        def task():
            try:
                result = self._use_case.execute(request, progress_cb=self._set_progress)
                self._last_output_dir = result.output_dir

                def _done():
                    self._show_open_dir_button()
                    self.logs.append(f"Stems gerados em: {result.output_dir}")

                self.root.after(0, _done)
            except Exception as exc:
                error = str(exc)

                def _error():
                    messagebox.showerror("Erro na separacao", error)
                    self.logs.append(f"ERRO: {error}")

                self.root.after(0, _error)

        import threading

        threading.Thread(target=task, daemon=True).start()

    def _start_batch(self, dest: str, mode: str, output_format: str, project_name: str):
        batch_use_case = BatchSeparateAudioUseCase(
            demucs=DemucsSubprocessAdapter(),
            path_config=self._path_config,
        )

        def task():
            try:
                result = batch_use_case.execute(
                    source_paths=self._source_paths,
                    mode=mode,
                    output_format=output_format,
                    dest_dir=dest,
                    project_name=project_name,
                    progress_cb=self._set_progress,
                )
                self._last_output_dir = result.output_dir

                def _done():
                    self._show_open_dir_button()
                    self.logs.append(f"Lote concluido em: {result.output_dir}")
                    self.logs.append(f"Sucesso: {result.succeeded}/{result.total}")
                    if result.failed:
                        self.logs.append("Falhas:")
                        for name, err in result.failed:
                            self.logs.append(f"  \u2717 {name}: {err}")

                self.root.after(0, _done)
            except Exception as exc:
                error = str(exc)

                def _error():
                    messagebox.showerror("Erro no lote", error)
                    self.logs.append(f"ERRO: {error}")

                self.root.after(0, _error)

        import threading

        threading.Thread(target=task, daemon=True).start()

    def _show_open_dir_button(self):
        if not self.open_dir_btn.winfo_manager():
            self.open_dir_btn.pack(side="left", padx=(0, 8))
