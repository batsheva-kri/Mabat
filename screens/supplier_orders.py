import flet as ft
from logic.suppliers import get_open_orders, get_closed_orders, close_order, reopen_order, get_all_suppliers

def OrdersScreen(page, navigator, user):
    page.title = "ניהול הזמנות ספקים"

    # --- שליפת נתונים ---
    open_orders = get_open_orders()
    closed_orders = get_closed_orders()
    suppliers = get_all_suppliers()

    # --- משתנים לסינון ---
    selected_supplier = "כל הספקים"
    selected_status = "כולן"  # אפשרויות: "פתוחות", "סגורות", "כולן"

    # --- פונקציה פנימית לעדכון הטבלאות לאחר פעולה ---
    def update_tables():
        nonlocal open_orders, closed_orders
        open_orders[:] = get_open_orders()
        closed_orders[:] = get_closed_orders()
        refresh_view()

    # # --- פעולה לסגירה / פתיחה מחדש ---
    # def toggle_order(order_id, is_open):
    #     if is_open:
    #         close_order(order_id)
    #     else:
    #         reopen_order(order_id)
    #     update_tables()

    # --- פונקציה ליצירת טבלה ---
    def build_table(orders, is_open=True):
        filtered = orders
        if selected_supplier != "כל הספקים":
            filtered = [o for o in orders if o["supplier_name"] == selected_supplier]

        if not filtered:
            return ft.Text("אין הזמנות", color="gray")

        rows = []
        for i, order in enumerate(filtered):
            # קביעת צבע רקע לפי סוג הזמנה
            row_color = None if is_open else "#d0f0c0"  # ירוק בהיר להזמנות סגורות

            row = ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(str(order["id"]))),
                    ft.DataCell(ft.Text(order["product_name"])),
                    ft.DataCell(ft.Text(order["size"])),
                    ft.DataCell(ft.Text(order["quantity"])),
                    ft.DataCell(ft.Text(order["supplier_name"])),
                    ft.DataCell(ft.Text(order["date"])),
                    ft.DataCell(ft.Text(str(order["total"]))),
                    ft.DataCell(ft.Text(order["customer_name"])),
                ],
                color=row_color
            )
            rows.append(row)

        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("מספר הזמנה")),
                ft.DataColumn(ft.Text("מוצר")),
                ft.DataColumn(ft.Text("מידה")),
                ft.DataColumn(ft.Text("כמות")),
                ft.DataColumn(ft.Text("ספק")),
                ft.DataColumn(ft.Text("תאריך")),
                ft.DataColumn(ft.Text("סכום")),
                ft.DataColumn(ft.Text("שם הלקוח")),
            ],
            rows=rows
        )

    # --- פריסת המסך ---
    def refresh_view():
        page.controls.clear()

        # סינון
        supplier_dropdown = ft.Dropdown(
            label="ספק",
            options=[ft.dropdown.Option("כל הספקים")] + [ft.dropdown.Option(s["name"]) for s in suppliers],
            value=selected_supplier,
            on_change=on_filter_change,
            width=250
        )

        status_dropdown = ft.Dropdown(
            label="סטטוס הזמנה",
            options=[
                ft.dropdown.Option("כולן"),
                ft.dropdown.Option("הזמנות שלא סופקו"),
                ft.dropdown.Option("הזמנות שסופקו")
            ],
            value=selected_status,
            on_change=on_filter_change,
            width=150
        )

        controls = [ft.Row([supplier_dropdown, status_dropdown], spacing=20)]

        if selected_status in ("כולן", "הזמנות שסופקו"):
            controls.append(ft.Text("הזמנות שסופקו", size=20, weight=ft.FontWeight.BOLD))
            controls.append(build_table(open_orders, is_open=False))
            controls.append(ft.Divider())

        if selected_status in ("כולן", "הזמנות שלא סופקו"):
            controls.append(ft.Text("הזמנות שלא סופקו", size=20, weight=ft.FontWeight.BOLD))
            controls.append(build_table(closed_orders, is_open=True))
            controls.append(ft.Divider())

        controls.append(ft.ElevatedButton("⬅ חזרה", on_click=lambda e: navigator.go_home(user)))

        page.add(ft.ListView(controls=controls, spacing=20, padding=20, auto_scroll=False))
        page.update()

    # --- אירוע שינוי סינון ---
    def on_filter_change(e):
        nonlocal selected_supplier, selected_status
        selected_supplier = e.control.value if e.control.label == "ספק" else selected_supplier
        selected_status = e.control.value if e.control.label == "סטטוס הזמנה" else selected_status
        refresh_view()

    # --- הצגת המסך ---
    refresh_view()
