import flet as ft
from logic.suppliers import get_supplier_monthly_report, get_all_suppliers, export_supplier_monthly_pdf
import datetime


def SupplierReportsScreen(page, current_user, navigator):
    page.title = "דו\"ח ספק חודשי"

    # --- תאריך נוכחי ---
    now = datetime.datetime.now()
    current_year = str(now.year)
    current_month = str(now.month)

    # --- שליפת ספקים ---
    suppliers = get_all_suppliers()

    supplier_dropdown = ft.Dropdown(
        label="בחר ספק",
        options=[ft.dropdown.Option(f"{s['name']} (ID:{s['id']})") for s in suppliers],
        width=300
    )

    year_dropdown = ft.Dropdown(
        label="בחר שנה",
        options=[ft.dropdown.Option(str(y)) for y in range(2020, 2031)],
        value=current_year,
        width=150
    )

    month_dropdown = ft.Dropdown(
        label="בחר חודש",
        options=[ft.dropdown.Option(str(m)) for m in range(1, 13)],
        value=current_month,
        width=150
    )

    # --- כפתורי חזרה ---
    back_suppliers_btn = ft.ElevatedButton(
        "⬅ חזרה לספקים",
        on_click=lambda e: navigator.go_suppliers(user=current_user)
    )
    back_home_btn = ft.ElevatedButton(
        "⬅ חזרה לבית",
        on_click=lambda e: navigator.go_home(user=current_user)
    )

    # --- כותרת עליונה ---
    title = ft.Text(
        "דו\"ח ספק חודשי",
        size=26,
        weight=ft.FontWeight.BOLD,
        color="#52b69a",
        text_align=ft.TextAlign.CENTER
    )

    # --- פונקציה לטעינת הדו"ח ---
    def load_report(e=None):
        supplier_val = supplier_dropdown.value
        if not supplier_val:
            return

        supplier_id = int(supplier_val.split("ID:")[1].strip(")"))
        year_val = year_dropdown.value
        month_val = month_dropdown.value

        rows_data = get_supplier_monthly_report(supplier_id, year_val, month_val)

        # אם אין נתונים - הודעה
        if not rows_data:
            page.controls.clear()
            page.add(
                ft.Column(
                    [
                        title,
                        ft.Text("אין נתונים עבור הספק או החודש שנבחר", color="red"),
                        ft.Row([back_suppliers_btn, back_home_btn], alignment=ft.MainAxisAlignment.CENTER)
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                    alignment=ft.MainAxisAlignment.CENTER
                )
            )
            page.update()
            return

        # נבנה מילון לפי תאריכים: {date: {product_name: {"quantity": X, "total": Y}}}
        daily_data = {}
        for r in rows_data:
            day = r["date"].split("T")[0] if "T" in r["date"] else r["date"]
            product = r["product_name"]
            quantity = r["quantity"]
            total = r["total"]

            if day not in daily_data:
                daily_data[day] = {}
            if product not in daily_data[day]:
                daily_data[day][product] = {"quantity": 0, "total": 0}

            daily_data[day][product]["quantity"] += quantity
            daily_data[day][product]["total"] += total

        # נבנה את המסך מחדש
        page.controls.clear()
        page.add(title)
        page.add(
            ft.Row(
                [supplier_dropdown, year_dropdown, month_dropdown,
                 ft.ElevatedButton("📄 ייצוא דוח חודשי PDF", on_click=on_export_pdf, bgcolor="#4d96ff", color="white"),],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            )
        )

        # --- סה"כ חודשי ---
        monthly_total = 0

        # טבלה לכל יום
        for day, products in sorted(daily_data.items()):
            total_sum = 0
            table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("שם מוצר", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("כמות", weight=ft.FontWeight.BOLD)),
                    ft.DataColumn(ft.Text("סה\"כ מחיר", weight=ft.FontWeight.BOLD))
                ],
                rows=[],
                heading_row_color="#52b69a",
                data_row_min_height=45,
                border=ft.border.all(1, ft.Colors.GREY_300),
                column_spacing=20
            )

            for product_name, info in products.items():
                total_sum += info["total"]
                table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(product_name)),
                            ft.DataCell(ft.Text(str(info["quantity"]))),
                            ft.DataCell(ft.Text(f"{info['total']:.2f} ש\"ח"))
                        ]
                    )
                )

            # סיכום יומי
            monthly_total += total_sum
            table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text("סה\"כ ליום", weight=ft.FontWeight.BOLD)),
                        ft.DataCell(ft.Text("")),
                        ft.DataCell(ft.Text(f"{total_sum:.2f} ש\"ח", weight=ft.FontWeight.BOLD))
                    ],
                    color="#ddd"
                )
            )

            # כותרת יום + טבלה
            page.add(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(f"תאריך: {day}", size=20, weight=ft.FontWeight.BOLD, color="#1b4332"),
                            table
                        ],
                        spacing=10
                    ),
                    bgcolor="#fefae0",
                    padding=15,
                    margin=ft.margin.symmetric(vertical=10),
                    border_radius=10
                )
            )

        # --- סה"כ חודשי ---
        page.add(
            ft.Container(
                content=ft.Text(
                    f"סה\"כ לחודש {month_val}/{year_val}: {monthly_total:.2f} ש\"ח",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                    color="#2a9d8f",
                    text_align=ft.TextAlign.CENTER
                ),
                padding=20,
                bgcolor="#e9f5f2",
                border_radius=10,
                margin=ft.margin.symmetric(vertical=10)
            )
        )

        # כפתורי חזרה
        page.add(
            ft.Row(
                [back_suppliers_btn, back_home_btn],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20
            )
        )

        page.update()

    def on_export_pdf(e):
        supplier_val = supplier_dropdown.value
        if not supplier_val:
            page.snack_bar = ft.SnackBar(ft.Text("יש לבחור ספק קודם"))
            page.snack_bar.open = True
            page.update()
            return

        supplier_id = int(supplier_val.split("ID:")[1].strip(")"))
        year_val = year_dropdown.value
        month_val = month_dropdown.value

        try:
            path = export_supplier_monthly_pdf(page, supplier_id, year_val, month_val)
            page.snack_bar = ft.SnackBar(ft.Text(f"הדוח נשמר בהצלחה: {path}"))
            page.snack_bar.open = True
            page.update()

            # פתח את התיקייה (ב-Windows)
            import os
            if os.name == "nt":
                os.startfile(os.path.dirname(path))
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"שגיאה ביצוא הדוח: {ex}"))
            page.snack_bar.open = True
            page.update()

    # --- חיבור אירועים ---
    supplier_dropdown.on_change = load_report
    year_dropdown.on_change = load_report
    month_dropdown.on_change = load_report

    # --- טען דוח ראשון אם יש ספקים ---
    if suppliers:
        supplier_dropdown.value = f"{suppliers[0]['name']} (ID:{suppliers[0]['id']})"
        load_report()

    page.update()
