import flet as ft
from logic.suppliers import (
    get_all_suppliers,
    get_suppliers_catalog_by_supplier_id,
    add_supplier_catalog_entry,
    update_supplier_catalog_entry,
    delete_supplier_catalog_entry
)

def SupplierCatalogScreen(page, current_user, navigator):
    page.title = "קטלוג ספקים"

    # --- DataTable ראשוני ---
    table = ft.DataTable(
        columns=[ft.DataColumn(ft.Text("טעינה..."))],
        rows=[ft.DataRow(cells=[ft.DataCell(ft.Text("-"))])]
    )

    # --- פונקציות עזר ---
    def show_snackbar(text):
        page.snack_bar = ft.SnackBar(ft.Text(text))
        page.snack_bar.open = True
        page.update()

    suppliers = get_all_suppliers()
    supplier_names = ["כל הספקים"] + [f"{s['name']} (ID:{s['id']})" for s in suppliers]

    supplier_cb = ft.Dropdown(
        label="בחר ספק",
        options=[ft.dropdown.Option(name) for name in supplier_names],
        value="כל הספקים",
        width=250
    )

    search_field = ft.TextField(label="חפש מוצר", width=250)

    # --- פונקציה לרענון הטבלה ---
    def refresh_table(e=None):
        selected = supplier_cb.value
        search_text = search_field.value.lower() if search_field.value else ""

        if selected == "כל הספקים":
            displayed_suppliers = suppliers
        else:
            parts = selected.split("ID:")
            supplier_id = int(parts[1].strip(")")) if len(parts) > 1 else None
            displayed_suppliers = [s for s in suppliers if s["id"] == supplier_id]

        table.columns.clear()
        table.rows.clear()

        if not displayed_suppliers:
            table.columns.append(ft.DataColumn(ft.Text("אין ספקים", weight=ft.FontWeight.BOLD)))
            table.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text("-"))]))
            page.update()
            return

        # כותרות
        table.columns.append(ft.DataColumn(ft.Text("מזהה מוצר", weight=ft.FontWeight.BOLD)))
        table.columns.append(ft.DataColumn(ft.Text("שם מוצר", weight=ft.FontWeight.BOLD)))
        for s in displayed_suppliers:
            table.columns.append(ft.DataColumn(ft.Text(s["name"], weight=ft.FontWeight.BOLD)))
        table.columns.append(ft.DataColumn(ft.Text("פעולות", weight=ft.FontWeight.BOLD)))

        # בניית נתונים
        all_catalogs = {}
        for s in displayed_suppliers:
            catalog = get_suppliers_catalog_by_supplier_id(s["id"])
            for entry in catalog:
                pid = entry["product_id"]
                if pid not in all_catalogs:
                    all_catalogs[pid] = {"product_name": entry.get("product_name", ""), "prices": {}, "entries": {}}
                all_catalogs[pid]["prices"][s["id"]] = entry.get("price", "")
                all_catalogs[pid]["entries"][s["id"]] = entry
        filtered_catalogs = {
            pid: data for pid, data in all_catalogs.items()
            if search_text in data["product_name"].lower()
        }

        if not filtered_catalogs:
            table.rows.append(
                ft.DataRow(cells=[ft.DataCell(ft.Text("אין נתונים")) for _ in range(len(table.columns))])
            )
        else:
            for pid, data in filtered_catalogs.items():
                # מציאת המחיר הזול ביותר (מתוך כל הספקים באותה שורה)
                valid_prices = [p for p in data["prices"].values() if isinstance(p, (int, float)) and p > 0]
                min_price = min(valid_prices) if valid_prices else None

                row_cells = [
                    ft.DataCell(ft.Text(pid)),
                    ft.DataCell(ft.Text(data["product_name"]))
                ]

                for s in displayed_suppliers:
                    entry = data["entries"].get(s["id"])
                    if entry:
                        price_value = data["prices"].get(s["id"], "")
                        price_text = str(price_value)
                        is_min = (min_price is not None and price_value == min_price)
                        # הוספת מסגרת צבעונית למחיר הזול ביותר
                        row_cells.append(ft.DataCell(
                            ft.Container(
                                content=ft.ElevatedButton(
                                    price_text or "–",
                                    on_click=lambda e, ent=entry: show_edit_dialog(ent),
                                    bgcolor="#f0f0f0",
                                    color="black"
                                ),
                                border=ft.border.all(3, "#52b69a") if is_min else None,
                                border_radius=8,
                                padding=2
                            )
                        ))
                    else:
                        dummy_entry = {"supplier_id": s["id"], "product_id": pid,
                                       "product_name": data["product_name"], "price": None}
                        row_cells.append(ft.DataCell(
                            ft.ElevatedButton(
                                "-",
                                on_click=lambda e, ent=dummy_entry: show_edit_dialog(ent),
                                bgcolor="#f0f0f0"
                            )
                        ))

                row_cells.append(ft.DataCell(
                    ft.ElevatedButton(
                        "🗑️ מחיקה",
                        on_click=lambda e, entries=data["entries"]: delete_product(entries)
                    )
                ))

                table.rows.append(ft.DataRow(cells=row_cells))

        page.update()

    # --- Overlay Dialogs ---
    def show_overlay_dialog(title_text, content_controls, on_save):
        def close_dialog():
            page.overlay.clear()
            page.update()

        dlg = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(title_text, size=24, weight=ft.FontWeight.BOLD),
                    *content_controls,
                    ft.Row([
                        ft.ElevatedButton("שמור", on_click=on_save, bgcolor="#52b69a", color="white"),
                        ft.ElevatedButton("ביטול", on_click=lambda e: close_dialog(), bgcolor="#f28c7d", color="white")
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=12)
                ],
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=25,
            bgcolor="#ffffff",
            border_radius=14,
            alignment=ft.alignment.center
        )
        page.overlay.clear()
        page.overlay.append(dlg)
        page.update()
        return close_dialog

    def add_product_dialog(e=None):
        name_field = ft.TextField(label="שם מוצר")
        price_field = ft.TextField(label="מחיר")
        supplier_dropdown = ft.Dropdown(label="בחר ספק", options=[ft.dropdown.Option(s["name"]) for s in suppliers])

        def save_product(ev):
            selected_name = supplier_dropdown.value
            supplier = next((s for s in suppliers if s["name"] == selected_name), None)
            if not supplier:
                show_snackbar("בחר ספק תקין")
                return
            entry = {"supplier_id": supplier["id"], "product_name": name_field.value, "price": float(price_field.value or 0)}
            add_supplier_catalog_entry(entry)
            close_fn()
            refresh_table()

        close_fn = show_overlay_dialog("הוסף מוצר חדש", [name_field, supplier_dropdown, price_field], save_product)

    def show_edit_dialog(entry):
        product_name_field = ft.TextField(label="שם מוצר", value=entry.get("product_name", ""), width=300)
        price_field = ft.TextField(label="מחיר", value=str(entry.get("price") or ""), width=300)

        def save_and_refresh(e):
            update_supplier_catalog_entry(
                supplier_id=entry["supplier_id"],
                product_id=entry["product_id"],
                updates={"price": None if price_field.value.strip() == "" else float(price_field.value)}
            )
            close_fn()
            refresh_table()

        close_fn = show_overlay_dialog("עריכת מוצר", [product_name_field, price_field], save_and_refresh)

    def delete_entry(entry):
        delete_supplier_catalog_entry(entry["supplier_id"], entry["product_id"])
        show_snackbar("✅ המוצר נמחק")
        refresh_table()

    def delete_product(entries):
        for entry in entries.values():
            delete_entry(entry)

    # --- כפתורי ניווט ---
    back_btn = ft.ElevatedButton("⬅ חזרה", on_click=lambda e: navigator.go_suppliers(user=current_user), bgcolor="#f28c7d", color="white")
    add_btn = ft.ElevatedButton("➕ הוסף מוצר", on_click=add_product_dialog, bgcolor="#52b69a", color="white")

    # --- Layout ---
    page.controls.clear()
    page.add(
        ft.ListView(
            controls=[
                ft.Text("קטלוג ספקים", size=26, weight=ft.FontWeight.BOLD, color="#52b69a"),
                ft.Row([supplier_cb, search_field, add_btn, back_btn], spacing=10),
                ft.Container(content=ft.Column([table], expand=True), padding=10, bgcolor="#f9f9f9", border_radius=10)
            ],
            spacing=20,
            padding=20,
            expand=True
        )
    )

    supplier_cb.on_change = refresh_table
    search_field.on_change = refresh_table

    refresh_table()
    page.update()
