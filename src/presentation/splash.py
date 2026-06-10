from pathlib import Path

import customtkinter as ctk
from PIL import Image


LOGO_PATH = Path(__file__).resolve().parent / "assets" / "logo.png"


class SplashScreen:
    def __init__(self, master: ctk.CTk):
        self._master = master
        self.frame = ctk.CTkFrame(master, corner_radius=16, width=460, height=300)
        self.frame.place(relx=0.5, rely=0.5, anchor="center")

        logo_frame = ctk.CTkFrame(self.frame, fg_color="transparent", height=100)
        logo_frame.pack(fill="x", pady=(16, 0))
        logo_frame.pack_propagate(False)

        if LOGO_PATH.exists():
            pil_image = Image.open(LOGO_PATH)
            ctk_image = ctk.CTkImage(
                dark_image=pil_image, light_image=pil_image, size=(200, 80)
            )
            ctk.CTkLabel(logo_frame, image=ctk_image, text="").pack(anchor="center")
        else:
            ctk.CTkLabel(
                logo_frame,
                text="ALE",
                font=ctk.CTkFont(size=48, weight="bold"),
                text_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"],
            ).pack(anchor="center")

        ctk.CTkLabel(
            self.frame,
            text="AudioLabEditor",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack(pady=(4, 0))

        self.status_label = ctk.CTkLabel(
            self.frame,
            text="Inicializando...",
            font=ctk.CTkFont(size=13),
        )
        self.status_label.pack(pady=(16, 8))

        self.progress_bar = ctk.CTkProgressBar(self.frame, width=360, height=10)
        self.progress_bar.pack()
        self.progress_bar.set(0)

        self._master.update()

    def set_progress(self, value: float, message: str = ""):
        self.progress_bar.set(value)
        if message:
            self.status_label.configure(text=message)
        self._master.update()

    def close(self):
        self.frame.destroy()
        self._master.update_idletasks()
