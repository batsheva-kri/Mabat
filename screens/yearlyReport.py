import flet as ft
from logic.suppliers import get_all_suppliers
from logic.suppliersReport import get_products_report, get_product_sizes_report

def YearlyReportScreen(page, user, navigator):
    page.title = "דוח שנתי לספקים"

    # --- שליפת ספקים ---
    suppliers = get_all_suppliers()

    supplier_dropdown = ft.Dropdown(
        label="בחר ספק",
        options=[
            ft.dropdown.Option(key=str(s["id"]), text=s["name"]) for s in suppliers
        ] + [ft.dropdown.Option(key="0", text="כל הספקים")],
        value="0",  # ברירת מחדל: כל הספקים
        width=250
    )
    # ימים 1–31
    days = [ft.dropdown.Option(str(d)) for d in range(1, 32)]

    # חודשים 1–12
    months = [ft.dropdown.Option(f"{m:02d}") for m in range(1, 13)]

    # שנים (למשל 2023–2030)
    years = [ft.dropdown.Option(str(y)) for y in range(2023, 2031)]
    start_day = ft.Dropdown(label="יום התחלה", options=days, value="1", width=80)
    start_month = ft.Dropdown(label="חודש התחלה", options=months, value="01", width=80)
    start_year = ft.Dropdown(label="שנה התחלה", options=years, value="2025", width=100)

    end_day = ft.Dropdown(label="יום סיום", options=days, value="31", width=80)
    end_month = ft.Dropdown(label="חודש סיום", options=months, value="12", width=80)
    end_year = ft.Dropdown(label="שנה סיום", options=years, value="2025", width=100)

    # --- תאריכים ---
    start_date = ft.TextField(label="תאריך התחלה (YYYY-MM-DD)", width=200)
    end_date = ft.TextField(label="תאריך סיום (YYYY-MM-DD)", width=200)

    # --- טבלת מוצרים ---
    main_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("מוצר", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("כמות בתקופה", size=18, weight=ft.FontWeight.BOLD)),
        ],
        rows=[],
        heading_row_color="#52b69a",
        border=ft.border.all(1, ft.Colors.GREY_300),
        column_spacing=20,
        divider_thickness=1,
        data_row_min_height=60
    )

    # --- טבלת מידות ---
    sizes_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("מידה", size=18, weight=ft.FontWeight.BOLD)),
            ft.DataColumn(ft.Text("כמות", size=18, weight=ft.FontWeight.BOLD)),
        ],
        rows=[]
    )

    sizes_container = ft.Container(visible=False, content=sizes_table, padding=10)

    # --- פונקציה לטעינת דוח ---
    def load_report(e):
        supplier_id = int(supplier_dropdown.value)

        # בונים מחרוזות תאריך
        s = f"{start_year.value}-{start_month.value}-{start_day.value}"
        e_date = f"{end_year.value}-{end_month.value}-{end_day.value}"

        data = get_products_report(supplier_id, s, e_date)

        main_table.rows.clear()
        sizes_container.visible = False

        for i, item in enumerate(data):
            main_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(item["product_name"])),
                        ft.DataCell(ft.Text(str(item["total_quantity"]))),
                    ],
                    color="#f28c7d" if i % 2 == 0 else "#ffffff",
                    on_select_changed=lambda e, it=item: load_sizes(it)
                )
            )

        page.update()

    # --- טוען טבלת מידות עבור מוצר שנבחר ---
    def load_sizes(item):
        supplier_id = int(supplier_dropdown.value)
        s = f"{start_year.value}-{start_month.value}-{start_day.value}"
        e_date = f"{end_year.value}-{end_month.value}-{end_day.value}"

        sizes = get_product_sizes_report(item["product_id"], supplier_id, s, e_date)

        sizes_table.rows.clear()
        for size_item in sizes:
            sizes_table.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(size_item["size"])),
                        ft.DataCell(ft.Text(str(size_item["quantity"])))
                    ]
                )
            )

        sizes_container.visible = True
        page.update()

    # --- מסך מלא ---
    layout = ft.Column(
        controls=[
            ft.Text(
                f"דוח שנתי לספקים - שלום {user['user_name']}",
                size=24,
                weight=ft.FontWeight.BOLD,
                color="#9bf6ff",
                text_align=ft.TextAlign.CENTER
            ),
            ft.Row([
                supplier_dropdown,
                start_day, start_month, start_year,
                end_day, end_month, end_year,
                ft.ElevatedButton("צור דוח", on_click=load_report, bgcolor="#52b69a", color="white")
            ], spacing=10),

            ft.Container(height=20),
            ft.Container(
                content=ft.ListView(controls=[main_table], expand=True, padding=0),
                expand=True,
                padding=10,
                bgcolor=ft.Colors.WHITE,
                border_radius=10,
                border=ft.border.all(1, ft.Colors.GREY_300),
            ),
            sizes_container,
            ft.Container(height=20),
            ft.ElevatedButton(
                "⬅ חזור", on_click=lambda e: navigator.go_home(user), bgcolor="#52b69a", color="white"
            )
        ],
        expand=True,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=20
    )

    page.controls.clear()
    page.add(layout)
    page.update()
