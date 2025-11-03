import flet as ft
from logic.inventory import get_all_products
from logic.products import get_product_name_by_id
from logic.suppliers import get_all_suppliers \
# , get_supplier_invitation
from logic.convert import get_supplier_invitation
from logic.orders import get_order_by_id, get_invitation_items_by_invitation_id
from logic.supply_flow import handle_supplied_item

def Invitation_supply(navigator, page, current_user):
    page.snack_bar = ft.SnackBar(content=ft.Text(""), bgcolor=ft.Colors.RED)
    page.snack_bar.open = False
    over_supplied_table = ft.DataTable(columns=[
        ft.DataColumn(ft.Text("מוצר")),
        ft.DataColumn(ft.Text("מידה")),
        ft.DataColumn(ft.Text("כמות")),
        ft.DataColumn(ft.Text("סטטוס")),
        ft.DataColumn(ft.Text("פעולה")),
    ])
    over_supplied_items = []

    def add_to_over_supplied(item_data):
        # item_data: {"customer_invitation_id": ..., "product_id": ..., "supplied": ..., "note": ...}
        print("item_data", item_data)
        product_name = get_product_name_by_id(item_data["product_id"])
        status = item_data.get("note",
                               "עודף ניתן להזמנה הבאה" if item_data["customer_invitation_id"] else "עודף – מיותר")
        button = None
        if item_data["customer_invitation_id"]:
            customer_invitation = get_order_by_id(item_data["customer_invitation_id"])
            items1 = get_invitation_items_by_invitation_id(item_data["customer_invitation_id"])
            # המרה לרשימה אם זה מילון בודד
            if isinstance(items1, dict):
                # items1 = [items1]
                customer_invitation["items"] = [items1]
            else:
                customer_invitation["items"] = items1
            for inv_item in customer_invitation["items"]:
                product_id = inv_item["product_id"]
                inv_item["product_name"] = get_product_name_by_id(product_id)
            button = ft.ElevatedButton(
                "פתח הזמנה",
                on_click=lambda e, inv_id=item_data["customer_invitation_id"]: navigator.go_new_invitation(
                    current_user, get_order_by_id(inv_id)["customer_id"],
                    existing_invitation=customer_invitation,edit=False
                )
            )
        else:
            button = ft.Text("-")

        over_supplied_table.rows.append(
            ft.DataRow(cells=[
                ft.DataCell(ft.Text(product_name)),
                ft.DataCell(ft.Text(item_data.get("size", ""))),
                ft.DataCell(ft.Text(str(item_data["supplied"]))),
                ft.DataCell(ft.Text(status)),
                ft.DataCell(button)
            ])
        )
        page.update()
    # --- בוחרים ספק ---
    suppliers = get_all_suppliers()
    supplier_dropdown = ft.Dropdown(
        label="בחר ספק",
        options=[ft.dropdown.Option(str(s['id']), s['name']) for s in suppliers],
        width=300
    )

    # --- מוצרים לפי קטגוריות ---
    all_products = get_all_products()
    print("all products: " , all_products)
    lens_products = [p for p in all_products if p["category_id"] in [1, 2]]  # עדשות
    print("lens_products", lens_products)
    solution_products = [p for p in all_products if p["category_id"] in [3, 4]]  # תמיסות
    products_by_name = {p["name"]: p for p in all_products}

    # --- עמודת מוצרים ---
    items_list = ft.DataTable(columns=[
        ft.DataColumn(ft.Text("סוג מוצר")),
        ft.DataColumn(ft.Text("מוצר")),
        ft.DataColumn(ft.Text("מידה")),
        ft.DataColumn(ft.Text("צילנדר")),
        ft.DataColumn(ft.Text("זווית")),
        ft.DataColumn(ft.Text("כמות")),
        ft.DataColumn(ft.Text("צבע")),
        ft.DataColumn(ft.Text("מולטיפוקל")),
        ft.DataColumn(ft.Text("קימור")),
    ])

    items = []

    products_column = ft.Column(spacing=10)

    def create_product_row(label):
        type_dropdown = ft.Dropdown(
            label="סוג מוצר",
            options=[
                ft.dropdown.Option("lens", "עדשות"),
                ft.dropdown.Option("solution", "תמיסות")
            ],
            value="lens",
            width=120
        )
        name_var = ft.TextField(label="מוצר", width=250)
        quantity_var = ft.TextField(label="כמות", width=80, value="1")
        size_var = ft.TextField(label="מידה", width=80)
        cylinder_var = ft.TextField(label="צילנדר", width=80)
        angle_var = ft.TextField(label="זווית", width=80)
        color_var = ft.TextField(label="צבע", width=80)
        multifocal_var = ft.TextField(label="מולטיפוקל", width=80)
        curvature_var = ft.TextField(label="קימור", width=80)
        suggestions_list = ft.Column()

        def update_suggestions(query: str):
            suggestions_list.controls.clear()

            if query:
                if type_dropdown.value == "lens":
                    matches = [p["name"] for p in lens_products if query.lower() in p["name"].lower()]
                else:
                    matches = [p["name"] for p in solution_products if query.lower() in p["name"].lower()]

                for match_name in matches:
                    btn = ft.TextButton(
                        text=match_name,
                        on_click=lambda e, val=match_name: select_product(val)
                    )
                    suggestions_list.controls.append(btn)

            page.update()

        def select_product(val: str):
            name_var.value = val
            suggestions_list.controls.clear()
            page.update()

        name_var.on_change = lambda e: update_suggestions(name_var.value)

        def add_item(e=None):
            if not supplier_dropdown.value:
                page.snack_bar = ft.SnackBar(ft.Text("חובה לבחור ספק!"))
                page.snack_bar.open = True
                page.update()
                return
            if not name_var.value:
                page.snack_bar = ft.SnackBar(ft.Text("חובה לבחור מוצר!"))
                page.snack_bar.open = True
                page.update()
                return

            quantity = int(quantity_var.value or 1)
            item = {
                "supplier_id": int(supplier_dropdown.value),
                "type": type_dropdown.value,
                "product_name": name_var.value,
                "quantity": quantity,
                "size": size_var.value,
                "cylinder": cylinder_var.value,
                "angle": angle_var.value,
                "color": color_var.value,
                "multifocal": multifocal_var.value,
                "curvature": curvature_var.value
            }
            items.append(item)

            # --- הפעלת עדכון מצב המוצר בהזמנות ---
            supplier_id = int(supplier_dropdown.value)
            product_name = name_var.value
            size = size_var.value
            cylinder = cylinder_var.value
            angle = angle_var.value
            multifocal = multifocal_var.value
            curvature = curvature_var.value
            color = color_var.value
            invitation_details= get_supplier_invitation(
                supplier_id,
                product_name,
                size,
                cylinder,
                angle,
                color=color if color else None,
                multifocal=multifocal if multifocal else None,
                curvature=curvature if curvature else None
            )
            if invitation_details is not None:
                supplier_invs = invitation_details["supplier_inv_id"]
                customer_invitation_item_id = invitation_details["customer_invitation_item_id"]
                invitation_id = supplier_invs
                results,leftover = handle_supplied_item(invitation_id,
                                            quantity,
                                            customer_invitation_item_id,
                                            supplier_id,
                                            product_name,
                                            size,
                                            cylinder,
                                            angle,
                                            color = color if color else None,
                                            multifocal = multifocal if multifocal else None,
                                            curvature = curvature if curvature else None
                                            )

                # טיפול במספר תוצאות (עודפים והזמנות שסופקו)
                if isinstance(results, list):  # יש עודפים או כמה הזמנות
                    for res in results:
                        add_to_over_supplied(res)
                    print("נמצאו עודפים — לא נפתח הזמנה נוספת")
                elif isinstance(results, dict):  # מקרה מיותר בודד
                    add_to_over_supplied(results)
                    print("נמצא עודף — לא נפתח הזמנה נוספת")
                else:
                    # אין עודפים → לפתוח את ההזמנה הרלוונטית
                    customer_invitation = get_order_by_id(results)
                    items1 = get_invitation_items_by_invitation_id(results)
                    customer_invitation["items"] = [items1] if isinstance(items1, dict) else items1
                    for inv_item in customer_invitation["items"]:
                        product_id = inv_item["product_id"]
                        inv_item["product_name"] = get_product_name_by_id(product_id)
                    navigator.go_new_invitation(
                        current_user,
                        customer_invitation["customer_id"],
                        existing_invitation=customer_invitation,
                        edit=False
                    )

            # --- עדכון הטבלה ---
            items_list.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item["type"])),
                    ft.DataCell(ft.Text(item["product_name"])),
                    ft.DataCell(ft.Text(item["size"])),
                    ft.DataCell(ft.Text(item["cylinder"])),
                    ft.DataCell(ft.Text(item["angle"])),
                    ft.DataCell(ft.Text(str(item["quantity"]))),
                    ft.DataCell(ft.Text(item["color"])),
                    ft.DataCell(ft.Text(item["multifocal"])),
                    ft.DataCell(ft.Text(item["curvature"]))
                ])
            )
            page.update()

        return ft.Column([
            ft.Row([type_dropdown, name_var, quantity_var, size_var, cylinder_var, angle_var, color_var, multifocal_var,
                    curvature_var], spacing=10),
            suggestions_list,
            ft.ElevatedButton(f"➕ {label}", on_click=add_item)
        ])

    # כפתור להוספת מוצר חדש
    def add_new_product(e):
        row = create_product_row("מוצר חדש")
        products_column.controls.append(row)
        page.update()

    add_product_btn = ft.ElevatedButton("➕ הוסף מוצר", on_click=add_new_product)

    # --- סידור הדף ---
    page.controls.clear()
    page.add(
        ft.Column([
            supplier_dropdown,
            products_column,
            add_product_btn,
            ft.Text("המוצרים שסופקו", weight=ft.FontWeight.BOLD),
            items_list,
            ft.Text("המוצרים המתאימים מהזמנות הלקוחות הרלוונטיות", weight=ft.FontWeight.BOLD),
            over_supplied_table,
            ft.ElevatedButton("סיום והחזרה", on_click=lambda e: navigator.go_home(current_user))
        ], spacing=15)
    )
    page.update()
