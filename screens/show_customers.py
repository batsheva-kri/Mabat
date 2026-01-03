import flet as ft
from logic.customers import get_all_customers, update_customer, delete_customer


def CustomersScreen(page, navigator, user):
    page.title = "לקוחות"

    # --- טבלת הלקוחות ---
    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("שם", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("טלפון", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("טלפון 2", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("כתובת", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("אימייל", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("הערות", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("פעולות", size=18, weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        heading_row_color="#52b69a",
        border=ft.border.all(1, ft.Colors.GREY_300),
        column_spacing=20,
        divider_thickness=1,
        data_row_min_height=50,
        expand=True
    )

    def handle_delete_customer(customer_id):
        delete_customer(customer_id)
        load_customers()

    # --- שליפת לקוחות ---
    def load_customers():
        rows = get_all_customers()
        data_table.rows.clear()
        for i, c in enumerate(rows):
            actions = ft.Row([
                ft.IconButton(
                    icon=ft.Icons.EDIT,
                    tooltip="ערוך",
                    on_click=lambda e, cid=c["id"]: open_customer_dialog(cid)
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    tooltip="מחק",
                    on_click=lambda e, cid=c["id"]: handle_delete_customer(cid)
                )

            ])

            data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(c["name"])),
                        ft.DataCell(ft.Text(c["phone"] or "-")),
                        ft.DataCell(ft.Text(c["phone2"] or "-")),
                        ft.DataCell(ft.Text(c["address"] or "-")),
                        ft.DataCell(ft.Text(c["email"] or "-")),
                        ft.DataCell(ft.Text(c["notes"] or "-")),
                        ft.DataCell(actions),
                    ],
                    color="#f28c7d" if i % 2 == 0 else "#ffffff"
                )
            )

        page.update()

    # --- חלון עריכת לקוח ---
    def open_customer_dialog(customer_id):
        customer = next(c for c in get_all_customers() if c["id"] == customer_id)

        name_field = ft.TextField(label="שם", value=customer["name"])
        phone_field = ft.TextField(label="טלפון", value=customer["phone"], width=200)
        phone2_field = ft.TextField(label="טלפון נוסף", value=customer["phone2"], width=200)
        address_field = ft.TextField(label="כתובת", value=customer["address"])
        email_field = ft.TextField(label="אימייל", value=customer["email"])
        notes_field = ft.TextField(label="הערות", value=customer["notes"], multiline=True, width=300)

        def close_dialog():
            page.overlay.clear()
            page.update()


        def save_customer(e):
            update_customer(
                customer_id,
                {
                    "name": name_field.value,
                    "phone": phone_field.value,
                    "phone2": phone2_field.value,
                    "address": address_field.value,
                    "email": email_field.value,
                    "notes": notes_field.value,
                }
            )
            close_dialog()
            load_customers()

        dlg_content = ft.Column(
            [
                name_field,
                phone_field,
                phone2_field,
                address_field,
                email_field,
                notes_field
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO
        )

        page.overlay.clear()
        page.overlay.append(
            ft.Container(
                content=ft.Column([
                    ft.Text("עריכת לקוח", size=24, weight=ft.FontWeight.BOLD),
                    dlg_content,
                    ft.Row([
                        ft.ElevatedButton("שמור", on_click=save_customer, bgcolor="#52b69a", color="white"),
                        ft.ElevatedButton("ביטול", on_click=lambda e: close_dialog(), bgcolor="#f28c7d", color="white"),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=12)
                ], spacing=15),
                padding=20,
                bgcolor="#ffffff",
                border_radius=14
            )
        )
        page.update()

    # --- כפתורי פעולה ---
    controls = ft.Column([
        ft.Row([
            ft.ElevatedButton(
                "חזרה לבית🏠",
                on_click=lambda e: navigator.go_home(user),
                width=120,
                bgcolor="#f28c7d",
                color="white"
            ),
            ft.ElevatedButton(
                "לקוח חדש🪪",
                on_click=lambda e: navigator.go_new_customer(user, invitation=False),
                width=120,
                bgcolor="#52b69a",
                color="white"
            )
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),

        ft.Container(
            content=ft.ListView([data_table], padding=0, expand=True),
            expand=True,
            padding=10,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300)
        )
    ], spacing=15, expand=True, scroll=ft.ScrollMode.AUTO,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    page.controls.clear()
    page.add(controls)
    load_customers()
    page.update()
