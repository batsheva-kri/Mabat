# import tkinter as tk
# from tkinter import ttk, messagebox
#
# from GUI.customers_gui import ExistingCustomerPage
# from GUI.new_invitation_gui import NewInvitationWindow
# from GUI.styles import setup_style
# from logic.inventory import (
#     get_all_suppliers,
#     get_products_by_category_status,
#     get_category_name,
#     sizes_for_category,
#     save_multiple_stock, process_inventory_input
# )
#
# class InventoryApp(tk.Tk):
#     def __init__(self):
#         super().__init__()
#         self.title("מערכת הזמנות")
#         screen_width = self.winfo_screenwidth()
#         screen_height = self.winfo_screenheight()
#         width = int(screen_width * 0.75)
#         height = int(screen_height * 0.75)
#         self.geometry(f"{width}x{height}")
#         self.configure(bg="#f9f9f9")
#         setup_style()
#
#         self.current_frame = None
#         self.show_main_orders_page()
#
#     def clear_frame(self):
#         if self.current_frame:
#             self.current_frame.destroy()
#
#     def show_main_orders_page(self):
#         self.clear_frame()
#         frame = tk.Frame(self)
#         frame.pack(fill="both", expand=True)
#         self.current_frame = frame
#
#         # כפתור למלאי
#         btn_inventory = ttk.Button(frame, text="למלאי", command=self.show_inventory_page)
#         btn_inventory.pack(pady=20)
#
#         # תיבת בחירה ללקוח
#         ttk.Label(frame, text="ללקוח:", font=("Arial", 12)).pack(pady=5)
#         customer_var = tk.StringVar()
#         customer_cb = ttk.Combobox(frame, textvariable=customer_var, state="readonly",
#                                    values=["לקוח קיים", "לקוח חדש"])
#         customer_cb.pack(pady=5)
#
#         def on_customer_select(event):
#             choice = customer_var.get()
#             if choice == "לקוח קיים":
#                 self.show_existing_customer_page()
#             elif choice == "לקוח חדש":
#                 self.show_new_customer_page()
#
#         customer_cb.bind("<<ComboboxSelected>>", on_customer_select)
#
#     def show_existing_customer_page(self):
#         self.clear_frame()
#         page = ExistingCustomerPage(self)
#         page.pack(fill="both", expand=True)
#         self.current_frame = page
#
#     def show_new_customer_page(self):
#         self.clear_frame()
#         frame = tk.Frame(self)
#         frame.pack(fill="both", expand=True)
#         self.current_frame = frame
#
#         ttk.Label(frame, text="לקוח חדש", font=("Arial", 16)).pack(pady=15)
#
#         form = tk.Frame(frame)
#         form.pack(pady=10)
#
#         ttk.Label(form, text="שם:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
#         name_var = tk.StringVar()
#         ttk.Entry(form, textvariable=name_var, width=30).grid(row=0, column=1, padx=5, pady=5)
#
#         ttk.Label(form, text="טלפון:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
#         phone_var = tk.StringVar()
#         ttk.Entry(form, textvariable=phone_var, width=30).grid(row=1, column=1, padx=5, pady=5)
#
#         ttk.Label(form, text="אימייל:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
#         email_var = tk.StringVar()
#         ttk.Entry(form, textvariable=email_var, width=30).grid(row=2, column=1, padx=5, pady=5)
#
#         ttk.Label(form, text="הערות:").grid(row=3, column=0, sticky="ne", padx=5, pady=5)
#         notes_txt = tk.Text(form, width=30, height=4)
#         notes_txt.grid(row=3, column=1, padx=5, pady=5)
#
#         def save_and_open_invitation():
#             try:
#                 from logic.customers import add_customer  # add_customer(name, phone, email, notes) -> new_id
#             except ImportError:
#                 messagebox.showerror("שגיאה", "חסר ייבוא: logic.customers.add_customer")
#                 return
#
#             name = name_var.get().strip()
#             if not name:
#                 messagebox.showwarning("שגיאה", "יש להזין שם לקוח")
#                 return
#
#             new_id = add_customer(
#                 name=name,
#                 phone=phone_var.get().strip() or None,
#                 email=email_var.get().strip() or None,
#                 notes=notes_txt.get("1.0", "end").strip() or None
#             )
#             if not new_id:
#                 messagebox.showerror("שגיאה", "שמירת לקוח נכשלה")
#                 return
#
#             # מיד לפתוח הזמנה חדשה ללקוח
#             self.open_new_invitation(new_id)
#
#         ttk.Button(frame, text="💾 שמור והמשך להזמנה", command=save_and_open_invitation).pack(pady=10)
#
#     def open_new_invitation(self, customer_id):
#         NewInvitationWindow(self, customer_id)
#
#     def show_inventory_page(self):
#         self.clear_frame()
#         frame = tk.Frame(self)
#         frame.pack(fill="both", expand=True)
#         self.current_frame = frame
#
#         btn_new_stock = ttk.Button(frame, text="מלאי שהגיע", command=self.show_new_stock_suppliers)
#         btn_new_stock.pack(pady=10)
#
#         btn_current_stock = ttk.Button(frame, text="כמויות קיימות במלאי", command=self.show_current_stock_page)
#         btn_current_stock.pack(pady=10)
#
#     def show_new_stock_suppliers(self):
#         self.clear_frame()
#         frame = tk.Frame(self)
#         frame.pack(fill="both", expand=True)
#         self.current_frame = frame
#
#         suppliers = get_all_suppliers()
#         ttk.Label(frame, text="בחר ספק:").pack(pady=10)
#
#         supplier_var = tk.StringVar()
#         supplier_cb = ttk.Combobox(frame, values=[s["name"] for s in suppliers], state="readonly", textvariable=supplier_var)
#         supplier_cb.pack(pady=10)
#
#         def on_select_supplier():
#             selected_name = supplier_var.get()
#             selected_supplier = next((s for s in suppliers if s["name"] == selected_name), None)
#             if not selected_supplier:
#                 messagebox.showwarning("שגיאה", "בחר ספק תקין")
#                 return
#             self.show_products_for_supplier(selected_supplier)
#
#         ttk.Button(frame, text="בחר ספק", command=on_select_supplier).pack(pady=10)
#
#     def show_products_for_supplier(self, supplier):
#         self.clear_frame()
#         frame = tk.Frame(self)
#         frame.pack(fill="both", expand=True)
#         self.current_frame = frame
#
#         category_id = 1
#         category_name = get_category_name(category_id)
#         ttk.Label(frame, text=f"קטגוריה: {category_name}", font=("Arial", 16)).pack(pady=15)
#
#         products = get_products_by_category_status(category_id)
#         for p in products:
#             btn = ttk.Button(frame, text=p["name"])
#             btn.pack(pady=5, padx=10, fill="x")
#
#     def show_current_stock_page(self):
#         self.clear_frame()
#         frame = tk.Frame(self)
#         frame.pack(fill="both", expand=True)
#         self.current_frame = frame
#
#         category_id = 1  # אפשר להרחיב לבחירת קטגוריה
#         category_name = get_category_name(category_id)
#         products = get_products_by_category_status(category_id)
#         sizes = sizes_for_category(category_id)
#
#         ttk.Label(frame, text=f"כמויות קיימות במלאי - {category_name}", font=("Arial", 16)).pack(pady=15)
#
#         # Frame לטבלאות
#         tables_frame = tk.Frame(frame)
#         tables_frame.pack(fill="both", expand=True)
#
#         # --- Frame לטבלת המידות עם גלילה ---
#         sizes_frame = tk.Frame(frame)
#         sizes_frame.pack(fill="both", expand=True, pady=(0, 20))  # קצת רווח מתחת
#
#         canvas = tk.Canvas(sizes_frame)
#         scrollbar_y = ttk.Scrollbar(sizes_frame, orient="vertical", command=canvas.yview)
#         scrollbar_x = ttk.Scrollbar(sizes_frame, orient="horizontal", command=canvas.xview)
#         scrollable_frame = tk.Frame(canvas)
#
#         scrollable_frame.bind(
#             "<Configure>",
#             lambda e: canvas.configure(
#                 scrollregion=canvas.bbox("all")
#             )
#         )
#
#         canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
#         canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
#
#         canvas.pack(side="left", fill="both", expand=True)
#         scrollbar_y.pack(side="right", fill="y")
#         scrollbar_x.pack(side="bottom", fill="x")
#
#         # כותרות (מוצרים)
#         ttk.Label(scrollable_frame, text="מידה", width=8).grid(row=0, column=len(products) + 1)
#         for col, product in enumerate(products):
#             ttk.Label(scrollable_frame, text=product["name"], width=15).grid(row=0, column=col)
#
#         entry_vars = []
#         for row, size in enumerate(sizes, start=1):
#             for col, product in enumerate(products):
#                 var = tk.StringVar(value="0")
#                 entry = ttk.Entry(scrollable_frame, textvariable=var, width=5)
#                 entry.grid(row=row, column=col)
#                 entry_vars.append((product["id"], size, var))
#
#             ttk.Label(scrollable_frame, text=str(size), width=8).grid(row=row, column=len(products) + 1)
#
#         # --- Frame נפרד לטבלת התמיסות ---
#         ttk.Label(frame, text="תמיסות", font=("Arial", 16)).pack(pady=15)
#
#         solutions_frame = tk.Frame(frame)
#         solutions_frame.pack(side="right", fill="y", padx=10, pady=10)
#
#         solutions = []
#         for cat_id in [3, 4]:
#             solutions.extend(get_products_by_category_status(cat_id, status="inventory"))
#         ttk.Label(solutions_frame, text="כמות במלאי", width=15).grid(row=0, column=0)
#         ttk.Label(solutions_frame, text="שם מוצר", width=30).grid(row=0, column=1)
#
#
#         solution_vars = []
#         for row, product in enumerate(solutions, start=1):
#             ttk.Label(solutions_frame, text=product["name"], width=30).grid(row=row, column=0)
#             var = tk.StringVar(value="0")
#             entry = ttk.Entry(solutions_frame, textvariable=var, width=10)
#             entry.grid(row=row, column=1)
#             solution_vars.append((product["id"], var))
#
#         def on_save():
#             quantities = []
#             for product_id, size, var in entry_vars:
#                 try:
#                     qty = int(var.get() or 0)
#                 except:
#                     qty = 0
#                 quantities.append((product_id, size, qty))
#
#             for product_id, var in solution_vars:
#                 try:
#                     qty = int(var.get() or 0)
#                 except:
#                     qty = 0
#                 quantities.append((product_id, '', qty))
#
#             process_inventory_input(quantities)
#             messagebox.showinfo("הצלחה", "הכמויות נשמרו והוזמנו מהספק במידת הצורך")
#             self.show_inventory_page()
#
#         ttk.Button(frame, text="שמור", command=on_save).pack(pady=10, side="bottom")
#
#
# if __name__ == "__main__":
#     app = InventoryApp()
#     app.mainloop()
# from kivy.app import App
# from kivy.uix.screenmanager import ScreenManager, Screen
# from kivy.properties import StringProperty, ObjectProperty, ListProperty
# from kivy.uix.popup import Popup
# from kivy.uix.label import Label
# from kivy.uix.textinput import TextInput
#
# from logic.inventory import (
#     get_all_suppliers,
#     get_products_by_category_status,
#     get_category_name,
#     sizes_for_category,
#     process_inventory_input
# )
# from logic.customers import add_customer
# from GUI.new_invitation_gui import NewInvitationWindow
# from GUI.customers_gui import ExistingCustomerPage
#
# class MainOrdersPage(Screen):
#     customer_choice = StringProperty()
#     def on_customer_choice(self, *args):
#         if self.customer_choice == "לקוח קיים":
#             self.manager.current = "existing_customer"
#         elif self.customer_choice == "לקוח חדש":
#             self.manager.current = "new_customer"
#
# class NewCustomerPage(Screen):
#     name_input = ObjectProperty()
#     phone_input = ObjectProperty()
#     email_input = ObjectProperty()
#     notes_input = ObjectProperty()
#
#     def save_and_continue(self):
#         name = self.name_input.text.strip()
#         if not name:
#             Popup(title="שגיאה", content=Label(text="יש להזין שם לקוח"), size_hint=(0.5,0.5)).open()
#             return
#
#         new_id = add_customer(
#             name=name,
#             phone=self.phone_input.text.strip() or None,
#             email=self.email_input.text.strip() or None,
#             notes=self.notes_input.text.strip() or None
#         )
#         if not new_id:
#             Popup(title="שגיאה", content=Label(text="שמירת לקוח נכשלה"), size_hint=(0.5,0.5)).open()
#             return
#
#         NewInvitationWindow(self.manager.get_screen("main_orders"), new_id)
#
# class ExistingCustomerPageKivy(Screen):
#     pass
#
# class InventoryPage(Screen):
#     pass
#
# class NewStockSuppliersPage(Screen):
#     suppliers_list = ListProperty([])
#
#     def load_suppliers(self):
#         self.suppliers_list = [s["name"] for s in get_all_suppliers()]
#
# class CurrentStockPage(Screen):
#     products_data = ListProperty([])
#     sizes_data = ListProperty([])
#
#     def load_products(self):
#         category_id = 1
#         self.products_data = get_products_by_category_status(category_id)
#         self.sizes_data = sizes_for_category(category_id)
#
# class InventoryApp(App):
#     def build(self):
#         sm = ScreenManager()
#         sm.add_widget(MainOrdersPage(name="main_orders"))
#         sm.add_widget(NewCustomerPage(name="new_customer"))
#         sm.add_widget(ExistingCustomerPageKivy(name="existing_customer"))
#         sm.add_widget(InventoryPage(name="inventory"))
#         sm.add_widget(NewStockSuppliersPage(name="new_stock"))
#         sm.add_widget(CurrentStockPage(name="current_stock"))
#         return sm
#
# if __name__ == "__main__":
#     InventoryApp().run()
#
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
# from kivy.uix.label import Label
# from kivy.uix.textinput import TextInput
# from kivy.uix.button import Button
# from kivy.uix.spinner import Spinner
# from kivy.uix.popup import Popup
#
# # ---------- פונקציות דמה, להחליף עם הלוגיקה שלך ----------
# def get_all_suppliers():
#     return [{"id": 1, "name": "ספק א"}, {"id": 2, "name": "ספק ב"}]
#
# def get_products_by_category_status(category_id, status="all"):
#     return [{"id": 1, "name": "מוצר א"}, {"id": 2, "name": "מוצר ב"}]
#
# def get_category_name(category_id):
#     return f"קטגוריה {category_id}"
#
# def sizes_for_category(category_id):
#     return ["S", "M", "L"]
#
# def process_inventory_input(quantities):
#     print("שמור מלאי:", quantities)
#
# def add_customer(name, phone=None, email=None, notes=None):
#     return 1234  # מזהה לקוח חדש
#
# # ---------- מסכים ----------
# class MainScreen(Screen):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
#
#         btn_inventory = Button(text="למלאי", size_hint_y=None, height=50)
#         btn_inventory.bind(on_release=lambda x: self.manager.current='inventory')
#         layout.add_widget(btn_inventory)
#
#         layout.add_widget(Label(text="ללקוח:", size_hint_y=None, height=30))
#         self.customer_spinner = Spinner(
#             text="בחר",
#             values=["לקוח קיים", "לקוח חדש"],
#             size_hint_y=None,
#             height=50
#         )
#         self.customer_spinner.bind(text=self.on_customer_select)
#         layout.add_widget(self.customer_spinner)
#
#         self.add_widget(layout)
#
#     def on_customer_select(self, spinner, text):
#         if text == "לקוח קיים":
#             self.manager.current = 'existing_customer'
#         elif text == "לקוח חדש":
#             self.manager.current = 'new_customer'
#
# class NewCustomerScreen(Screen):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
#
#         layout.add_widget(Label(text="לקוח חדש", font_size=24, size_hint_y=None, height=40))
#
#         form = GridLayout(cols=2, spacing=5, size_hint_y=None)
#         form.bind(minimum_height=form.setter('height'))
#
#         form.add_widget(Label(text="שם:"))
#         self.name_input = TextInput(multiline=False)
#         form.add_widget(self.name_input)
#
#         form.add_widget(Label(text="טלפון:"))
#         self.phone_input = TextInput(multiline=False)
#         form.add_widget(self.phone_input)
#
#         form.add_widget(Label(text="אימייל:"))
#         self.email_input = TextInput(multiline=False)
#         form.add_widget(self.email_input)
#
#         form.add_widget(Label(text="הערות:"))
#         self.notes_input = TextInput(multiline=True, size_hint_y=None, height=100)
#         form.add_widget(self.notes_input)
#
#         layout.add_widget(form)
#
#         save_btn = Button(text="💾 שמור והמשך להזמנה", size_hint_y=None, height=50)
#         save_btn.bind(on_release=self.save_and_open_invitation)
#         layout.add_widget(save_btn)
#
#         self.add_widget(layout)
#
#     def save_and_open_invitation(self, instance):
#         name = self.name_input.text.strip()
#         if not name:
#             popup = Popup(title='שגיאה', content=Label(text='יש להזין שם לקוח'), size_hint=(0.5, 0.3))
#             popup.open()
#             return
#         new_id = add_customer(
#             name=name,
#             phone=self.phone_input.text.strip() or None,
#             email=self.email_input.text.strip() or None,
#             notes=self.notes_input.text.strip() or None
#         )
#         self.manager.get_screen('new_invitation').customer_id = new_id
#         self.manager.current = 'new_invitation'
#
# class ExistingCustomerScreen(Screen):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.add_widget(Label(text="מסך לקוח קיים (יש לממש)", font_size=24))
#
# class InventoryScreen(Screen):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
#
#         btn_new_stock = Button(text="מלאי שהגיע", size_hint_y=None, height=50)
#         btn_new_stock.bind(on_release=lambda x: self.manager.current='new_stock')
#         layout.add_widget(btn_new_stock)
#
#         btn_current_stock = Button(text="כמויות קיימות במלאי", size_hint_y=None, height=50)
#         btn_current_stock.bind(on_release=lambda x: self.manager.current='current_stock')
#         layout.add_widget(btn_current_stock)
#
#         self.add_widget(layout)
#
# class NewStockScreen(Screen):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
#
#         layout.add_widget(Label(text="בחר ספק:", font_size=20, size_hint_y=None, height=30))
#
#         self.suppliers = get_all_suppliers()
#         self.supplier_spinner = Spinner(
#             text="בחר ספק",
#             values=[s["name"] for s in self.suppliers],
#             size_hint_y=None,
#             height=50
#         )
#         layout.add_widget(self.supplier_spinner)
#
#         select_btn = Button(text="בחר ספק", size_hint_y=None, height=50)
#         select_btn.bind(on_release=self.select_supplier)
#         layout.add_widget(select_btn)
#
#         self.add_widget(layout)
#
#     def select_supplier(self, instance):
#         selected_name = self.supplier_spinner.text
#         selected_supplier = next((s for s in self.suppliers if s["name"] == selected_name), None)
#         if not selected_supplier:
#             popup = Popup(title='שגיאה', content=Label(text='בחר ספק תקין'), size_hint=(0.5, 0.3))
#             popup.open()
#             return
#         self.manager.get_screen('products_supplier').supplier = selected_supplier
#         self.manager.current = 'products_supplier'
#
# class ProductsForSupplierScreen(Screen):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.supplier = None
#         self.layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
#         self.add_widget(self.layout)
#
#     def on_pre_enter(self):
#         self.layout.clear_widgets()
#         if not self.supplier:
#             return
#         category_id = 1
#         category_name = get_category_name(category_id)
#         self.layout.add_widget(Label(text=f"קטגוריה: {category_name}", font_size=20, size_hint_y=None, height=40))
#
#         products = get_products_by_category_status(category_id)
#         for p in products:
#             btn = Button(text=p["name"], size_hint_y=None, height=40)
#             self.layout.add_widget(btn)
#
# class CurrentStockScreen(Screen):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         self.layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
#         self.add_widget(self.layout)
#
#     def on_pre_enter(self):
#         self.layout.clear_widgets()
#         category_id = 1
#         category_name = get_category_name(category_id)
#         products = get_products_by_category_status(category_id)
#         sizes = sizes_for_category(category_id)
#
#         self.layout.add_widget(Label(text=f"כמויות קיימות במלאי - {category_name}", font_size=20, size_hint_y=None, height=40))
#
#         scroll = ScrollView()
#         table = GridLayout(cols=len(products)+1, spacing=5, size_hint_y=None)
#         table.bind(minimum_height=table.setter('height'))
#
#         # כותרות
#         table.add_widget(Label(text="מידה", size_hint_y=None, height=30))
#         for product in products:
#             table.add_widget(Label(text=product["name"], size_hint_y=None, height=30))
#
#         # תוכן הטבלה
#         for size in sizes:
#             for product in products:
#                 ti = TextInput(text="0", multiline=False, size_hint_y=None, height=30)
#                 table.add_widget(ti)
#             table.add_widget(Label(text=size, size_hint_y=None, height=30))
#
#         scroll.add_widget(table)
#         self.layout.add_widget(scroll)
#
#         save_btn = Button(text="שמור", size_hint_y=None, height=50)
#         save_btn.bind(on_release=self.save_stock)
#         self.layout.add_widget(save_btn)
#
#     def save_stock(self, instance):
#         popup = Popup(title='נשמר', content=Label(text='הכמויות נשמרו'), size_hint=(0.5, 0.3))
#         popup.open()
#         self.manager.current = 'inventory'
#
# # ---------- App ----------
# class InventoryApp(App):
#     def build(self):
#         sm = ScreenManager(transition=FadeTransition())
#
#         sm.add_widget(MainScreen(name='main'))
#         sm.add_widget(NewCustomerScreen(name='new_customer'))
#         sm.add_widget(ExistingCustomerScreen(name='existing_customer'))
#         sm.add_widget(InventoryScreen(name='inventory'))
#         sm.add_widget(NewStockScreen(name='new_stock'))
#         sm.add_widget(ProductsForSupplierScreen(name='products_supplier'))
#         sm.add_widget(CurrentStockScreen(name='current_stock'))
#
#         return sm
#
# if __name__ == "__main__":
#     InventoryApp().run()
