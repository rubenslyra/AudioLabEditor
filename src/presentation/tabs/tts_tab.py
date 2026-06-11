from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk

from application.generate_tts_use_case import GenerateTtsUseCase
from domain.interfaces import TtsRequest
from infrastructure.ai_runtime_manager import (
    TTS_PACKAGES,
    AiRuntimeStatus,
    check_tts_runtime,
)
from infrastructure.edge_tts_adapter import TTS_VOICES, EdgeTtsSubprocessAdapter
from infrastructure.path_config import PathConfig
from presentation.widgets import LogBox


class TtsTab:
    def __init__(self, parent, app, use_case: GenerateTtsUseCase | None = None):
        self._app = app
        self._use_case = use_case
        self._path_config = PathConfig()
        self._last_output_dir: Path | None = None
        self._ai_status: AiRuntimeStatus | None = None

        self.text_var = ctk.StringVar(value="")
        self.dest_var = ctk.StringVar(value="")
        self.project_var = ctk.StringVar(value="")
        self.voice_var = ctk.StringVar(value=TTS_VOICES[0])

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
        frame = self._push("Sintese de Voz (TTS)", "Verificando dependencias...")
        self._spinner = ctk.CTkProgressBar(frame, mode="indeterminate", width=400)
        self._spinner.pack(pady=20)
        self._spinner.start()
        self._status_msg = ctk.CTkLabel(frame, text="Verificando pacotes de TTS...")
        self._status_msg.pack()
        self.root.after(50, self._do_check)

    def _do_check(self):
        self._ai_status = check_tts_runtime()
        if self._spinner:
            self._spinner.stop()
        if self._ai_status.available:
            self._show_ready()
        else:
            self._show_missing()

    def _show_missing(self):
        self._push("Sintese de Voz (TTS)", "Dependencias de TTS necessarias")

        container = ctk.CTkFrame(self.root, corner_radius=16)
        container.pack(fill="x", padx=14, pady=(0, 20))
        self._stack.append(container)

        ctk.CTkLabel(
            container,
            text="Pacotes necessarios para sintese de voz:",
            font=ctk.CTkFont(size=14),
        ).pack(anchor="w", padx=20, pady=(16, 8))

        pkg_box = ctk.CTkTextbox(container, height=100, width=520)
        pkg_box.pack(padx=20, pady=(0, 12))
        lines = []
        for pkg in TTS_PACKAGES:
            status = "\u2713" if pkg not in self._ai_status.missing else "\u2717"
            lines.append(f"  {status} {pkg['import']} ({pkg['pip']})")
        pkg_box.insert("1.0", "\n".join(lines))
        pkg_box.configure(state="disabled")

        ctk.CTkLabel(
            container,
            text="Esse pacote nao esta disponivel no momento.\n"
                  "Para usar sintese de voz (TTS), baixe a versao completa em:\n"
                  "github.com/anomalyco/AudioLabEditor/releases",
            font=ctk.CTkFont(size=12),
            justify="left",
            anchor="w",
        ).pack(anchor="w", padx=20, pady=(0, 16))

    def _show_ready(self):
        if self._use_case is None:
            self._use_case = GenerateTtsUseCase(tts=EdgeTtsSubprocessAdapter())

        self._clear()

        self._push(
            "Sintese de Voz (TTS)",
            "Converta texto em audio natural usando Microsoft Edge TTS.",
        )
        sep_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        sep_frame.pack(fill="x", padx=14, pady=(0, 12))
        for i in range(3):
            sep_frame.grid_columnconfigure(1, weight=1)
        self._stack.append(sep_frame)

        row = 0
        ctk.CTkLabel(sep_frame, text="Pasta de destino:", width=140).grid(row=row, column=0, sticky="w", pady=4)
        self.dest_entry = ctk.CTkEntry(
            sep_frame, textvariable=self.dest_var, placeholder_text="Escolha onde salvar o audio..."
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
        self._stack.append(options_frame)

        ctk.CTkLabel(options_frame, text="Voz").grid(row=0, column=0, padx=(12, 8), pady=12, sticky="w")
        self.voice_menu = ctk.CTkOptionMenu(
            options_frame,
            values=TTS_VOICES,
            variable=self.voice_var,
            width=260,
        )
        self.voice_menu.grid(row=0, column=1, padx=(0, 12), pady=12, sticky="w")

        text_frame = ctk.CTkFrame(self.root, corner_radius=16)
        text_frame.pack(fill="x", padx=14, pady=(0, 12))
        self._stack.append(text_frame)

        ctk.CTkLabel(text_frame, text="Texto para sintetizar:", font=ctk.CTkFont(size=14)).pack(
            anchor="w", padx=12, pady=(12, 4)
        )

        self.text_box = ctk.CTkTextbox(text_frame, height=160, wrap="word")
        self.text_box.pack(fill="x", padx=12, pady=(0, 12))
        self.text_box.insert("1.0", "Digite aqui o texto que deseja converter em audio...")

        self.start_btn = ctk.CTkButton(self.root, text="Gerar audio", height=44, command=self._start_synthesis)
        self.start_btn.pack(fill="x", padx=14, pady=(0, 12))
        self._stack.append(self.start_btn)

        self.status_label = ctk.CTkLabel(self.root, text="Digite o texto, configure a voz e clique em Gerar.")
        self.status_label.pack(anchor="w", padx=14)
        self._stack.append(self.status_label)

        self.progress = ctk.CTkProgressBar(self.root)
        self.progress.set(0)
        self.progress.pack(fill="x", padx=14, pady=(8, 12))
        self._stack.append(self.progress)

        self.logs = LogBox(self.root, height=180)
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

    def _choose_dest(self):
        from tkinter import filedialog
        folder = filedialog.askdirectory(title="Selecionar pasta de destino do audio TTS")
        if folder:
            self.dest_var.set(folder)
            self._path_config.set_dest_dir(folder)

    def _set_progress(self, percent, message):
        self.progress.set(max(0.0, min(1.0, percent / 100.0)) if percent is not None else 0.0)
        self.status_label.configure(text=message)
        self.logs.append(message)

    def _start_synthesis(self):
        text = self.text_box.get("1.0", "end-1c").strip()
        dest = self.dest_var.get().strip()

        if not text:
            messagebox.showerror("Texto ausente", "Digite o texto que deseja converter em audio.")
            return
        if not dest:
            messagebox.showerror("Destino ausente", "Escolha uma pasta de destino para o audio.")
            return

        self.progress.set(0)
        self.logs.append("Preparando sintese de voz...")

        request = TtsRequest(
            text=text,
            voice=self.voice_var.get(),
            dest_dir=dest,
            project_name=self.project_var.get().strip(),
        )

        def task():
            try:
                result = self._use_case.execute(request, progress_cb=self._set_progress)
                self._last_output_dir = result.output_path.parent

                def _done():
                    self._show_open_dir_button()
                    self.logs.append(f"Audio TTS gerado: {result.output_path}")
                    self.logs.append(f"Voz: {result.voice}")
                    self.logs.append(f"Tamanho do texto: {result.text_length} caracteres")

                self.root.after(0, _done)
            except Exception as exc:
                error = str(exc)

                def _error():
                    messagebox.showerror("Erro na sintese", error)
                    self.logs.append(f"ERRO: {error}")

                self.root.after(0, _error)

        import threading

        threading.Thread(target=task, daemon=True).start()

    def _show_open_dir_button(self):
        if not self.open_dir_btn.winfo_manager():
            self.open_dir_btn.pack(side="left", padx=(0, 8))
