import flet as ft
from logic.suppliers import (
    get_all_suppliers,
    get_suppliers_catalog_by_supplier_id,
    add_supplier_catalog_entry,
    update_supplier_catalog_entry,
    delete_supplier_catalog_entry
)

class SupplierCatalog:
    def __init__(self, page, navigator,user):
        self.page = page
        self.table = None
        self.supplier_cb = None  # Dropdown לבחירת ספק
        self.navigator = navigator
        self.user = user

    def open(self):
        suppliers = get_all_suppliers()
        supplier_names = ["כל הספקים"] + [f"{s['name']} (ID:{s['id']})" for s in suppliers]

        self.supplier_cb = ft.Dropdown(
            options=[ft.dropdown.Option(name) for name in supplier_names],
            value="כל הספקים",
            on_change=self.refresh_table
        )

        # תיבת חיפוש חיה
        self.search_field = ft.TextField(
            label="חפש מוצר",
            on_change=self.refresh_table
        )

        # כפתור חזרה
        self.back_button = ft.ElevatedButton("⬅ חזרה", on_click=lambda e: self.navigator.go_suppliers(user=self.user))
        # כפתור הוספת מוצר
        self.add_button = ft.ElevatedButton("➕ הוסף מוצר", on_click=self.add_product_dialog, bgcolor="#52b69a", color="white")

        self.table = ft.DataTable(columns=[], rows=[])
        self.refresh_table(self.supplier_cb)

        controls = []
        if self.back_button:
            controls.append(self.back_button)
        controls.append(self.add_button)
        controls.extend([
            ft.Row([ft.Text("בחר ספק:"), self.supplier_cb], alignment=ft.MainAxisAlignment.START),
            self.search_field,
            self.table
        ])

        self.page.controls.clear()
        self.page.add(ft.Column(controls, spacing=20))
        self.page.update()

    def refresh_table(self, e_or_dropdown=None):
        if hasattr(e_or_dropdown, "control"):
            selected = e_or_dropdown.control.value
        elif e_or_dropdown is not None:
            selected = e_or_dropdown.value
        else:
            selected = self.supplier_cb.value

        suppliers = get_all_suppliers()

        # בדיקה על פורמט הספק
        if selected == "כל הספקים":
            displayed_suppliers = suppliers
        else:
            parts = selected.split("ID:")
            if len(parts) > 1:
                supplier_id = int(parts[1].strip(")"))
                displayed_suppliers = [s for s in suppliers if s["id"] == supplier_id]
            else:
                displayed_suppliers = suppliers

        self.table.columns.clear()
        self.table.rows.clear()

        self.table.columns.append(ft.DataColumn(ft.Text("מזהה מוצר", size=18, weight=ft.FontWeight.BOLD)))
        self.table.columns.append(ft.DataColumn(ft.Text("שם מוצר", size=18, weight=ft.FontWeight.BOLD)))
        for s in displayed_suppliers:
            self.table.columns.append(ft.DataColumn(ft.Text(s["name"], size=18, weight=ft.FontWeight.BOLD)))
        self.table.columns.append(ft.DataColumn(ft.Text("פעולות", size=18, weight=ft.FontWeight.BOLD)))

        # בניית מילון מוצר -> ספק -> מחיר
        all_catalogs = {}
        for s in displayed_suppliers:
            catalog = get_suppliers_catalog_by_supplier_id(s["id"])
            for entry in catalog:
                pid = entry["product_id"]
                if pid not in all_catalogs:
                    all_catalogs[pid] = {"product_name": entry.get("product_name", ""), "prices": {}, "entries": {}}
                all_catalogs[pid]["prices"][s["id"]] = entry.get("price", "")
                all_catalogs[pid]["entries"][s["id"]] = entry

        # סינון לפי חיפוש
        search_text = self.search_field.value.lower() if hasattr(self, "search_field") else ""
        filtered_catalogs = {pid: data for pid, data in all_catalogs.items() if search_text in data["product_name"].lower()}

        if not filtered_catalogs:
            self.table.rows.append(
                ft.DataRow(cells=[ft.DataCell(ft.Text("אין נתונים")) for _ in range(3 + len(displayed_suppliers))])
            )
        else:
            for pid, data in filtered_catalogs.items():
                row_cells = [
                    ft.DataCell(ft.Text(pid)),
                    ft.DataCell(ft.Text(data["product_name"]))
                ]
                for s in displayed_suppliers:
                    entry = data["entries"].get(s["id"])
                    if entry:
                        price_text = str(data["prices"].get(s["id"], ""))
                        row_cells.append(ft.DataCell(
                            ft.ElevatedButton(
                                price_text or "–",
                                on_click=lambda e, ent=entry: self.show_edit_dialog(ent),
                                bgcolor="#f0f0f0"
                            )
                        ))
                    else:
                        # במקרה שאין מחיר / אין ערך, יוצרים כפתור עם "-" שמפעיל דיאלוג עריכה חדש
                        dummy_entry = {"supplier_id": s["id"], "product_id": pid, "product_name": data["product_name"],
                                       "price": None}
                        row_cells.append(ft.DataCell(
                            ft.ElevatedButton(
                                "-",
                                on_click=lambda e, ent=dummy_entry: self.show_edit_dialog(ent),
                                bgcolor="#f0f0f0"
                            )
                        ))

                row_cells.append(ft.DataCell(
                    ft.ElevatedButton(
                        "🗑️ מחיקה",
                        on_click=lambda e, entries=data["entries"]: self.delete_product(entries)
                    )
                ))

                self.table.rows.append(ft.DataRow(cells=row_cells))

        self.page.update()

    def add_product_dialog(self, e=None):
        suppliers = get_all_suppliers()
        supplier_options = [ft.dropdown.Option(s["name"]) for s in suppliers]

        name_field = ft.TextField(label="שם מוצר")
        price_field = ft.TextField(label="מחיר")
        supplier_dropdown = ft.Dropdown(label="בחר ספק", options=supplier_options)

        def save_product(ev):
            selected_supplier_name = supplier_dropdown.value
            supplier = next((s for s in suppliers if s["name"] == selected_supplier_name), None)
            if not supplier:
                self.page.snack_bar = ft.SnackBar(ft.Text("בחר ספק תקין"))
                self.page.snack_bar.open = True
                self.page.update()
                return
            entry = {"supplier_id": supplier["id"], "product_name" : name_field.value, "price":float(price_field.value or 0)}
            add_supplier_catalog_entry(entry)
            self.close_dialog(dialog)
            self.refresh_table(self.supplier_cb)

        dialog = ft.AlertDialog(
            title=ft.Text("הוסף מוצר חדש"),
            content=ft.Column([name_field, supplier_dropdown, price_field], spacing=10),
            actions=[
                ft.ElevatedButton("שמור", on_click=save_product),
                ft.ElevatedButton("ביטול", on_click=lambda e: self.close_dialog(dialog))
            ]
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.add(dialog)
        self.page.update()

    def show_edit_dialog(self, entry):
        product_name_field = ft.TextField(
            label="שם מוצר",
            value=entry.get("product_name", "") or "",
            width=300
        )
        price_field = ft.TextField(
            label="מחיר",
            value="" if entry.get("price") is None else str(entry.get("price")),
            width=300
        )

        def save_and_refresh(e):
            self.save_entry(entry, price_field, dialog)

        dialog = ft.AlertDialog(
            title=ft.Text("עריכת מוצר"),
            content=ft.Column(
                controls=[
                    product_name_field,
                    price_field,
                    ft.Row([
                        ft.ElevatedButton("שמירה", on_click=save_and_refresh),
                        ft.ElevatedButton("ביטול", on_click=lambda e: self.close_dialog(dialog))
                    ], spacing=10)
                ],
                spacing=10
            ),
            actions=[]
        )

        self.page.dialog = dialog
        dialog.open = True
        self.page.add(dialog)
        self.page.update()

    def save_entry(self, entry, price_field, dialog):
        update_supplier_catalog_entry(
            supplier_id=entry["supplier_id"],
            product_id=entry["product_id"],
            updates={
                "price": None if price_field.value.strip() == "" else float(price_field.value)
            }
        )
        self.refresh_table(self.supplier_cb)
        self.close_dialog(dialog)

    def close_dialog(self, dialog):
        dialog.open = False
        self.page.update()

    def delete_entry(self, entry):
        delete_supplier_catalog_entry(supplier_id=entry["supplier_id"], product_id=entry["product_id"])
        self.page.snack_bar = ft.SnackBar(ft.Text("✅ המוצר נמחק"))
        self.page.snack_bar.open = True
        self.page.update()
        self.refresh_table(self.supplier_cb)

    def delete_product(self, entries):
        for entry in entries.values():
            self.delete_entry(entry)
