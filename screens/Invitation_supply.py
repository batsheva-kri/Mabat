import flet as ft

from logic.customers import get_item
from logic.orders import get_order_by_id, get_invitation_items_by_invitation_id
from logic.products import get_product_name_by_id
from logic.suppliers import get_all_suppliers
from logic.supply_flow import handle_supplied_item, get_open_invitations

def Invitation_supply(navigator, page, current_user):
    page.snack_bar = ft.SnackBar(content=ft.Text(""), bgcolor=ft.Colors.RED)
    page.snack_bar.open = False

    # --- טבלת הזמנות פתוחות ---
    open_invitations_table = ft.DataTable(columns=[
        ft.DataColumn(ft.Text("קוד הזמנה")),
        ft.DataColumn(ft.Text("לקוח")),
        ft.DataColumn(ft.Text("מוצר")),
        ft.DataColumn(ft.Text("מידה")),
        ft.DataColumn(ft.Text("צילנדר")),
        ft.DataColumn(ft.Text("זווית")),
        ft.DataColumn(ft.Text("צבע")),
        ft.DataColumn(ft.Text("מולטיפוקל")),
        ft.DataColumn(ft.Text("קימור")),
        ft.DataColumn(ft.Text("כמות נדרשת")),
        ft.DataColumn(ft.Text("פעולה")),
    ])

    suppliers = get_all_suppliers()
    supplier_dropdown = ft.Dropdown(
        label="בחר ספק",
        options=[ft.dropdown.Option(str(s['id']), s['name']) for s in suppliers],
        width=300
    )

    def format_number(n):
        if n is None or n == "-":
            return "-"
        try:
            if float(n).is_integer():
                return str(int(n))
            return str(n)
        except:
            return str(n)

    # --- עזרי פרסינג קטן עם הדפסות דיבאג ---
    def _to_float_safe(x):
        if x is None:
            return None
        try:
            return float(x)
        except Exception:
            try:
                return float(str(x).split()[0])
            except Exception:
                return None

    # --- עדכון פונקציית הסינון ---
    def filter_open_invitations(supplier_id, name=None, size=None, cylinder=None, angle=None,
                                color=None, multifokal=None, curvature=None):
        invitations = get_open_invitations()
        filtered = []

        name_q = name.strip() if name and str(name).strip() else None
        size_q = size.strip() if size and str(size).strip() else None
        cyl_q = _to_float_safe(cylinder) if cylinder is not None and str(cylinder).strip() != "" else None
        angle_q = _to_float_safe(angle) if angle is not None and str(angle).strip() != "" else None
        color_q = color.strip().lower() if color and str(color).strip() else None
        multifokal_q = multifokal.strip().lower() if multifokal and str(multifokal).strip() else None
        curvature_q = curvature.strip().lower() if curvature and str(curvature).strip() else None

        for inv in invitations:
            # --- ספק ---
            if supplier_id and supplier_id != "" and supplier_id is not None:
                try:
                    if int(inv.get("supplier_id")) != int(supplier_id):
                        continue
                except:
                    continue

            # --- שם מוצר ---
            if name_q and name_q not in str(inv.get("product_name", "")).lower():
                continue

            # --- מידה ---
            if size_q:
                inv_size_str = str(inv.get("size", "")).strip()
                if size_q not in inv_size_str:
                    try:
                        inv_base = float(inv_size_str.split()[0])
                        q_base = float(size_q.split()[0])
                        if not abs(inv_base - q_base) <= 1e-3:
                            continue
                    except:
                        continue

            # --- צילינדר ---
            if cyl_q is not None:
                inv_cyl = _to_float_safe(inv.get("cylinder"))
                if inv_cyl is None or abs(inv_cyl - cyl_q) > 1e-3:
                    continue

            # --- זווית ±20 ---
            if angle_q is not None:
                inv_angle = _to_float_safe(inv.get("angle"))
                if inv_angle is None or not (angle_q - 20 <= inv_angle <= angle_q + 20):
                    continue

            # --- צבע ---
            if color_q and color_q not in str(inv.get("color", "")).lower():
                continue

            # --- מולטיפוקל ---
            if multifokal_q and multifokal_q not in str(inv.get("multifokal", "")).lower():
                continue

            # --- קימור ---
            if curvature_q and curvature_q not in str(inv.get("curvature", "")).lower():
                continue

            filtered.append(inv)

        return filtered

    def update_open_invitations_table():
        open_invitations_table.rows.clear()

        filtered = filter_open_invitations(
            supplier_id=supplier_dropdown.value,
            name=name_var.value,
            size=size_var.value,
            cylinder=cylinder_var.value,
            angle=angle_var.value,
            color=color_var.value,
            multifokal=multifokal_var.value,
            curvature=curvature_var.value
        )

        for inv in filtered:
            if inv["cylinder"] is None:
                inv["cylinder"] = "-"
            if inv["angle"] is None:
                inv["angle"] = "-"
            open_invitations_table.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(inv.get("id", "-"))),
                    ft.DataCell(ft.Text(inv.get("customer_name", "-"))),
                    ft.DataCell(ft.Text(inv.get("product_name", "-"))),
                    ft.DataCell(ft.Text(inv.get("size", "-"))),
                    ft.DataCell(ft.Text(str(inv.get("cylinder", "-")))),
                    ft.DataCell(ft.Text(format_number(inv.get("angle", "-")))),
                    ft.DataCell(ft.Text(inv.get("color", "-"))),
                    ft.DataCell(ft.Text(inv.get("multifokal", "-"))),
                    ft.DataCell(ft.Text(inv.get("curvature", "-"))),
                    ft.DataCell(ft.Text(inv.get("quantity_remaining", "-"))),
                    ft.DataCell(ft.ElevatedButton(
                        "סמן כסופקה",
                        on_click=lambda e, inv_id=inv["inv_item_id"]: mark_as_supplied(inv_id)
                    )),
                ])
            )

        page.update()

    # Dropdown שינוי ספק — עכשיו עובד!
    supplier_dropdown.on_change = lambda e: update_open_invitations_table()
    # --- סימון כסופק ---
    def mark_as_supplied(inv_id):
        item = get_item(inv_id)
        if not item:
            return
        print("item", item)
        qty_to_mark = item["quantity"] - item["supplied"]
        print("qty_to_mark", qty_to_mark)
        quan = quantity_var.value
        print("quan", quan)
        handle_supplied_item(
            page=page,
            invitation_id=item["invitation_id"],
            quantity=quan,
            customer_invitation_item_id=item["id"],
            supplier_id=int(supplier_dropdown.value),
            product_name=get_product_name_by_id(item["product_id"]),
            quantity_var=quantity_var
        )

        page.snack_bar.content = ft.Text("הפריט סומן כסופקה!")
        page.snack_bar.open = True
        update_open_invitations_table()
        exist = get_order_by_id(item["invitation_id"])
        exist["items"] = get_invitation_items_by_invitation_id(item["invitation_id"])
        navigator.go_new_invitation(user=current_user, c_id=item["customer_id"], existing_invitation= exist,edit=False  )

    # --- שדות סינון ---
    name_var = ft.TextField(label="שם מוצר", width=150)
    size_var = ft.TextField(label="מידה", width=150)
    cylinder_var = ft.TextField(label="צילנדר", width=150)
    angle_var = ft.TextField(label="זווית", width=150)
    quantity_var = ft.TextField(label="כמות", value="1", width=80)
    color_var = ft.TextField(label="צבע", width=100)
    multifokal_var = ft.TextField(label="מולטיפוקל", width=120)
    curvature_var = ft.TextField(label="קימור", width=100)

    name_var.on_change = lambda e: update_open_invitations_table()
    size_var.on_change = lambda e: update_open_invitations_table()
    cylinder_var.on_change = lambda e: update_open_invitations_table()
    angle_var.on_change = lambda e: update_open_invitations_table()
    quantity_var.on_change = lambda  e: update_open_invitations_table()
    color_var.on_change = lambda e: update_open_invitations_table()
    multifokal_var.on_change = lambda e: update_open_invitations_table()
    curvature_var.on_change = lambda e: update_open_invitations_table()

    # --- טבלת סופקו ---
    supplied_items_table = ft.DataTable(columns=[
        ft.DataColumn(ft.Text("מוצר")),
        ft.DataColumn(ft.Text("מידה")),
        ft.DataColumn(ft.Text("כמות")),
        ft.DataColumn(ft.Text("סטטוס")),
    ])

    items = []

    def add_new_product(e=None):
        if not supplier_dropdown.value:
            page.snack_bar.content = ft.Text("חובה לבחור ספק!")
            page.snack_bar.open = True
            return

        if not name_var.value:
            page.snack_bar.content = ft.Text("חובה לבחור מוצר!")
            page.snack_bar.open = True
            return

        qty = int(quantity_var.value or 1)

        item = {
            "supplier_id": int(supplier_dropdown.value),
            "product_name": name_var.value,
            "quantity": qty,
            "size": size_var.value,
            "cylinder": cylinder_var.value,
            "angle": angle_var.value
        }
        items.append(item)

        supplied_items_table.rows.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(item["product_name"])),
                ft.DataCell(ft.Text(item["size"])),
                ft.DataCell(ft.Text(str(item["quantity"]))),
                ft.DataCell(ft.Text("סופק"))
            ])
        )
        page.update()

    add_product_btn = ft.ElevatedButton("➕ הוסף מוצר", on_click=add_new_product)

    # --- ממשק ---
    page.controls.clear()
    page.add(ft.Column([
        supplier_dropdown,
        ft.Row([name_var, size_var, cylinder_var, angle_var, color_var, multifokal_var, curvature_var, quantity_var],
               spacing=10),
        add_product_btn,
        ft.Text("המוצרים שסופקו", weight=ft.FontWeight.BOLD),
        supplied_items_table,
        ft.Text("הזמנות פתוחות", weight=ft.FontWeight.BOLD),
        open_invitations_table,
        ft.ElevatedButton("סיום והחזרה", on_click=lambda e: navigator.go_orders(current_user))
    ], spacing=15))

    update_open_invitations_table()
    page.update()
