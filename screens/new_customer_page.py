import flet as ft
from logic.customers import add_customer, customer_exists_by_name, customer_exists_by_phone, PhoneAlreadyExists, \
    get_customer_by_phone


def NewCustomerPage(page, current_user, navigator):
    name_var = ft.TextField(label="שם", width=200)
    phone_var = ft.TextField(label="טלפון", width=200)
    phone2_var = ft.TextField(label="טלפון 2", width=200)
    address_var = ft.TextField(label="כתובת", width=200)
    email_var = ft.TextField(label="אימייל", width=200)
    notes_var = ft.TextField(label="הערות", multiline=True, width=400, height=80)

    allow_duplicate_name = False  # יפעיל מצב "לחיצה שנייה" במקרה של שם קיים

    def show_dialog(title, message):
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("אישור", on_click=lambda e: close_dialog())
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        def close_dialog():
            dlg.open = False
            page.update()

        page.overlay.append(dlg)

        dlg.open = True
        page.update()

    def save_customer(e):
        nonlocal allow_duplicate_name

        name = name_var.value.strip()
        phone = phone_var.value.strip()
        phone2 = phone2_var.value.strip()
        address = address_var.value.strip()
        if not name:
            show_dialog("שגיאה", "יש להזין שם לקוח.")
            return

        # בדיקת טלפון – לא לאפשר
        if customer_exists_by_phone(phone):
            name = get_customer_by_phone(phone)
            show_dialog("שגיאה", f"מספר הטלפון הזה רשום על הלקוח {name['name']} לא ניתן להוסיף.")
            return

        # בדיקת שם – לא לחסום, רק להתריע
        if not allow_duplicate_name and customer_exists_by_name(name):
            allow_duplicate_name = True
            show_dialog("שגיאה", "קיים כבר לקוח עם שם זהה. לחיצה נוספת תוסיף בכל זאת.")

            return

        # ניסיון להוספה בפועל
        try:
            new_id = add_customer(
                name,
                phone,
                phone2,
                address,
                email_var.value.strip(),
                notes_var.value.strip(),
                allow_duplicate_name=allow_duplicate_name
            )
        except PhoneAlreadyExists:
            show_dialog("שגיאה"," לא ניתן להוסיף – קיים כבר לקוח עם מספר הטלפון הזה.")

            return
        print("new_id", new_id)
        navigator.go_new_invitation(
            user=current_user,
            c_id=new_id,
            is_new_invitation=True
        )

    page.controls.clear()
    page.add(
        ft.Column([
            ft.Text("לקוח חדש", size=24, weight=ft.FontWeight.BOLD),
            name_var,
            phone_var,
            phone2_var,
            address_var,
            email_var,
            notes_var,
            ft.Row([
                ft.ElevatedButton("💾 שמור והמשך להזמנה", on_click=save_customer ,bgcolor="#52b69a", color="white"),
                ft.ElevatedButton("חזרה⬅️", on_click=lambda e: navigator.go_orders(user=current_user),bgcolor="#f28c7d", color="white",)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
        ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
    )
    page.update()
