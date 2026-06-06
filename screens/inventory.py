import flet as ft
from logic.inventory import get_category_name, sizes_for_category, get_inventory_products, get_categories
from logic.suppliers import get_all_suppliers


def InventoryScreen(page, current_user, navigator, save_fn, show_dropdown=False):
    page.title = "מסך מלאי"
    content = []

    # --- בחירת ספק ---
    supplier_var = None
    if show_dropdown:
        suppliers = get_all_suppliers()
        supplier_var = ft.Dropdown(
            label="בחר ספק",
            options=[ft.dropdown.Option(str(s["id"]), s["name"]) for s in suppliers],
            width=300
        )
        content.append(ft.Row([supplier_var], spacing=20))

    # שליפת כל הקטגוריות מהדאטה-בייס (במקום רשימה קבועה)
    # בהנחה שכל קטגוריה היא אובייקט עם: id, name, has_sizes
    all_categories = get_categories()

    # כפתור חזרה
    content.append(ft.ElevatedButton(
        "⬅ חזרה",
        on_click=lambda e: navigator.go_orders(user=current_user),
        bgcolor="#F28C7D",
        color="#FFFFFF"
    ))

    # מילון שיחזיק את כל השדות כדי לאסוף נתונים בשמירה אחת בסוף
    all_text_fields = []

    for cat in all_categories:
        products = get_inventory_products(cat["id"])
        if not products:
            continue

        content.append(ft.Text(cat["name"], size=20, weight=ft.FontWeight.BOLD))

        # --- תצוגה לפי מידות (דינאמי לפי העמודה החדשה) ---
        if cat.get("has_sizes"):
            sizes = sizes_for_category(cat["id"])

            # כותרות
            header_row = ft.Row(
                controls=[ft.Text("מידה", weight=ft.FontWeight.BOLD, width=60)] +
                         [ft.Text(p['name'], weight=ft.FontWeight.BOLD, width=60) for p in products],
                spacing=0
            )
            content.append(header_row)

            table_rows = []
            for size in sizes:
                row_controls = [ft.Text(str(size), width=60)]
                for product in products:
                    tf = ft.TextField(width=60, height=40, data={"pid": product["id"], "size": size})
                    all_text_fields.append(tf)
                    row_controls.append(tf)
                table_rows.append(ft.Row(controls=row_controls, spacing=0))

            content.append(ft.Container(
                content=ft.Column(controls=table_rows, spacing=0, scroll=ft.ScrollMode.AUTO),
                border=ft.border.all(1, "#B0B0B0"),
                border_radius=8,
                padding=5,
                height=300
            ))

        # --- תצוגה פשוטה (ללא מידות) ---
        else:
            simple_rows = []
            for product in products:
                tf = ft.TextField(width=100, data={"pid": product["id"], "size": -1})
                all_text_fields.append(tf)
                simple_rows.append(ft.Row(
                    controls=[ft.Text(product['name'], width=200), tf],
                    spacing=10
                ))
            content.append(ft.Container(
                content=ft.Column(controls=simple_rows, spacing=5),
                border=ft.border.all(1, "#B0B0B0"),
                border_radius=8,
                padding=10
            ))

    # --- כפתור שמירה מאוחד לכל המסך ---
    def save_all_handler(e):
        items = []
        for tf in all_text_fields:
            if tf.value and tf.value.isdigit():
                items.append({
                    "product_id": tf.data["pid"],
                    "size": tf.data["size"],
                    "count": int(tf.value)
                })

        if not items:
            return  # או להציג הודעה שאין מה לשמור

        supplier_id = int(supplier_var.value) if supplier_var and supplier_var.value else 0
        save_fn(items, supplier_id, page)
        navigator.go_home(current_user)

    content.append(ft.ElevatedButton(
        "שמור הכל",
        on_click=save_all_handler,
        bgcolor="#52b69a",
        color="#FFFFFF",
        height=50
    ))

    page.controls.clear()
    page.add(ft.ListView(controls=content, expand=True, spacing=20, padding=20))
    page.update()