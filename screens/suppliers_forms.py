# import flet as ft
# from logic.suppliers import add_supplier, update_supplier, delete_supplier, get_all_suppliers
#
#
# class AddSupplierForm:
#     def __init__(self, page, on_save = None):
#         self.page = page
#         self.update_table = on_save
#
#     def open(self):
#         name_field = ft.TextField(label="שם ספק", width=300)
#         phone_field = ft.TextField(label="טלפון", width=300)
#         email_field = ft.TextField(label="אימייל", width=300)
#
#         def close_dialog():
#             self.page.overlay.clear()
#             self.page.update()
#
#         def save_supplier(e):
#             add_supplier({
#                 "name": name_field.value,
#                 "phone": phone_field.value,
#                 "email": email_field.value
#             })
#             self.update_table()
#             close_dialog()
#
#         dlg_content = ft.Column([name_field, phone_field, email_field], spacing=10)
#
#         self.page.overlay.clear()
#         self.page.overlay.append(
#             ft.Container(
#                 content=ft.Column([
#                     ft.Text("הוסף ספק", size=24, weight=ft.FontWeight.BOLD),
#                     dlg_content,
#                     ft.Row([
#                         ft.ElevatedButton("שמור", on_click=save_supplier, bgcolor="#52b69a", color="white"),
#                         ft.ElevatedButton("ביטול", on_click=lambda e: close_dialog(), bgcolor="#f28c7d", color="white")
#                     ], alignment=ft.MainAxisAlignment.CENTER, spacing=12)
#                 ], spacing=15),
#                 padding=20, bgcolor="#ffffff", border_radius=14
#             )
#         )
#         self.page.update()
#
#
# class EditSupplierForm:
#     def __init__(self, page, supplier_data=None, on_save=None):
#         self.page = page
#         self.supplier_data = supplier_data
#         self.update_table = on_save
#
#     def open(self):
#         suppliers = get_all_suppliers()
#         supplier_dropdown = ft.Dropdown(
#             label="בחר ספק לעריכה",
#             options=[ft.dropdown.Option(str(s["id"]), s["name"]) for s in suppliers],
#             width=300
#         )
#         name_field = ft.TextField(label="שם ספק חדש", width=300)
#         phone_field = ft.TextField(label="טלפון חדש", width=300)
#         email_field = ft.TextField(label="אימייל חדש", width=300)
#
#         # אם supplier_data הגיע, מלא את השדות מיד
#         if self.supplier_data:
#             supplier_dropdown.value = str(self.supplier_data["id"])
#             name_field.value = self.supplier_data["name"]
#             phone_field.value = self.supplier_data["phone"]
#             email_field.value = self.supplier_data["email"]
#
#         def load_supplier(e):
#             selected = next((s for s in suppliers if str(s["id"]) == supplier_dropdown.value), None)
#             if selected:
#                 name_field.value = selected["name"]
#                 phone_field.value = selected["phone"]
#                 email_field.value = selected["email"]
#                 self.page.update()
#
#         supplier_dropdown.on_change = load_supplier
#
#         def close_dialog():
#             self.page.overlay.clear()
#             self.page.update()
#
#         def save_changes(e):
#             update_supplier(supplier_dropdown.value, {
#                 "name": name_field.value,
#                 "phone": phone_field.value,
#                 "email": email_field.value
#             })
#             close_dialog()
#             self.update_table()
#         dlg_content = ft.Column([supplier_dropdown, name_field, phone_field, email_field], spacing=10)
#
#         self.page.overlay.clear()
#         self.page.overlay.append(
#             ft.Container(
#                 content=ft.Column([
#                     ft.Text("ערוך ספק", size=24, weight=ft.FontWeight.BOLD),
#                     dlg_content,
#                     ft.Row([
#                         ft.ElevatedButton("שמור", on_click=save_changes, bgcolor="#52b69a", color="white"),
#                         ft.ElevatedButton("ביטול", on_click=lambda e: close_dialog(), bgcolor="#f28c7d", color="white")
#                     ], alignment=ft.MainAxisAlignment.CENTER, spacing=12)
#                 ], spacing=15),
#                 padding=20, bgcolor="#ffffff", border_radius=14
#             )
#         )
#         self.page.update()
#
# class DeleteSupplierForm:
#     def __init__(self, page, supplier_data=None, on_save=None):
#         self.page = page
#         self.supplier_data = supplier_data
#         self.update_table = on_save
#
#     def open(self):
#         suppliers = get_all_suppliers()
#         supplier_dropdown = ft.Dropdown(
#             label="בחר ספק למחיקה",
#             options=[ft.dropdown.Option(str(s["id"]), s["name"]) for s in suppliers],
#             width=300
#         )
#
#         # אם supplier_data הגיע, בחר אותו מראש
#         if self.supplier_data:
#             supplier_dropdown.value = str(self.supplier_data["id"])
#
#         def close_dialog():
#             self.page.overlay.clear()
#             self.page.update()
#
#         def confirm_delete(e):
#             delete_supplier(supplier_dropdown.value)
#             self.update_table()
#             close_dialog()
#
#         dlg_content = ft.Column([supplier_dropdown], spacing=10)
#
#         self.page.overlay.clear()
#         self.page.overlay.append(
#             ft.Container(
#                 content=ft.Column([
#                     ft.Text("מחיקת ספק", size=24, weight=ft.FontWeight.BOLD),
#                     dlg_content,
#                     ft.Row([
#                         ft.ElevatedButton("מחק", on_click=confirm_delete, bgcolor="#f28c7d", color="white"),
#                         ft.ElevatedButton("ביטול", on_click=lambda e: close_dialog(), bgcolor="#52b69a", color="white")
#                     ], alignment=ft.MainAxisAlignment.CENTER, spacing=12)
#                 ], spacing=15),
#                 padding=20, bgcolor="#ffffff", border_radius=14
#             )
#         )
#         self.page.update()
import flet as ft
from logic.suppliers import add_supplier, update_supplier, delete_supplier, get_all_suppliers


def AddSupplierScreen(page, navigator,user, on_save=None):
    page.title = "הוספת ספק חדש"

    name_field = ft.TextField(label="שם ספק", width=300)
    phone_field = ft.TextField(label="טלפון", width=300)
    email_field = ft.TextField(label="אימייל", width=300)
    link_field = ft.TextField(label="לינק לגוגל שיט", width=300)

    def save_supplier(e):
        add_supplier({
            "name": name_field.value,
            "phone": phone_field.value,
            "email": email_field.value,
            "link":link_field.value
        })
        if on_save:
            on_save()
        back_to_suppliers()

    def back_to_suppliers():
        navigator.go_suppliers(user)

    page.controls.clear()
    page.add(
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("הוסף ספק", size=24, weight=ft.FontWeight.BOLD),
                    name_field,
                    phone_field,
                    email_field,
                    link_field,
                    ft.Row([
                        ft.ElevatedButton("שמור", on_click=save_supplier, bgcolor="#52b69a", color="white"),
                        ft.ElevatedButton("⬅ חזרה", on_click=lambda e: back_to_suppliers(), bgcolor="#f28c7d", color="white")
                    ], spacing=10)
                ],
                spacing=15
            ),
            padding=20
        )
    )
    page.update()


def EditSupplierScreen(page, navigator,user, supplier_data=None, on_save=None):
    page.title = "עריכת ספק"

    suppliers = get_all_suppliers()

    supplier_dropdown = ft.Dropdown(
        label="בחר ספק לעריכה",
        options=[ft.dropdown.Option(str(s["id"]), s["name"]) for s in suppliers],
        width=300
    )

    name_field = ft.TextField(label="שם ספק חדש", width=300)
    phone_field = ft.TextField(label="טלפון חדש", width=300)
    email_field = ft.TextField(label="אימייל חדש", width=300)
    link_field = ft.TextField(label="לינק חדש", width=300)

    # מילוי אוטומטי במקרה שנשלח ספק
    if supplier_data:
        supplier_dropdown.value = str(supplier_data["id"])
        name_field.value = supplier_data["name"]
        phone_field.value = supplier_data["phone"]
        email_field.value = supplier_data["email"]
        link_field.value = supplier_data["googleSheetLink"]

    def load_supplier(e):
        selected = next((s for s in suppliers if str(s["id"]) == supplier_dropdown.value), None)
        if selected:
            name_field.value = selected["name"]
            phone_field.value = selected["phone"]
            email_field.value = selected["email"]
            link_field.value = selected["link"]
            page.update()

    supplier_dropdown.on_change = load_supplier

    def save_changes(e):
        update_supplier(supplier_dropdown.value, {
            "name": name_field.value,
            "phone": phone_field.value,
            "email": email_field.value,
            "googleSheetLink": link_field.value
        })
        if on_save:
            on_save()
        back_to_suppliers()

    def back_to_suppliers():
        navigator.go_suppliers(user)

    page.controls.clear()
    page.add(
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("ערוך ספק", size=24, weight=ft.FontWeight.BOLD),
                    supplier_dropdown,
                    name_field,
                    phone_field,
                    email_field,
                    link_field,
                    ft.Row([
                        ft.ElevatedButton("שמור", on_click=save_changes, bgcolor="#52b69a", color="white"),
                        ft.ElevatedButton("⬅ חזרה", on_click=lambda e: back_to_suppliers(), bgcolor="#f28c7d", color="white")
                    ], spacing=10)
                ],
                spacing=15
            ),
            padding=20
        )
    )
    page.update()


def DeleteSupplierScreen(page, navigator,user, supplier_data=None, on_save=None):
    page.title = "מחיקת ספק"

    suppliers = get_all_suppliers()

    supplier_dropdown = ft.Dropdown(
        label="בחר ספק למחיקה",
        options=[ft.dropdown.Option(str(s["id"]), s["name"]) for s in suppliers],
        width=300
    )

    if supplier_data:
        supplier_dropdown.value = str(supplier_data["id"])

    def confirm_delete(e):
        delete_supplier(supplier_dropdown.value)
        if on_save:
            on_save()
        back_to_suppliers()

    def back_to_suppliers():
        navigator.go_suppliers(user)

    page.controls.clear()
    page.add(
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("מחק ספק", size=24, weight=ft.FontWeight.BOLD),
                    supplier_dropdown,
                    ft.Row([
                        ft.ElevatedButton("מחק", on_click=confirm_delete, bgcolor="#f28c7d", color="white"),
                        ft.ElevatedButton("⬅ חזרה", on_click=lambda e: back_to_suppliers(), bgcolor="#52b69a", color="white")
                    ], spacing=10)
                ],
                spacing=15
            ),
            padding=20
        )
    )
    page.update()
