import flet as ft

def InventoryMenuScreen(page, current_user, navigator, save_arrived, save_existing):
    page.title = "ניהול מלאי"

    page.controls.clear()
    page.add(
        ft.Column(
            controls=[
                ft.Text("בחר פעולה", size=22, weight=ft.FontWeight.BOLD),

                # מלאי שהגיע → לוקח ישר למסך מלאי בלי dropdown
                ft.ElevatedButton(
                    "מלאי שהגיע",
                    on_click=lambda e: navigator.go_inventory_screen(
                        current_user,
                        save_fn=save_arrived,
                        show_dropdown=True    # לא צריך dropdown
                    )
                ),

                # כמויות קיימות במלאי → גם לוקח ישר למסך מלאי
                ft.ElevatedButton(
                    "כמויות קיימות במלאי",
                    on_click=lambda e: navigator.go_inventory_screen(
                        current_user,
                        save_fn=save_existing,
                        show_dropdown=False
                    )
                ),

                ft.ElevatedButton("⬅ חזרה", on_click=lambda e: navigator.go_orders(current_user)),
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )
    )
    page.update()
