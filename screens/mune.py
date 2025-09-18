import flet as ft
from .inventory import InventoryScreen
from logic.suppliers import get_all_suppliers

def InventoryMenuScreen(page, current_user, navigator, save_arrived, save_existing):
    page.title = "ניהול מלאי"

    def show_supplier_dropdown(save_fn):
        suppliers = get_all_suppliers()
        options = [ft.dropdown.Option(str(s["id"]), s["name"]) for s in suppliers]
        supplier_var = ft.Dropdown(
            label="בחר ספק",
            options=options,
            width=300
        )
        confirm_btn = ft.ElevatedButton(
            "המשך",
            on_click=lambda e: InventoryScreen(
                page,
                current_user,
                navigator,
                save_fn=lambda s: save_fn,
                supplier_id=supplier_var.value
            )
        )
        page.controls.clear()
        page.add(
            ft.Column(
                controls=[
                    ft.Text("בחר ספק למלאי שהגיע", size=22, weight=ft.FontWeight.BOLD),
                    supplier_var,
                    confirm_btn,
                    ft.ElevatedButton("⬅ חזרה", on_click=lambda e: navigator.go_orders(current_user))
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        )
        page.update()

    def go_arrived(e):
        show_supplier_dropdown(save_arrived)

    def go_existing(e):
        InventoryScreen(page, current_user, navigator, save_fn = save_existing,supplier_id=0)

    page.controls.clear()
    page.add(
        ft.Column(
            controls=[
                ft.Text("בחר פעולה", size=22, weight=ft.FontWeight.BOLD),
                ft.ElevatedButton("מלאי שהגיע", on_click=go_arrived),
                ft.ElevatedButton("כמויות קיימות במלאי", on_click=go_existing),
                ft.ElevatedButton("⬅ חזרה", on_click=lambda e: navigator.go_orders(current_user)),
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )
    )
    page.update()
