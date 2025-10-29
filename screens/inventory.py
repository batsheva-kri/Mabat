import flet as ft
from logic.inventory import get_category_name, sizes_for_category, get_inventory_products

def InventoryScreen(page, current_user, navigator, save_fn, supplier_id=0):
    page.title = "מסך מלאי"

    content = []
    categories = [1, 2, 3, 4]

    for cat_id in categories:
        products = get_inventory_products(cat_id)

        # אם אין מוצרים לקטגוריה הזו → דילוג
        if not products:
            continue

        cat_name = get_category_name(cat_id)
        content.append(ft.Text(cat_name, size=20, weight=ft.FontWeight.BOLD))

        # קטגוריות 1 ו־2 מוצגות כטבלה עם מידות
        if cat_id in [1, 2]:
            sizes = sizes_for_category(cat_id)
            header_row = [ft.Text("מידות")] + [ft.Text(p['name']) for p in products]
            table_rows = []

            # מילון חדש עבור TextFields
            text_fields_sizes = {}

            for size in sizes:
                row = [ft.Text(size)]
                for product in products:
                    tf = ft.TextField(width=50)
                    row.append(tf)
                    text_fields_sizes[(size, product['id'])] = tf
                table_rows.append(ft.Row(controls=row, spacing=10))

            table = ft.Column(
                controls=[ft.Row(controls=header_row, spacing=10)] + table_rows,
                spacing=5
            )
            content.append(table)

            def save_handler(e):
                items = []
                for (size, pid), tf in text_fields_sizes.items():
                    if tf.value and tf.value.isdigit():
                        items.append({
                            "product_id": pid,
                            "size": size,
                            "count": int(tf.value)
                        })
                save_fn(items,supplier_id)

            content.append(
                ft.ElevatedButton("שמור", on_click=save_handler)
            )

        # קטגוריות 3 ו־4 מוצגות כרשימה פשוטה של מוצר + כמות
        else:
            rows = []
            text_fields_simple = {}

            for product in products:
                tf = ft.TextField(width=100)
                rows.append(ft.Row(controls=[
                    ft.Text(product['name'], width=200),
                    tf
                ], spacing=10))
                text_fields_simple[product['id']] = tf

            content.append(ft.Column(controls=rows, spacing=5))

            def save_handler(e):
                items = []
                for pid, tf in text_fields_simple.items():
                    if tf.value and tf.value.isdigit():
                        items.append({
                            "product_id": pid,
                            "size": -1,
                            "count": int(tf.value)
                        })
                save_fn(items,supplier_id)

            content.append(
                ft.ElevatedButton("שמור", on_click=save_handler)
            )

    # כפתור חזרה
    back_button = ft.ElevatedButton(
        "⬅ חזרה",
        on_click=lambda e: navigator.go_inventory(
            user=current_user,
            save_arrived=save_fn,
            save_existing=save_fn
        )
    )
    content.append(back_button)

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
