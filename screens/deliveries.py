import flet as ft
import os
from datetime import datetime
from logic.deliveries import (
    get_deliveries,
    get_delivery_by_id,
    add_delivery,
    update_delivery,
    delete_delivery,
    export_single_pdf_preview,
    export_month_pdf_download
)

downloads_dir = os.path.join(os.path.expanduser("~"), "Downloads")

def DeliveriesScreen(page, navigator, user):
    page.title = "מעקב משלוחים"
    page.scroll = "always"
    page.rtl = True

    # refs
    search_field = ft.Ref[ft.TextField]()
    only_unpaid = ft.Ref[ft.Checkbox]()
    month_picker = ft.Ref[ft.Dropdown]()
    data_table = ft.Ref[ft.DataTable]()

    # month picker options
    now = datetime.now()
    month_options = [ft.dropdown.Option(f"{y}-{m:02d}") for y in range(now.year-1, now.year+1) for m in range(1,13)]
    month_picker_control = ft.Dropdown(width=140, options=month_options, value=f"{now.year}-{now.month:02d}")
    month_picker.current = month_picker_control

    # --- Load table ---
    def load_table(e=None):
        paid_filter = None if not only_unpaid.current.value else False
        month_val = month_picker.current.value
        month_filter = tuple(map(int, month_val.split("-"))) if month_val else None
        search_val = search_field.current.value.strip() if search_field.current.value else None

        rows_raw = get_deliveries(filter_paid=paid_filter, month_year=month_filter, search_text=search_val)
        rows = []
        for i, d in enumerate(rows_raw):
            paid_text = "✓" if d["paid"] else ""
            home_text = "כן" if d["home_delivery"] else "לא"
            created = d.get("created_at") or ""
            actions = ft.Row([
                ft.IconButton(icon=ft.Icons.EDIT, tooltip="ערוך", on_click=lambda e, did=d["id"]: open_edit(did)),
                ft.IconButton(icon=ft.Icons.DELETE, tooltip="מחק", on_click=lambda e, did=d["id"]: confirm_delete(did)),
                ft.IconButton(icon=ft.Icons.PRINT, tooltip="הדפס (תצוגה)", on_click=lambda e, did=d["id"]: export_single_pdf_preview(get_delivery_by_id(did), page)),
            ])
            rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(d["id"]))),
                    ft.DataCell(ft.Text(d["name"])),
                    ft.DataCell(ft.Text(d["address"] or "-")),
                    ft.DataCell(ft.Text(d["phone1"] or "-")),
                    ft.DataCell(ft.Text(d["phone2"] or "-")),
                    ft.DataCell(ft.Text(paid_text)),
                    ft.DataCell(ft.Text(home_text)),
                    ft.DataCell(ft.Text(created)),
                    ft.DataCell(actions),
                ], color="#f8f8f8" if i % 2 == 0 else "#ffffff")
            )

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("שם", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("כתובת", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("טלפון 1", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("טלפון 2", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("שולם", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("עד הבית", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("תאריך", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("פעולות", weight=ft.FontWeight.BOLD)),
            ],
            rows=rows,
            heading_row_color="#52b69a",
            border=ft.border.all(1, ft.Colors.GREY_300),
            column_spacing=12,
            divider_thickness=1,
            data_row_min_height=56,
            expand=True
        )

        if data_table.current:
            try:
                page.controls.remove(data_table.current)
            except ValueError:
                pass
        data_table.current = table
        page.controls.append(table)
        page.update()

    # --- dialogs ---
    def open_edit(delivery_id=None):
        if delivery_id:
            d = get_delivery_by_id(delivery_id)
            if not d:
                page.snack_bar = ft.SnackBar(ft.Text("משלוח לא נמצא"))
                page.snack_bar.open = True
                page.update()
                return
            name_val, addr_val, p1_val, p2_val = d["name"], d["address"] or "", d["phone1"] or "", d["phone2"] or ""
            paid_val, home_val, notes_val = bool(d["paid"]), bool(d["home_delivery"]), d.get("notes") or ""
        else:
            name_val = addr_val = p1_val = p2_val = notes_val = ""
            paid_val = home_val = False

        name_field = ft.TextField(label="שם", value=name_val, width=400)
        address_field = ft.TextField(label="כתובת", value=addr_val, width=400, multiline=True)
        phone1_field = ft.TextField(label="טלפון 1", value=p1_val)
        phone2_field = ft.TextField(label="טלפון 2", value=p2_val)
        paid_cb = ft.Checkbox(label="שולם", value=paid_val)
        home_cb = ft.Checkbox(label="עד הבית", value=home_val)
        notes_field = ft.TextField(label="הערות", value=notes_val, multiline=True, width=400)

        def close():
            page.overlay.clear()
            page.update()

        def save(e):
            try:
                if delivery_id:
                    update_delivery(delivery_id, name_field.value, address_field.value, phone1_field.value, phone2_field.value, paid_cb.value, home_cb.value, notes_field.value)
                    page.snack_bar = ft.SnackBar(ft.Text("המשלוח עודכן"))
                else:
                    add_delivery(name_field.value, address_field.value, phone1_field.value, phone2_field.value, paid_cb.value, home_cb.value, user["id"], notes_field.value)
                    page.snack_bar = ft.SnackBar(ft.Text("משלוח נוסף"))
                page.snack_bar.open = True
                page.update()
                close()
                load_table()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"שגיאה בשמירה: {ex}"))
                page.snack_bar.open = True
                page.update()

        dlg = ft.Container(
            content=ft.Column([
                ft.Text("עריכת משלוח" if delivery_id else "הוספת משלוח", size=20, weight=ft.FontWeight.BOLD),
                name_field, address_field,
                ft.Row([phone1_field, phone2_field], spacing=10),
                ft.Row([paid_cb, home_cb], spacing=20),
                notes_field,
                ft.Row([
                    ft.ElevatedButton("שמור", on_click=save, bgcolor="#52b69a", color="white"),
                    ft.ElevatedButton("ביטול", on_click=lambda e: close(), bgcolor="#f28c7d", color="white"),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=12)
            ], spacing=10),
            padding=20, bgcolor="#ffffff", border_radius=12
        )
        page.overlay.clear()
        page.overlay.append(dlg)
        page.update()

    def confirm_delete(delivery_id):
        def close():
            page.overlay.clear()
            page.update()
        def do_delete(e):
            try:
                delete_delivery(delivery_id)
                page.snack_bar = ft.SnackBar(ft.Text("המשלוח נמחק"))
                page.snack_bar.open = True
                page.update()
                page.overlay.clear()
                load_table()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"שגיאה במחיקה: {ex}"))
                page.snack_bar.open = True
                page.update()

        dlg = ft.Container(
            content=ft.Column([
                ft.Text("מחק משלוח", size=18, weight=ft.FontWeight.BOLD),
                ft.Text("האם למחוק את המשלוח?"),
                ft.Row([
                    ft.ElevatedButton("מחק", on_click=do_delete, bgcolor="#f28c7d", color="white"),
                    ft.ElevatedButton("ביטול",  on_click=lambda e: close(), bgcolor="#888", color="white")
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=12)
            ], spacing=10),
            padding=20, bgcolor="#ffffff", border_radius=12
        )
        page.overlay.clear()
        page.overlay.append(dlg)
        page.update()

    # --- Export monthly ---
    def on_export_month(e):
        month_val = month_picker.current.value
        y, m = map(int, month_val.split("-")) if month_val else (now.year, now.month)
        path = export_month_pdf_download(page, year=y, month=m)
        try:
            folder = os.path.dirname(path)
            if os.name == 'nt':
                os.startfile(folder)
        except Exception:
            pass

    # --- Build UI ---
    search_field_control = ft.TextField(ref=search_field, label="חיפוש לפי שם / טלפון", width=300, on_change=load_table)
    only_unpaid_control = ft.Checkbox(ref=only_unpaid, label="הצג רק לא שולם", value=False, on_change=load_table)

    controls = ft.Column([
        ft.Row([ft.Text("מעקב משלוחים", size=28, weight=ft.FontWeight.BOLD, color="#52b69a")]),
        ft.Row([
            search_field_control,
            only_unpaid_control,
            month_picker_control,
            ft.ElevatedButton("➕ הוסף משלוח", on_click=lambda e: open_edit(None), bgcolor="#52b69a", color="white"),
            ft.ElevatedButton("ייצוא דוח חודשי PDF", on_click=on_export_month, bgcolor="#4d96ff", color="white"),
            ft.ElevatedButton("חזור", on_click=lambda e: navigator.go_home(user), bgcolor="#f28c7d", color="white"),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=12),
    ], spacing=12, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    page.controls.clear()
    page.add(controls)
    load_table()
    page.update()
