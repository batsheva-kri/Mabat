import flet as ft
from logic.suppliers import get_open_orders, get_closed_orders, close_order, reopen_order

class OrdersView:
    def __init__(self, page,navigator):
        self.page = page
        self.open_orders_table = None
        self.closed_orders_table = None
        self.navigator = navigator

    def build_table(self, orders, is_open=True):
        rows = []
        for order in orders:
            action_btn = ft.ElevatedButton(
                "סגור" if is_open else "פתח מחדש",
                on_click=lambda e, o_id=order["id"]: self.toggle_order(o_id, is_open)
            )
            row = ft.DataRow(cells=[
                ft.DataCell(ft.Text(order["id"])),
                ft.DataCell(ft.Text(order["supplier_name"])),
                ft.DataCell(ft.Text(order["date"])),
                ft.DataCell(ft.Text(order["total"])),
                ft.DataCell(action_btn)
            ])
            rows.append(row)
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("מספר הזמנה")),
                ft.DataColumn(ft.Text("ספק")),
                ft.DataColumn(ft.Text("תאריך")),
                ft.DataColumn(ft.Text("סכום")),
                ft.DataColumn(ft.Text("פעולות"))
            ],
            rows=rows
        )

    def toggle_order(self, order_id, is_open):
        if is_open:
            close_order(order_id)
        else:
            reopen_order(order_id)
        self.update_tables()

    def update_tables(self):
        open_orders = get_open_orders()
        closed_orders = get_closed_orders()
        self.open_orders_table = self.build_table(open_orders, is_open=True)
        self.closed_orders_table = self.build_table(closed_orders, is_open=False)
        self.page.update()

    def open(self):
        self.update_tables()
        self.page.add(
            ft.Column([
                ft.Text("הזמנות פתוחות", style="headlineMedium"),
                self.open_orders_table,
                ft.Divider(),
                ft.Text("הזמנות סגורות", style="headlineMedium"),
                self.closed_orders_table
            ], spacing=20)
        )

