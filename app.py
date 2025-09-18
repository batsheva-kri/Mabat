# import flet as ft
#
# from logic.reminder import check_or_create_reminder, mark_done
# from screens.login import LoginScreen
# from screens.home import HomeScreen
# from screens.mainInventory import MainInvitationScreen
# from screens.suppliers import SuppliersScreen
#
#
# def main(page: ft.Page):
#     page.title = "מבט"
#     user_data = {}

#     # --- מעבר למסך הבית ---
#     def go_home(user):
#         user_data["current"] = user
#         HomeScreen(
#             page,
#             user,
#             go_login,
#             go_orders,
#             go_suppliers
#         )
#
#     # --- מסך התחברות ---
#     def go_login():
#         LoginScreen(page, go_home)
#     def go_suppliers(e):
#         SuppliersScreen(page, user_data["current"],go_home(user_data["current"]))
#     # --- מסך הזמנות / מסך ראשי לאחר התחברות ---
#     def go_orders(e=None):
#
#         # כאן שולחים callbacks למסכים הנכונים
#         MainInvitationScreen(
#             page,
#             current_user=user_data["current"],
#             go_back=lambda: go_home
#         )
#
#     print(page.controls)
#     go_login()
#
#
# ft.app(target=main)
import flet as ft

from logic.reminder import check_or_create_reminder, mark_done
from navigation import Navigator

def main(page: ft.Page):
    navigator = Navigator(page)
    navigator.go_login()   # מתחילים במסך ההתחברות
    page.rtl = True
    page.update()
    reminder = check_or_create_reminder()
    reminder_card = None
    if reminder:
        month_year = reminder["month_year"]
        print("I use reminder")

        def on_done(e):
            mark_done(month_year)
            page.snack_bar = ft.SnackBar(ft.Text("המשימה סומנה כבוצעה ✅"))
            page.snack_bar.open = True
            if reminder_card in page.overlay:
                page.overlay.remove(reminder_card)
            page.update()

        reminder_card = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Text("תזכורת לבדיקת מלאי!", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text("יש לבצע בדיקת מלאי החודש."),
                        ft.ElevatedButton("סימנתי שביצעתי", on_click=on_done, bgcolor="green", color="white"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20,
                bgcolor=ft.Colors.AMBER_100,
            ),
        )
        page.overlay.append(reminder_card)
        page.update()
ft.app(target=main)