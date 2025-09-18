import flet as ft
from logic.suppliers import get_supplier_monthly_report, get_all_suppliers
import datetime


class SupplierReports:
    def __init__(self, page,user, navigator):
        self.page = page
        self.report_table = None
        self.navigator = navigator
        self.user= user

    def open(self):
        self.page.title = "דו\"ח ספק חודשי"

        # --- פונקציות עזר ---
        def format_currency(value):
            return f"{value:.2f} ש\"ח"

        # קבלת חודש ושנה נוכחיים
        now = datetime.datetime.now()
        current_year = str(now.year)
        current_month = str(now.month)

        # --- ממשק ---
        suppliers = get_all_suppliers()

        supplier_dropdown = ft.Dropdown(
            label="בחר ספק",
            options=[ft.dropdown.Option(f"{s['name']} (ID:{s['id']})") for s in suppliers],
            width=300
        )

        year_dropdown = ft.Dropdown(
            label="בחר שנה",
            options=[ft.dropdown.Option(str(y)) for y in range(2020, 2031)],
            value=current_year
        )

        month_dropdown = ft.Dropdown(
            label="בחר חודש",
            options=[ft.dropdown.Option(str(m)) for m in range(1, 13)],
            value=current_month
        )

        self.report_table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("תאריך", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("שם מוצר", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("כמות", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("סה\"כ", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("פעולות", weight=ft.FontWeight.BOLD))
            ],
            rows=[],
            heading_row_color="#52b69a",
            column_spacing=20,
            divider_thickness=1,
            data_row_min_height=60,
            border=ft.border.all(1, ft.Colors.GREY_300)
        )

        title = ft.Text(
            "דו\"ח ספק חודשי",
            size=28,
            weight=ft.FontWeight.BOLD,
            color="#52b69a",
            text_align=ft.TextAlign.CENTER
        )

        # --- כפתורי חזרה ---
        back_suppliers_btn = ft.ElevatedButton(
            "⬅ חזרה לספקים",
            on_click=lambda e: self.navigator.go_suppliers(user=self.user)
        )
        back_home_btn = ft.ElevatedButton(
            "⬅ חזרה לבית",
            on_click=lambda e: self.navigator.go_home(user=self.user)
        )

        controls_column = ft.Column(
            controls=[
                title,
                ft.Row([supplier_dropdown, year_dropdown, month_dropdown], alignment=ft.MainAxisAlignment.CENTER,
                       spacing=10),
                ft.Container(
                    content=self.report_table,
                    padding=15,
                    bgcolor="#ffe5ec",
                    border_radius=12,
                    expand=True
                ),
                ft.Row([back_suppliers_btn, back_home_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
            ],
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )

        self.page.controls.clear()
        self.page.add(controls_column)

        # --- פונקציה לטעינת הדו"ח ---
        def load_report(e=None):
            supplier_val = supplier_dropdown.value
            year_val = year_dropdown.value
            month_val = month_dropdown.value

            if not supplier_val:
                return

            supplier_id = int(supplier_val.split("ID:")[1].strip(")"))
            rows_data = get_supplier_monthly_report(supplier_id, year_val, month_val)

            self.report_table.rows.clear()
            total_sum = 0

            for i, r in enumerate(rows_data):
                actions_row = ft.Row(
                    controls=[
                        ft.IconButton(icon=ft.Icons.EDIT, icon_color="#52b69a", icon_size=28, tooltip="ערוך"),
                        ft.IconButton(icon=ft.Icons.DELETE, icon_color="#f28c7d", icon_size=28, tooltip="מחק")
                    ],
                    spacing=8
                )

                self.report_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(r["date"])),
                            ft.DataCell(ft.Text(r["product_name"])),
                            ft.DataCell(ft.Text(str(r["quantity"]))),
                            ft.DataCell(ft.Text(format_currency(r["total"]))),
                            ft.DataCell(actions_row)
                        ],
                        color="#ffffff" if i % 2 == 0 else "#fceef3"
                    )
                )
                total_sum += r["total"]

            # שורה מסכמת
            self.report_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("סה\"כ", weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text("-")),
                        ft.DataCell(ft.Text("-")),
                        ft.DataCell(ft.Text(format_currency(total_sum), weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text(""))
                    ],
                    color="#ddd"
                )
            )
            self.page.update()

        # חיבור האירועים ל-Dropdown
        supplier_dropdown.on_change = load_report
        year_dropdown.on_change = load_report
        month_dropdown.on_change = load_report

        # טען כבר את הדו"ח הראשון אם יש ספקים
        if suppliers:
            supplier_dropdown.value = f"{suppliers[0]['name']} (ID:{suppliers[0]['id']})"
            supplier_dropdown.update()
            load_report()

        self.page.update()
