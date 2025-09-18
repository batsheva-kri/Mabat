import flet as ft
from logic.db import run_query, run_action
from screens.monthly_worker_report import MonthlyWorkerReportScreen

def EmployeeManagementScreen(page, navigator, user):

    page.title = "ניהול עובדים"

    # --- טבלת עובדים בסגנון Catalog (DataTable) ---
    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("שם משתמש", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("סיסמה", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("תפקיד", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("פעולות", size=18, weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        heading_row_color="#52b69a",
        column_spacing=20,
        divider_thickness=1,
        data_row_min_height=60,
        border=ft.border.all(1, ft.Colors.GREY_300)
    )

    def load_employees():
        employees = run_query("SELECT id, user_name, password_, role FROM users")
        data_table.rows.clear()

        for i, emp in enumerate(employees):
            role_display = "מנהל" if emp["role"] == "manager" else "עובד"

            actions_row = ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.EDIT,
                        tooltip="ערוך עובד",
                        icon_size=28,
                        icon_color="#52b69a",
                        on_click=lambda e, emp_copy=emp: edit_employee(emp_copy)
                    ),
                    (ft.IconButton(
                        icon=ft.Icons.DELETE,
                        tooltip="מחק עובד",
                        icon_size=28,
                        icon_color="#52b69a",
                        on_click=lambda e, emp_id=emp["id"]: delete_employee(emp_id)
                    ) if emp["role"] != "manager" else ft.Container(width=50))
                ],
                spacing=8
            )

            data_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(emp["user_name"])),
                        ft.DataCell(ft.Text(emp["password_"])),
                        ft.DataCell(ft.Text(role_display)),
                        ft.DataCell(actions_row),
                    ],
                    color="#f28c7d" if i % 2 == 0 else "#ffffff"
                )
            )

        page.update()

    def delete_employee(emp_id):
        run_action("DELETE FROM users WHERE id=?", (emp_id,))
        load_employees()

    def show_dialog(title_text, content_controls, on_save, message=None):
        controls = [ft.Text(title_text, size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER)]
        if message:
            controls.append(message)
        controls.extend(content_controls)
        controls.append(
            ft.Row([
                ft.ElevatedButton("שמור", on_click=on_save, bgcolor="#52b69a", color="white"),
                ft.ElevatedButton("ביטול", on_click=lambda e: close_dialog(), bgcolor="#f28c7d", color="white")
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=12)
        )

        dlg = ft.Container(
            content=ft.Column(
                controls=controls,
                spacing=12,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=25,
            bgcolor="#ffffff",
            border_radius=14,
            alignment=ft.alignment.center
        )

        def close_dialog():
            page.overlay.clear()
            page.update()

        page.overlay.clear()
        page.overlay.append(dlg)
        page.update()

        return close_dialog

    def edit_employee(emp):
        name_field = ft.TextField(label="שם עובד", value=emp["user_name"])
        pass_field = ft.TextField(label="סיסמה", value=emp["password_"])
        role_field = ft.Dropdown(
            label="תפקיד",
            options=[ft.dropdown.Option("manager"), ft.dropdown.Option("worker")],
            value=emp["role"]
        )
        message = ft.Text("", color=ft.Colors.RED_700, weight=ft.FontWeight.BOLD)

        def save_edit(e):
            existing = run_query("SELECT id FROM users WHERE password_=? AND id!=?", (pass_field.value, emp["id"]))
            if existing:
                message.value = "סיסמה קיימת"
                page.update()
                return
            run_action(
                "UPDATE users SET user_name=?, password_=?, role=? WHERE id=?",
                (name_field.value, pass_field.value, role_field.value, emp["id"])
            )
            close_fn()
            load_employees()

        close_fn = show_dialog("עריכת עובד", [name_field, pass_field, role_field], save_edit, message)

    def add_employee(e):
        name_field = ft.TextField(label="שם עובד")
        pass_field = ft.TextField(label="סיסמה")
        role_field = ft.Dropdown(
            label="תפקיד",
            options=[ft.dropdown.Option("manager"), ft.dropdown.Option("worker")],
            value="worker"
        )
        message = ft.Text("", color=ft.Colors.RED_700, weight=ft.FontWeight.BOLD)

        def save_new(e):
            existing = run_query("SELECT id FROM users WHERE password_=?", (pass_field.value,))
            if existing:
                message.value = "סיסמה קיימת"
                page.update()
                return
            run_action(
                "INSERT INTO users (user_name, password_, role) VALUES (?, ?, ?)",
                (name_field.value, pass_field.value, role_field.value)
            )
            close_fn()
            load_employees()

        close_fn = show_dialog("הוספת עובד חדש", [name_field, pass_field, role_field], save_new, message)

    # --- ממשק ---
    title = ft.Text(
        "ניהול עובדים",
        size=34,
        weight=ft.FontWeight.BOLD,
        color="#52b69a",
        text_align=ft.TextAlign.CENTER
    )

    add_btn = ft.ElevatedButton("➕ הוספת עובד", bgcolor="#52b69a", color="white", on_click=add_employee)
    report_btn = ft.ElevatedButton(
        "📊 דו\"ח עובד חודשי", bgcolor="#f28c7d", color="white",
        on_click=lambda e: MonthlyWorkerReportScreen(page, navigator.go_home(user)
)
    )

    page.controls.clear()
    page.add(
        ft.Column(
            controls=[
                title,
                # כאן השארתי את המכולה החיצונית בצבע המקורי שלך, אבל הטבלה עצמה פנימית לבנה עם קצוות כמו בקטלוג
                ft.Container(
                    content=ft.Column([
                        ft.Container(
                            content=ft.ListView(controls=[data_table], on_scroll=ft.ScrollMode.AUTO, padding=0, expand=True),
                            expand=True,
                            padding=10,
                            bgcolor=ft.Colors.WHITE,
                            border_radius=10,
                            border=ft.border.all(1, ft.Colors.GREY_300),
                        )
                    ], expand=True),
                    expand=True,
                    padding=20,
                    bgcolor="#ffe5ec",   # שמרתי את הרקע החיצוני שלך
                    border_radius=16,
                    rtl=True
                ),
                ft.Row([add_btn, report_btn], alignment=ft.MainAxisAlignment.SPACE_EVENLY),
                ft.Container(height=20),
                ft.TextButton("⬅ חזרה לבית", on_click=lambda e:  navigator.go_home(user)
)
            ],
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )
    )

    load_employees()
    page.update()
