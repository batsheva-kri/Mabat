import ttkbootstrap as ttk
from ttkbootstrap.constants import *

def setup_style():
    style = ttk.Style()
    style.theme_use("litera")

    style.configure("TFrame", background="#fff0f6")  # ורוד לבן בהיר
    style.configure("TLabel",
                    background="#fff0f6",
                    foreground="#4a4a4a",
                    font=("Arial", 14))
    style.configure("Header.TLabel",
                    font=("Arial", 18, "bold"),
                    foreground="#b2226f")  # ורוד חזק לכותרות

    style.configure("TEntry",
                    font=("Arial", 14),
                    justify="right",
                    foreground="#333")

    style.configure("TButton",
                    font=("Arial", 14, "bold"),
                    padding=10,
                    relief="flat",
                    borderwidth=0,
                    background="#a3d9a5",  # ירוק בהיר
                    foreground="white")
    style.map("TButton",
              background=[("active", "#7bc16e"), ("!disabled", "#4CAF50")],
              foreground=[("active", "white")])

    style.configure("Accent.TButton",
                    font=("Arial", 14, "bold"),
                    padding=10,
                    background="#b2226f",  # ורוד כהה לכפתורי Accent
                    foreground="white",
                    relief="flat",
                    borderwidth=0)
    style.map("Accent.TButton",
              background=[("active", "#801340"), ("!disabled", "#b2226f")],
              foreground=[("active", "white")])

    style.configure("Treeview",
                    font=("Arial", 12),
                    background="white",
                    fieldbackground="white",
                    foreground="#333")
    style.configure("Treeview.Heading",
                    font=("Arial", 14, "bold"),
                    background="#fce4ec",  # ורוד חיוור לכותרות
                    foreground="#b2226f",
                    relief="flat")

    # גלילה ומראה נעים
    style.configure("Vertical.TScrollbar",
                    gripcount=0,
                    background="#f0f0f0",
                    troughcolor="#ddd",
                    bordercolor="#ccc",
                    arrowcolor="#b2226f")

    return style
def set_3_4_size(self, window):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    width = int(screen_width * 0.75)
    height = int(screen_height * 0.75)
    window.geometry(f"{width}x{height}")
