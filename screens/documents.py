import flet as ft
import os
import sys
from pathlib import Path
import shutil  # להעתקה/הורדה אם צריך
import win32print
import win32api

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    else:
        return Path(__file__).parent

BASE_DIR = get_base_dir()
UPLOAD_DIR = BASE_DIR / "uploaded_files"
UPLOAD_DIR.mkdir(exist_ok=True)

def DocumentsScreen(page, user, navigator):
    page.title = "מסמכים"

    files_column = ft.Column(spacing=12, expand=True)

    # --- פונקציה לרענון תצוגת הקבצים ---
    def refresh_files():
        files_column.controls.clear()
        for i, file_path in enumerate(UPLOAD_DIR.iterdir()):
            if file_path.is_file():
                card = ft.Card(
                    content=ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.DESCRIPTION, size=32, color="#52b69a"),
                                ft.Text(file_path.name, size=18, expand=True),
                                ft.IconButton(
                                    icon=ft.Icons.OPEN_IN_NEW,
                                    tooltip="פתיחה",
                                    icon_color="#52b69a",
                                    on_click=lambda e, fp=file_path: os.startfile(fp)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DOWNLOAD,
                                    tooltip="הורדה",
                                    icon_color="#f28c7d",
                                    on_click=lambda e, fp=file_path: download_file(fp)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.PRINT,
                                    tooltip="הדפסה",
                                    icon_color="#52b69a",
                                    on_click=lambda e, fp=file_path: print_file(fp)
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    tooltip="מחיקה",
                                    icon_color="#d62828",
                                    on_click=lambda e, fp=file_path: (fp.unlink(), refresh_files())
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            spacing=10
                        ),
                        padding=12,
                        bgcolor="#ffffff" if i % 2 == 0 else "#f8f9fa",
                        border_radius=12
                    )
                )
                files_column.controls.append(card)
        page.update()

    # --- פונקציה להעתקת הקובץ ליעד אחר (הורדה) ---
    def download_file(file_path: Path):
        downloads_dir = Path.home() / "Downloads"
        downloads_dir.mkdir(exist_ok=True)
        dest_path = downloads_dir / file_path.name
        shutil.copy(file_path, dest_path)
        print(f"הקובץ הורד ל: {dest_path}")

    # --- פונקציה להדפסה של כל סוגי הקבצים ---
    def print_file(file_path: Path):
        try:
            printer_name = win32print.GetDefaultPrinter()
            win32api.ShellExecute(
                0,
                "print",
                str(file_path),
                f'/d:"{printer_name}"',
                ".",
                0
            )
            print(f"הקובץ נשלח להדפסה: {file_path.name}")
        except Exception as e:
            print(f"שגיאה בהדפסה של {file_path.name}: {e}")

    def print_file(file_path: Path):
        try:
            # אם זה PDF – רק לפתוח
            if file_path.suffix.lower() == ".pdf":
                os.startfile(str(file_path))
                print(f"PDF נפתח (ללא הדפסה): {file_path.name}")
                return

            # כל שאר הקבצים – הדפסה רגילה
            printer_name = win32print.GetDefaultPrinter()
            win32api.ShellExecute(
                0,
                "print",
                str(file_path),
                f'/d:"{printer_name}"',
                ".",
                0
            )
            print(f"הקובץ נשלח להדפסה: {file_path.name}")

        except Exception as e:
            print(f"שגיאה בפעולת הדפסה/פתיחה של {file_path.name}: {e}")

    # --- פונקציה להעלאת קבצים ---
    def on_file_picker_result(e: ft.FilePickerResultEvent):
        if e.files:
            for f in e.files:
                dest = UPLOAD_DIR / f.name
                try:
                    with open(f.path, "rb") as src_file, open(dest, "wb") as out_file:
                        out_file.write(src_file.read())
                except Exception as ex:
                    print(f"שגיאה בשמירת הקובץ {f.name}: {ex}")
            refresh_files()

    file_picker = ft.FilePicker(on_result=on_file_picker_result)

    # --- כפתורי עליון ---
    upload_button = ft.ElevatedButton(
        "📤 העלאת מסמך",
        bgcolor="#52b69a",
        color="white",
        on_click=lambda e: file_picker.pick_files()
    )

    back_button = ft.ElevatedButton(
        "חזרה לבית🏠",
        bgcolor="#f28c7d",
        color="white",
        on_click=lambda e: navigator.go_home(user)
    )

    # --- בניית העמוד ---
    page.controls.clear()
    page.add(
        file_picker,
        ft.Column(
            controls=[
                ft.Text("📂 ניהול מסמכים", size=34, weight=ft.FontWeight.BOLD, color="#52b69a"),
                ft.Row([upload_button, back_button], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                ft.Container(
                    content=ft.ListView(controls=[files_column], expand=True),
                    expand=True,
                    padding=20,
                    bgcolor="#ffe5ec",
                    border_radius=16
                )
            ],
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )
    )

    refresh_files()
    page.update()
