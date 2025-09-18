# import tkinter as tk
# from tkinter import ttk, messagebox
# from datetime import datetime
#
# class NewInvitationWindow(tk.Toplevel):
#     def __init__(self, app: "InventoryApp", customer_id: int):
#         super().__init__(app)
#         self.app = app
#         self.customer_id = customer_id
#
#         self.title("הזמנה חדשה")
#         self.geometry("900x600")
#
#         # --- ייבוא דאטה ---
#         try:
#             from logic.users import get_all_users
#             from logic.products import get_all_products_for_invitation, get_catalog_prices
#         except ImportError:
#             messagebox.showerror("שגיאה", "חסר ייבוא: logic.users / logic.products")
#             self.destroy()
#             return
#
#         self.users = get_all_users()
#         self.products = get_all_products_for_invitation()
#
#         # מיפויים לעזר
#         self.users_by_id = {u["id"]: u for u in self.users}
#         self.products_by_name = {p["name"]: p for p in self.products}
#         self.products_by_id = {p["id"]: p for p in self.products}
#         self.get_catalog_prices = get_catalog_prices
#
#         self.items = []
#
#         # --- כותרת / מידע לקוח ---
#         header = tk.Frame(self)
#         header.pack(fill="x", padx=10, pady=10)
#         ttk.Label(header, text=f"לקוח ID: {self.customer_id}", font=("Arial", 12, "bold")).pack(side="right", padx=10)
#
#         # --- עובד מטפל ---
#         user_frame = tk.Frame(self)
#         user_frame.pack(fill="x", padx=10)
#         ttk.Label(user_frame, text="עובד מטפל:").pack(side="right", padx=5)
#         self.user_var = tk.StringVar()
#         user_options = [f'{u["user_name"]} (ID:{u["id"]})' for u in self.users]
#         self.user_combo = ttk.Combobox(user_frame, values=user_options, state="readonly", textvariable=self.user_var, width=30)
#         self.user_combo.pack(side="right")
#         default_user = self.users_by_id.get(1234)
#         if default_user:
#             self.user_combo.set(f'{default_user["user_name"]} (ID:1234)')
#
#         # --- תאריך/שעה, סטטוס, הערות ---
#         meta = tk.Frame(self)
#         meta.pack(fill="x", padx=10, pady=(10, 0))
#         self.now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         ttk.Label(meta, text=f"תאריך: {self.now_str}").pack(side="right", padx=15)
#         ttk.Label(meta, text=f"סטטוס: open").pack(side="right", padx=15)
#
#         notes_frame = tk.Frame(self)
#         notes_frame.pack(fill="x", padx=10, pady=10)
#         ttk.Label(notes_frame, text="הערות:").pack(side="right", padx=5)
#         self.notes_txt = tk.Text(notes_frame, height=3)
#         self.notes_txt.pack(side="right", fill="x", expand=True)
#
#         # --- טבלת פריטים ---
#         table_frame = tk.Frame(self)
#         table_frame.pack(fill="both", expand=True, padx=10, pady=10)
#         columns = ("product_name", "product_id", "qty", "size", "unit_price", "line_total", "supplied")
#         self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
#         for c, w in zip(columns, (240, 80, 60, 80, 80, 100, 70)):
#             self.tree.heading(c, text={
#                 "product_name": "שם מוצר",
#                 "product_id": "קוד",
#                 "qty": "כמות",
#                 "size": "מידה",
#                 "unit_price": "מחיר יח'",
#                 "line_total": "סה\"כ שורה",
#                 "supplied": "סופק",
#             }[c])
#             self.tree.column(c, width=w, anchor="center")
#         self.tree.pack(side="top", fill="both", expand=True)
#
#         # --- שורת הוספת פריט עם AutoComplete ---
#         add_frame = tk.Frame(self)
#         add_frame.pack(fill="x", padx=10, pady=(0, 10))
#         ttk.Label(add_frame, text="מוצר:").pack(side="right", padx=5)
#
#         self.product_combo, self.product_var = self.make_autocomplete_combobox(
#             add_frame,
#             [p["name"] for p in self.products],
#             width=40
#         )
#         self.product_combo.pack(side="right", padx=5)
#
#         ttk.Label(add_frame, text="כמות:").pack(side="right", padx=5)
#         self.qty_var = tk.StringVar(value="1")
#         ttk.Spinbox(add_frame, from_=1, to=999, textvariable=self.qty_var, width=6).pack(side="right")
#
#         ttk.Label(add_frame, text="מידה:").pack(side="right", padx=5)
#         self.size_var = tk.StringVar()
#         ttk.Entry(add_frame, textvariable=self.size_var, width=10).pack(side="right", padx=5)
#
#         self.unit_price_var = tk.StringVar(value="0")
#         ttk.Label(add_frame, text="מחיר יח':").pack(side="right", padx=5)
#         ttk.Label(add_frame, textvariable=self.unit_price_var, width=10).pack(side="right", padx=5)
#
#         def recompute_unit_price(*_):
#             name = self.product_var.get().strip()
#             qty = self._safe_int(self.qty_var.get(), 1)
#             product = self.products_by_name.get(name)
#             if not product:
#                 self.unit_price_var.set("0")
#                 return
#             prices = self.get_catalog_prices(product["id"])
#             unit_price, _ = self._calc_price_for_qty(prices, qty)
#             self.unit_price_var.set(f"{unit_price:.2f}")
#
#         self.product_combo.bind("<<ComboboxSelected>>", recompute_unit_price)
#         self.qty_var.trace_add("write", recompute_unit_price)
#
#         ttk.Button(add_frame, text="➕ הוסף פריט", command=self._add_item_from_row).pack(side="left")
#
#         # --- סכום כולל + כפתורי שמירה ---
#         footer = tk.Frame(self)
#         footer.pack(fill="x", padx=10, pady=10)
#         self.total_var = tk.StringVar(value="0")
#         ttk.Label(footer, text="סה\"כ:", font=("Arial", 12, "bold")).pack(side="right", padx=5)
#         ttk.Label(footer, textvariable=self.total_var, font=("Arial", 12, "bold")).pack(side="right")
#
#         ttk.Button(footer, text="🔒 סגור הזמנה (invented)", command=self._save_as_invented).pack(side="left", padx=5)
#         ttk.Button(footer, text="💾 שמור פתוחה (open)", command=self._save_as_open).pack(side="left", padx=5)
#
#         tip = tk.Label(self, text="טיפ: לחיצה כפולה על פריט תמחק אותו", fg="gray")
#         tip.pack(pady=(0, 5))
#         self.tree.bind("<Double-1>", self._on_delete_item)
#
#     @staticmethod
#     def make_autocomplete_combobox(parent, values, **kwargs):
#         var = tk.StringVar()
#         combo = ttk.Combobox(parent, textvariable=var, values=values, **kwargs)
#         def _on_keyrelease(event):
#             typed = var.get()
#             if typed == "":
#                 combo["values"] = values
#             else:
#                 combo["values"] = [v for v in values if typed.lower() in v.lower()]
#             if combo["values"]:
#                 combo.event_generate("<Down>")
#         combo.bind("<KeyRelease>", _on_keyrelease)
#         return combo, var
#
#     def _calc_price_for_qty(self, prices: dict, qty: int):
#         p1 = prices.get("price") or 0
#         p3 = prices.get("price_3") or 0
#         p6 = prices.get("price_6") or 0
#         p12 = prices.get("price_12") or 0
#         if qty < 3:
#             line = qty * p1
#         elif qty == 3:
#             line = p3
#         elif 4 <= qty <= 5:
#             line = p3 + (qty - 3) * p1
#         elif qty == 6:
#             line = p6
#         elif 7 <= qty <= 11:
#             line = p6 + (qty - 6) * p1
#         else:
#             line = p12 + (qty - 12) * p1
#         return (line / qty if qty > 0 else 0), line
#
#     def _add_item_from_row(self):
#         name = self.product_var.get().strip()
#         if not name or name not in self.products_by_name:
#             messagebox.showwarning("שגיאה", "בחר/י מוצר תקין")
#             return
#         product = self.products_by_name[name]
#         qty = self._safe_int(self.qty_var.get(), 1)
#         size = self.size_var.get().strip()
#         prices = self.get_catalog_prices(product["id"])
#         unit_price, line_total = self._calc_price_for_qty(prices, qty)
#         item = {
#             "product_id": product["id"],
#             "product_name": product["name"],
#             "qty": qty,
#             "size": size or None,
#             "unit_price": unit_price,
#             "line_total": line_total,
#             "supplied": 0
#         }
#         self.items.append(item)
#         self.tree.insert("", "end", values=(
#             item["product_name"], item["product_id"], item["qty"], item["size"] or "",
#             f"{item['unit_price']:.2f}", f"{item['line_total']:.2f}", item["supplied"]
#         ))
#         self._recompute_total()
#         self.product_var.set("")
#         self.qty_var.set("1")
#         self.size_var.set("")
#         self.unit_price_var.set("0")
#
#     def _recompute_total(self):
#         self.total_var.set(f"{sum(i['line_total'] for i in self.items):.2f}")
#
#     def _on_delete_item(self, _event):
#         sel = self.tree.selection()
#         if not sel:
#             return
#         idx = self.tree.index(sel[0])
#         self.tree.delete(sel[0])
#         if 0 <= idx < len(self.items):
#             self.items.pop(idx)
#         self._recompute_total()
#
#     @staticmethod
#     def _safe_int(text, default):
#         try:
#             v = int(text)
#             return v if v > 0 else default
#         except:
#             return default
#
#     # --- שמירה ל-DB ---
#     def _collect_header(self, status_when_save: str):
#         user_id = None
#         user_text = self.user_var.get().strip()
#         if user_text.endswith(")"):
#             try:
#                 user_id = int(user_text.split("ID:")[1].rstrip(")"))
#             except:
#                 pass
#         if user_id is None and 1234 in self.users_by_id:
#             user_id = 1234
#         notes = self.notes_txt.get("1.0", "end").strip() or None
#         total_price = sum(i["line_total"] for i in self.items)
#         return {
#             "customer_id": self.customer_id,
#             "created_by_user_id": user_id,
#             "date_": self.now_str,
#             "notes": notes,
#             "total_price": total_price,
#             "status": status_when_save,
#             "call": None
#         }
#
#     def _save_as_invented(self):
#         self._save_invitation_with_status("invented")
#
#     def _save_as_open(self):
#         self._save_invitation_with_status("open")
#
#     def _save_invitation_with_status(self, status_value: str):
#         if not self.items:
#             if not messagebox.askyesno("אישור", "אין פריטים בהזמנה. לשמור בכל זאת?"):
#                 return
#         try:
#             from logic.orders import create_invitation, add_invitation_items
#         except ImportError:
#             messagebox.showerror("שגיאה", "חסר ייבוא: logic.orders")
#             return
#         header = self._collect_header(status_value)
#         inv_id = create_invitation(header)
#         if not inv_id:
#             messagebox.showerror("שגיאה", "שמירת ההזמנה נכשלה")
#             return
#         if self.items:
#             add_invitation_items(inv_id, self.items)
#         messagebox.showinfo("נשמר", f"ההזמנה נשמרה בהצלחה. מספר הזמנה: {inv_id}")
#         self.destroy()
from kivy.uix.screenmanager import Screen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.datatables import MDDataTable
from kivy.metrics import dp
from datetime import datetime

from logic.users import get_all_users
from logic.products import get_all_products_for_invitation, get_catalog_prices

class NewInvitationScreen(Screen):
    dialog = None

    def on_enter(self):
        self.users = get_all_users()
        self.products = get_all_products_for_invitation()
        self.users_by_id = {u["id"]: u for u in self.users}
        self.products_by_name = {p["name"]: p for p in self.products}
        self.items = []

        self.now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.total_price = 0

    def open_add_product_dialog(self):
        """פותח דיאלוג להוספת פריט להזמנה"""
        if self.dialog:
            self.dialog.dismiss()
        self.product_input = MDTextField(hint_text="שם מוצר")
        self.qty_input = MDTextField(hint_text="כמות", text="1")
        self.size_input = MDTextField(hint_text="מידה (אופציונלי)")
        self.unit_price_label = MDLabel(text="מחיר יח': 0", halign="center")

        box = MDBoxLayout(orientation="vertical", spacing=10)
        box.add_widget(self.product_input)
        box.add_widget(self.qty_input)
        box.add_widget(self.size_input)
        box.add_widget(self.unit_price_label)

        self.dialog = MDDialog(
            title="➕ הוסף פריט",
            type="custom",
            content_cls=box,
            buttons=[
                MDRaisedButton(text="💾 שמור", on_release=self.add_item)
            ]
        )
        self.dialog.open()

    def add_item(self, *args):
        name = self.product_input.text.strip()
        if not name or name not in self.products_by_name:
            MDDialog(title="שגיאה", text="בחר מוצר תקין").open()
            return

        product = self.products_by_name[name]
        try:
            qty = max(1, int(self.qty_input.text))
        except:
            qty = 1
        size = self.size_input.text.strip() or None

        prices = get_catalog_prices(product["id"])
        unit_price, line_total = self._calc_price_for_qty(prices, qty)

        item = {
            "product_id": product["id"],
            "product_name": product["name"],
            "qty": qty,
            "size": size,
            "unit_price": unit_price,
            "line_total": line_total,
            "supplied": 0
        }
        self.items.append(item)
        self.total_price += line_total

        self.dialog.dismiss()
        self.dialog = None
        self.update_table()

    def update_table(self):
        """מעדכן את טבלת הפריטים (MDDataTable)"""
        if hasattr(self, "data_table"):
            self.ids.table_box.remove_widget(self.data_table)

        table_data = [
            (
                i["product_name"],
                i["product_id"],
                i["qty"],
                i["size"] or "",
                f"{i['unit_price']:.2f}",
                f"{i['line_total']:.2f}",
                i["supplied"]
            ) for i in self.items
        ]

        self.data_table = MDDataTable(
            size_hint=(1, None),
            height=dp(300),
            column_data=[
                ("שם מוצר", dp(120)),
                ("קוד", dp(50)),
                ("כמות", dp(50)),
                ("מידה", dp(50)),
                ("מחיר יח'", dp(70)),
                ("סה\"כ שורה", dp(80)),
                ("סופק", dp(50))
            ],
            row_data=table_data
        )
        self.ids.table_box.add_widget(self.data_table)
        self.ids.total_label.text = f"סה\"כ: {self.total_price:.2f}"

    def _calc_price_for_qty(self, prices: dict, qty: int):
        p1 = prices.get("price") or 0
        p3 = prices.get("price_3") or 0
        p6 = prices.get("price_6") or 0
        p12 = prices.get("price_12") or 0
        if qty < 3:
            line = qty * p1
        elif qty == 3:
            line = p3
        elif 4 <= qty <= 5:
            line = p3 + (qty - 3) * p1
        elif qty == 6:
            line = p6
        elif 7 <= qty <= 11:
            line = p6 + (qty - 6) * p1
        else:
            line = p12 + (qty - 12) * p1
        return (line / qty if qty > 0 else 0), line
