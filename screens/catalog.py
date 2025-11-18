import flet as ft
from logic.db import run_query, run_action
import os, shutil

def CatalogScreen(page, navigator, user, mode="inventory"):
    page.title = "מחירון"

    selected_category = ft.Ref[ft.Dropdown]()
    search_field = ft.Ref[ft.TextField]()
    price_sort = ft.Ref[ft.Dropdown]()

    # --- FilePicker כללי ---
    file_picker = ft.FilePicker()
    def pick_image():
        if file_picker not in page.overlay:
            page.overlay.append(file_picker)
            page.update()
        file_picker.pick_files()

    # --- טבלת מוצרים ---
    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("שם מוצר", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("חברה", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("תמונה", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("קטגוריה", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("מחיר", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("מחיר 3 ח'", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("מחיר 6 ח'", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("מחיר 12 ח'", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("סטטוס", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("פעולות", size=18, weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        heading_row_color="#52b69a",
        border=ft.border.all(1, ft.Colors.GREY_300),
        column_spacing=20,
        divider_thickness=1,
        data_row_min_height=60
    )

    # --- שליפת קטגוריות וספקים ---
    def get_categories():
        rows = run_query("SELECT name FROM categories")
        return [ft.dropdown.Option(r["name"] or "-") for r in rows]

    def get_suppliers():
        rows = run_query("SELECT name FROM suppliers")
        return [ft.dropdown.Option(r["name"] or "-") for r in rows]

    def refresh_category_dropdown():
        if selected_category.current:
            selected_category.current.options = get_categories()
        page.update()

    # --- שליפת מוצרים ---
    def load_products():
        query = """
            SELECT p.id, p.name, p.company, p.image_path, c.name AS category,
                   p.price, p.price_3, p.price_6, p.price_12, p.status
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.status=?
        """
        params = [mode]

        if selected_category.current.value:
            query += " AND c.name=?"
            params.append(selected_category.current.value)
        if search_field.current.value:
            query += " AND (p.name LIKE ? OR p.company LIKE ?)"
            params.append(f"%{search_field.current.value}%")
            params.append(f"%{search_field.current.value}%")

        order = "ASC"
        if price_sort.current.value == "מהגבוה לנמוך":
            order = "DESC"
        query += f" ORDER BY p.price {order}"

        return run_query(query, tuple(params))

    # --- עדכון טבלה ---
    def update_table():
        products = load_products()
        data_table.rows.clear()

        for i, p in enumerate(products):
            image_control = ft.Image(src=p["image_path"], width=50, height=50) if p["image_path"] else ft.Text("-")
            status_display = "מלאי" if p["status"] == "inventory" else "הזמנות"
            actions = ft.Row([
                ft.IconButton(icon=ft.Icons.EDIT, tooltip="ערוך",
                              on_click=lambda e, pid=p["id"]: edit_product_dialog(pid)),
                ft.IconButton(icon=ft.Icons.DELETE, tooltip="מחק",
                              on_click=lambda e, pid=p["id"]: delete_product(pid)),
            ])
            data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(p["name"])),
                        ft.DataCell(ft.Text(p["company"] or "-")),
                        ft.DataCell(image_control),
                        ft.DataCell(ft.Text(p["category"] or "-")),
                        ft.DataCell(ft.Text(str(p["price"]))),
                        ft.DataCell(ft.Text(str(p["price_3"]))),
                        ft.DataCell(ft.Text(str(p["price_6"]))),
                        ft.DataCell(ft.Text(str(p["price_12"]))),
                        ft.DataCell(ft.Text(status_display)),
                        ft.DataCell(actions),
                    ],
                    color="#f28c7d" if i % 2 == 0 else "#ffffff",
                )
            )
        page.update()

    # --- מחיקת מוצר ---
    def delete_product(pid):
        run_action("DELETE FROM products WHERE id=?", (pid,))
        update_table()

    # --- דיאלוג הוספה/עריכה ---
    def product_dialog(pid=None):
        categories = get_categories()
        suppliers = get_suppliers()

        if pid:
            product_list = run_query("SELECT * FROM products WHERE id=?", (pid,))
            if not product_list:
                ft.alert("המוצר לא נמצא")
                return
            product = product_list[0]
            name_val = product["name"]
            company_val = product["company"]
            image_val = product["image_path"]
            cat_query = run_query("SELECT name FROM categories WHERE id=?", (product.get("category_id"),))
            cat_val = cat_query[0]["name"] if cat_query else None
            status_val = product["status"]
            price_val = product["price"]
            p3_val = product["price_3"]
            p6_val = product["price_6"]
            p12_val = product["price_12"]
            info_val = product["information"]
            sup_val = None
            if product.get("preferred_supplier_id"):
                sup_query = run_query("SELECT name FROM suppliers WHERE id=?", (product["preferred_supplier_id"],))
                if sup_query:
                    sup_val = sup_query[0]["name"]
        else:
            name_val = company_val = image_val = cat_val = status_val = info_val = sup_val = None
            price_val = p3_val = p6_val = p12_val = 0

        name_field = ft.TextField(label="שם מוצר", value=name_val)
        company_field = ft.TextField(label="חברה", value=company_val)
        selected_image = ft.Text(value=image_val or "-", size=12)

        def pick_image_result(e: ft.FilePickerResultEvent):
            if e.files:
                file = e.files[0]
                os.makedirs("assets", exist_ok=True)
                dest = os.path.join("assets", file.name)
                shutil.copy(file.path, dest)
                selected_image.value = dest
                page.update()

        file_picker.on_result = pick_image_result
        pick_button = ft.ElevatedButton("בחר תמונה", on_click=lambda e: pick_image())

        category_dropdown = ft.Dropdown(label="קטגוריה", options=categories, value=cat_val, width=200)
        status_dropdown = ft.Dropdown(
            label="סטטוס",
            options=[ft.dropdown.Option("מלאי"), ft.dropdown.Option("הזמנות")],
            value="מלאי" if (status_val == "inventory" or mode == "inventory") else "הזמנות",
            width=200
        )
        price_field = ft.TextField(label="מחיר", value=str(price_val))
        price_3_field = ft.TextField(label="מחיר 3 חודשים", value=str(p3_val))
        price_6_field = ft.TextField(label="מחיר 6 חודשים", value=str(p6_val))
        price_12_field = ft.TextField(label="מחיר 12 חודשים", value=str(p12_val))
        info_field = ft.TextField(label="מידע נוסף", multiline=True, width=300, value=info_val)
        supplier_dropdown = ft.Dropdown(label="ספק מועדף", options=suppliers, value=sup_val, width=200)

        def close_dialog():
            page.overlay.clear()
            page.update()

        def save_product(ev, pid=pid):
            cat_name = category_dropdown.value
            cat = run_query("SELECT id FROM categories WHERE name=?", (cat_name,))
            if not cat:
                run_action("INSERT INTO categories (name) VALUES (?)", (cat_name,))
                cat_id = run_query("SELECT last_insert_rowid() AS id")[0]["id"]
                refresh_category_dropdown()
            else:
                cat_id = cat[0]["id"]

            sup_name = supplier_dropdown.value
            sup = run_query("SELECT id FROM suppliers WHERE name=?", (sup_name,))
            sup_id = sup[0]["id"] if sup else None

            status_value = "inventory" if status_dropdown.value == "מלאי" else "invitation"
            image_path = selected_image.value if selected_image.value != "-" else None

            if pid:
                run_action("""
                     UPDATE products
                     SET name=?, company=?, image_path=?, category_id=?, status=?, information=?,
                         preferred_supplier_id=?, price=?, price_3=?, price_6=?, price_12=?
                     WHERE id=?
                 """, (
                    name_field.value, company_field.value, image_path, cat_id, status_value, info_field.value,
                    sup_id, float(price_field.value or 0), float(price_3_field.value or 0),
                    float(price_6_field.value or 0), float(price_12_field.value or 0), pid
                ))
            else:
                run_action("""
                     INSERT INTO products (name, company, image_path, category_id, status, information,
                                           preferred_supplier_id, price, price_3, price_6, price_12)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                 """, (
                    name_field.value, company_field.value, image_path, cat_id, status_value, info_field.value,
                    sup_id, float(price_field.value or 0), float(price_3_field.value or 0),
                    float(price_6_field.value or 0), float(price_12_field.value or 0)
                ))

            close_dialog()
            update_table()

        # --- Container עם גלילה ודינמי לפי מסך ---
        dlg_content = ft.Container(
            content=ft.Column([
                name_field, company_field,
                ft.Row([pick_button, selected_image]),
                category_dropdown, status_dropdown,
                price_field, price_3_field, price_6_field, price_12_field,
                info_field, supplier_dropdown
            ], spacing=10, scroll=ft.ScrollMode.AUTO),  # העברת scroll לכאן
            height=400  # במקום max_height
        )

        page.overlay.clear()
        page.overlay.append(
            ft.Container(
                content=ft.Column([
                    ft.Text("ערוך מוצר" if pid else "הוסף מוצר לקטלוג", size=24, weight=ft.FontWeight.BOLD),
                    dlg_content,
                    ft.Row([
                        ft.ElevatedButton("שמור", on_click=save_product, bgcolor="#52b69a", color="white"),
                        ft.ElevatedButton("ביטול", on_click=lambda e: close_dialog(), bgcolor="#f28c7d", color="white"),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=12)
                ], spacing=15),
                padding=20, bgcolor="#ffffff", border_radius=14
            )
        )
        page.update()

    def add_product_dialog(e):
        product_dialog()

    def edit_product_dialog(pid):
        product_dialog(pid)

    # --- דיאלוג הוספת קטגוריה ---
    def add_category_dialog(e):
        name_field = ft.TextField(label="שם קטגוריה")

        def close_dialog():
            page.overlay.clear()
            page.update()

        def save_category(ev):
            run_action("INSERT INTO categories (name) VALUES (?)", (name_field.value,))
            close_dialog()
            refresh_category_dropdown()

        dlg_content = ft.Column([name_field], spacing=10)
        page.overlay.clear()
        page.overlay.append(
            ft.Container(
                content=ft.Column([
                    ft.Text("הוסף קטגוריה", size=24, weight=ft.FontWeight.BOLD),
                    dlg_content,
                    ft.Row([
                        ft.ElevatedButton("שמור", on_click=save_category, bgcolor="#52b69a", color="white"),
                        ft.ElevatedButton("ביטול", on_click=lambda e: close_dialog(), bgcolor="#f28c7d", color="white")
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=12)
                ], spacing=15),
                padding=20, bgcolor="#ffffff", border_radius=14
            )
        )
        page.update()

    # --- בניית המסך ---
    controls = ft.Column(
        controls=[
            ft.Row([
                ft.ElevatedButton("מחירון מלאי", on_click=lambda e: CatalogScreen(page, navigator, user, "inventory")),
                ft.ElevatedButton("מחירון הזמנות", on_click=lambda e: CatalogScreen(page, navigator, user, "invitation")),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),

            ft.Row([
                ft.Dropdown(ref=selected_category, label="קטגוריה", options=get_categories(),
                            on_change=lambda e: update_table()),
                ft.TextField(ref=search_field, label="חיפוש לפי שם או חברה", on_change=lambda e: update_table()),
                ft.Dropdown(ref=price_sort, label="סדר לפי מחיר",
                            options=[ft.dropdown.Option("מהנמוך לגבוה"), ft.dropdown.Option("מהגבוה לנמוך")],
                            on_change=lambda e: update_table())
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),

            ft.Row([
                ft.ElevatedButton("➕ הוסף מוצר לקטלוג", on_click=add_product_dialog, bgcolor="#52b69a", color="white"),
                ft.ElevatedButton("➕ הוסף קטגוריה", on_click=add_category_dialog, bgcolor="#4d96ff", color="white"),
                ft.ElevatedButton("חזרה לבית🏠", on_click=lambda e: navigator.go_home(user), width=120,
                                  bgcolor="#f28c7d", color=ft.Colors.WHITE)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),

            ft.Container(
                content=ft.ListView(controls=[data_table], padding=0, expand=True),
                expand=True, padding=10, bgcolor=ft.Colors.WHITE, border_radius=10,
                border=ft.border.all(1, ft.Colors.GREY_300),
            ),
        ],
        expand=True, spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO, rtl=True
    )

    page.controls.clear()
    page.add(controls)
    update_table()
    page.update()
