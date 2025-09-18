# from kivy.lang import Builder
# from kivymd.app import MDApp
# from kivy.uix.screenmanager import ScreenManager, Screen
# from kivy.core.text import LabelBase
# from kivy.core.window import Window
# from kivy.metrics import dp
# from kivy.clock import Clock
# from kivymd.uix.button import MDRaisedButton, MDFlatButton
# # from GUI.inventory_gui import InventoryScreen
# from GUI.customers_gui import CustomersScreen
# import os
# from GUI.suppliers_gui import SupplierScreen
# from logic.auth import authenticate_by_password
# from logic.utils import insert_worker_entry, update_worker_exit
# # from logic.manage_employees import ManageEmployeesScreen  # מבוטל לעכשיו
#
# # הגדרות חלון
# Window.size = (1024, 768)
#
# # פונט עברי
# LabelBase.register(name="HebrewFont", fn_regular=r"C:\Windows\Fonts\arial.ttf")
#
#
# class WindowManager(ScreenManager):
#     pass
#
#
# class LoginScreen(Screen):
#     pass
#
#
# class HomePage(Screen):
#     pass
#
#
# class StoreApp(MDApp):
#     sm: WindowManager
#     current_user = None
#     active_users = []
#
#     # ---------------- RTL ----------------
#     def make_rtl1(self, text):
#         return text[::-1]
#
#     def make_rtl(self, text: str) -> str:
#         return "\u202B" + text
#
#     # ---------------- BUILD ----------------
#     def build(self):
#         BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#         self.image_path = os.path.join(BASE_DIR, "shop_bg.png")
#
#         # טעינת קבצי KV
#         Builder.load_file("GUI/login_gui.kv")
#         Builder.load_file("GUI/homepage_gui.kv")
#         Builder.load_file("GUI/suppliers_gui.kv")
#         # Builder.load_file("inventory_gui.kv")
#         # Builder.load_file("GUI/customers_gui.kv")
#
#         # קודם יוצרים את ScreenManager
#         self.sm = WindowManager()
#
#         # מוסיפים מסכים
#         self.sm.add_widget(LoginScreen(name="login"))
#         self.sm.add_widget(HomePage(name="home"))
#         self.sm.add_widget(CustomersScreen(name="customers"))
#         self.sm.add_widget(SupplierScreen(name="suppliers"))
#
#         self.title = "מבט - ניהול חנות עדשות"
#         self.theme_cls.primary_palette = "Pink"
#         self.theme_cls.accent_palette = "Amber"
#
#         return self.sm
#
#     # ---------------- AUTH ----------------
#     def login_by_password(self, password: str):
#         if not password:
#             self._set_login_error("נא להכניס סיסמה")
#             return
#
#         user = authenticate_by_password(password)
#         if not user:
#             self._set_login_error("סיסמה שגויה")
#             return
#
#         self.current_user = user
#         if not any(u["id"] == user["id"] for u in self.active_users):
#             self.active_users.append(user)
#
#         if self.current_user["role"] != "manager":
#             insert_worker_entry(self.current_user["id"])
#
#         self.sm.current = "home"
#         self._populate_homepage()
#
#     def _set_login_error(self, msg: str):
#         self.sm.get_screen("login").ids.error_label.text = self.make_rtl(msg)
#
#     def logout_to_login(self):
#         if self.current_user and self.current_user["role"] != "manager":
#             update_worker_exit(self.current_user["id"])
#
#         self.current_user = None
#         self.sm.current = "login"
#         self.sm.get_screen("login").ids.error_label.text = ""
#
#     # ---------------- HOMEPAGE ----------------
#     def _populate_homepage(self):
#         scr = self.sm.get_screen("home")
#         username = self.current_user["user_name"] if self.current_user else ""
#         if username == 'admin':
#             scr.ids.welcome_label.text = self.make_rtl1("ברוכה הבאה מנהל")
#         else:
#             scr.ids.welcome_label.text = self.make_rtl1(f"ברוכה הבאה, {username}")
#
#         menu_box = scr.ids.menu_box
#         menu_box.clear_widgets()
#
#         base_options = [
#             ("מחירון", "open_price_list"),
#             ("המרת מספרים", "open_number_converter"),
#             ("מחשבון", "open_calculator"),
#             ("מסמכים", "open_documents"),
#             ("הזמנות", "open_orders"),
#         ]
#         manager_only = [
#             ("ניהול ספקים", "manage_suppliers"),
#             # ("ניהול עובדים", "manage_employees"),  # מבוטל
#             ("חשבון חודשי", "monthly_account"),
#         ]
#
#         options = list(base_options)
#         if self.current_user["role"] == "manager":
#             options += manager_only
#
#         for text, action in options:
#             btn = MDRaisedButton(
#                 text=self.make_rtl1(text),
#                 pos_hint={"center_x": 0.5},
#                 size_hint=(0.8, None),
#                 height=dp(50),
#                 on_release=lambda btn, act=action: self._navigate_to(act),
#                 font_name="HebrewFont"
#             )
#             menu_box.add_widget(btn)
#
#         self._refresh_active_users_chips()
#
#     def _navigate_to(self, action):
#         if action == "manage_employees":
#             self.show_custom_toast("דף ניהול עובדים מושבת לעכשיו ✨")
#             return
#         if action == "manage_suppliers":
#             self.sm.current = "suppliers"  # מעבר למסך ספקים
#             return
#         self.show_custom_toast(f"דף {action} ייבנה בשלב הבא ✨")
#
#     def _refresh_active_users_chips(self):
#         scr = self.sm.get_screen("home")
#         cont = scr.ids.active_users_chips
#         cont.clear_widgets()
#         for u in self.active_users:
#             from kivymd.uix.chip import MDChip
#             chip = MDChip(
#                 text=self.make_rtl(f"{u['user_name']} ({u['role']})"),
#                 icon_left="account"
#             )
#             cont.add_widget(chip)
#
#     # ---------------- CUSTOM TOAST ----------------
#     def show_custom_toast(self, msg: str, duration=2):
#         from kivymd.uix.label import MDLabel
#         from kivymd.uix.dialog import MDDialog
#
#         label = MDLabel(
#             text=self.make_rtl1(msg),
#             halign="center",
#             font_name="HebrewFont",
#         )
#
#         dialog = MDDialog(
#             type="custom",
#             content_cls=label,
#             auto_dismiss=True
#         )
#         dialog.open()
#         Clock.schedule_once(lambda dt: dialog.dismiss(), duration)
#
#
# if __name__ == "__main__":
#     StoreApp().run()
from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.uix.button import MDRaisedButton
import os

# הגדרות חלון
Window.size = (1024, 768)

# פונט עברי
LabelBase.register(name="HebrewFont", fn_regular=r"C:\Windows\Fonts\arial.ttf")


# ------------------- מסכים -------------------
class LoginScreen(Screen):
    pass


class HomeScreen(Screen):
    pass


class SuppliersListScreen(Screen):
    def edit_selected(self):
        print("עריכת ספק נבחר")


class DeleteSupplierScreen(Screen):
    def delete_selected(self):
        print("מחיקת ספק נבחר")


class CatalogScreen(Screen):
    def add_entry(self):
        pass

    def refresh(self):
        pass

    def show_all(self):
        pass

    def pick_supplier(self):
        pass


class GenericListScreen(Screen):
    pass


class MonthlyReportSelectorScreen(Screen):
    def pick_supplier(self):
        pass

    def run_report(self):
        pass


class MonthlyReportScreen(Screen):
    pass


# ------------------- ScreenManager -------------------
class WindowManager(ScreenManager):
    pass


# ------------------- האפליקציה -------------------
class StoreApp(MDApp):
    sm: WindowManager
    current_user = None
    active_users = []

    # ---------------- RTL ----------------
    def make_rtl1(self, text):
        return text[::-1]

    def make_rtl(self, text: str) -> str:
        return "\u202B" + text

    # ---------------- BUILD ----------------
    def build(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.image_path = os.path.join(BASE_DIR, "shop_bg.png")

        # טעינת קובץ KV
        Builder.load_file("GUI/suppliers_gui.kv")

        # יצירת ScreenManager והוספת המסכים
        self.sm = WindowManager()
        self.sm.add_widget(LoginScreen(name="login"))
        self.sm.add_widget(HomeScreen(name="home"))
        self.sm.add_widget(SuppliersListScreen(name="suppliers_list"))
        self.sm.add_widget(DeleteSupplierScreen(name="delete_supplier"))
        self.sm.add_widget(CatalogScreen(name="catalog"))
        self.sm.add_widget(GenericListScreen(name="generic_list"))
        self.sm.add_widget(MonthlyReportSelectorScreen(name="monthly_report_selector"))
        self.sm.add_widget(MonthlyReportScreen(name="monthly_report"))

        self.title = "מבט - ניהול חנות עדשות"
        self.theme_cls.primary_palette = "Pink"
        self.theme_cls.accent_palette = "Amber"

        return self.sm

    # ---------------- AUTH ----------------
    def login_by_password(self, password: str):
        # לדוגמה בלבד – יש להוסיף אימות אמיתי
        if password == "1234":
            self.current_user = {"user_name": "admin", "role": "manager"}
            self.sm.current = "home"
        else:
            self.sm.get_screen("login").ids.error_label.text = self.make_rtl("סיסמה שגויה")


if __name__ == "__main__":
    StoreApp().run()
