import tkinter as tk

def open_homepage(is_admin):
    window = tk.Tk()
    window.title("דף הבית")
    window.geometry("300x200")

    welcome_label = tk.Label(window, text="ברוכה הבאה לחנות!", font=("Arial", 14))
    welcome_label.pack(pady=10)

    btn_inventory = tk.Button(window, text="צפייה במלאי")
    btn_inventory.pack(pady=5)

    btn_sales = tk.Button(window, text="ניהול מכירות")
    btn_sales.pack(pady=5)

    if is_admin:
        btn_report = tk.Button(window, text="דוח עובדים")
        btn_report.pack(pady=5)

    window.mainloop()
