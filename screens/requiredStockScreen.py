import flet as ft
from logic.inventory import (
    sizes_for_category,
    get_inventory_products,
    get_categories,
    get_required_stock_products,
    add_required_stock
)


def RequiredStockScreen(page, current_user, navigator):
    page.title = "ניהול מלאי נדרש"

    # --- פונקציית עריכה (דיאלוג) ---
    # --- פונקציית עריכה (שימוש ב-Overlay כמו בקטלוג) ---
    def open_edit_dialog(category):
        cat_id = category["id"]
        products = get_inventory_products(cat_id)
        has_sizes = category.get("has_sizes")

        dialog_fields = []
        # בניית תוכן השדות
        container_content = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, tight=True)

        if has_sizes:
            sizes = sizes_for_category(cat_id)
            header = ft.Row([
                                ft.Text("מידה", width=50, weight=ft.FontWeight.BOLD)] +
                            [ft.Text(p['name'], width=70, size=11, weight=ft.FontWeight.BOLD) for p in products]
                            )
            container_content.controls.append(header)

            for s in sizes:
                row_fields = [ft.Text(str(s), width=50)]
                for p in products:
                    tf = ft.TextField(width=70, height=40, text_size=13, data={"pid": p["id"], "size": s})
                    dialog_fields.append(tf)
                    row_fields.append(tf)
                container_content.controls.append(ft.Row(row_fields, spacing=5))
        else:
            for p in products:
                tf = ft.TextField(label=p['name'], width=200, data={"pid": p["id"], "size": -1})
                dialog_fields.append(tf)
                container_content.controls.append(ft.Row([tf], alignment=ft.MainAxisAlignment.CENTER))

        def close_overlay():
            page.overlay.clear()
            page.update()

        def save_and_close(e):
            for tf in dialog_fields:
                if tf.value and tf.value.isdigit():
                    add_required_stock(
                        product_id=tf.data["pid"],
                        required_count=int(tf.value),
                        size=tf.data["size"]
                    )
            close_overlay()
            # רענון המסך כולו כדי לראות את הנתונים החדשים בטבלאות
            RequiredStockScreen(page, current_user, navigator)

        # יצירת הקונטיינר של ה"דיאלוג"
        overlay_container = ft.Container(
            content=ft.Column([
                ft.Text(f"עריכת מלאי נדרש: {category['name']}", size=22, weight=ft.FontWeight.BOLD),
                ft.Container(content=container_content, height=400),  # הגבלת גובה לתוכן הנגלל
                ft.Row([
                    ft.ElevatedButton("שמור הכל", on_click=save_and_close, bgcolor="#52b69a", color="white"),
                    ft.ElevatedButton("ביטול", on_click=lambda _: close_overlay(), bgcolor="#f28c7d", color="white"),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=12)
            ], spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            padding=20,
            bgcolor="#ffffff",
            border_radius=14,
            border=ft.border.all(2, "#52b69a"),
            shadow=ft.BoxShadow(blur_radius=20, color=ft.Colors.BLACK45),
            width=600,
            # מרכוז ה-Container על המסך
            left=page.window_width / 2 - 300 if page.window_width else 100,
            top=50
        )

        page.overlay.clear()
        page.overlay.append(overlay_container)
        page.update()
    # --- בניית תוכן המסך הראשי ---
    required_data = get_required_stock_products()
    all_categories = get_categories()

    # בניית מפה לגישה מהירה לנתונים: {(product_id, size): count}
    stock_map = {(item['id'], item['size']): item['required_count'] for item in required_data}

    content_list = []

    # כפתור חזרה
    content_list.append(
        ft.ElevatedButton(
            "⬅ חזרה",
            on_click=lambda _: navigator.go_orders(current_user),
            bgcolor="#F28C7D",
            color="white"
        )
    )

    for cat in all_categories:
        cat_id = cat['id']
        products = get_inventory_products(cat_id)
        if not products:
            continue

        # כותרת קטגוריה וכפתור עריכה
        content_list.append(
            ft.Row([
                ft.Text(cat['name'], size=20, weight=ft.FontWeight.BOLD, color="#2a9d8f"),
                ft.IconButton(
                    icon=ft.Icons.EDIT_NOTE,
                    on_click=lambda e, c=cat: open_edit_dialog(c),
                    icon_color="#2a9d8f",
                    tooltip="ערוך כמויות"
                )
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

        if cat.get("has_sizes"):
            sizes = sizes_for_category(cat_id)

            # בניית ה-DataTable
            columns = [ft.DataColumn(ft.Text("מידה", weight="bold"))]
            for p in products:
                columns.append(ft.DataColumn(ft.Text(p['name'], weight="bold")))

            rows = []
            for s in sizes:
                cells = [ft.DataCell(ft.Text(str(s)))]
                for p in products:
                    count = stock_map.get((p['id'], s), 0)
                    cells.append(ft.DataCell(ft.Text(str(count) if count > 0 else "-")))
                rows.append(ft.DataRow(cells=cells))

            content_list.append(
                ft.Container(
                    content=ft.DataTable(columns=columns, rows=rows, heading_row_color="#F0F0F0"),
                    border=ft.border.all(1, "#E0E0E0"),
                    border_radius=10,
                    padding=5
                )
            )
        else:
            # תצוגה פשוטה ללא מידות
            simple_items = []
            for p in products:
                count = stock_map.get((p['id'], -1), 0)
                simple_items.append(
                    ft.Row([
                        ft.Text(p['name'], width=200),
                        ft.Text(str(count), weight=ft.FontWeight.BOLD)
                    ])
                )
            content_list.append(
                ft.Container(
                    content=ft.Column(simple_items, spacing=5),
                    padding=10,
                    border=ft.border.all(1, "#E0E0E0"),
                    border_radius=10
                )
            )

        content_list.append(ft.Divider(height=20, color="transparent"))

    # ניקוי והוספה לדף כפי שאת עושה תמיד
    page.controls.clear()
    page.add(
        ft.ListView(
            controls=content_list,
            expand=True,
            padding=20,
            spacing=15
        )
    )
    page.update()