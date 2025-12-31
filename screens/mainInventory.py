import flet as ft
from logic.inventory import save_existing_inventory
from logic.suppliers import save_arrived_inventory

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

    # פונקציות למסכים
    def go_existing_customer_click(e=None):
        navigator.go_customer(current_user)

    def go_new_customer_click(e=None):
        navigator.go_new_customer(current_user)

    def go_supply_click(e=None):
        navigator.go_invitations_supply(current_user)

    def go_inventory_arrived_click(e=None):
        navigator.go_inventory_screen(current_user, save_fn=save_arrived_inventory, show_dropdown=True)

    def go_inventory_existing_click(e=None):
        navigator.go_inventory_screen(current_user, save_fn=save_existing_inventory, show_dropdown=False)

    # כפתורים ללקוח
    customer_section = ft.Column(
        controls=[
            ft.Text("לקוח", size=22, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton("הזמנה שהגיעה", on_click=go_supply_click),
            ft.ElevatedButton("לקוח קיים", on_click=go_existing_customer_click),
            ft.ElevatedButton("לקוח חדש", on_click=go_new_customer_click),
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # כפתורים למלאי
    inventory_section = ft.Column(
        controls=[
            ft.Text("מלאי", size=22, weight=ft.FontWeight.BOLD),
            ft.ElevatedButton("מלאי שהגיע", on_click=go_inventory_arrived_click),
            ft.ElevatedButton("כמויות קיימות במלאי", on_click=go_inventory_existing_click),
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.START,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    back_button = ft.ElevatedButton("⬅ חזרה", on_click=lambda e: navigator.go_home(current_user))

    # מסך מחולק לשני חלקים בצורה אופקית
    page.controls.clear()
    page.add(
        ft.Column(
            controls=[
                header,
                ft.Row(
                    controls=[
                        customer_section,
                        inventory_section
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    spacing=50
                ),
                back_button
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=30
        )
    )
    page.update()
import flet as ft
from logic.inventory import save_existing_inventory
from logic.suppliers import save_arrived_inventory


def MainInvitationScreen(page, navigator, current_user):
    page.title = "מערכת הזמנות"
    page.window_width = 800
    page.window_height = 600

    # כותרת
    header = ft.Text(
        f"ברוך הבא, {current_user['user_name']}",
        size=26,
        weight=ft.FontWeight.BOLD,
        color="#52b69a",
        text_align=ft.TextAlign.CENTER
    )

    # פונקציות ניווט
    def go_existing_customer_click(e):
        navigator.go_customer(current_user)

    def go_new_customer_click(e):
        navigator.go_new_customer(current_user)

    def go_supply_click(e):
        navigator.go_invitations_supply(current_user)

    def go_inventory_arrived_click(e):
        navigator.go_inventory_screen(
            current_user,
            save_fn=save_arrived_inventory,
            show_dropdown=True
        )

    def go_inventory_existing_click(e):
        navigator.go_inventory_screen(
            current_user,
            save_fn=save_existing_inventory,
            show_dropdown=False
        )

    # עיצוב אחיד לכפתורים
    def styled_button(text, on_click, bg):
        return ft.ElevatedButton(
            text=text,
            on_click=on_click,
            bgcolor=bg,
            color=ft.Colors.WHITE,
            width=220,
            height=45,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=12),
                elevation=4
            )
        )

    # אזור לקוח
    customer_section = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("👤 לקוח", size=22, weight=ft.FontWeight.BOLD, color="#4d96ff"),
                styled_button("📦 הזמנה שהגיעה", go_supply_click, "#52b69a"),
                styled_button("🔁 לקוח קיים", go_existing_customer_click, "#4d96ff"),
                styled_button("➕ לקוח חדש", go_new_customer_click, "#e63946"),
            ],
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=20,
        bgcolor="#f8f9fa",
        border_radius=15,
        width=300
    )

    # אזור מלאי
    inventory_section = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text("📦 מלאי", size=22, weight=ft.FontWeight.BOLD, color="#52b69a"),
                styled_button("📥 מלאי שהגיע", go_inventory_arrived_click, "#52b69a"),
                styled_button("📊 כמויות קיימות", go_inventory_existing_click, "#4d96ff"),
            ],
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        padding=20,
        bgcolor="#f8f9fa",
        border_radius=15,
        width=300
    )

    # כפתור חזרה
    back_button = ft.ElevatedButton(
        "חזרה לבית🏠",
        on_click=lambda e: navigator.go_home(current_user),
        bgcolor="#f28c7d",
        color=ft.Colors.WHITE,
        width=140,
        style=ft.ButtonStyle(
            shape=ft.RoundedRectangleBorder(radius=12),
            elevation=4
        )
    )

    # בניית המסך
    page.controls.clear()
    page.add(
        ft.Column(
            controls=[
                header,
                ft.Row(
                    controls=[customer_section, inventory_section],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    spacing=40
                ),
                back_button
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=30
        )
    )

    page.update()
