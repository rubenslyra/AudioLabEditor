import sys
import tkinter as tk
from tkinter import messagebox

from application.bootstrap import validate_startup


def show_startup_error(message: str) -> None:
    root = tk.Tk()
    root.withdraw()
    messagebox.showerror("Dependencias ausentes", message)
    root.destroy()


def build_window():
    try:
        import customtkinter as ctk
    except Exception:
        root = tk.Tk()
        root.title("AudioLabEditor")
        label = tk.Label(root, text="AudioLabEditor\nCustomTkinter nao esta disponivel.", padx=32, pady=32)
        label.pack()
        return root

    app = ctk.CTk()
    app.title("AudioLabEditor")
    app.geometry("1120x720")
    app.minsize(960, 640)
    title = ctk.CTkLabel(app, text="AudioLabEditor", font=ctk.CTkFont(size=28, weight="bold"))
    title.pack(anchor="w", padx=24, pady=(24, 8))
    subtitle = ctk.CTkLabel(
        app,
        text="Scaffold da aplicacao mesclada: captura, edicao e separacao de stems.",
    )
    subtitle.pack(anchor="w", padx=24, pady=(0, 24))
    status = ctk.CTkLabel(app, text="Fase 0: infraestrutura portavel e startup doctor.")
    status.pack(anchor="w", padx=24)
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
