import flet as ft
from logic.auth import logout
from .employees import EmployeeManagementScreen
from .calculator import CalculatorScreen
from .catalog import CatalogScreen

def HomeScreen(page, user, navigator):
    page.scroll = "always"
    connected_users = navigator.connected_users
    is_manager = user['role'] == 'manager'

    def perform_logout(u):
        logout(u["id"])
        navigator.connected_users[:] = [x for x in connected_users if x["id"] != u["id"]]
        # אם אין משתמשים מחוברים – חזרה למסך התחברות
        if not navigator.connected_users:
            navigator.go_login()
        else:
            HomeScreen(page, navigator.connected_users[0], navigator)

    # --- טקסט עם כל המשתמשים המחוברים ---
    users_column = ft.Column(
        controls=[
            ft.Row(
                controls=[
                    ft.Text(f"{u['user_name']} ({'מנהל' if u['role']=='manager' else 'עובד'})",
                            size=16, weight=ft.FontWeight.BOLD, color="#52b69a"),
                    ft.ElevatedButton("התנתק", on_click=lambda e, uu=u: perform_logout(uu), bgcolor="#f28c7d", color="white")
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            ) for u in connected_users
        ],
        spacing=10
    )

    # --- כרטיסי פעולה ---
    base_buttons = [("מחירון", "#ffddd2"), ("המרת מספרים", "#ffe5ec"),
                    ("מחשבון", "#e0fbfc"), ("מסמכים", "#edf6f9"), ("הזמנות", "#fefae0")]
    if is_manager:
        base_buttons += [("ניהול עובדים", "#caffbf"), ("ניהול ספקים", "#9bf6ff"), ("מעקב משלוחים", "#ffd6a5")]

    cards = []
    for label, color in base_buttons:
        def make_handler(lbl):
            def handler(e):
                if lbl == "ניהול עובדים":
                    navigator.go_employee_management(user)
                elif lbl == "מחשבון":
                    navigator.go_calculator(user)
                elif lbl == "מחירון":
                    navigator.go_catalog(user,"inventory")
                elif lbl == "המרת מספרים":
                    page.launch_url("https://www.jnjvisionpro.com/he-il/calculators/astigmatism-fitting-calculator/")
                elif lbl == "מסמכים":
                    navigator.go_documents(user)
                elif lbl == "הזמנות":
                    navigator.go_orders(user)
                elif lbl == "ניהול ספקים":
                    navigator.go_suppliers(user)
            return handler



        btn = ft.Container(
            content=ft.Text(label, size=20, weight=ft.FontWeight.BOLD, color="black"),
            bgcolor=color,
            border_radius=20,
            alignment=ft.alignment.center,
            padding=40,
            ink=True,
            on_click=make_handler(label)
        )
        cards.append(btn)

    # --- כפתורי ניווט תחתונים ---
    multi_login_button = ft.Container(
        content=ft.Text("כניסה מרובה", size=16, weight=ft.FontWeight.BOLD, color="white"),
        bgcolor="#52b69a",
        border_radius=12,
        alignment=ft.alignment.center,
        padding=ft.padding.symmetric(vertical=10, horizontal=20),
        ink=True,
        on_click=lambda e: navigator.go_login()
    )

    # --- בניית העמוד ---
    page.controls.clear()
    page.add(
        ft.Column(
            controls=[
                ft.Text("משתמשים מחוברים:", size=22, weight=ft.FontWeight.BOLD, color="#52b69a", text_align=ft.TextAlign.CENTER),
                users_column,
                ft.GridView(
                    expand=1,
                    runs_count=1,
                    max_extent=400,
                    child_aspect_ratio=2,
                    spacing=15,
                    run_spacing=15,
                    controls=cards
                ),
                multi_login_button
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        )
    )
    page.update()