import flet as ft
from logic.db import run_query
from datetime import datetime

HOUR_RATE = 35  # ש"ח לשעה

def MonthlyWorkerReportScreen(page, user, go_employee_management):
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
            ft.DataColumn(ft.Text("תאריך", size=18, weight=ft.FontWeight.BOLD )),
            ft.DataColumn(ft.Text("כניסה", size=18, weight=ft.FontWeight.BOLD )),
            ft.DataColumn(ft.Text("יציאה", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("שעות עבודה", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("פעולות", size=18, weight=ft.FontWeight.BOLD))
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
                    ft.IconButton(icon=ft.Icons.DELETE, icon_color="#f28c7d", icon_size=28, tooltip="מחק")
                ],
                spacing=8,
                alignment=ft.MainAxisAlignment.END
            )

            report_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(r["date_"], text_align=ft.TextAlign.RIGHT)),
                        ft.DataCell(ft.Text(r["enter_time"] or "-", text_align=ft.TextAlign.RIGHT)),
                        ft.DataCell(ft.Text(r["exit_time"] or "-", text_align=ft.TextAlign.RIGHT)),
                        ft.DataCell(ft.Text(format_hours(hours), text_align=ft.TextAlign.RIGHT)),
                        ft.DataCell(actions_row)
                    ],
                    color="#ffffff" if i % 2 == 0 else "#fceef3"
                )
            )

        # --- שורה מסכמת חדשה ---
        total_hours_text = f"{format_hours(total_hours)}"
        total_payment_text = f"{total_hours*HOUR_RATE:.2f} ש\"ח"

        report_table.rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(f" סה\"כ שעות:{total_hours_text} ", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.RIGHT)),
                    ft.DataCell(ft.Text(" ")),
                    ft.DataCell(ft.Text("-")),
                    ft.DataCell(ft.Text(f"סה\"כ לתשלום: {total_payment_text}", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.RIGHT)),
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

    # --- כפתור חזור לניהול עובדים ---
    back_btn = ft.ElevatedButton(
        "⬅ חזור לניהול עובדים",
        on_click=lambda e: go_employee_management(user),
        bgcolor="#f28c7d",
        color="white",
        width=200
    )

    page.controls.clear()
    page.add(
        ft.Column(
            controls=[
                title,
                ft.Row([user_dropdown], alignment=ft.MainAxisAlignment.CENTER),
                month_row,
                ft.Container(
                    content=ft.ListView(
                        controls=[report_table],
                        expand=True
                    ),
                    padding=15,
                    bgcolor="#ffe5ec",
                    border_radius=12,
                    expand=True
                ),
                ft.Row([back_btn], alignment=ft.MainAxisAlignment.CENTER)
            ],
            expand=True,
            spacing=15,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,

        )
    )

    if users:
        user_dropdown.value = str(users[0]["id"])
        set_default_month()

    page.update()