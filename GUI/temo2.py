
# דרישות: pip install kivy kivymd==1.2.0
# אם כבר מותקן 1.2.0 תקבלי אזהרת deprecate – זה בסדר. הקוד מותאם אליו.

from kivy.core.text import LabelBase
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty, NumericProperty, ObjectProperty, ListProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.core.window import Window

from kivymd.app import MDApp
from kivymd.uix.button import MDRectangleFlatIconButton, MDFlatButton
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.menu import MDDropdownMenu

# פונטים – להימנע מריבועים:
# נרשום את Segoe UI המובנה ב-Windows כ"Roboto" כדי שכל רכיבי KivyMD יירשו אותו.
try:
    LabelBase.register(name="Roboto", fn_regular=r"C:\Windows\Fonts\segoeui.ttf")
except Exception:
    # אם לא הצליח (מערכת לא-ווינדוס), נמשיך עם ברירת מחדל. רק בלי אימוג'ים.
    pass

# ====== DAL שסיפקת ======
from logic.suppliers import (
    add_supplier, get_supplier_by_id, update_supplier, delete_supplier,
    get_open_supplier_invitations, get_closed_unsupplied_invitations,
    get_supplier_monthly_report, get_all_suppliers,
    get_supplier_catalog, get_suppliers_catalog_by_supplier_id,
    add_supplier_catalog_entry, update_supplier_catalog_entry, delete_supplier_catalog_entry
)

# ====== KV ======
KV = '''
#:import dp kivy.metrics.dp

<Heading@MDLabel>:
    halign: "center"
    font_style: "H5"

<SectionTitle@MDLabel>:
    halign: "right"
    font_style: "H6"
    padding: [0, 8]

<RightLabel@MDLabel>:
    halign: "right"

<MainMenuScreen>:
    name: "menu"
    MDBoxLayout:
        orientation: "vertical"
        md_bg_color: 1, 1, 1, 1

        MDToolbar:
            title: "מערכת ניהול ספקים והזמנות"
            elevation: 4
            right_action_items: [["refresh", lambda x: app.refresh_everything()]]

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(16), dp(8)
            spacing: dp(12)

            Heading:
                text: "ברוכה הבאה"

            MDGridLayout:
                cols: 3
                adaptive_height: True
                spacing: dp(12)
                padding: 0, dp(8)

                MDRectangleFlatIconButton:
                    icon: "plus"
                    text: "הוספת ספק"
                    on_release: app.open_add_supplier_dialog()

                MDRectangleFlatIconButton:
                    icon: "magnify"
                    text: "חיפוש/עריכת ספק"
                    on_release: app.goto_suppliers_table()

                MDRectangleFlatIconButton:
                    icon: "trash-can-outline"
                    text: "מחיקת ספק"
                    on_release: app.open_delete_supplier_dialog()

                MDRectangleFlatIconButton:
                    icon: "folder-open"
                    text: "הזמנות פתוחות"
                    on_release: app.select_supplier_and_run(app.load_open_invitations)

                MDRectangleFlatIconButton:
                    icon: "package-variant"
                    text: "הזמנות סגורות שלא סופקו"
                    on_release: app.select_supplier_and_run(app.load_closed_unsupplied)

                MDRectangleFlatIconButton:
                    icon: "chart-box-outline"
                    text: "דו\"ח חודשי"
                    on_release: app.goto_monthly_report()

                MDRectangleFlatIconButton:
                    icon: "currency-ils"
                    text: "מחירון ספקים"
                    on_release: app.goto_catalog()

        Widget:

<SuppliersTableScreen>:
    name: "suppliers_table"
    MDBoxLayout:
        orientation: "vertical"

        MDToolbar:
            title: "רשימת ספקים"
            left_action_items: [["arrow-right", lambda x: app.back_to_menu()]]
            right_action_items: [["pencil", lambda x: app.edit_selected_supplier_from_table()],
                                 ["refresh", lambda x: app.reload_suppliers_table()]]

        MDBoxLayout:
            id: table_holder
            padding: dp(8)
            md_bg_color: 1,1,1,1

<MonthlyReportScreen>:
    name: "monthly"
    supplier_id: None
    MDBoxLayout:
        orientation: "vertical"

        MDToolbar:
            title: "דו\"ח חודשי"
            left_action_items: [["arrow-right", lambda x: app.back_to_menu()]]

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(16)
            spacing: dp(8)

            SectionTitle:
                text: "בחירת ספק, שנה וחודש"

            MDBoxLayout:
                spacing: dp(8)
                adaptive_height: True

                MDTextField:
                    id: supplier_field
                    hint_text: "בחר ספק"
                    readonly: True
                    on_focus: if self.focus: app.open_suppliers_menu(self)

                MDTextField:
                    id: year_field
                    hint_text: "שנה (YYYY)"
                    input_filter: "int"
                    helper_text: "לדוגמה: 2025"
                    helper_text_mode: "on_focus"

                MDTextField:
                    id: month_field
                    hint_text: "חודש (1-12)"
                    input_filter: "int"
                    helper_text: "לדוגמה: 8"
                    helper_text_mode: "on_focus"

                MDRectangleFlatIconButton:
                    icon: "download"
                    text: "טען דו\"ח"
                    on_release: app.load_monthly_report(supplier_field.text, year_field.text, month_field.text)

            MDBoxLayout:
                id: report_holder
                padding: dp(8)

<CatalogScreen>:
    name: "catalog"
    MDBoxLayout:
        orientation: "vertical"

        MDToolbar:
            title: "מחירון ספקים"
            left_action_items: [["arrow-right", lambda x: app.back_to_menu()]]
            right_action_items: [["plus", lambda x: app.open_add_catalog_entry_dialog()], ["refresh", lambda x: app.refresh_catalog()]]

        MDBoxLayout:
            orientation: "vertical"
            padding: dp(16)
            spacing: dp(8)

            SectionTitle:
                text: "בחירת ספק לתצוגה"

            MDBoxLayout:
                spacing: dp(8)
                adaptive_height: True

                MDTextField:
                    id: catalog_supplier_field
                    hint_text: "כל הספקים (ברירת מחדל)"
                    readonly: True
                    on_focus: if self.focus: app.open_suppliers_menu(self, include_all=True)

                MDRectangleFlatIconButton:
                    icon: "table"
                    text: "טען מחירון"
                    on_release: app.refresh_catalog()

            MDBoxLayout:
                id: catalog_holder
                padding: dp(8)

<GenericListScreen>:
    name: "list_screen"
    title_text: ""
    MDBoxLayout:
        orientation: "vertical"
        MDToolbar:
            id: bar
            title: root.title_text
            left_action_items: [["arrow-right", lambda x: app.back_to_menu()]]

        MDBoxLayout:
            id: list_holder
            padding: dp(8)

'''

# ====== מסכי Python ======
class MainMenuScreen(Screen):
    pass

class SuppliersTableScreen(Screen):
    pass

class MonthlyReportScreen(Screen):
    supplier_id = NumericProperty(None)

class CatalogScreen(Screen):
    pass

class GenericListScreen(Screen):
    title_text = StringProperty("")

# ====== האפליקציה ======
class SupplierApp(MDApp):
    suppliers_cache = ListProperty([])
    suppliers_menu = ObjectProperty(None, allownone=True)

    def build(self):
        self.title = "מערכת ניהול ספקים והזמנות"
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        Window.minimum_width, Window.minimum_height = 960, 600

        root = Builder.load_string(KV)
        self.sm: ScreenManager = root

        # יצירת מסכים
        self.sm.add_widget(MainMenuScreen())
        self.sm.add_widget(SuppliersTableScreen())
        self.sm.add_widget(MonthlyReportScreen())
        self.sm.add_widget(CatalogScreen())
        self.sm.add_widget(GenericListScreen())

        # טעינת רשימת ספקים מראש
        self.refresh_suppliers_cache()

        return self.sm

    # ===== ניווט =====
    def back_to_menu(self):
        self.sm.current = "menu"

    def goto_suppliers_table(self):
        self.sm.current = "suppliers_table"
        self.reload_suppliers_table()

    def goto_monthly_report(self):
        self.sm.current = "monthly"
        # נקה טבלה ישנה אם קיימת
        holder = self.sm.get_screen("monthly").ids.report_holder
        holder.clear_widgets()

    def goto_catalog(self):
        self.sm.current = "catalog"
        self.refresh_catalog()

    def refresh_everything(self):
        self.refresh_suppliers_cache()
        if self.sm.current == "suppliers_table":
            self.reload_suppliers_table()
        elif self.sm.current == "catalog":
            self.refresh_catalog()

    # ===== ספקים – מטמון + תפריט =====
    def refresh_suppliers_cache(self):
        try:
            self.suppliers_cache = get_all_suppliers() or []
        except Exception as e:
            self.show_alert("שגיאה", f"בעיה בטעינת ספקים: {e}")

    def open_suppliers_menu(self, anchor_widget, include_all=False):
        # בונה תפריט נפתח לבחירת ספק
        items = []
        if include_all:
            items.append({
                "viewclass": "OneLineListItem",
                "text": "כל הספקים",
                "on_release": lambda t="כל הספקים": self._set_menu_text(anchor_widget, t)
            })
        for s in self.suppliers_cache:
            text = f'{s.get("name","")} (ID:{s.get("id")})'
            items.append({
                "viewclass": "OneLineListItem",
                "text": text,
                "on_release": (lambda t=text: self._set_menu_text(anchor_widget, t))
            })

        if self.suppliers_menu:
            self.suppliers_menu.dismiss()
        self.suppliers_menu = MDDropdownMenu(
            caller=anchor_widget,
            items=items,
            width_mult=4,
        )
        self.suppliers_menu.open()

    def _set_menu_text(self, widget, text):
        widget.text = text
        if self.suppliers_menu:
            self.suppliers_menu.dismiss()

    # ===== דיאלוגים כלליים =====
    def show_alert(self, title, text):
        dlg = MDDialog(
            title=title,
            text=text,
            buttons=[MDFlatButton(text="סגור", on_release=lambda x: dlg.dismiss())]
        )
        dlg.open()

    # ===== הוספת ספק =====
    def open_add_supplier_dialog(self):
        layout = MDBoxLayout(orientation="vertical", spacing=10, padding=10)
        name_field = MDTextField(hint_text="שם ספק", helper_text_mode="on_focus")
        phone_field = MDTextField(hint_text="טלפון", helper_text_mode="on_focus")
        email_field = MDTextField(hint_text="אימייל", helper_text_mode="on_focus")
        layout.add_widget(name_field)
        layout.add_widget(phone_field)
        layout.add_widget(email_field)

        dlg = MDDialog(
            title="הוספת ספק",
            type="custom",
            content_cls=layout,
            buttons=[
                MDFlatButton(text="ביטול", on_release=lambda x: dlg.dismiss()),
                MDFlatButton(
                    text="שמור",
                    on_release=lambda x: self._save_supplier_from_dialog(
                        name_field.text, phone_field.text, email_field.text, dlg
                    )
                ),
            ]
        )
        dlg.open()

    def _save_supplier_from_dialog(self, name, phone, email, dlg):
        try:
            add_supplier({"name": name, "phone": phone, "email": email})
            dlg.dismiss()
            self.show_alert("הצלחה", "הספק נוסף בהצלחה")
            self.refresh_suppliers_cache()
            if self.sm.current == "suppliers_table":
                self.reload_suppliers_table()
        except Exception as e:
            self.show_alert("שגיאה", f"לא ניתן להוסיף ספק: {e}")

    # ===== מחיקת ספק =====
    def open_delete_supplier_dialog(self):
        layout = MDBoxLayout(orientation="vertical", spacing=10, padding=10)
        id_field = MDTextField(hint_text="ID של ספק למחיקה", input_filter="int")
        layout.add_widget(id_field)

        dlg = MDDialog(
            title="מחיקת ספק",
            type="custom",
            content_cls=layout,
            buttons=[
                MDFlatButton(text="ביטול", on_release=lambda x: dlg.dismiss()),
                MDFlatButton(
                    text="מחק",
                    on_release=lambda x: self._delete_supplier_by_id(id_field.text, dlg)
                ),
            ]
        )
        dlg.open()

    def _delete_supplier_by_id(self, id_text, dlg):
        try:
            sid = int(id_text)
        except:
            self.show_alert("שגיאה", "אנא הזיני ID מספרי תקין")
            return
        try:
            delete_supplier(sid)
            dlg.dismiss()
            self.show_alert("הצלחה", "הספק נמחק בהצלחה")
            self.refresh_suppliers_cache()
            if self.sm.current == "suppliers_table":
                self.reload_suppliers_table()
        except Exception as e:
            self.show_alert("שגיאה", f"מחיקה נכשלה: {e}")

    # ===== טבלת ספקים + עריכה =====
    _suppliers_table = None
    _selected_rows_cache = []

    def reload_suppliers_table(self):
        screen = self.sm.get_screen("suppliers_table")
        holder = screen.ids.table_holder
        holder.clear_widgets()

        rows = [(s.get("id"), s.get("name",""), s.get("phone",""), s.get("email",""))
                for s in self.suppliers_cache]

        table = MDDataTable(
            size_hint=(1, 1),
            check=True,  # כדי לבחור רשומה
            use_pagination=False,
            column_data=[
                ("ID", dp(30)),
                ("שם", dp(50)),
                ("טלפון", dp(40)),
                ("אימייל", dp(60)),
            ],
            row_data=rows
        )
        table.bind(on_check_press=self._on_table_check)
        holder.add_widget(table)
        self._suppliers_table = table
        self._selected_rows_cache = []

    def _on_table_check(self, table, row):
        # שמור בחירה אחרונה (אם בחרו כמה – ניקח את הראשונה)
        self._selected_rows_cache = table.get_row_checks() or []

    def edit_selected_supplier_from_table(self):
        if not self._suppliers_table:
            return
        checked = self._suppliers_table.get_row_checks()
        if not checked:
            self.show_alert("שגיאה", "בחרי רשומה לעריכה (תיבת סימון)")
            return
        row = checked[0]
        supplier_id = row[0]
        try:
            supplier = get_supplier_by_id(supplier_id)
        except Exception as e:
            self.show_alert("שגיאה", f"שגיאה בשליפה: {e}")
            return
        if not supplier:
            self.show_alert("שגיאה", "ספק לא נמצא")
            return
        self._open_edit_supplier_dialog(supplier)

    def _open_edit_supplier_dialog(self, supplier):
        layout = MDBoxLayout(orientation="vertical", spacing=10, padding=10)
        name_field = MDTextField(hint_text="שם ספק", text=supplier.get("name",""))
        phone_field = MDTextField(hint_text="טלפון", text=supplier.get("phone",""))
        email_field = MDTextField(hint_text="אימייל", text=supplier.get("email",""))
        layout.add_widget(name_field)
        layout.add_widget(phone_field)
        layout.add_widget(email_field)

        dlg = MDDialog(
            title=f"עריכת ספק ID {supplier.get('id')}",
            type="custom",
            content_cls=layout,
            buttons=[
                MDFlatButton(text="ביטול", on_release=lambda x: dlg.dismiss()),
                MDFlatButton(
                    text="שמור",
                    on_release=lambda x: self._save_supplier_changes(
                        supplier.get("id"), name_field.text, phone_field.text, email_field.text, dlg
                    )
                ),
            ]
        )
        dlg.open()

    def _save_supplier_changes(self, sid, name, phone, email, dlg):
        try:
            update_supplier(sid, {"name": name, "phone": phone, "email": email})
            dlg.dismiss()
            self.show_alert("הצלחה", "הספק עודכן בהצלחה")
            self.refresh_suppliers_cache()
            if self.sm.current == "suppliers_table":
                self.reload_suppliers_table()
        except Exception as e:
            self.show_alert("שגיאה", f"עדכון נכשל: {e}")

    # ===== בחירת ספק להפעלה של פעולה =====
    def select_supplier_and_run(self, callback):
        layout = MDBoxLayout(orientation="vertical", spacing=10, padding=10)
        field = MDTextField(hint_text="בחר ספק", readonly=True)
        layout.add_widget(field)

        def open_menu(*_):
            self.open_suppliers_menu(field)

        field.bind(on_focus=lambda w, f: open_menu() if f else None)

        dlg = MDDialog(
            title="בחירת ספק",
            type="custom",
            content_cls=layout,
            buttons=[
                MDFlatButton(text="ביטול", on_release=lambda x: dlg.dismiss()),
                MDFlatButton(
                    text="בחר",
                    on_release=lambda x: self._confirm_supplier_pick(field.text, dlg, callback)
                ),
            ]
        )
        dlg.open()

    def _confirm_supplier_pick(self, text, dlg, callback):
        if "ID:" not in text:
            self.show_alert("שגיאה", "אנא בחרי ספק מהרשימה")
            return
        sid = int(text.split("ID:")[-1].strip(") "))
        dlg.dismiss()
        callback(sid)

    # ==== הזמנות פתוחות/סגורות-לא-סופקו ====
    def load_open_invitations(self, supplier_id):
        try:
            rows = get_open_supplier_invitations(supplier_id) or []
        except Exception as e:
            self.show_alert("שגיאה", f"שגיאה בטעינת הזמנות: {e}")
            return
        self._show_list_of_dicts(f'הזמנות פתוחות לספק {supplier_id}', rows)

    def load_closed_unsupplied(self, supplier_id):
        try:
            rows = get_closed_unsupplied_invitations(supplier_id) or []
        except Exception as e:
            self.show_alert("שגיאה", f"שגיאה בטעינת הזמנות: {e}")
            return
        self._show_list_of_dicts(f'הזמנות סגורות שלא סופקו לספק {supplier_id}', rows)

    # ===== דו"ח חודשי =====
    def load_monthly_report(self, supplier_text, year, month):
        if "ID:" not in supplier_text:
            self.show_alert("שגיאה", "יש לבחור ספק")
            return
        try:
            supplier_id = int(supplier_text.split("ID:")[-1].strip(") "))
            year = int(year)
            month = int(month)
        except:
            self.show_alert("שגיאה", "חודש/שנה חייבים להיות מספרים")
            return
        try:
            rows = get_supplier_monthly_report(supplier_id, year, month) or []
        except Exception as e:
            self.show_alert("שגיאה", f"שגיאה בשליפת דו\"ח: {e}")
            return

        screen = self.sm.get_screen("monthly")
        holder = screen.ids.report_holder
        holder.clear_widgets()

        if not rows:
            self.show_alert("מידע", "לא נמצאו נתונים לדו\"ח הזה")
            return

        # הנחה: כל הרשומות באותו מבנה
        cols = list(rows[0].keys())
        table = MDDataTable(
            size_hint=(1, 1),
            column_data=[(c, dp(50)) for c in cols],
            row_data=[tuple(r[c] for c in cols) for r in rows]
        )
        holder.add_widget(table)

    # ===== מחירון ספקים =====
    _catalog_table = None
    _catalog_current_supplier_id = None

    def refresh_catalog(self):
        screen = self.sm.get_screen("catalog")
        field = screen.ids.catalog_supplier_field
        text = field.text or ""
        screen.ids.catalog_holder.clear_widgets()

        if text.startswith("כל הספקים") or text.strip() == "":
            # טען מחירון מלא
            self._load_full_catalog()
            self._catalog_current_supplier_id = None
        else:
            sid = int(text.split("ID:")[-1].strip(") "))
            self._load_single_supplier_catalog(sid)
            self._catalog_current_supplier_id = sid

    def _load_single_supplier_catalog(self, supplier_id):
        holder = self.sm.get_screen("catalog").ids.catalog_holder
        holder.clear_widgets()

        try:
            data = get_suppliers_catalog_by_supplier_id(supplier_id) or []
        except Exception as e:
            self.show_alert("שגיאה", f"שגיאה בטעינת מחירון: {e}")
            return

        if not data:
            self.show_alert("מידע", "לא נמצאו רשומות למחירון הספק")
            return

        cols = [("מחיר", dp(40)), ("שם מוצר", dp(80)), ("קוד מוצר", dp(40))]
        rows = [(d.get("price",""), d.get("product_name",""), d.get("product_id","")) for d in data]

        table = MDDataTable(
            size_hint=(1, 1),
            column_data=cols,
            row_data=rows
        )
        table.bind(on_row_press=lambda t, r: self._open_catalog_row_actions(supplier_id, t, r))
        holder.add_widget(table)
        self._catalog_table = table

    def _open_catalog_row_actions(self, supplier_id, table, row):
        # שחזור הערכים של השורה שנלחצה:
        try:
            row_values = [c.text for c in row.children[::-1]]  # price, name, product_id לפי הסדר שהוגדר
            price, product_name, product_id = row_values
        except Exception:
            return

        # דיאלוג פעולות: עריכה/מחיקה
        dlg = MDDialog(
            title=f"פריט מחירון: {product_id}",
            text=f"שם: {product_name}\nמחיר: {price}",
            buttons=[
                MDFlatButton(text="מחק", on_release=lambda x: self._delete_catalog_entry_confirm(dlg, supplier_id, product_id)),
                MDFlatButton(text="ערוך", on_release=lambda x: self._open_edit_catalog_entry_dialog(dlg, supplier_id, product_id, price)),
                MDFlatButton(text="סגור", on_release=lambda x: dlg.dismiss()),
            ]
        )
        dlg.open()

    def _delete_catalog_entry_confirm(self, parent_dlg, supplier_id, product_id):
        parent_dlg.dismiss()
        try:
            delete_supplier_catalog_entry(supplier_id=supplier_id, product_id=product_id)
            self.show_alert("הצלחה", "המוצר נמחק")
            self._load_single_supplier_catalog(supplier_id)
        except Exception as e:
            self.show_alert("שגיאה", f"מחיקה נכשלה: {e}")

    def open_add_catalog_entry_dialog(self):
        if self.sm.current != "catalog":
            return
        sid = self._catalog_current_supplier_id
        if sid is None:
            # כדי להוסיף מוצר – בחרי תחילה ספק ספציפי
            self.show_alert("מידע", "להוספת מוצר, בחרי ספק מסוים (לא 'כל הספקים')")
            return

        layout = MDBoxLayout(orientation="vertical", spacing=10, padding=10)
        product_field = MDTextField(hint_text="קוד מוצר")
        price_field = MDTextField(hint_text="מחיר", input_filter="float")
        layout.add_widget(product_field)
        layout.add_widget(price_field)

        dlg = MDDialog(
            title=f"הוספת מוצר לספק {sid}",
            type="custom",
            content_cls=layout,
            buttons=[
                MDFlatButton(text="ביטול", on_release=lambda x: dlg.dismiss()),
                MDFlatButton(
                    text="שמור",
                    on_release=lambda x: self._save_new_catalog_entry(dlg, sid, product_field.text, price_field.text)
                ),
            ]
        )
        dlg.open()

    def _save_new_catalog_entry(self, dlg, supplier_id, product_id, price_text):
        try:
            price = float(price_text)
        except:
            self.show_alert("שגיאה", "מחיר חייב להיות מספר תקין")
            return
        if not product_id.strip():
            self.show_alert("שגיאה", "יש להזין קוד מוצר")
            return
        try:
            add_supplier_catalog_entry({"supplier_id": supplier_id, "product_id": product_id.strip(), "price": price})
            dlg.dismiss()
            self.show_alert("הצלחה", "המוצר נוסף למחירון")
            self._load_single_supplier_catalog(supplier_id)
        except Exception as e:
            self.show_alert("שגיאה", f"הוספה נכשלה: {e}")

    def _open_edit_catalog_entry_dialog(self, parent_dlg, supplier_id, product_id, price):
        parent_dlg.dismiss()

        layout = MDBoxLayout(orientation="vertical", spacing=10, padding=10)
        price_field = MDTextField(hint_text="מחיר", text=str(price), input_filter="float")
        layout.add_widget(price_field)

        dlg = MDDialog(
            title=f"עריכת מוצר {product_id}",
            type="custom",
            content_cls=layout,
            buttons=[
                MDFlatButton(text="ביטול", on_release=lambda x: dlg.dismiss()),
                MDFlatButton(
                    text="שמור",
                    on_release=lambda x: self._save_edit_catalog_entry(dlg, supplier_id, product_id, price_field.text)
                ),
            ]
        )
        dlg.open()

    def _save_edit_catalog_entry(self, dlg, supplier_id, product_id, price_text):
        try:
            price = float(price_text)
        except:
            self.show_alert("שגיאה", "מחיר חייב להיות מספר תקין")
            return
        try:
            update_supplier_catalog_entry(supplier_id, product_id, {"price": price})
            dlg.dismiss()
            self.show_alert("הצלחה", "המוצר עודכן")
            self._load_single_supplier_catalog(supplier_id)
        except Exception as e:
            self.show_alert("שגיאה", f"עדכון נכשל: {e}")

    def _load_full_catalog(self):
        holder = self.sm.get_screen("catalog").ids.catalog_holder
        holder.clear_widgets()
        try:
            catalog = get_supplier_catalog() or []
        except Exception as e:
            self.show_alert("שגיאה", f"שגיאה בטעינת מחירון: {e}")
            return

        if not catalog:
            self.show_alert("מידע", "המחירון ריק")
            return

        # בנה מטריצה: עמודות = ספקים, ועוד 'שם מוצר', 'קוד מוצר'
        products = sorted(set(r["product_id"] for r in catalog))
        suppliers = sorted(set(r["supplier_id"] for r in catalog))

        # בניית מיפוי מחירים ושמות
        price_map = {}
        name_map = {}
        for r in catalog:
            price_map[(r["product_id"], r["supplier_id"])] = r.get("price", "-")
            name_map[r["product_id"]] = r.get("product_name", "-")

        # עמודות
        columns = [("שם מוצר", dp(70)), ("קוד מוצר", dp(50))] + [(f"ספק {sid}", dp(45)) for sid in suppliers]

        # שורות
        row_data = []
        for pid in products:
            row = [name_map.get(pid, "-"), pid]
            for sid in suppliers:
                row.append(price_map.get((pid, sid), "-"))
            row_data.append(tuple(row))

        table = MDDataTable(
            size_hint=(1, 1),
            column_data=columns,
            row_data=row_data
        )
        holder.add_widget(table)
        self._catalog_table = table

    # ===== הצגה כללית של רשימת מילונים =====
    def _show_list_of_dicts(self, title, rows):
        screen = self.sm.get_screen("list_screen")
        screen.title_text = title
        holder = screen.ids.list_holder
        holder.clear_widgets()

        if not rows:
            self.show_alert("מידע", "אין נתונים להצגה")
            return

        cols = list(rows[0].keys())
        table = MDDataTable(
            size_hint=(1, 1),
            column_data=[(c, dp(50)) for c in cols],
            row_data=[tuple(r.get(c, "")) for r in rows] if isinstance(rows[0], (list, tuple)) else
                     [tuple(r[c] for c in cols) for r in rows]
        )
        holder.add_widget(table)
        self.sm.current = "list_screen"


if __name__ == "__main__":
    SupplierApp().run()
