import asyncio
import flet as ft

from logic.inventory import save_existing_inventory
from logic.suppliers import save_arrived_inventory
from .mune import InventoryMenuScreen
from .customers import ExistingCustomerScreen
from .new_customer_page import NewCustomerPage

def MainInvitationScreen(page, navigator, current_user):
    page.title = "מערכת הזמנות"
    page.window_width = 800
    page.window_height = 600

    header = ft.Text(
        f"ברוך הבא, {current_user['user_name']}",
        size=24,
        weight=ft.FontWeight.BOLD,
        color="#52b69a",
        text_align=ft.TextAlign.CENTER
    )

    # פונקציות מעבר למסכים
    def go_existing_customer_click(e=None):
        ExistingCustomerScreen(page, current_user, navigator)

    def go_new_customer_click(e=None):
        NewCustomerPage(page, current_user, navigator)

    def go_inventory_click(e=None):
        InventoryMenuScreen(
            page,
            current_user,
            navigator,
            save_arrived=save_arrived_inventory,
            save_existing=save_existing_inventory
        )

    # לחיצה על "לקוח" – פותחת דיאלוג לבחירה בין קיים/חדש
    def customer_button_click(e):
        async def select_existing(e):
            page.dialog.open = False
            page.update()
            await asyncio.sleep(0.1)  # דיליי קטן
            go_existing_customer_click()

        async def select_new(e):
            page.dialog.open = False
            page.update()
            await asyncio.sleep(0.1)  # דיליי קטן
            go_new_customer_click()

        dialog = ft.AlertDialog(
            title=ft.Text("בחר סוג לקוח"),
            content=ft.Column(
                controls=[
                    ft.ElevatedButton("הזמנה שהגיעה", on_click=lambda e: navigator.go_invitations_supply(current_user)),
                    ft.ElevatedButton("לקוח קיים", on_click=lambda e: asyncio.run(select_existing(e))),
                    ft.ElevatedButton("לקוח חדש", on_click=lambda e: asyncio.run(select_new(e)))
                ],
                spacing=10
            ),
            actions=[]
        )

        page.dialog = dialog
        page.dialog.open = True
        page.add(page.dialog)
        page.update()
    # כפתורי ניווט
    buttons_info = [
        ("לקוח", "#c0f7b3", customer_button_click),
        ("למלאי", "#ffddb3", go_inventory_click),
    ]

    cards = []
    for label, color, callback in buttons_info:
        card = ft.Container(
            content=ft.Text(label, size=20, weight=ft.FontWeight.BOLD, color="black"),
            bgcolor=color,
            border_radius=20,
            alignment=ft.alignment.center,
            padding=ft.padding.symmetric(vertical=40, horizontal=20),
            ink=True,
            on_click=callback
        )
        cards.append(card)

    grid = ft.GridView(
        expand=True,
        runs_count=2,
        max_extent=350,
        child_aspect_ratio=2,
        spacing=15,
        run_spacing=15,
        controls=cards
    )

    back_button = ft.ElevatedButton("⬅ חזרה", on_click=lambda e: navigator.go_home(current_user))

    page.controls.clear()
    page.add(
        ft.Column(
            controls=[header, grid, back_button],
            expand=True,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )
    )
    page.update()
