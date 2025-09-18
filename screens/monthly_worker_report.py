import flet as ft
from logic.db import run_query
from datetime import datetime

HOUR_RATE = 35  # ש"ח לשעה

def MonthlyWorkerReportScreen(page, go_home):
    page.title = "דו\"ח עובד חודשי"

    # --- פונקציות עזר ---
    def get_last_month_with_data(user_id):
        result = run_query("""
            SELECT MAX(strftime('%Y-%m', date_)) as last_month
            FROM worker_reports
            WHERE user_id=?
        """, (user_id,))
        if result and result[0]["last_month"]:
            return result[0]["last_month"]
        else:
            return datetime.now().strftime("%Y-%m")

    def change_month(delta):
        if not month_dropdown.value:
            return
        current = datetime.strptime(month_dropdown.value + "-01", "%Y-%m-%d")
        month = current.month + delta
        year = current.year
        if month > 12:
            month = 1
            year += 1
        elif month < 1:
            month = 12
            year -= 1
        month_dropdown.value = f"{year}-{month:02d}"
        month_dropdown.update()
        load_report(user_dropdown.value, month_dropdown.value)

    def parse_time(t):
        if not t:
            return None
        parts = t.split(":")
        try:
            h = int(parts[0])
            m = int(parts[1]) if len(parts) > 1 else 0
            return h, m
        except:
            return None

    def format_hours(hours_float):
        h = int(hours_float)
        m = int(round((hours_float - h) * 60))
        return f"{h}:{m:02d}"

    # --- DataTable להדוח ---
    report_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("תאריך", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("כניסה", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("יציאה", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("שעות עבודה", weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("פעולות", weight=ft.FontWeight.BOLD))
        ],
        rows=[],
        heading_row_color="#52b69a",
        column_spacing=20,
        divider_thickness=1,
        data_row_min_height=60,
        border=ft.border.all(1, ft.Colors.GREY_300)
    )

    def load_report(user_id, month_value):
        if not user_id or not month_value:
            return

        rows_data = run_query("""
            SELECT date_, enter_time, exit_time
            FROM worker_reports
            WHERE user_id=? AND strftime('%Y-%m', date_) = ?
            ORDER BY date_
        """, (user_id, month_value))

        report_table.rows.clear()
        total_hours = 0.0

        for i, r in enumerate(rows_data):
            enter = parse_time(r["enter_time"])
            exit_ = parse_time(r["exit_time"])
            hours = 0.0
            if enter and exit_:
                eh, em = enter
                xh, xm = exit_
                hours = (xh + xm / 60) - (eh + em / 60)
                if hours < 0:
                    hours = 0
            total_hours += hours

            actions_row = ft.Row(
                controls=[
                    ft.IconButton(icon=ft.Icons.EDIT, icon_color="#52b69a", icon_size=28, tooltip="ערוך"),
                    ft.IconButton(icon=ft.Icons.DELETE, icon_color="#52b69a", icon_size=28, tooltip="מחק")
                ],
                spacing=8
            )

            report_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(r["date_"])),
                        ft.DataCell(ft.Text(r["enter_time"] or "-")),
                        ft.DataCell(ft.Text(r["exit_time"] or "-")),
                        ft.DataCell(ft.Text(format_hours(hours))),
                        ft.DataCell(actions_row)
                    ],
                    color="#ffffff" if i % 2 == 0 else "#fceef3"
                )
            )

        # שורה מסכמת
        report_table.rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text("סה\"כ", weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text("-")),
                    ft.DataCell(ft.Text("-")),
                    ft.DataCell(ft.Text(f"{format_hours(total_hours)} שעות / {total_hours*HOUR_RATE:.2f} ש\"ח", weight=ft.FontWeight.BOLD)),
                    ft.DataCell(ft.Text(""))
                ],
                color="#ddd"
            )
        )

        page.update()

    # --- ממשק ---
    title = ft.Text(
        "דו\"ח עובד חודשי",
        size=28,
        weight=ft.FontWeight.BOLD,
        color="#52b69a",
        text_align=ft.TextAlign.CENTER
    )

    users = run_query("SELECT id, user_name FROM users")
    user_dropdown = ft.Dropdown(
        label="בחר עובד",
        options=[ft.dropdown.Option(str(u["id"]), u["user_name"]) for u in users],
        on_change=lambda e: set_default_month()
    )

    month_dropdown = ft.TextField(label="חודש (YYYY-MM)")

    def set_default_month():
        if user_dropdown.value:
            month_dropdown.value = get_last_month_with_data(user_dropdown.value)
            month_dropdown.update()
            load_report(user_dropdown.value, month_dropdown.value)

    prev_month_btn = ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=lambda e: change_month(-1))
    next_month_btn = ft.IconButton(icon=ft.Icons.ARROW_FORWARD, on_click=lambda e: change_month(1))
    month_row = ft.Row([prev_month_btn, month_dropdown, next_month_btn], alignment=ft.MainAxisAlignment.CENTER, spacing=5)

    page.controls.clear()
    page.add(
        ft.Column(
            controls=[
                title,
                ft.Row([user_dropdown], alignment=ft.MainAxisAlignment.CENTER),
                month_row,
                ft.Container(
                    content=report_table,
                    padding=15,
                    bgcolor="#ffe5ec",
                    border_radius=12,
                    expand=True
                ),
                ft.Container(height=20),

            ],
            expand=True,
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

    if users:
        user_dropdown.value = str(users[0]["id"])
        set_default_month()

    page.update()