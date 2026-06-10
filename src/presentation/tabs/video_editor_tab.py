from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from application.output_organizer import OutputOrganizer, PROJECT_NAME_FALLBACK
from domain.entities import MediaType, OutputCategory, OutputRequest
from infrastructure.path_config import PathConfig
from presentation.widgets import LogBox


class VideoEditorTab:
    def __init__(self, parent, app):
        self._app = app
        self._path_config = PathConfig()
        self._output_organizer = OutputOrganizer(self._path_config)
        self._last_output_path: Path | None = None

        self.input_var = ctk.StringVar()
        self.output_dir_var = ctk.StringVar(value=self._path_config.get_dest_dir())
        self.project_var = ctk.StringVar(value=self._path_config.get_project_name())
        self.start_var = ctk.StringVar(value="00:00")
        self.end_var = ctk.StringVar(value="00:10")

        self.root = ctk.CTkScrollableFrame(parent, corner_radius=14)
        self.root.pack(fill="both", expand=True, padx=10, pady=10)
        self._build()

    def _build(self):
        ctk.CTkLabel(self.root, text="Editor de Video", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", padx=14, pady=(12, 4))
        ctk.CTkLabel(self.root, text="Corte e exportacao de video com presets de qualidade.").pack(anchor="w", padx=14, pady=(0, 12))

        self.io_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.io_frame.pack(fill="x", padx=14, pady=(0, 8))
        ctk.CTkLabel(self.io_frame, text="Video:").pack(side="left")
        self.input_entry = ctk.CTkEntry(self.io_frame, textvariable=self.input_var, placeholder_text="Selecione um arquivo de video...")
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(8, 8))
        self.choose_btn = ctk.CTkButton(self.io_frame, text="Procurar", width=100, command=self.choose_input)
        self.choose_btn.pack(side="left")

        self.io_frame2 = ctk.CTkFrame(self.root, fg_color="transparent")
        self.io_frame2.pack(fill="x", padx=14, pady=(0, 8))
        ctk.CTkLabel(self.io_frame2, text="Destino:").pack(side="left")
        self.output_entry = ctk.CTkEntry(self.io_frame2, textvariable=self.output_dir_var, placeholder_text="Pasta de saida...")
        self.output_entry.pack(side="left", fill="x", expand=True, padx=(8, 8))
        self.output_btn = ctk.CTkButton(self.io_frame2, text="Pasta", width=100, command=self.choose_output)
        self.output_btn.pack(side="left")

        self.proj_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.proj_frame.pack(fill="x", padx=14, pady=(0, 8))
        ctk.CTkLabel(self.proj_frame, text="Projeto:").pack(side="left")
        self.project_entry = ctk.CTkEntry(self.proj_frame, textvariable=self.project_var, placeholder_text=f"Em branco usa '{PROJECT_NAME_FALLBACK}'")
        self.project_entry.pack(side="left", fill="x", expand=True, padx=(8, 0))

        self.cut_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.cut_frame.pack(fill="x", padx=14, pady=(0, 8))
        ctk.CTkLabel(self.cut_frame, text="Inicio:").pack(side="left")
        self.start_entry = ctk.CTkEntry(self.cut_frame, textvariable=self.start_var, width=120)
        self.start_entry.pack(side="left", padx=(8, 8))
        ctk.CTkLabel(self.cut_frame, text="Fim:").pack(side="left")
        self.end_entry = ctk.CTkEntry(self.cut_frame, textvariable=self.end_var, width=120)
        self.end_entry.pack(side="left", padx=(8, 8))
        self.render_btn = ctk.CTkButton(self.cut_frame, text="Renderizar", width=140, command=self.render)
        self.render_btn.pack(side="left", padx=(8, 0))

        self.options_frame = ctk.CTkFrame(self.root, corner_radius=16)
        self.options_frame.pack(fill="x", padx=14, pady=(0, 12))
        ctk.CTkLabel(self.options_frame, text="Formato:").pack(side="left", padx=(12, 8))
        self.format_var = ctk.StringVar(value="mp4")
        self.format_menu = ctk.CTkOptionMenu(self.options_frame, values=["mp4", "mkv", "avi"], variable=self.format_var, width=120)
        self.format_menu.pack(side="left", padx=(0, 16))
        ctk.CTkLabel(self.options_frame, text="Qualidade:").pack(side="left", padx=(0, 8))
        self.quality_var = ctk.StringVar(value="Alta")
        self.quality_menu = ctk.CTkOptionMenu(self.options_frame, values=["Alta", "Balanceada", "Compacta"], variable=self.quality_var, width=140)
        self.quality_menu.pack(side="left")

        self.status_label = ctk.CTkLabel(self.root, text="Aguardando edicao de video...")
        self.status_label.pack(anchor="w", padx=14)
        self.progress = ctk.CTkProgressBar(self.root)
        self.progress.set(0)
        self.progress.pack(fill="x", padx=14, pady=(8, 12))

        self.logs = LogBox(self.root, height=220)
        self.logs.pack(fill="x", padx=14, pady=(0, 12))

        self.actions = ctk.CTkFrame(self.root, fg_color="transparent")
        self.actions.pack(fill="x", padx=14, pady=(0, 14))
        self.open_dir_btn = ctk.CTkButton(
            self.actions, text="Abrir pasta", width=140,
            command=self._reveal_file,
        )
        self.open_dir_btn.pack(side="left")
        self.open_dir_btn.pack_forget()
        ctk.CTkButton(self.actions, text="Limpar logs", width=150, command=lambda: self.logs.delete("1.0", "end")).pack(side="left", padx=(8, 0))

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

    def choose_input(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Video", "*.mp4 *.mkv *.avi *.mov *.webm"), ("Todos", "*.*")]
        )
        if file_path:
            self.input_var.set(file_path)

    def choose_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir_var.set(folder)
            self._path_config.set_dest_dir(folder)

    def _set_progress(self, percent, message):
        self.progress.set(max(0.0, min(1.0, percent / 100.0)))
        self.status_label.configure(text=message)
        self.logs.append(message)

    def render(self):
        input_path = self.input_var.get().strip()
        output_dir = self.output_dir_var.get().strip()
        project_name = self.project_var.get().strip()
        if not input_path or not Path(input_path).exists():
            messagebox.showerror("Arquivo invalido", "Selecione um arquivo de video valido.")
            return
        if not output_dir:
            messagebox.showerror("Destino invalido", "Escolha uma pasta de destino.")
            return

        self._path_config.set_project_name(project_name)

        ext = self.format_var.get()
        request = OutputRequest(
            media_type=MediaType.VIDEO,
            category=OutputCategory.RENDER,
            project_name=project_name,
            extension=ext,
        )
        output_path = self._output_organizer.build_output_path(
            request, dest_dir=output_dir, project_name=project_name,
        )

        self.progress.set(0)
        self.logs.append("Iniciando renderizacao...")

        _qp = {
            "Alta": {"crf": 18, "preset": "slow"},
            "Balanceada": {"crf": 22, "preset": "medium"},
            "Compacta": {"crf": 26, "preset": "medium"},
        }
        preset = _qp.get(self.quality_var.get(), _qp["Alta"])

        import os
        import subprocess
        import sys
        try:
            threads = str(max(1, os.cpu_count() or 1))
            cmd = [
                sys.executable, "-m", "ffmpeg",
                "-y",
                "-hide_banner",
                "-loglevel", "error",
                "-threads", threads,
                "-i", str(Path(input_path).resolve()),
                "-ss", self.start_var.get(),
                "-to", self.end_var.get(),
                "-c:v", "libx264",
                "-preset", preset["preset"],
                "-crf", str(preset["crf"]),
                "-c:a", "aac",
                "-b:a", "160k",
                str(output_path),
            ]
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            proc.wait()
            if proc.returncode != 0:
                raise RuntimeError(f"FFmpeg falhou com codigo {proc.returncode}")
            self._last_output_path = output_path
            self.logs.append(f"Video renderizado em: {output_path}")
            self.progress.set(1.0)
            self.status_label.configure(text="Renderizacao concluida.")
            if not self.open_dir_btn.winfo_manager():
                self.open_dir_btn.pack(side="left")
        except Exception as exc:
            messagebox.showerror("Erro na renderizacao", str(exc))
