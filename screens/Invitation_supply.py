import flet as ft
from logic.customers import get_item
from logic.inventory import get_all_products
from logic.orders import get_order_by_id, get_invitation_items_by_invitation_id
from logic.products import get_product_name_by_id
from logic.suppliers import get_all_suppliers
from logic.supply_flow import handle_supplied_item, get_open_invitations
def Invitation_supply(navigator, page, current_user):
    page.snack_bar = ft.SnackBar(content=ft.Text(""), bgcolor=ft.Colors.RED)
    page.snack_bar.open = False

    # ---------- טבלת הזמנות פתוחות ----------
    open_invitations_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("קוד הזמנה", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("לקוח", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("מוצר", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("מידה", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("צילנדר", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("זווית", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("צבע", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("מולטיפוקל", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("קימור", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("כמות נדרשת", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("פעולה", weight=ft.FontWeight.BOLD)),
        ],
        heading_row_color="#52b69a",
        border=ft.border.all(1, ft.Colors.GREY_300),
        column_spacing=18,
        divider_thickness=1,
        data_row_min_height=55,
        rows=[]
    )

    # ---------- ספקים ----------
    suppliers = get_all_suppliers()
    supplier_dropdown = ft.Dropdown(
        label="בחר ספק",
        options=[ft.dropdown.Option(str(s["id"]), s["name"]) for s in suppliers],
        width=260
    )
    products = get_all_products()
    products_by_name = {p["name"]: p for p in products}
    product_names = list(products_by_name.keys())
    suggestions_list = ft.Column()

    def select_product(val: str):
        name_var.value = val
        suggestions_list.controls.clear()
        page.update()
    def update_suggestions(query: str):
        suggestions_list.controls.clear()
        if query:
            matches = [p for p in product_names if query.lower() in p.lower()]
            for m in matches:
                suggestions_list.controls.append(
                    ft.TextButton(text=m, on_click=lambda e, val=m: select_product(val))
                )
        page.update()

    # ---------- שדות ----------
    name_var = ft.TextField(label="שם מוצר", width=140)
    size_var = ft.TextField(label="מידה", width=120)
    cylinder_var = ft.TextField(label="צילנדר", width=120)
    angle_var = ft.TextField(label="זווית", width=120)
    color_var = ft.TextField(label="צבע", width=120)
    multifokal_var = ft.TextField(label="מולטיפוקל", width=120)
    curvature_options = ["8.4", "8.5", "8.6", "8.7", "8.8", "8.9"]
    curvature_var = ft.Dropdown(label="קימור", width=120,
                                options=[ft.dropdown.Option(c, c) for c in curvature_options], )
    quantity_var = ft.TextField(label="כמות", value="1", width=80)
    name_var.on_change = lambda e: (update_suggestions(name_var.value))
    # ---------- עזרי המרה ----------
    def format_number(n):
        if n is None or n == "-":
            return "-"
        try:
            return str(int(n)) if float(n).is_integer() else str(n)
        except:
            return str(n)

    def _to_float_safe(x):
        try:
            return float(str(x).split()[0])
        except:
            return None

    # ---------- סינון ----------
    def filter_open_invitations(supplier_id, name=None, size=None, cylinder=None,
                                angle=None, color=None, multifokal=None, curvature=None):
        invitations = get_open_invitations()
        filtered = []

        for inv in invitations:
            if supplier_id and int(inv["supplier_id"]) != int(supplier_id):
                continue
            if name and name.lower() not in str(inv.get("product_name", "")).lower():
                continue
            if size and size not in str(inv.get("size", "")):
                continue
            if cylinder:
                if _to_float_safe(inv.get("cylinder")) != _to_float_safe(cylinder):
                    continue
            if angle:
                inv_angle = _to_float_safe(inv.get("angle"))
                if inv_angle is None or not (_to_float_safe(angle) - 20 <= inv_angle <= _to_float_safe(angle) + 20):
                    continue
            if color and color.lower() not in str(inv.get("color", "")).lower():
                continue
            if multifokal and multifokal.lower() not in str(inv.get("multifokal", "")).lower():
                continue
            if curvature and curvature.lower() not in str(inv.get("curvature", "")).lower():
                continue

            filtered.append(inv)
        return filtered

    # ---------- עדכון טבלה ----------
    def update_open_invitations_table():
        open_invitations_table.rows.clear()
        filtered = filter_open_invitations(
            supplier_dropdown.value,
            name_var.value,
            size_var.value,
            cylinder_var.value,
            angle_var.value,
            color_var.value,
            multifokal_var.value,
            curvature_var.value
        )

        for i, inv in enumerate(filtered):
            open_invitations_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(inv.get("id", "-"))),
                        ft.DataCell(ft.Text(inv.get("customer_name", "-"))),
                        ft.DataCell(ft.Text(inv.get("product_name", "-"))),
                        ft.DataCell(ft.Text(inv.get("size", "-"))),
                        ft.DataCell(ft.Text(str(inv.get("cylinder") or "-"))),
                        ft.DataCell(ft.Text(format_number(inv.get("angle") or "-"))),
                        ft.DataCell(ft.Text(inv.get("color", "-"))),
                        ft.DataCell(ft.Text(inv.get("multifokal", "-"))),
                        ft.DataCell(ft.Text(inv.get("curvature", "-"))),
                        ft.DataCell(ft.Text(inv.get("quantity_remaining", "-"))),
                        ft.DataCell(
                            ft.ElevatedButton(
                                "סמן כסופקה",
                                bgcolor="#52b69a",
                                color="white",
                                on_click=lambda e, iid=inv["inv_item_id"]: mark_as_supplied(iid)
                            )
                        ),
                    ],
                    color="#f28c7d" if i % 2 == 0 else "#ffffff"
                )
            )
        page.update()

    # ---------- סימון כסופק ----------
    def mark_as_supplied(inv_id):
        item = get_item(inv_id)
        handle_supplied_item(
            page,
            item["invitation_id"],
            quantity_var.value,
            item["id"],
            int(supplier_dropdown.value),
            get_product_name_by_id(item["product_id"]),
            quantity_var
        )

        page.snack_bar.content = ft.Text("הפריט סומן כסופקה!")
        page.snack_bar.open = True
        update_open_invitations_table()
        exist = get_order_by_id(item["invitation_id"])
        exist["items"] = get_invitation_items_by_invitation_id(item["invitation_id"])
        navigator.go_new_invitation(user=current_user, c_id=item["customer_id"], existing_invitation= exist,edit=False  )


    # ---------- הוספת מוצר ידנית ----------
    items = []

    def add_new_product(e=None):
        if not supplier_dropdown.value or not name_var.value:
            page.snack_bar.content = ft.Text("יש לבחור ספק ומוצר")
            page.snack_bar.open = True
            return

        item = {
            "supplier_id": supplier_dropdown.value,
            "product_name": name_var.value,
            "size": size_var.value,
            "quantity": quantity_var.value
        }
        items.append(item)
        page.update()

    # ---------- ממשק ----------
    page.controls.clear()
    page.add(
        ft.Column(
            [
                supplier_dropdown,
                ft.Row(
                    [name_var, size_var, cylinder_var, angle_var,
                     color_var, multifokal_var, curvature_var, quantity_var],
                    spacing=10
                ),
                suggestions_list,
                ft.ElevatedButton("➕ הוסף מוצר", on_click=add_new_product,
                                  bgcolor="#52b69a", color="white"),

                ft.ElevatedButton("סיום וחזרה לבית🏠",
                                  on_click=lambda e: navigator.go_home(current_user),
                                  bgcolor="#f28c7d", color="white"),

                ft.Text("הזמנות פתוחות", size=20, weight=ft.FontWeight.BOLD),
                ft.Container(
                    content=ft.ListView([open_invitations_table], expand=True),
                    padding=10,
                    bgcolor="white",
                    border_radius=10,
                    border=ft.border.all(1, ft.Colors.GREY_300)
                ),
            ],
            spacing=15,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            rtl=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

    update_open_invitations_table()
    page.update()
