import flet as ft
from logic.customers import search_customer_by_name, search_customer_by_phone, get_orders_for_customer
from logic.orders import get_latest_orders
from screens.new_invitation_page import NewInvitationPage
import datetime

def ExistingCustomerScreen(page, user, navigator):
    page.title = "חיפוש לקוח קיים"

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

    orders_column = ft.Column()

    def format_datetime(date_str):
        try:
            dt = datetime.datetime.fromisoformat(date_str)
            return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S")
        except Exception as e:
            print("Error parsing date:", e)
            return date_str, ""

    def show_orders_for_order(cust, order):
        status_map = {
            "invented": "הוזמן",
            "open": "פתוחה",
            "in_shop": "סופק",
            "callected": "נאסף"
        }

        # חישוב סה"כ להזמנה
        total = sum(item["line_total"] for item in order["items"])

        # עין ימין
        right_eye = order["items"][0] if len(order["items"]) > 0 else None
        # עין שמאל
        left_eye = order["items"][1] if len(order["items"]) > 1 else None

        right_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Text("👁️ עין ימין", weight=ft.FontWeight.BOLD, size=16, color="blue"),
                    ft.Text(f"מוצר: {right_eye['product_name']}" if right_eye else "אין"),
                    ft.Text(f"מידה: {right_eye['size']}" if right_eye else ""),
                    ft.Text(f"כמות: {right_eye['qty']}" if right_eye else "")
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
                    ft.Text(f"כמות: {left_eye['qty']}" if left_eye else "")
                ]),
                padding=10,
                bgcolor="#f1f8e9",
                border_radius=10
            )
        )
        order_date, order_time = format_datetime(order["date"])

        # רשימת כפתורים
        buttons = []
        # כפתור עריכה/העתק
        buttons.append(
            ft.ElevatedButton(
                "✏️ ערוך הזמנה" if order["status"] == "open" else "📄 העתק הזמנה",
                on_click=lambda e, inv=order: NewInvitationPage(navigator,
                                                                page, user, cust["id"],
                                                                existing_invitation=inv
                                                                )
            )
        )
        # כפתור כניסה להזמנה רק אם ההזמנה לא פתוחה
        if order["status"] != "open":
            buttons.append(
                ft.ElevatedButton(
                    "✏️ כניסה להזמנה",
                    on_click=lambda e, inv=order: NewInvitationPage(navigator,
                                                                    page, user, cust["id"],
                                                                    existing_invitation=inv
                                                                    )
                )
            )

        # כרטיס ראשי של ההזמנה
        order_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
                    ft.Row([
                        ft.Text(f"הזמנה מלקוח: {cust['name']} – תאריך: {order_date}", weight=ft.FontWeight.BOLD, size=18),
                            ft.Text(f"שעה: {order_time}", size=16, color="grey"),
                        ft.Text(f"סטטוס: {status_map.get(order['status'], order['status'])}", color="grey")
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                    ft.Row([right_card, left_card], spacing=20),

                    ft.Text(f"סה\"כ להזמנה: {total:.2f} ₪",
                            weight=ft.FontWeight.BOLD, size=16, color="red"),

                    ft.Row(buttons, alignment=ft.MainAxisAlignment.END)
                ]),
                padding=15
            )
        )

        orders_column.controls.append(order_card)
        orders_column.controls.append(ft.Divider(thickness=2))

    def perform_search():
        customer_list.rows.clear()
        orders_column.controls.clear()

        name = name_field.value.strip()
        phone = phone_field.value.strip()

        if not name and not phone:
            # השדות ריקים – מציגים הזמנות אחרונות של כל הלקוחות
            latest_orders = get_latest_orders()  # מחזירה רשימה של הזמנות, כל אחת עם cust ו-items
            if not latest_orders:
                orders_column.controls.append(ft.Text("אין הזמנות אחרונות"))
            else:
                # מציגים את ההזמנות החדשות ביותר למעלה
                for order_data in sorted(latest_orders, key=lambda x: x["order"]["date"], reverse=True):
                    show_orders_for_order(order_data["customer"], order_data["order"])
            page.update()
            return

        # חיפוש רגיל לפי שם/טלפון
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
                    cells=[
                        ft.DataCell(ft.Text(cust["name"])),
                        ft.DataCell(ft.Text(cust["phone"]))
                    ],
                    on_select_changed=lambda e, c=cust: show_orders(c)
                )
            )
        customer_list.update()

    def show_orders(cust):
        orders_column.controls.clear()
        orders = get_orders_for_customer(cust["id"])
        status_map = {
            "invented": "הוזמן",
            "open": "פתוחה",
            "in_shop": "סופק",
            "callected": "נאסף"
        }

        if not orders:
            orders_column.controls.append(ft.Text("אין הזמנות ללקוח זה"))
        else:
            for order in orders:
                # חישוב סה"כ להזמנה
                total = sum(item["line_total"] for item in order["items"])
                order_date, order_time = format_datetime(order["date"])
                # עין ימין
                right_eye = order["items"][0] if len(order["items"]) > 0 else None
                # עין שמאל
                left_eye = order["items"][1] if len(order["items"]) > 1 else None

                right_card = ft.Card(
                    content=ft.Container(
                        content=ft.Column([
                            ft.Text("👁️ עין ימין", weight=ft.FontWeight.BOLD, size=16, color="blue"),
                            ft.Text(f"מוצר: {right_eye['product_name']}" if right_eye else "אין"),
                            ft.Text(f"מידה: {right_eye['size']}" if right_eye else ""),
                            ft.Text(f"כמות: {right_eye['qty']}" if right_eye else "")
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
                            ft.Text(f"כמות: {left_eye['qty']}" if left_eye else "")
                        ]),
                        padding=10,
                        bgcolor="#f1f8e9",
                        border_radius=10
                    )
                )
                # כרטיס ראשי של ההזמנה
                buttons = []
                # כפתור עריכה או העתק
                buttons.append(
                    ft.ElevatedButton(
                        "✏️ ערוך הזמנה" if order["status"] == "open" else "📄 העתק הזמנה",
                        on_click=lambda e, inv=order: NewInvitationPage(navigator,
                                                                        page, user, cust["id"],
                                                                        existing_invitation=inv
                                                                        )
                    )
                )

                # כפתור כניסה להזמנה רק אם ההזמנה סגורה
                if order["status"] != "open":
                    buttons.append(
                        ft.ElevatedButton(
                            "✏️ כניסה להזמנה",
                            on_click=lambda e, inv=order: NewInvitationPage(navigator,
                                                                            page, user, cust["id"],
                                                                            existing_invitation=inv
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

                            ft.Text(f"סה\"כ להזמנה: {total:.2f} ₪",
                                    weight=ft.FontWeight.BOLD, size=16, color="red"),

                            # Row של כפתורים
                            ft.Row(buttons, alignment=ft.MainAxisAlignment.END)
                        ]),
                        padding=15
                    )
                )

                orders_column.controls.append(order_card)
                orders_column.controls.append(ft.Divider(thickness=2))

        # כפתור להזמנה חדשה
        orders_column.controls.append(
            ft.ElevatedButton(
                "➕ הזמנה חדשה",
                on_click=lambda e: NewInvitationPage(navigator,
                    page, user, cust["id"]

                )
            )
        )
        page.update()

    def copy_order(order):
        page.dialog = ft.AlertDialog(
            title=ft.Text("העתקה"),
            content=ft.Text(f"מעביר להזמנה: {order}"),
            actions=[ft.TextButton("סגור", on_click=lambda e: page.dialog.close())]
        )
        page.dialog.open = True
        page.update()

    perform_search()
    search_row = ft.Row(
        controls=[name_field, phone_field, message],
        alignment=ft.MainAxisAlignment.START,
        spacing=20
    )

    # כפתור חזרה
    back_button = ft.ElevatedButton("חזור", on_click=lambda e: navigator.go_orders(user=user))

    page.controls.clear()
    page.add(
        ft.Column(
            controls=[
                ft.Text("חיפוש לקוח קיים", size=24, weight=ft.FontWeight.BOLD, color="#52b69a"),
                search_row,
                customer_list,
                ft.Divider(thickness=2),
                orders_column,
                back_button  # מוסיפים את כפתור החזרה
            ],
            spacing=20,
            expand=True
        )
    )
    page.update()
