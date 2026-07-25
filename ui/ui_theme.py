# ui/ui_theme.py
"""
UI Theme y componentes visuales para la aplicación BiblioRUA.
Soporta CustomTkinter con fallback a Tkinter estándar.
"""

import tkinter as tk
from tkinter import ttk

try:
    import customtkinter as ctk
    HAS_CTK = True
except ImportError:
    HAS_CTK = False

# Paleta de colores moderna RUA / UNAH
COLORS = {
    "navy": "#1E293B",
    "gold": "#D97706",
    "cream": "#F8FAFC",
    "white": "#FFFFFF",
    "text_muted": "#64748B",
    "danger": "#EF4444",
    "warning": "#F59E0B",
    "success": "#10B981",
    "border": "#E2E8F0"
}

FONT_SECTION = ("Poppins", 14, "bold") if HAS_CTK else ("Helvetica", 12, "bold")
FONT_BODY = ("Poppins", 11) if HAS_CTK else ("Helvetica", 10)
FONT_SMALL = ("Poppins", 10) if HAS_CTK else ("Helvetica", 9)


if HAS_CTK:
    class StatusBadge(ctk.CTkFrame):
        def __init__(self, parent, text, status="success", **kwargs):
            bg_color = COLORS.get(status, COLORS["navy"])
            super().__init__(parent, fg_color=bg_color, corner_radius=12, **kwargs)
            label = ctk.CTkLabel(self, text=text, font=FONT_SMALL, text_color=COLORS["white"])
            label.pack(padx=10, pady=4)

    class AppShell(ctk.CTk):
        def __init__(self, app_title="BiblioRUA", screen_title="Préstamos", screen_subtitle="", menu_items=None, active_item="", **kwargs):
            super().__init__(**kwargs)
            self.title(app_title)
            self.geometry("1000x700")
            ctk.set_appearance_mode("light")

            # Header
            self.header = ctk.CTkFrame(self, fg_color=COLORS["navy"], corner_radius=0, height=80)
            self.header.pack(fill="x", side="top")
            
            title_lbl = ctk.CTkLabel(self.header, text=screen_title, font=("Poppins", 20, "bold"), text_color=COLORS["white"])
            title_lbl.pack(anchor="w", padx=24, pady=(14, 0))

            if screen_subtitle:
                sub_lbl = ctk.CTkLabel(self.header, text=screen_subtitle, font=FONT_SMALL, text_color=COLORS["cream"])
                sub_lbl.pack(anchor="w", padx=24, pady=(0, 10))

            # Contenido principal
            self.content = ctk.CTkFrame(self, fg_color=COLORS["cream"], corner_radius=0)
            self.content.pack(fill="both", expand=True)

else:
    # Fallback Tkinter Estándar si customtkinter no está instalado
    class StatusBadge(tk.Frame):
        def __init__(self, parent, text, status="success", **kwargs):
            bg_color = COLORS.get(status, COLORS["navy"])
            super().__init__(parent, bg=bg_color, **kwargs)
            label = tk.Label(self, text=text, font=FONT_SMALL, fg="white", bg=bg_color)
            label.pack(padx=8, pady=2)

    class AppShell(tk.Tk):
        def __init__(self, app_title="BiblioRUA", screen_title="Préstamos", screen_subtitle="", menu_items=None, active_item="", **kwargs):
            super().__init__(**kwargs)
            self.title(app_title)
            self.geometry("1000x700")
            self.configure(bg=COLORS["cream"])

            # Header
            self.header = tk.Frame(self, bg=COLORS["navy"], height=70)
            self.header.pack(fill="x", side="top")
            
            title_lbl = tk.Label(self.header, text=screen_title, font=("Helvetica", 16, "bold"), fg="white", bg=COLORS["navy"])
            title_lbl.pack(anchor="w", padx=20, pady=(10, 0))

            if screen_subtitle:
                sub_lbl = tk.Label(self.header, text=screen_subtitle, font=FONT_SMALL, fg=COLORS["cream"], bg=COLORS["navy"])
                sub_lbl.pack(anchor="w", padx=20, pady=(0, 10))

            # Contenido principal
            self.content = tk.Frame(self, bg=COLORS["cream"])
            self.content.pack(fill="both", expand=True, padx=10, pady=10)
