import flet as ft
from logic.suppliers import get_all_suppliers, delete_supplier
from screens.suppliers_forms import AddSupplierForm, EditSupplierForm, DeleteSupplierForm
from screens.supplier_orders import OrdersView
from screens.supplier_reports import SupplierReports
from screens.supplier_catalog import SupplierCatalog


def SuppliersScreen(page, user, navigator):
    def update_table():
        suppliers = get_all_suppliers()
        supplier_table.rows.clear()

        for i, sl in enumerate(suppliers):
            supplier_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(sl["id"])),
                        ft.DataCell(ft.Text(sl["name"])),
                        ft.DataCell(ft.Text(sl["phone"])),
                        ft.DataCell(ft.Text(sl["email"])),
                        ft.DataCell(
                            ft.Row([
                                ft.IconButton(icon="edit",
                                              on_click=lambda e, s=sl: EditSupplierForm(page, supplier_data=s,
                                                                                       on_save=update_table).open()),
                                ft.IconButton(icon="delete",
                                              on_click=lambda e, s=sl: DeleteSupplierForm(page, supplier_data=s,
                                                                                         on_save=update_table).open())
                            ])
                        ),
                    ],
                    color="#f28c7d" if i % 2 == 0 else "#ffffff"
                )
            )
        page.update()

    def delete_supplier_direct(supplier_id):
        delete_supplier(supplier_id)
        update_table()

    def handle_logout(e):
        from logic.auth import logout
        logout(user['id'])
        navigator.go_home()

    screen_title = ft.Text(
        f"ניהול ספקים - שלום {user['user_name']}",
        size=24,
        weight=ft.FontWeight.BOLD,
        color="#9bf6ff",
        text_align=ft.TextAlign.CENTER,
    )

    # כפתורי פעולה עליונים
    buttons = [
        ("➕ הוספת ספק", "#caffbf", lambda e: AddSupplierForm(page,on_save= update_table).open()),
        ("📂 הזמנות ספקים", "#ffe5ec", lambda e: OrdersView(page,navigator).open()),
        ("📊 דוחות ספקים", "#e0fbfc", lambda e: SupplierReports(page,user, navigator).open()),
        ("💲 קטלוג ספקים", "#edf6f9", lambda e: SupplierCatalog(page,navigator,user=user).open()),
    ]

    cards = []
    for label, color, callback in buttons:
        btn = ft.Container(
            content=ft.Text(label, size=20, weight=ft.FontWeight.BOLD, color="black"),
            bgcolor=color,
            border_radius=20,
            alignment=ft.alignment.center,
            padding=ft.padding.symmetric(vertical=40, horizontal=20),
            ink=True,
            on_click=callback
        )
        cards.append(btn)

    logout_button = ft.Container(
        content=ft.Text("התנתקות", size=16, weight=ft.FontWeight.BOLD, color="white"),
        bgcolor="#ff4d4d",
        border_radius=12,
        alignment=ft.alignment.center,
        padding=ft.padding.symmetric(vertical=10, horizontal=20),
        ink=True,
        on_click=handle_logout
    )

    # כפתור חזור
    back_button = ft.Container(
        content=ft.Text("⬅ חזור", size=16, weight=ft.FontWeight.BOLD, color="white"),
        bgcolor="#52b69a",
        border_radius=12,
        alignment=ft.alignment.center,
        padding=ft.padding.symmetric(vertical=10, horizontal=20),
        ink=True,
        on_click=lambda e: navigator.go_home(user)
    )

    # --- טבלת ספקים ---
    suppliers = get_all_suppliers()

    supplier_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("שם", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("טלפון", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("אימייל", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("פעולות", size=18, weight=ft.FontWeight.BOLD)),
        ],
        rows=[
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(s["id"])),
                    ft.DataCell(ft.Text(s["name"])),
                    ft.DataCell(ft.Text(s["phone"])),
                    ft.DataCell(ft.Text(s["email"])),
                    ft.DataCell(
                        ft.Row([
                            ft.IconButton(icon="edit", on_click=lambda e, s=s: EditSupplierForm(page,navigator,
                                                                                                supplier_data=s,on_save=update_table).open()),
                            ft.IconButton(icon="delete", on_click=lambda e, s=s: delete_supplier_direct(s["id"]))
                        ])
                    ),
                ],
                color="#f28c7d" if i % 2 == 0 else "#ffffff"
            )
            for i, s in enumerate(suppliers)
        ],
        heading_row_color="#52b69a",
        border=ft.border.all(1, ft.Colors.GREY_300),
        column_spacing=20,
        divider_thickness=1,
        data_row_min_height=60
    )

    # --- בניית המסך ---
    page.controls.clear()
    page.add(
        ft.Column(
            controls=[
                screen_title,
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
                ft.Container(
                    content=ft.ListView(controls=[supplier_table], expand=True, padding=0),
                    expand=True,
                    padding=10,
                    bgcolor=ft.Colors.WHITE,
                    border_radius=10,
                    border=ft.border.all(1, ft.Colors.GREY_300),
                ),
                ft.Container(height=20),
                ft.Row([back_button, logout_button], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
            ],
            expand=True,
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
        )
    )
    page.update()
