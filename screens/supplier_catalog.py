# import flet as ft
# from logic.suppliers import (
#     get_all_suppliers,
#     get_suppliers_catalog_by_supplier_id,
#     add_supplier_catalog_entry,
#     update_supplier_catalog_entry,
#     delete_supplier_catalog_entry
# )
#
# class SupplierCatalog:
#     def __init__(self, page, navigator,user):
#         self.page = page
#         self.table = None
#         self.supplier_cb = None  # Dropdown לבחירת ספק
#         self.navigator = navigator
#         self.user = user
#
#     def open(self):
#         suppliers = get_all_suppliers()
#         supplier_names = ["כל הספקים"] + [f"{s['name']} (ID:{s['id']})" for s in suppliers]
#
#         self.supplier_cb = ft.Dropdown(
#             options=[ft.dropdown.Option(name) for name in supplier_names],
#             value="כל הספקים",
#             on_change=self.refresh_table
#         )
#
#         # תיבת חיפוש חיה
#         self.search_field = ft.TextField(
#             label="חפש מוצר",
#             on_change=self.refresh_table
#         )
#
#         # כפתור חזרה
#         self.back_button = ft.ElevatedButton("⬅ חזרה", on_click=lambda e: self.navigator.go_suppliers(user=self.user))
#         # כפתור הוספת מוצר
#         self.add_button = ft.ElevatedButton("➕ הוסף מוצר", on_click=self.add_product_dialog, bgcolor="#52b69a", color="white")
#
#         self.table = ft.DataTable(columns=[], rows=[])
#         self.refresh_table(self.supplier_cb)
#
#         controls = []
#         if self.back_button:
#             controls.append(self.back_button)
#         controls.append(self.add_button)
#         controls.extend([
#             ft.Row([ft.Text("בחר ספק:"), self.supplier_cb], alignment=ft.MainAxisAlignment.START),
#             self.search_field,
#             self.table
#         ])
#
#         self.page.controls.clear()
#         self.page.add(ft.Column(controls, spacing=20))
#         self.page.update()
#
#     def refresh_table(self, e_or_dropdown=None):
#         if hasattr(e_or_dropdown, "control"):
#             selected = e_or_dropdown.control.value
#         elif e_or_dropdown is not None:
#             selected = e_or_dropdown.value
#         else:
#             selected = self.supplier_cb.value
#
#         suppliers = get_all_suppliers()
#
#         # בדיקה על פורמט הספק
#         if selected == "כל הספקים":
#             displayed_suppliers = suppliers
#         else:
#             parts = selected.split("ID:")
#             if len(parts) > 1:
#                 supplier_id = int(parts[1].strip(")"))
#                 displayed_suppliers = [s for s in suppliers if s["id"] == supplier_id]
#             else:
#                 displayed_suppliers = suppliers
#
#         self.table.columns.clear()
#         self.table.rows.clear()
#
#         self.table.columns.append(ft.DataColumn(ft.Text("מזהה מוצר", size=18, weight=ft.FontWeight.BOLD)))
#         self.table.columns.append(ft.DataColumn(ft.Text("שם מוצר", size=18, weight=ft.FontWeight.BOLD)))
#         for s in displayed_suppliers:
#             self.table.columns.append(ft.DataColumn(ft.Text(s["name"], size=18, weight=ft.FontWeight.BOLD)))
#         self.table.columns.append(ft.DataColumn(ft.Text("פעולות", size=18, weight=ft.FontWeight.BOLD)))
#
#         # בניית מילון מוצר -> ספק -> מחיר
#         all_catalogs = {}
#         for s in displayed_suppliers:
#             catalog = get_suppliers_catalog_by_supplier_id(s["id"])
#             for entry in catalog:
#                 pid = entry["product_id"]
#                 if pid not in all_catalogs:
#                     all_catalogs[pid] = {"product_name": entry.get("product_name", ""), "prices": {}, "entries": {}}
#                 all_catalogs[pid]["prices"][s["id"]] = entry.get("price", "")
#                 all_catalogs[pid]["entries"][s["id"]] = entry
#
#         # סינון לפי חיפוש
#         search_text = self.search_field.value.lower() if hasattr(self, "search_field") else ""
#         filtered_catalogs = {pid: data for pid, data in all_catalogs.items() if search_text in data["product_name"].lower()}
#
#         if not filtered_catalogs:
#             self.table.rows.append(
#                 ft.DataRow(cells=[ft.DataCell(ft.Text("אין נתונים")) for _ in range(3 + len(displayed_suppliers))])
#             )
#         else:
#             for pid, data in filtered_catalogs.items():
#                 row_cells = [
#                     ft.DataCell(ft.Text(pid)),
#                     ft.DataCell(ft.Text(data["product_name"]))
#                 ]
#                 for s in displayed_suppliers:
#                     entry = data["entries"].get(s["id"])
#                     if entry:
#                         price_text = str(data["prices"].get(s["id"], ""))
#                         row_cells.append(ft.DataCell(
#                             ft.ElevatedButton(
#                                 price_text or "–",
#                                 on_click=lambda e, ent=entry: self.show_edit_dialog(ent),
#                                 bgcolor="#f0f0f0"
#                             )
#                         ))
#                     else:
#                         # במקרה שאין מחיר / אין ערך, יוצרים כפתור עם "-" שמפעיל דיאלוג עריכה חדש
#                         dummy_entry = {"supplier_id": s["id"], "product_id": pid, "product_name": data["product_name"],
#                                        "price": None}
#                         row_cells.append(ft.DataCell(
#                             ft.ElevatedButton(
#                                 "-",
#                                 on_click=lambda e, ent=dummy_entry: self.show_edit_dialog(ent),
#                                 bgcolor="#f0f0f0"
#                             )
#                         ))
#
#                 row_cells.append(ft.DataCell(
#                     ft.ElevatedButton(
#                         "🗑️ מחיקה",
#                         on_click=lambda e, entries=data["entries"]: self.delete_product(entries)
#                     )
#                 ))
#
#                 self.table.rows.append(ft.DataRow(cells=row_cells))
#
#         self.page.update()
#
#     def add_product_dialog(self, e=None):
#         suppliers = get_all_suppliers()
#         supplier_options = [ft.dropdown.Option(s["name"]) for s in suppliers]
#
#         name_field = ft.TextField(label="שם מוצר")
#         price_field = ft.TextField(label="מחיר")
#         supplier_dropdown = ft.Dropdown(label="בחר ספק", options=supplier_options)
#
#         def save_product(ev):
#             selected_supplier_name = supplier_dropdown.value
#             supplier = next((s for s in suppliers if s["name"] == selected_supplier_name), None)
#             if not supplier:
#                 self.page.snack_bar = ft.SnackBar(ft.Text("בחר ספק תקין"))
#                 self.page.snack_bar.open = True
#                 self.page.update()
#                 return
#             entry = {"supplier_id": supplier["id"], "product_name" : name_field.value, "price":float(price_field.value or 0)}
#             add_supplier_catalog_entry(entry)
#             self.close_dialog(dialog)
#             self.refresh_table(self.supplier_cb)
#
#         dialog = ft.AlertDialog(
#             title=ft.Text("הוסף מוצר חדש"),
#             content=ft.Column([name_field, supplier_dropdown, price_field], spacing=10),
#             actions=[
#                 ft.ElevatedButton("שמור", on_click=save_product),
#                 ft.ElevatedButton("ביטול", on_click=lambda e: self.close_dialog(dialog))
#             ]
#         )
#
#         self.page.dialog = dialog
#         dialog.open = True
#         self.page.add(dialog)
#         self.page.update()
#
#     def show_edit_dialog(self, entry):
#         product_name_field = ft.TextField(
#             label="שם מוצר",
#             value=entry.get("product_name", "") or "",
#             width=300
#         )
#         price_field = ft.TextField(
#             label="מחיר",
#             value="" if entry.get("price") is None else str(entry.get("price")),
#             width=300
#         )
#
#         def save_and_refresh(e):
#             self.save_entry(entry, price_field, dialog)
#
#         dialog = ft.AlertDialog(
#             title=ft.Text("עריכת מוצר"),
#             content=ft.Column(
#                 controls=[
#                     product_name_field,
#                     price_field,
#                     ft.Row([
#                         ft.ElevatedButton("שמירה", on_click=save_and_refresh),
#                         ft.ElevatedButton("ביטול", on_click=lambda e: self.close_dialog(dialog))
#                     ], spacing=10)
#                 ],
#                 spacing=10
#             ),
#             actions=[]
#         )
#
#         self.page.dialog = dialog
#         dialog.open = True
#         self.page.add(dialog)
#         self.page.update()
#
#     def save_entry(self, entry, price_field, dialog):
#         update_supplier_catalog_entry(
#             supplier_id=entry["supplier_id"],
#             product_id=entry["product_id"],
#             updates={
#                 "price": None if price_field.value.strip() == "" else float(price_field.value)
#             }
#         )
#         self.refresh_table(self.supplier_cb)
#         self.close_dialog(dialog)
#
#     def close_dialog(self, dialog):
#         dialog.open = False
#         self.page.update()
#
#     def delete_entry(self, entry):
#         delete_supplier_catalog_entry(supplier_id=entry["supplier_id"], product_id=entry["product_id"])
#         self.page.snack_bar = ft.SnackBar(ft.Text("✅ המוצר נמחק"))
#         self.page.snack_bar.open = True
#         self.page.update()
#         self.refresh_table(self.supplier_cb)
#
#     def delete_product(self, entries):
#         for entry in entries.values():
#             self.delete_entry(entry)
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

        filtered_catalogs = {pid: data for pid, data in all_catalogs.items()
                             if search_text in data["product_name"].lower()}

        if not filtered_catalogs:
            table.rows.append(
                ft.DataRow(cells=[ft.DataCell(ft.Text("אין נתונים")) for _ in range(len(table.columns))])
            )
        else:
            for pid, data in filtered_catalogs.items():
                row_cells = [ft.DataCell(ft.Text(pid)), ft.DataCell(ft.Text(data["product_name"]))]
                for s in displayed_suppliers:
                    entry = data["entries"].get(s["id"])
                    if entry:
                        price_text = str(data["prices"].get(s["id"], ""))
                        row_cells.append(ft.DataCell(
                            ft.ElevatedButton(
                                price_text or "–",
                                on_click=lambda e, ent=entry: show_edit_dialog(ent),
                                bgcolor="#f0f0f0"
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
    back_btn = ft.ElevatedButton("⬅ חזרה", on_click=lambda e: navigator.go_suppliers(user=current_user))
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
