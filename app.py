import flet as ft

from logic.reminder import check_or_create_reminder, mark_done
from navigation import Navigator

def main(page: ft.Page):
    navigator = Navigator(page)
    navigator.go_login()
    page.rtl = True
    page.update()
    reminder = check_or_create_reminder()
    reminder_card = None
    if reminder:
        month_year = reminder["month_year"]

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