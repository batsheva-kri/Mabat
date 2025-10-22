import flet as ft
from logic.inventory import get_all_products
from logic.products import get_catalog_prices, get_product_name_by_id
from logic.suppliers import get_all_suppliers, get_supplier_invitation
from logic.orders import get_order_by_id, get_invitation_items_by_invitation_id
from logic.supply_flow import handle_supplied_item
from logic.users import get_all_users

def Invitation_supply(navigator, page, current_user):
    page.snack_bar = ft.SnackBar(content=ft.Text(""), bgcolor=ft.Colors.RED)

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
        qty_var = ft.TextField(label="כמות", width=80, value="1")
        size_var = ft.TextField(label="מידה", width=80)
        cylinder_var = ft.TextField(label="צילנדר", width=80)
        angle_var = ft.TextField(label="זווית", width=80)
        color_var = ft.TextField(label="צבע", width=80)
        multifocal_var = ft.TextField(label="מולטיפוקל", width=80)
        curvature_var = ft.TextField(label="קימור", width=80)
        suggestions_list = ft.Column()

        def update_suggestions(query: str):
            suggestions_list.controls.clear()
            print("------ UPDATE SUGGESTIONS ------")
            print("Type selected:", type_dropdown.value)
            print("Query:", query)

            if query:
                print(type_dropdown.value)
                if type_dropdown.value == "lens":
                    matches = [p["name"] for p in lens_products if query.lower() in p["name"].lower()]
                    print("lens")
                else:
                    matches = [p["name"] for p in solution_products if query.lower() in p["name"].lower()]
                    print("solution")

                print("Matches found:", matches)

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

            qty = int(qty_var.value or 1)
            item = {
                "supplier_id": int(supplier_dropdown.value),
                "type": type_dropdown.value,
                "product_name": name_var.value,
                "qty": qty,
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
            supplier_invs = get_supplier_invitation(supplier_id, product_name, size, cylinder, angle)

            if supplier_invs:
                invitation_id = supplier_invs[0]["id"]
                customer_invitation_id = handle_supplied_item(invitation_id, qty)
                customer_invitation = get_order_by_id(customer_invitation_id)
                items1 = get_invitation_items_by_invitation_id(customer_invitation_id)
                # המרה לרשימה אם זה מילון בודד
                if isinstance(items1, dict):
                    # items1 = [items1]
                    customer_invitation["items"] = [items1]
                else:
                    customer_invitation["items"] = items1
                print(customer_invitation)
                for inv_item in customer_invitation["items"]:
                    product_id = inv_item["product_id"]
                    inv_item["product_name"] = get_product_name_by_id(product_id)

                navigator.go_new_invitation(current_user,customer_invitation["customer_id"],is_new_invitation=True,existing_invitation=customer_invitation, edit = False)
            else:
                print(f"לא נמצאה הזמנת ספק מתאימה עבור {product_name}")

            # --- עדכון הטבלה ---
            items_list.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item["type"])),
                    ft.DataCell(ft.Text(item["product_name"])),
                    ft.DataCell(ft.Text(item["size"])),
                    ft.DataCell(ft.Text(item["cylinder"])),
                    ft.DataCell(ft.Text(item["angle"])),
                    ft.DataCell(ft.Text(str(item["qty"]))),
                    ft.DataCell(ft.Text(item["color"])),
                    ft.DataCell(ft.Text(item["multifocal"])),
                    ft.DataCell(ft.Text(item["curvature"]))
                ])
            )
            page.update()

        return ft.Column([
            ft.Row([type_dropdown, name_var, qty_var, size_var, cylinder_var, angle_var, color_var, multifocal_var,
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
            items_list,
            ft.ElevatedButton("סיום והחזרה", on_click=lambda e: navigator.go_home(current_user))
        ], spacing=15)
    )
    page.update()
