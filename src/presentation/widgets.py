import customtkinter as ctk


class LogBox(ctk.CTkTextbox):
    def append(self, text: str):
        self.insert("end", text + "\n")
        self.see("end")
