import flet as ft
from logic.auth import authenticate_by_password
from logic.db import resource_path


def LoginScreen(page, navigator):
    page.title = "Mabat Login"
    page.window_width = 400
    page.window_height = 600

    password_field = ft.TextField(
        password=True,
        can_reveal_password=True,
        width=250,
        label="הכנס סיסמה",
        text_align=ft.TextAlign.CENTER,
        border_color="#f28c7d"
    )

    message = ft.Text("", color=ft.Colors.RED_700, weight=ft.FontWeight.BOLD)

    def handle_login(e):
        user = authenticate_by_password(password_field.value)
        if user:
            navigator.go_home(user)
        else:
            message.value = "סיסמה שגויה"
            message.update()

    login_column = ft.Column(
        controls=[
            password_field,
            ft.ElevatedButton(
                "כניסה",
                on_click=handle_login,
                bgcolor="#52b69a",
                color=ft.Colors.WHITE,
                width=200
            ),
            message
        ],
        alignment=ft.MainAxisAlignment.END,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10
    )

    bg_image = ft.Container(
        content=ft.Image(src=resource_path("assets/shop_bg.png"), fit=ft.ImageFit.CONTAIN),
        alignment=ft.alignment.center,
        expand=True
    )

    page.controls.clear()
    page.add(
        ft.Stack(
            controls=[
                bg_image,
                ft.Container(
                    content=login_column,
                    alignment=ft.alignment.bottom_center,
                    padding=ft.padding.only(bottom=50)
                )
            ],
            expand=True
        )
    )
    page.update()