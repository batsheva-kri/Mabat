import flet as ft
from logic.customers import search_customer_by_name, search_customer_by_phone, get_orders_for_customer
from logic.orders import get_latest_orders
import datetime

def ExistingCustomerScreen(page, user, navigator):
    page.title = "חיפוש לקוח קיים"

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
        ft.dropdown.Option("collected", "נאסף")
    ]

    orders_column = ft.Column()

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
            return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S")
        except Exception as e:
            print("Error parsing date:", e)
            return date_str, ""

    def build_order_card(cust, order):
        total = sum(item["line_total"] for item in order["items"])
        order_date, order_time = format_datetime(order["date"])
        right_eye = order["items"][0] if len(order["items"]) > 0 else None
        left_eye = order["items"][1] if len(order["items"]) > 1 else None

        right_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("👁️ עין ימין", weight=ft.FontWeight.BOLD, size=16, color="blue"),
                    ft.Text(f"מוצר: {right_eye['product_name']}" if right_eye else "אין"),
                    ft.Text(f"מידה: {right_eye['size']}" if right_eye else ""),
                    ft.Text(f"כמות: {right_eye['quantity']}" if right_eye else "")
                ]),
                padding=10,
                bgcolor="#e0f7fa",
                border_radius=10
            )
        )

        left_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("👁️ עין שמאל", weight=ft.FontWeight.BOLD, size=16, color="green"),
                    ft.Text(f"מוצר: {left_eye['product_name']}" if left_eye else "אין"),
                    ft.Text(f"מידה: {left_eye['size']}" if left_eye else ""),
                    ft.Text(f"כמות: {left_eye['quantity']}" if left_eye else "")
                ]),
                padding=10,
                bgcolor="#f1f8e9",
                border_radius=10
            )
        )

        status_map = {
            "invented": "הוזמן",
            "open": "פתוחה",
            "in_shop": "סופק",
            "collected": "נאסף"
        }

        buttons = [
            ft.ElevatedButton(
                "✏️ ערוך הזמנה" if order["status"] == "open" else "📄 העתק הזמנה",
                on_click=lambda e, inv=order: navigator.go_new_invitation(
                    user, cust["id"], existing_invitation=inv,edit=True
                )
            )
        ]
        if order["status"] != "open":
            buttons.append(
                ft.ElevatedButton(
                    "✏️ כניסה להזמנה",
                    on_click=lambda e, inv=order: navigator.go_new_invitation(
                        user=user, c_id=cust["id"], is_new_invitation=True,
                        existing_invitation=inv, edit=False
                    )
                )
            )

        order_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(f"הזמנה מלקוח: {cust['name']} – תאריך: {order_date}", weight=ft.FontWeight.BOLD,
                                size=18),
                        ft.Text(f"שעה: {order_time}", size=16, color="grey"),
                        ft.Text(f"סטטוס: {status_map.get(order['status'], order['status'])}", color="grey")
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Row([right_card, left_card], spacing=20),
                    ft.Text(f"סה\"כ להזמנה: {total:.2f} ₪", weight=ft.FontWeight.BOLD, size=16, color="red"),
                    ft.Row(buttons, alignment=ft.MainAxisAlignment.END)
                ]),
                padding=15
            )
        )

        return order_card

    def show_orders(cust, selected_status="all"):
        orders_column.controls.clear()
        orders = get_orders_for_customer(cust["id"])
        status_map = {
            "invented": "הוזמן",
            "open": "פתוחה",
            "in_shop": "סופק",
            "collected": "נאסף"
        }

        # סדר לפי תאריך הפוך
        orders = sorted(orders, key=lambda o: o["date"], reverse=True)

        if selected_status != "all":
            orders = [o for o in orders if o["status"] == selected_status]

        if not orders:
            orders_column.controls.append(ft.Text("אין הזמנות ללקוח זה"))
        else:
            for order in orders:
                total = sum(item["line_total"] for item in order["items"])
                order_date, order_time = format_datetime(order["date"])
                right_eye = order["items"][0] if len(order["items"]) > 0 else None
                left_eye = order["items"][1] if len(order["items"]) > 1 else None

                right_card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("👁️ עין ימין", weight=ft.FontWeight.BOLD, size=16, color="blue"),
                            ft.Text(f"מוצר: {right_eye['product_name']}" if right_eye else "אין"),
                            ft.Text(f"מידה: {right_eye['size']}" if right_eye else ""),
                            ft.Text(f"כמות: {right_eye['quantity']}" if right_eye else "")
                        ]),
                        padding=10,
                        bgcolor="#e0f7fa",
                        border_radius=10
                    )
                )

                left_card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("👁️ עין שמאל", weight=ft.FontWeight.BOLD, size=16, color="green"),
                            ft.Text(f"מוצר: {left_eye['product_name']}" if left_eye else "אין"),
                            ft.Text(f"מידה: {left_eye['size']}" if left_eye else ""),
                            ft.Text(f"כמות: {left_eye['quantity']}" if left_eye else "")
                        ]),
                        padding=10,
                        bgcolor="#f1f8e9",
                        border_radius=10
                    )
                )

                buttons = [
                    ft.ElevatedButton(
                        "✏️ ערוך הזמנה" if order["status"] == "open" else "📄 העתק הזמנה",
                        on_click=lambda e, inv=order: navigator.go_new_invitation(
                            user, cust["id"], existing_invitation=inv,edit= True
                        )
                    )
                ]

                if order["status"] != "open":
                    buttons.append(
                        ft.ElevatedButton(
                            "✏️ כניסה להזמנה",
                            on_click=lambda e, inv=order: navigator.go_new_invitation(
                                user=user, c_id=cust["id"], is_new_invitation=True,
                                existing_invitation=inv, edit=False
                            )
                        )
                    )

                order_card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Row([
                                ft.Text(f"הזמנה מלקוח: {cust['name']} – תאריך: {order_date}", weight=ft.FontWeight.BOLD, size=18),
                                ft.Text(f"שעה: {order_time}", size=16, color="grey"),
                                ft.Text(f"סטטוס: {status_map.get(order['status'], order['status'])}", color="grey")
                            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Row([right_card, left_card], spacing=20),
                            ft.Text(f"סה\"כ להזמנה: {total:.2f} ₪", weight=ft.FontWeight.BOLD, size=16, color="red"),
                            ft.Row(buttons, alignment=ft.MainAxisAlignment.END)
                        ]),
                        padding=15
                    )
                )

                orders_column.controls.append(order_card)
                orders_column.controls.append(ft.Divider(thickness=2))

        orders_column.controls.append(
            ft.ElevatedButton(
                "➕ הזמנה חדשה",
                on_click=lambda e: navigator.go_new_invitation(user, cust["id"], is_new_invitation=True)
            )
        )
        page.update()

    def filter_orders_by_status():
        selected_status = status_filter.current.value

        def create_order_card(cust, order):
            total = sum(item["line_total"] for item in order["items"])
            order_date, order_time = format_datetime(order["date"])
            right_eye = order["items"][0] if len(order["items"]) > 0 else None
            left_eye = order["items"][1] if len(order["items"]) > 1 else None

            right_card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("👁️ עין ימין", weight=ft.FontWeight.BOLD, size=16, color="blue"),
                        ft.Text(f"מוצר: {right_eye['product_name']}" if right_eye else "אין"),
                        ft.Text(f"מידה: {right_eye['size']}" if right_eye else ""),
                        ft.Text(f"כמות: {right_eye['quantity']}" if right_eye else "")
                    ]),
                    padding=10,
                    bgcolor="#e0f7fa",
                    border_radius=10
                )
            )

            left_card = ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Text("👁️ עין שמאל", weight=ft.FontWeight.BOLD, size=16, color="green"),
                        ft.Text(f"מוצר: {left_eye['product_name']}" if left_eye else "אין"),
                        ft.Text(f"מידה: {left_eye['size']}" if left_eye else ""),
                        ft.Text(f"כמות: {left_eye['quantity']}" if left_eye else "")
                    ]),
                    padding=10,
                    bgcolor="#f1f8e9",
                    border_radius=10
                )
            )

            status_map = {
                "invented": "הוזמן",
                "open": "פתוחה",
                "in_shop": "סופק",
                "collected": "נאסף"
            }

            buttons = [
                ft.ElevatedButton(
                    "✏️ ערוך הזמנה" if order["status"] == "open" else "📄 העתק הזמנה",
                    on_click=lambda e, inv=order: navigator.go_new_invitation(
                        user, cust["id"], existing_invitation=inv, edit=True
                    )
                )
            ]
            if order["status"] != "open":
                buttons.append(
                    ft.ElevatedButton(
                        "✏️ כניסה להזמנה",
                        on_click=lambda e, inv=order: navigator.go_new_invitation(
                            user=user, c_id=cust["id"], is_new_invitation=True,
                            existing_invitation=inv, edit=False
                        )
                    )
                )

            return ft.Card(
                content=ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(f"הזמנה מלקוח: {cust['name']} – תאריך: {order_date}", weight=ft.FontWeight.BOLD,
                                    size=18),
                            ft.Text(f"שעה: {order_time}", size=16, color="grey"),
                            ft.Text(f"סטטוס: {status_map.get(order['status'], order['status'])}", color="grey")
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([right_card, left_card], spacing=20),
                        ft.Text(f"סה\"כ להזמנה: {total:.2f} ₪", weight=ft.FontWeight.BOLD, size=16, color="red"),
                        ft.Row(buttons, alignment=ft.MainAxisAlignment.END)
                    ]),
                    padding=15
                )
            )

        if current_customer:
            show_orders(current_customer, selected_status=selected_status)
        else:
            # אין לקוח נבחר – מציגים את כל ההזמנות האחרונות עם הסינון
            orders_column.controls.clear()
            latest_orders = get_latest_orders()
            if not latest_orders:
                orders_column.controls.append(ft.Text("אין הזמנות אחרונות"))
            else:
                all_orders = []
                for order_data in latest_orders:
                    cust = order_data["customer"]
                    order = order_data["order"]
                    if selected_status == "all" or order["status"] == selected_status:
                        all_orders.append((cust, order))

                all_orders = sorted(all_orders, key=lambda x: x[1]["date"], reverse=True)

                for cust, order in all_orders:
                    order_card = create_order_card(cust, order)
                    orders_column.controls.append(order_card)
                    orders_column.controls.append(ft.Divider(thickness=2))

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
                # אוסף את כל ההזמנות של כל הלקוחות
                all_orders = []
                for order_data in latest_orders:
                    cust = order_data["customer"]
                    order = order_data["order"]
                    all_orders.append((cust, order))

                # ממיין לפי תאריך הפוך
                all_orders = sorted(all_orders, key=lambda x: x[1]["date"], reverse=True)

                # מציג את כל ההזמנות בפעם אחת
                for cust, order in all_orders:
                    # --- הוספת כרטיס ההזמנה ---
                    total = sum(item["line_total"] for item in order["items"])
                    order_date, order_time = format_datetime(order["date"])
                    right_eye = order["items"][0] if len(order["items"]) > 0 else None
                    left_eye = order["items"][1] if len(order["items"]) > 1 else None

                    right_card = ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("👁️ עין ימין", weight=ft.FontWeight.BOLD, size=16, color="blue"),
                                ft.Text(f"מוצר: {right_eye['product_name']}" if right_eye else "אין"),
                                ft.Text(f"מידה: {right_eye['size']}" if right_eye else ""),
                                ft.Text(f"כמות: {right_eye['quantity']}" if right_eye else "")
                            ]),
                            padding=10,
                            bgcolor="#e0f7fa",
                            border_radius=10
                        )
                    )

                    left_card = ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Text("👁️ עין שמאל", weight=ft.FontWeight.BOLD, size=16, color="green"),
                                ft.Text(f"מוצר: {left_eye['product_name']}" if left_eye else "אין"),
                                ft.Text(f"מידה: {left_eye['size']}" if left_eye else ""),
                                ft.Text(f"כמות: {left_eye['quantity']}" if left_eye else "")
                            ]),
                            padding=10,
                            bgcolor="#f1f8e9",
                            border_radius=10
                        )
                    )

                    status_map = {
                        "invented": "הוזמן",
                        "open": "פתוחה",
                        "in_shop": "סופק",
                        "collected": "נאסף"
                    }

                    buttons = [
                        ft.ElevatedButton(
                            "✏️ ערוך הזמנה" if order["status"] == "open" else "📄 העתק הזמנה",
                            on_click=lambda e, inv=order: navigator.go_new_invitation(
                                user, cust["id"],
                                existing_invitation=inv, edit=True
                            )
                        )
                    ]

                    if order["status"] != "open":
                        buttons.append(
                            ft.ElevatedButton(
                                "✏️ כניסה להזמנה",
                                on_click=lambda e, inv=order: navigator.go_new_invitation(
                                    user=user, c_id=cust["id"], is_new_invitation=True,
                                    existing_invitation=inv, edit=False
                                )
                            )
                        )

                    order_card = ft.Card(
                        content=ft.Container(
                            content=ft.Column([
                                ft.Row([
                                    ft.Text(f"הזמנה מלקוח: {cust['name']} – תאריך: {order_date}",
                                            weight=ft.FontWeight.BOLD, size=18),
                                    ft.Text(f"שעה: {order_time}", size=16, color="grey"),
                                    ft.Text(f"סטטוס: {status_map.get(order['status'], order['status'])}", color="grey")
                                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ft.Row([right_card, left_card], spacing=20),
                                ft.Text(f"סה\"כ להזמנה: {total:.2f} ₪", weight=ft.FontWeight.BOLD, size=16,
                                        color="red"),
                                ft.Row(buttons, alignment=ft.MainAxisAlignment.END)
                            ]),
                            padding=15
                        )
                    )

                    orders_column.controls.append(order_card)
                    orders_column.controls.append(ft.Divider(thickness=2))

            page.update()  # ← עדכון הדף רק פעם אחת בסוף
            return

        # --- מצב: חיפוש לפי שם או טלפון ---
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
                    cells=[ft.DataCell(ft.Text(cust["name"])),
                           ft.DataCell(ft.Text(cust["phone"]))],
                    on_select_changed=lambda e, c=cust: select_customer(c)
                )
            )
        customer_list.update()

    search_row = ft.Row(
        controls=[name_field, phone_field, message],
        alignment=ft.MainAxisAlignment.START,
        spacing=20
    )

    back_button = ft.ElevatedButton("חזור", on_click=lambda e: navigator.go_orders(user=user))

    page.controls.clear()
    page.add(
        ft.Column(
            controls=[
                ft.Text("חיפוש לקוח קיים", size=24, weight=ft.FontWeight.BOLD, color="#52b69a"),
                search_row,
                back_button,
                customer_list,
                ft.Divider(thickness=2),
                status_dropdown,
                orders_column
            ],
            spacing=20,
            expand=True
        )
    )

    perform_search()
    page.update()
