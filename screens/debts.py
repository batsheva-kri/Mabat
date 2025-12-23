import flet as ft
from logic.db import run_query, run_action  # הפונקציות שלך ל-SQLITE

def DebtsScreen(page, navigator, user):
    page.title = "חובות"

    # --- References ---
    name_ref = ft.Ref[ft.TextField]()
    phone_ref = ft.Ref[ft.TextField]()
    amount_ref = ft.Ref[ft.TextField]()
    notes_ref = ft.Ref[ft.TextField]()

    # --- DataTable חובות ---
    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("שם", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("טלפון", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("סכום", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("פירוט / הערות", size=18, weight=ft.FontWeight.BOLD)),
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

    # --- שליפת חובות ---
    def load_debts():
        rows = run_query("SELECT * FROM debts")
        data_table.rows.clear()
        for i, r in enumerate(rows):
            actions = ft.Row([
                ft.IconButton(icon=ft.Icons.EDIT, tooltip="ערוך", on_click=lambda e, rid=r["id"]: open_debt_dialog(rid)),
                ft.IconButton(icon=ft.Icons.DELETE, tooltip="מחק", on_click=lambda e, rid=r["id"]: delete_debt(rid)),
            ])
            data_table.rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(r["name"])),
                    ft.DataCell(ft.Text(r["phone"] or "-")),
                    ft.DataCell(ft.Text(str(r["amount"]))),
                    ft.DataCell(ft.Text(r["notes"] or "-")),
                    ft.DataCell(actions),
                ],
                color="#f28c7d" if i % 2 == 0 else "#ffffff"
            ))
        page.update()

    # --- מחיקת חוב ---
    def delete_debt(debt_id):
        run_action("DELETE FROM debts WHERE id=?", (debt_id,))
        load_debts()

    # --- דיאלוג הוספה/עריכה ---
    def open_debt_dialog(debt_id=None):
        if debt_id:
            debt = run_query("SELECT * FROM debts WHERE id=?", (debt_id,))[0]
            name_val = debt["name"]
            phone_val = debt["phone"]
            amount_val = str(debt["amount"])
            notes_val = debt["notes"]
        else:
            name_val = phone_val = amount_val = notes_val = ""

        name_field = ft.TextField(ref=name_ref, label="שם", value=name_val)
        phone_field = ft.TextField(ref=phone_ref, label="טלפון", value=phone_val, width=200)
        amount_field = ft.TextField(ref=amount_ref, label="סכום", value=amount_val)
        notes_field = ft.TextField(ref=notes_ref, label="פירוט / הערות", value=notes_val, multiline=True, width=300)

        def close_dialog():
            page.overlay.clear()
            page.update()

        def save_debt(e):
            name = name_field.value
            phone = phone_field.value
            amount = float(amount_field.value or 0)
            notes = notes_field.value

            if debt_id:
                run_action("UPDATE debts SET name=?, phone=?, amount=?, notes=? WHERE id=?", (name, phone, amount, notes, debt_id))
            else:
                run_action("INSERT INTO debts (name, phone, amount, notes) VALUES (?, ?, ?, ?)", (name, phone, amount, notes))
            close_dialog()
            load_debts()

        dlg_content = ft.Column(
            [name_field, phone_field, amount_field, notes_field],
            spacing=10,
            scroll=ft.ScrollMode.AUTO
        )

        page.overlay.clear()
        page.overlay.append(
            ft.Container(
                content=ft.Column([
                    ft.Text("עריכת חוב" if debt_id else "הוספת חוב", size=24, weight=ft.FontWeight.BOLD),
                    dlg_content,
                    ft.Row([
                        ft.ElevatedButton("שמור", on_click=save_debt, bgcolor="#52b69a", color="white"),
                        ft.ElevatedButton("ביטול", on_click=lambda e: close_dialog(), bgcolor="#f28c7d", color="white"),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=12)
                ], spacing=15),
                padding=20, bgcolor="#ffffff", border_radius=14
            )
        )
        page.update()

    # --- כפתורי פעולה ראשיים ---
    controls = ft.Column([
        ft.Row([
            ft.ElevatedButton("חזרה לבית🏠", on_click=lambda e: navigator.go_home(user), width=120, bgcolor="#f28c7d", color="white"),
            ft.ElevatedButton("➕ הוסף חוב", on_click=lambda e: open_debt_dialog(), bgcolor="#52b69a", color="white")
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=10),
        ft.Container(
            content=ft.ListView([data_table], padding=0, expand=True),
            expand=True, padding=10, bgcolor=ft.Colors.WHITE, border_radius=10,
            border=ft.border.all(1, ft.Colors.GREY_300)
        )
    ], spacing=15, expand=True, scroll=ft.ScrollMode.AUTO, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    page.controls.clear()
    page.add(controls)
    load_debts()
    page.update()
