# import tkinter as tk
# from tkinter import ttk, messagebox
#
# from logic.customers import search_customer_by_name, search_customer_by_phone, get_orders_for_customer
#
# class ExistingCustomerPage(ttk.Frame):
#     def __init__(self, master):
#         super().__init__(master)
#
#
#         self.master = master
#         self.configure(style="TFrame")
#         self.create_widgets()
#
#     def create_widgets(self):
#         ttk.Label(self, text="חיפוש לקוח קיים", style="Header.TLabel").grid(row=0, column=0, columnspan=4, pady=15, sticky="e")
#
#         # שדות חיפוש
#         ttk.Label(self, text="שם:", anchor="e", style="TLabel").grid(row=1, column=3, sticky="e", padx=5, pady=5)
#         self.name_var = tk.StringVar()
#         name_entry = ttk.Entry(self, textvariable=self.name_var, justify="right", style="TEntry")
#         name_entry.grid(row=1, column=2, sticky="we", padx=5, pady=5)
#         self.name_var.trace_add("write", lambda *args: self.perform_search())
#
#         ttk.Label(self, text="טלפון:", anchor="e", style="TLabel").grid(row=1, column=1, sticky="e", padx=5, pady=5)
#         self.phone_var = tk.StringVar()
#         phone_entry = ttk.Entry(self, textvariable=self.phone_var, justify="right", style="TEntry")
#         phone_entry.grid(row=1, column=0, sticky="we", padx=5, pady=5)
#         self.phone_var.trace_add("write", lambda *args: self.perform_search())
#
#         # טבלת תוצאות
#         columns = ("name", "phone")
#         self.tree_customers = ttk.Treeview(self, columns=columns, show="headings", height=8, style="Treeview")
#         self.tree_customers.heading("name", text="שם לקוח", anchor="e")
#         self.tree_customers.heading("phone", text="טלפון", anchor="w")  # תיקן יישור טלפון לימין (RTL)
#         self.tree_customers.column("name", anchor="e", width=200)
#         self.tree_customers.column("phone", anchor="w", width=150)
#         self.tree_customers.grid(row=2, column=0, columnspan=4, sticky="nsew", pady=10)
#
#         # גלילה
#         scrollbar_cust = ttk.Scrollbar(self, orient="vertical", command=self.tree_customers.yview, style="Vertical.TScrollbar")
#         self.tree_customers.configure(yscrollcommand=scrollbar_cust.set)
#         scrollbar_cust.grid(row=2, column=4, sticky="ns")
#
#         self.tree_customers.bind("<Double-1>", self.on_customer_select)
#
#         # מסגרת להזמנות
#         self.orders_frame = ttk.Frame(self, style="TFrame")
#         self.orders_frame.grid(row=3, column=0, columnspan=5, sticky="nsew", pady=15)
#
#         for col in range(4):
#             self.grid_columnconfigure(col, weight=1)
#         self.grid_rowconfigure(2, weight=1)
#         self.grid_rowconfigure(3, weight=1)
#
#     def perform_search(self):
#         self.tree_customers.delete(*self.tree_customers.get_children())
#
#         name = self.name_var.get().strip()
#         phone = self.phone_var.get().strip()
#
#         customers = []
#         if name:
#             customers = search_customer_by_name(name)
#         elif phone:
#             customers = search_customer_by_phone(phone)
#
#         if not customers:
#             self.tree_customers.insert("", "end", values=("לא נמצאו לקוחות", ""))
#             return
#
#         for cust in customers:
#             self.tree_customers.insert("", "end", values=(cust["name"], cust["phone"]), iid=cust["id"])
#
#     def on_customer_select(self, event):
#         selected = self.tree_customers.selection()
#         if not selected:
#             return
#         cust_id = int(selected[0])
#         cust_name = self.tree_customers.item(selected, "values")[0]
#         self.show_customer_orders(cust_id, cust_name)
#
#     def show_customer_orders(self, customer_id, customer_name):
#         for widget in self.orders_frame.winfo_children():
#             widget.destroy()
#
#         ttk.Label(self.orders_frame, text=f"הזמנות של {customer_name}", style="Header.TLabel").pack(pady=5)
#
#         orders = get_orders_for_customer(customer_id)
#
#         if not orders:
#             ttk.Label(self.orders_frame, text="אין הזמנות ללקוח זה").pack()
#             return
#
#         for order in orders:
#             frame = ttk.Frame(self.orders_frame, style="TFrame")
#             frame.pack(fill="x", pady=2)
#
#             text = f"{order['date']} | {order['product_name']} | מידה: {order['size']} | כמות: {order['quantity']} | מחיר: {order['price']}"
#             ttk.Label(frame, text=text, style="TLabel").pack(side="left", padx=5)
#
#             ttk.Button(frame, text="העתק", style="Accent.TButton", command=lambda o=order: self.copy_order(o)).pack(side="right", padx=5)
#
#     def copy_order(self, order):
#         messagebox.showinfo("העתקה", f"מעביר להזמנה: {order}")
from kivy.uix.screenmanager import Screen
from logic.customers import search_customer_by_name, search_customer_by_phone


class CustomersScreen(Screen):
    def search_customers(self):
        """חיפוש לקוחות לפי שם או טלפון"""
        name = self.ids.name_input.text.strip()
        phone = self.ids.phone_input.text.strip()

        customers = []
        if name:
            customers = search_customer_by_name(name)
        elif phone:
            customers = search_customer_by_phone(phone)

        if not customers:
            self.ids.customers_table.row_data = [("לא נמצאו תוצאות", "")]
        else:
            self.ids.customers_table.row_data = [(c["name"], c["phone"]) for c in customers]
