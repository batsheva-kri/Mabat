import flet as ft
from navigation import Navigator

def main(page: ft.Page):
    navigator = Navigator(page)
    navigator.go_login()

ft.app(target=main)
