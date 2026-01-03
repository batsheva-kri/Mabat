import flet as ft
from logic.customers import search_customer_by_name, search_customer_by_phone, get_orders_for_customer
from logic.orders import get_latest_orders
import datetime


def ExistingCustomerScreen(page, user, navigator):
    page.title = "חיפוש לקוח קיים"
    current_customer = None
    current_customer = None  # לקוח נבחר

    name_field = ft.TextField(
        label="שם",
        text_align=ft.TextAlign.RIGHT,
        width=250,
        border_color="#52b69a",
        on_change=lambda e: perform_search()
    )

    phone_field = ft.TextField(
        label="טלפון",
        text_align=ft.TextAlign.RIGHT,
        width=250,
        border_color="#52b69a",
        on_change=lambda e: perform_search()
    )

    message = ft.Text("", color=ft.Colors.RED_700)

    customer_list = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("שם לקוח")),
            ft.DataColumn(ft.Text("טלפון"))
        ],
        rows=[]
    )

    status_filter = ft.Ref[ft.Dropdown]()
    status_options = [
        ft.dropdown.Option("all", "הכל"),
        ft.dropdown.Option("open", "פתוחה"),
        ft.dropdown.Option("invented", "הוזמנה"),
        ft.dropdown.Option("in_shop", "סופק"),
        ft.dropdown.Option("collected", "נאסף"),
        ft.dropdown.Option("canceled", "בוטל"),
        ft.dropdown.Option("old", "הזמנה ישנה"),

    ]
    orders_column = ft.Column(spacing=4)


    status_dropdown = ft.Dropdown(
        ref=status_filter,
        options=status_options,
        value="all",
        width=180,
        label="סינון לפי סטטוס",
        on_change=lambda e: filter_orders_by_status()
    )

    def format_datetime(date_str):
        try:
            dt = datetime.datetime.fromisoformat(date_str)
            return dt.strftime("%Y-%m-%d")
        except Exception:
            return date_str

    # --- כרטיס עין מעוצב בשורה אחת ---
    def mini_eye_card(title, color, eye):
        if not eye:
            return ft.Container(
                content=ft.Text(f"{title}: אין", size=11, color="white"),
                padding=3,
                border_radius=6,
                bgcolor="#f28c7d",
                width=150,
                height=28,
                alignment=ft.alignment.center_right
            )
        p_arr = eye['size'].split()
        if p_arr == []:
            text_line = (
                f"{title}    : {eye['product_name']} | כמות: {eye['quantity']}"
            )
        elif len(p_arr) < 3:
            text_line = (
                f"{title}    : {eye['product_name']} | מידה: {p_arr[0]} | כמות: {eye['quantity']}"
            )
        else:
            text_line = (
                f"{title}    : {eye['product_name']} | מידה: {p_arr[2]} {p_arr[1]} {p_arr[0]} | כמות: {eye['quantity']}"
            )

        return ft.Container(
            content=ft.Text(text_line, size=11, color="white"),
            padding=3,
            border_radius=6,
            bgcolor="#f28c7d",
            width=400,
            height=28,
            alignment=ft.alignment.center_right
        )

    # --- כרטיס הזמנה מלא ---
    def build_order_card(cust, order):
        order["customer_id"] = cust["id"]
        total = sum(item["line_total"] for item in order["items"])
        order_date = format_datetime(order["date"])
        right_eye = order["items"][0] if len(order["items"]) > 0 else None
        left_eye = order["items"][1] if len(order["items"]) > 1 else None

        right_card = mini_eye_card("ימין 👁️", "#0077b6", right_eye)
        left_card = mini_eye_card("שמאל 👁️", "#2a9d8f", left_eye)

        status_map = {
            "invented": "הוזמן",
            "open": "פתוחה",
            "in_shop": "סופק",
            "collected": "נאסף",
            "canceled": "בוטל",
            "old":"הזמנה ישנה"
        }

        # --- כפתורים קומפקטיים ---
        edit_btn =None
        if order["status"] == "open":
            edit_btn = ft.TextButton(
            "✏️ ערוך" ,
            on_click=lambda e, inv=order: navigator.go_new_invitation(
                user, cust["id"], existing_invitation=inv, edit=True
            ),
            style=ft.ButtonStyle(padding=0, visual_density=ft.VisualDensity.COMPACT)
        )
        view_btn = None
        copy_btn = None
        if order["status"] != "open":
            view_btn = ft.TextButton(
                "👁️ כניסה",
                on_click=lambda e, inv=order: navigator.go_new_invitation(
                    user=user, c_id=cust["id"], is_new_invitation=True,
                    existing_invitation=inv, edit=False
                ),
                style=ft.ButtonStyle(padding=0, visual_density=ft.VisualDensity.COMPACT)
            )
            copy_btn = ft.TextButton(
                "📄 העתק",
                on_click=lambda e, inv=order: navigator.go_new_invitation(
                    user, cust["id"], existing_invitation=inv, edit=True, copy=True
                ),
                style=ft.ButtonStyle(padding=0, visual_density=ft.VisualDensity.COMPACT)
            )
        buttons_row = ft.Row(
            controls=([edit_btn] if edit_btn else []) + ([view_btn] if view_btn else [])+ ([copy_btn] if copy_btn else []),
            alignment=ft.MainAxisAlignment.END,
            spacing=4
        )

        # --- כל השדות בשורה אחת ---
        main_row = ft.Row(
            controls=[
                ft.Text(f"{cust['name']} – {order_date}", weight=ft.FontWeight.BOLD, size=12),
                right_card,
                left_card,
                ft.Text(status_map.get(order['status'], order['status']), size=11, color="grey"),
                ft.Text(f"סה\"כ: {total:.2f} ₪", size=11, weight=ft.FontWeight.BOLD, color="red"),
                buttons_row
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            wrap=True,
            spacing=10
        )

        return ft.Card(
            content=ft.Container(content=main_row, padding=6),
            elevation=1,
            margin=4
        )

    # --- הצגת ההזמנות של לקוח נבחר ---
    def show_orders(cust, selected_status="all"):
        orders_column.controls.clear()
        orders = get_orders_for_customer(cust["id"])
        orders = sorted(orders, key=lambda o: o["date"], reverse=True)
        if selected_status != "all":
            orders = [o for o in orders if o["status"] == selected_status]
        orders_column.controls.append(
            ft.TextButton(
                "➕ הזמנה חדשה",
                on_click=lambda e: navigator.go_new_invitation(user, cust["id"], is_new_invitation=True),
                style=ft.ButtonStyle(padding=0, visual_density=ft.VisualDensity.COMPACT)
            )
        )
        if not orders:
            orders_column.controls.append(ft.Text("אין הזמנות ללקוח זה"))
        else:
            for order in orders:
                orders_column.controls.append(build_order_card(cust, order))
        page.update()

    def filter_orders_by_status():
        selected_status = status_filter.current.value

        if current_customer:
            show_orders(current_customer, selected_status=selected_status)
        else:
            orders_column.controls.clear()
            latest_orders = get_latest_orders()
            if not latest_orders:
                orders_column.controls.append(ft.Text("אין הזמנות אחרונות"))
            else:
                for order_data in sorted(latest_orders, key=lambda x: x["order"]["date"], reverse=True):
                    cust, order = order_data["customer"], order_data["order"]
                    if selected_status == "all" or order["status"] == selected_status:
                        orders_column.controls.append(build_order_card(cust, order))
            page.update()

    def select_customer(cust):
        nonlocal current_customer
        current_customer = cust
        show_orders(cust, selected_status=status_filter.current.value)

    def perform_search():
        customer_list.rows.clear()
        orders_column.controls.clear()
        name = name_field.value.strip()
        phone = phone_field.value.strip()

        # --- מצב: אין שם ואין טלפון, מציגים את כל ההזמנות האחרונות ---
        if not name and not phone:
            latest_orders = get_latest_orders()
            if not latest_orders:
                orders_column.controls.append(ft.Text("אין הזמנות אחרונות"))
            else:
                for order_data in sorted(latest_orders, key=lambda x: x["order"]["date"], reverse=True):
                    cust, order = order_data["customer"], order_data["order"]
                    orders_column.controls.append(build_order_card(cust, order))
            page.update()
            return


        customers = []
        if name:
            customers = search_customer_by_name(name)
        elif phone:
            customers = search_customer_by_phone(phone)

        if not customers:
            message.value = "לא נמצאו לקוחות"
            message.update()
            return
        else:
            message.value = ""
            message.update()

        for cust in customers:
            customer_list.rows.append(
                ft.DataRow(
                    cells=[ft.DataCell(ft.Text(cust["name"])), ft.DataCell(ft.Text(cust["phone"]))],
                    on_select_changed=lambda e, c=cust: select_customer(c)
                )
            )
        customer_list.update()

    search_row = ft.Row(
        controls=[name_field, phone_field, message],
        alignment=ft.MainAxisAlignment.START,
        spacing=10
    )

    back_button = ft.ElevatedButton("⬅️ חזור להזמנות", on_click=lambda e: navigator.go_orders(user=user),width=140,bgcolor="#52b69a", color= ft.Colors.WHITE)


    page.controls.clear()
    page.add(
        ft.Column(
            controls=[
                ft.Text("חיפוש לקוח קיים", size=20, weight=ft.FontWeight.BOLD, color="#52b69a"),
                search_row,
                back_button,ft.ElevatedButton("סיום וחזרה לבית🏠", on_click=lambda e: navigator.go_orders(user),width=140,
                                  bgcolor="#f28c7d", color=ft.Colors.WHITE),
                customer_list,
                ft.Divider(thickness=1),
                status_dropdown,
                orders_column
            ],
            spacing=10,
            expand=True
        )
    )

    perform_search()
    page.update()
