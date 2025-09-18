import flet as ft
from logic.auth import logout

def HomeScreen(page, user, navigator):
    is_manager = user['role'] == 'manager'
    page.scroll = "always"  # אפשר גם "auto" או "hidden"
    def handle_logout(e):
        logout(user['id'])
        navigator.go_login()

    # כותרת עם שם המשתמש
    user_title = ft.Text(
        f"שלום {user['user_name']} ({'מנהל' if is_manager else 'עובד'})",
        size=24,
        weight=ft.FontWeight.BOLD,
        color="#52b69a" if not is_manager else "#f28c7d",
        text_align=ft.TextAlign.CENTER,
    )

    # רשימת כרטיסי פעולה
    base_buttons = [
        ("מחירון", "#ffddd2", None),
        ("המרת מספרים", "#ffe5ec", None),
        ("מחשבון", "#e0fbfc", None),
        ("מסמכים", "#edf6f9", None),
        ("הזמנות", "#fefae0", lambda e: navigator.go_orders(user)),
    ]

    if is_manager:
        base_buttons += [
            ("ניהול עובדים", "#caffbf", None),
            ("ניהול ספקים", "#9bf6ff", lambda e: navigator.go_suppliers(user)),
            ("חשבון חודשי", "#ffd6a5", None),
        ]

    # יצירת כרטיסים גדולים
    cards = []
    for label, color, callback in base_buttons:
        btn = ft.Container(
            content=ft.Text(label, size=20, weight=ft.FontWeight.BOLD, color="black"),
            bgcolor=color,
            border_radius=20,
            alignment=ft.alignment.center,
            padding=ft.padding.symmetric(vertical=40, horizontal=20),
            ink=True,
            on_click=callback  # לחיצה על הכרטיס מפעילה את callback
        )
        cards.append(btn)

    # כפתור התנתקות קטן ומובדל
    logout_button = ft.Container(
        content=ft.Text("התנתקות", size=16, weight=ft.FontWeight.BOLD, color="white"),
        bgcolor="#ff4d4d",
        border_radius=12,
        alignment=ft.alignment.center,
        padding=ft.padding.symmetric(vertical=10, horizontal=20),
        ink=True,
        on_click=handle_logout
    )

    page.controls.clear()
    page.add(
        ft.Column(
            controls=[
                user_title,
                ft.GridView(
                    expand=1,
                    runs_count=1,
                    max_extent=400,
                    child_aspect_ratio=2,
                    spacing=15,
                    run_spacing=15,
                    controls=cards,
                ),
                ft.Container(height=20),
                logout_button
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        )
    )
    page.update()
# import flet as ft
# from logic.auth import logout
# from screens.mainInventory import MainInvitationScreen
# from screens.customers import ExistingCustomerScreen
# # אם יש מסכים נוספים של לקוחות, ניתן להוסיף אותם כאן
#
# def HomeScreen(page, user, navigator):
#     is_manager = user['role'] == 'manager'
#     page.scroll = "always"  # אפשר גם "auto" או "hidden"
#
#     def handle_logout(e):
#         logout(user['id'])
#         navigator.go_login()
#
#     # כותרת עם שם המשתמש
#     user_title = ft.Text(
#         f"שלום {user['user_name']} ({'מנהל' if is_manager else 'עובד'})",
#         size=24,
#         weight=ft.FontWeight.BOLD,
#         color="#52b69a" if not is_manager else "#f28c7d",
#         text_align=ft.TextAlign.CENTER,
#     )
#
#     # רשימת כרטיסי פעולה
#     base_buttons = [
#         ("מחירון", "#ffddd2", lambda e: navigator.go_catalog(user, mode="inventory")),
#         ("המרת מספרים", "#ffe5ec", lambda e: MainInvitationScreen(page, navigator, user, go_back=lambda: HomeScreen(page, user, navigator))),
#         ("מחשבון", "#e0fbfc", lambda e: print("מחשבון")),  # כאן תכניסי את המסך המתאים
#         ("מסמכים", "#edf6f9", lambda e: print("מסמכים")),   # כאן תכניסי את המסך המתאים
#         ("הזמנות", "#fefae0", lambda e: ExistingCustomerScreen(page, navigator, user, go_back=lambda: HomeScreen(page, user, navigator))),
#     ]
#
#     if is_manager:
#         base_buttons += [
#             ("ניהול עובדים", "#caffbf", lambda e: print("ניהול עובדים")),  # כאן תכניסי את המסך המתאים
#             ("ניהול ספקים", "#9bf6ff", lambda e: navigator.go_supplier(user)),
#             ("חשבון חודשי", "#ffd6a5", lambda e: print("חשבון חודשי")),  # כאן תכניסי את המסך המתאים
#         ]
#
#     # יצירת כרטיסים גדולים
#     cards = []
#     for label, color, callback in base_buttons:
#         btn = ft.Container(
#             content=ft.Text(label, size=20, weight=ft.FontWeight.BOLD, color="black"),
#             bgcolor=color,
#             border_radius=20,
#             alignment=ft.alignment.center,
#             padding=ft.padding.symmetric(vertical=40, horizontal=20),
#             ink=True,
#             on_click=callback
#         )
#         cards.append(btn)
#
#     # כפתור התנתקות קטן ומובדל
#     logout_button = ft.Container(
#         content=ft.Text("התנתקות", size=16, weight=ft.FontWeight.BOLD, color="white"),
#         bgcolor="#ff4d4d",
#         border_radius=12,
#         alignment=ft.alignment.center,
#         padding=ft.padding.symmetric(vertical=10, horizontal=20),
#         ink=True,
#         on_click=handle_logout
#     )
#
#     # כפתור חזור במסך הבית (אם רוצים)
#     back_button = ft.Container(
#         content=ft.Text("⬅ חזור", size=16, weight=ft.FontWeight.BOLD, color="white"),
#         bgcolor="#52b69a",
#         border_radius=12,
#         alignment=ft.alignment.center,
#         padding=ft.padding.symmetric(vertical=10, horizontal=20),
#         ink=True,
#         on_click=lambda e: navigator.go_login()
#     )
#
#     page.controls.clear()
#     page.add(
#         ft.Column(
#             controls=[
#                 user_title,
#                 ft.GridView(
#                     expand=1,
#                     runs_count=1,
#                     max_extent=400,
#                     child_aspect_ratio=2,
#                     spacing=15,
#                     run_spacing=15,
#                     controls=cards,
#                 ),
#                 ft.Container(height=20),
#                 ft.Row([back_button, logout_button], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
#             ],
#             expand=True,
#             alignment=ft.MainAxisAlignment.START,
#             horizontal_alignment=ft.CrossAxisAlignment.CENTER,
#             spacing=15,
#         )
#     )
#     page.update()
