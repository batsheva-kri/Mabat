import threading
import os

def print_pdf_async(pdf_path):
    threading.Thread(
        target=lambda: os.startfile(pdf_path, "print"),
        daemon=True
    ).start()
