# import flet as ft
# from logic.inventory import get_category_name, sizes_for_category, get_inventory_products
# from logic.suppliers import get_all_suppliers
# def InventoryScreen(page, current_user, navigator, save_fn, show_dropdown=False):
#     page.title = "מסך מלאי"
#     content = []
#
#     # --- Dropdown של ספקים אם נדרש ---
#     if show_dropdown:
#         suppliers = get_all_suppliers()
#         supplier_var = ft.Dropdown(
#             label="בחר ספק",
#             options=[ft.dropdown.Option(str(s["id"]), s["name"]) for s in suppliers],
#             width=300
#         )
#         content.append(ft.Row([supplier_var], spacing=20))
#     else:
#         supplier_var = None  # אם אין dropdown
#     categories = [1, 2, 3, 4]
#
#     for cat_id in categories:
#         products = get_inventory_products(cat_id)
#
#         # אם אין מוצרים לקטגוריה הזו → דילוג
#         if not products:
#             continue
#
#         cat_name = get_category_name(cat_id)
#         content.append(ft.Text(cat_name, size=20, weight=ft.FontWeight.BOLD))
#
#         # קטגוריות 1 ו־2 מוצגות כטבלה עם מידות
#         if cat_id in [1, 2]:
#             sizes = sizes_for_category(cat_id)
#             header_row = [ft.Text("מידות")] + [ft.Text(p['name']) for p in products]
#             table_rows = []
#
#             # מילון חדש עבור TextFields
#             text_fields_sizes = {}
#
#             for size in sizes:
#                 row = [ft.Text(size)]
#                 for product in products:
#                     tf = ft.TextField(width=50)
#                     row.append(tf)
#                     text_fields_sizes[(size, product['id'])] = tf
#                 table_rows.append(ft.Row(controls=row, spacing=10))
#
#             table = ft.Column(
#                 controls=[ft.Row(controls=header_row, spacing=10)] + table_rows,
#                 spacing=5
#             )
#             content.append(table)
#
#             def save_handler(e):
#                 items = []
#                 for (size, pid), tf in text_fields_sizes.items():
#                     if tf.value and tf.value.isdigit():
#                         items.append({
#                             "product_id": pid,
#                             "size": size,
#                             "count": int(tf.value)
#                         })
#                 supplier_id = int(supplier_var.value) if supplier_var else 0
#                 save_fn(items,supplier_id,page)
#                 navigator.go_home(current_user)
#
#             content.append(
#                 ft.ElevatedButton("שמור", on_click=save_handler)
#             )
#
#         # קטגוריות 3 ו־4 מוצגות כרשימה פשוטה של מוצר + כמות
#         else:
#             rows = []
#             text_fields_simple = {}
#
#             for product in products:
#                 tf = ft.TextField(width=100)
#                 rows.append(ft.Row(controls=[
#                     ft.Text(product['name'], width=200),
#                     tf
#                 ], spacing=10))
#                 text_fields_simple[product['id']] = tf
#
#             content.append(ft.Column(controls=rows, spacing=5))
#
#             def save_handler(e):
#                 items = []
#                 for pid, tf in text_fields_simple.items():
#                     if tf.value and tf.value.isdigit():
#                         items.append({
#                             "product_id": pid,
#                             "size": -1,
#                             "count": int(tf.value)
#                         })
#                 supplier_id = int(supplier_var.value) if supplier_var else 0
#                 print("I am save 3,4")
#                 print("items", items)
#                 save_fn(items,supplier_id)
#                 navigator.go_home(current_user)
#
#             content.append(
#                 ft.ElevatedButton("שמור", on_click=save_handler)
#             )
#
#     # כפתור חזרה
#     back_button = ft.ElevatedButton(
#         "⬅ חזרה",
#         on_click=lambda e: navigator.go_orders(
#             user=current_user)
#     )
#     content.append(back_button)
#
#     # הוספת תוכן ל־page
#     page.controls.clear()
#     page.add(
#         ft.ListView(
#             controls=content,
#             expand=True,
#             spacing=20,
#             padding=20,
#             auto_scroll=False
#         )
#     )
#     page.update()
import flet as ft
from logic.inventory import get_category_name, sizes_for_category, get_inventory_products
from logic.suppliers import get_all_suppliers

def InventoryScreen(page, current_user, navigator, save_fn, show_dropdown=False):
    page.title = "מסך מלאי"
    content = []

    # --- Dropdown של ספקים אם נדרש ---
    if show_dropdown:
        suppliers = get_all_suppliers()
        supplier_var = ft.Dropdown(
            label="בחר ספק",
            options=[ft.dropdown.Option(str(s["id"]), s["name"]) for s in suppliers],
            width=300
        )
        content.append(ft.Row([supplier_var], spacing=20))
    else:
        supplier_var = None

    categories = [1, 2, 3, 4]

    # כפתור חזרה
    back_button = ft.ElevatedButton(
        "⬅ חזרה",
        on_click=lambda e: navigator.go_orders(user=current_user),
        bgcolor="#F28C7D",
        color="#FFFFFF"
    )
    content.append(back_button)

    for cat_id in categories:
        products = get_inventory_products(cat_id)
        if not products:
            continue

        cat_name = get_category_name(cat_id)
        content.append(ft.Text(cat_name, size=20, weight=ft.FontWeight.BOLD))

        # קטגוריות 1 ו־2 עם מידות
        if cat_id in [1, 2]:
            sizes = sizes_for_category(cat_id)

            # כותרות עמודות
            header_row = ft.Row(
                controls=[ft.Text("מידה", weight=ft.FontWeight.BOLD, width=60)] +
                         [ft.Text(p['name'], weight=ft.FontWeight.BOLD, width=60) for p in products],
                spacing=0
            )
            content.append(header_row)

            # יצירת שורות עם TextFields
            table_rows = []
            text_fields_sizes = {}
            for size in sizes:
                row_controls = [ft.Text(size, width=60)]
                for product in products:
                    tf = ft.TextField(width=60, height=40)
                    text_fields_sizes[(size, product["id"])] = tf
                    row_controls.append(tf)
                table_rows.append(ft.Row(controls=row_controls, spacing=0))

            # Column גלילה לשורות בלבד
            scrollable_rows = ft.Container(
                content=ft.Column(
                    controls=table_rows,
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True
                ),
                border=ft.border.all(1, "#B0B0B0"),
                border_radius=8,
                padding=5,
                height=300
            )
            content.append(scrollable_rows)

            # כפתור שמירה
            def save_handler(e):
                items = []
                for (size, pid), tf in text_fields_sizes.items():
                    if tf.value and tf.value.isdigit():
                        items.append({
                            "product_id": pid,
                            "size": size,
                            "count": int(tf.value)
                        })
                supplier_id = int(supplier_var.value) if supplier_var else 0
                save_fn(items, supplier_id, page)
                navigator.go_home(current_user)

            content.append(ft.ElevatedButton(
                "שמור",
                on_click=save_handler,
                bgcolor="#52b69a",
                color="#FFFFFF"
            ))

        # קטגוריות 3 ו־4 כרשימה פשוטה
        else:
            rows = []
            text_fields_simple = {}

            for product in products:
                tf = ft.TextField(width=100)
                text_fields_simple[product['id']] = tf
                rows.append(ft.Row(
                    controls=[ft.Text(product['name'], width=200), tf],
                    spacing=10
                ))

            content.append(
                ft.Container(
                    content=ft.Column(controls=rows, spacing=5),
                    border=ft.border.all(1, "#B0B0B0"),
                    border_radius=8,
                    padding=10
                )
            )

            def save_handler(e):
                items = []
                for pid, tf in text_fields_simple.items():
                    if tf.value and tf.value.isdigit():
                        items.append({
                            "product_id": pid,
                            "size": -1,
                            "count": int(tf.value)
                        })
                supplier_id = int(supplier_var.value) if supplier_var else 0
                save_fn(items, supplier_id, page)
                navigator.go_home(current_user)

            content.append(ft.ElevatedButton(
                "שמור",
                on_click=save_handler,
                bgcolor="#52b69a",
                color="#FFFFFF"
            ))

    # הוספת תוכן ל־page
    page.controls.clear()
    page.add(
        ft.ListView(
            controls=content,
            expand=True,
            spacing=20,
            padding=20,
            auto_scroll=False
        )
    )
    page.update()
