import flet as ft
from datetime import datetime
from logic.deliveries import (
    get_deliveries,
    get_delivery_by_id,
    add_delivery,
    update_delivery,
    delete_delivery,
    export_range_summary_pdf
)

from Mabat.logic.deliveries import export_single_pdf_print


def DeliveriesScreen(page, navigator, user):
    page.title = "מעקב משלוחים"
    page.scroll = ft.ScrollMode.AUTO
    page.rtl = True
    now = datetime.now()
    search_field = ft.Ref[ft.TextField]()
    month_picker = ft.Ref[ft.Dropdown]()
    start_picker = ft.Dropdown(
        label="מחודש",
        value=f"{now.year}-{now.month:02d}",
        options=[ft.dropdown.Option(f"{y}-{m:02d}") for y in range(2023, now.year + 1) for m in range(1, 13)]
    )

    end_picker = ft.Dropdown(
        label="עד חודש",
        value=f"{now.year}-{now.month:02d}",
        options=[ft.dropdown.Option(f"{y}-{m:02d}") for y in range(2023, now.year + 1) for m in range(1, 13)]
    )
    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("שם", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("כתובת", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("טלפון 1", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("טלפון 2", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("תשלום", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("סכום", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("עד הבית", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("תאריך", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("פעולות", size=18, weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        heading_row_color="#52b69a",
        border=ft.border.all(1, ft.Colors.GREY_300),
        column_spacing=20,
        divider_thickness=1,
        data_row_min_height=50,
        expand=True
    )

    # --- Month Picker ---

    month_picker_control = ft.Dropdown(
        ref=month_picker,
        width=140,
        value=f"{now.year}-{now.month:02d}",
        options=[
            ft.dropdown.Option(f"{y}-{m:02d}")
            for y in range(now.year - 1, now.year + 1)
            for m in range(1, 13)
        ],
        on_change=lambda e: load_table()
    )

    # --- Load Table ---
    def load_table(e=None):
        data_table.rows.clear()

        month_val = month_picker.current.value
        month_filter = tuple(map(int, month_val.split("-"))) if month_val else None
        search_val = search_field.current.value.strip() if search_field.current.value else None

        rows = get_deliveries(
            filter_paid=None,
            month_year=month_filter,
            search_text=search_val
        )

        for i, d in enumerate(rows):
            payment = "מזומן" if d["cash"] else "אשראי"
            amount = str(d["cash_amount"]) if d["cash"] else "-"
            home = "כן" if d["home_delivery"] else "לא"

            actions = ft.Row([
                ft.IconButton(
                    icon=ft.Icons.CONTENT_COPY,
                    tooltip="שכפל",
                    on_click=lambda e, did=d["id"]: copy_delivery(did)
                ),
                ft.IconButton(
                    icon=ft.Icons.EDIT,
                    tooltip="ערוך",
                    on_click=lambda e, did=d["id"]: open_edit(did)
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE,
                    tooltip="מחק",
                    on_click=lambda e, did=d["id"]: confirm_delete(did)
                ),
                ft.IconButton(
                    icon=ft.Icons.PRINT,
                    tooltip="הדפס",
                    on_click=lambda e, did=d["id"]: export_single_pdf_print(
                        get_delivery_by_id(did), page
                    )

                ),
            ])

            data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(d["name"])),
                        ft.DataCell(ft.Text(d["address"] or "-")),
                        ft.DataCell(ft.Text(d["phone1"] or "-")),
                        ft.DataCell(ft.Text(d["phone2"] or "-")),
                        ft.DataCell(ft.Text(payment)),
                        ft.DataCell(ft.Text(amount)),
                        ft.DataCell(ft.Text(home)),
                        ft.DataCell(ft.Text(d["created_at"])),
                        ft.DataCell(actions),
                    ],
                    color="#f8f8f8" if i % 2 == 0 else "#ffffff"
                )
            )

        page.update()

    # --- Copy Delivery ---
    def copy_delivery(delivery_id):
        d = get_delivery_by_id(delivery_id)
        if d:
            open_edit(None, preset_data=d)

    # --- Edit / Add / Copy Dialog ---
    def open_edit(delivery_id=None, preset_data=None):
        d = preset_data or (get_delivery_by_id(delivery_id) if delivery_id else {})

        name = d.get("name", "")
        address = d.get("address", "")
        phone1 = d.get("phone1", "")
        phone2 = d.get("phone2", "")
        cash = bool(d.get("cash", True))
        amount = d.get("cash_amount", 0)
        home = bool(d.get("home_delivery", False))
        notes = d.get("notes", "")

        name_f = ft.TextField(label="שם", value=name)
        address_f = ft.TextField(label="כתובת", value=address, multiline=True)
        phone1_f = ft.TextField(label="טלפון 1", value=phone1)
        phone2_f = ft.TextField(label="טלפון 2", value=phone2)
        cash_cb = ft.Checkbox(label="מזומן", value=cash)
        credit_cb = ft.Checkbox(label="אשראי", value=not cash)
        amount_f = ft.TextField(label="סכום", value=str(amount), visible=cash)
        home_cb = ft.Checkbox(label="עד הבית", value=home)
        notes_f = ft.TextField(label="הערות", value=notes, multiline=True)

        # Toggle נכון: כל לחיצה משנה את השני וגם שדה הסכום
        def toggle(e=None):
            if e.control == cash_cb:
                credit_cb.value = not cash_cb.value
            elif e.control == credit_cb:
                cash_cb.value = not credit_cb.value

            amount_f.visible = cash_cb.value  # רק כשמזומן מסומן הסכום נראה
            page.update()

        cash_cb.on_change = toggle
        credit_cb.on_change = toggle

        def save(e):
            if delivery_id:
                update_delivery(
                    delivery_id, name_f.value, address_f.value,
                    phone1_f.value, phone2_f.value,
                    cash_cb.value, float(amount_f.value or 0),
                    home_cb.value, notes_f.value
                )
            else:
                add_delivery(
                    name_f.value, address_f.value,
                    phone1_f.value, phone2_f.value,
                    cash_cb.value, float(amount_f.value or 0),
                    home_cb.value, user["id"], notes_f.value
                )
            page.overlay.clear()
            load_table()

        page.overlay.clear()
        page.overlay.append(
            ft.Container(
                content=ft.Column([
                    ft.Text(
                        "שכפול משלוח" if preset_data else
                        ("עריכת משלוח" if delivery_id else "הוספת משלוח"),
                        size=22, weight=ft.FontWeight.BOLD
                    ),
                    name_f, address_f,
                    ft.Row([phone1_f, phone2_f]),
                    ft.Row([cash_cb, credit_cb]),
                    amount_f, home_cb, notes_f,
                    ft.Row([
                        ft.ElevatedButton("שמור", on_click=save,
                                          bgcolor="#52b69a", color="white"),
                        ft.ElevatedButton(
                            "ביטול",
                            on_click=lambda e: (page.overlay.clear(), page.update()),
                            bgcolor="#f28c7d",
                            color="white"
                        )

                    ], alignment=ft.MainAxisAlignment.CENTER)
                ], spacing=10),
                padding=20,
                bgcolor="white",
                border_radius=14
            )
        )
        page.update()

    def confirm_delete(delivery_id):
        delete_delivery(delivery_id)
        load_table()

    # --- UI ---
    controls = ft.Column([
        ft.Row([ft.Text("מעקב משלוחים", size=28,
                        weight=ft.FontWeight.BOLD, color="#52b69a")]),
        ft.Row([
            ft.TextField(ref=search_field, label="חיפוש", width=250,
                         on_change=load_table),start_picker,end_picker,
            ft.ElevatedButton("➕ הוסף משלוח",
                              on_click=lambda e: open_edit(),
                              bgcolor="#52b69a", color="white"),
            ft.ElevatedButton(
                "PDF טווח",
                on_click=lambda e: export_range_summary_pdf(
                    page,
                    *map(int, start_picker.value.split("-")),
                    *map(int, end_picker.value.split("-"))
                ),
                bgcolor="#4d96ff",
                color="white"
            ),

            ft.ElevatedButton("🏠 חזרה",
                              on_click=lambda e: navigator.go_home(user),
                              bgcolor="#f28c7d", color="white"),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=12),
        ft.Container(
            content=ft.ListView([data_table], expand=True),
            expand=True,
            padding=10,
            bgcolor="white",
            border_radius=12,
            border=ft.border.all(1, ft.Colors.GREY_300)
        )
    ], expand=True, spacing=15,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    page.controls.clear()
    page.add(controls)
    load_table()
