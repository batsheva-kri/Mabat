import flet as ft
from logic.customers import add_customer
from screens.new_invitation_page import NewInvitationPage


def  NewCustomerPage(page,current_user, navigator):
    name_var = ft.TextField(label="שם", width=200)
    phone_var = ft.TextField(label="טלפון", width=200)
    email_var = ft.TextField(label="אימייל", width=200)
    notes_var = ft.TextField(label="הערות", multiline=True, width=400, height=80)

    def save_customer(e):
        name = name_var.value.strip()
        if not name:
            page.dialog = ft.AlertDialog(title=ft.Text("שגיאה"), content=ft.Text("יש להזין שם לקוח"))
            page.dialog.open = True
            page.update()
            return

        # שימוש בפונקציה מהלוגיקה שלך
        new_id = add_customer(name, phone_var.value.strip(), email_var.value.strip(), notes_var.value.strip())
        navigator.go_new_invitation(
            user=current_user,
            c_id=new_id,
            is_new_invitation = True
        )

    page.controls.clear()
    page.add(
        ft.Column([
            ft.Text("לקוח חדש", size=24, weight=ft.FontWeight.BOLD),
            name_var,
            phone_var,
            email_var,
            notes_var,
            ft.Row([
                ft.ElevatedButton("💾 שמור והמשך להזמנה", on_click=save_customer),
                ft.ElevatedButton("חזרה", on_click=lambda e: navigator.go_orders(user=current_user))
            ], alignment=ft.MainAxisAlignment.START, spacing=10)
        ], alignment=ft.MainAxisAlignment.START, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=15)
    )
    page.update()
