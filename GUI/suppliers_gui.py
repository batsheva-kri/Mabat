# import tkinter as tk
# from tkinter import ttk, messagebox, simpledialog
#
# from GUI.styles import setup_style
# from logic.suppliers import (
#     add_supplier, get_supplier_by_id, update_supplier, delete_supplier,
#     get_open_supplier_invitations, get_closed_unsupplied_invitations,
#     get_supplier_monthly_report, get_all_suppliers,
#     get_supplier_catalog, get_suppliers_catalog_by_supplier_id,
#     add_supplier_catalog_entry, update_supplier_catalog_entry, delete_supplier_catalog_entry
# )
#
# class SupplierApp(ttk.Frame):
#     def __init__(self, root):
#         super().__init__(root)
#         self.root = root
#         self.root.title("📦 מערכת ניהול ספקים והזמנות")
#         screen_width = self.root.winfo_screenwidth()
#         screen_height = self.root.winfo_screenheight()
#         width = int(screen_width * 0.75)
#         height = int(screen_height * 0.75)
#         self.root.geometry(f"{width}x{height}")
#
#         self.root.configure(background="#fff0f6")
#         setup_style()
#
#         self.pack(fill="both", expand=True)
#         self.create_widgets()
#
#     def create_widgets(self):
#         buttons_frame = ttk.Frame(self, style="TFrame")
#         buttons_frame.pack(pady=20, padx=10)
#
#         ttk.Button(buttons_frame, text="➕ הוספת ספק", style="TButton", command=self.open_add_supplier_form).grid(row=0, column=0, padx=10, pady=10)
#         ttk.Button(buttons_frame, text="🔍 חיפוש ועריכת ספק", style="TButton", command=self.show_suppliers_list_window).grid(row=0, column=1, padx=10, pady=10)
#         ttk.Button(buttons_frame, text="🗑 מחיקת ספק", style="TButton", command=self.open_delete_supplier).grid(row=0, column=2, padx=10, pady=10)
#         ttk.Button(buttons_frame, text="📂 הזמנות פתוחות", style="TButton", command=self.show_open_invitations_by_supplier).grid(row=1, column=0, padx=10, pady=10)
#         ttk.Button(buttons_frame, text="📦 הזמנות סגורות שלא סופקו", style="TButton", command=self.show_closed_unsupplied_invitations_by_supplier).grid(row=1, column=1, padx=10, pady=10)
#         ttk.Button(
#             buttons_frame,
#             text="📊 דוח חודשי",
#             style="TButton",
#             command=self.open_monthly_report_selector
#         ).grid(row=1, column=2, padx=10, pady=10)
#
#         ttk.Button(buttons_frame, text="💲 מחירון ספקים", style="TButton", command=self.show_supplier_catalog_window).grid(row=2, column=0, padx=10, pady=10)
#
#     def open_add_supplier_form(self):
#         win = tk.Toplevel(self.root)
#         win.title("➕ הוספת ספק")
#         win.geometry("400x300")
#         win.configure(bg="#fff0f6")
#
#         ttk.Label(win, text="שם ספק:", style="TLabel").pack(pady=5)
#         name_entry = ttk.Entry(win, justify="right", style="TEntry")
#         name_entry.pack(pady=5)
#
#         ttk.Label(win, text="טלפון:", style="TLabel").pack(pady=5)
#         phone_entry = ttk.Entry(win, justify="right", style="TEntry")
#         phone_entry.pack(pady=5)
#
#         ttk.Label(win, text="אימייל:", style="TLabel").pack(pady=5)
#         email_entry = ttk.Entry(win, justify="right", style="TEntry")
#         email_entry.pack(pady=5)
#
#         def save_supplier():
#             add_supplier({
#                 "name": name_entry.get(),
#                 "phone": phone_entry.get(),
#                 "email": email_entry.get()
#             })
#             messagebox.showinfo("הצלחה", "✅ הספק נוסף בהצלחה")
#             win.destroy()
#
#         ttk.Button(win, text="💾 שמור", style="Accent.TButton", command=save_supplier).pack(pady=10)
#
#     def show_suppliers_list_window(self):
#         win = tk.Toplevel(self.root)
#         win.title("רשימת ספקים")
#         win.geometry("600x400")
#         win.configure(bg="#fff0f6")
#
#         suppliers = get_all_suppliers()
#
#         columns = ("id", "name", "phone", "email")
#         tree = ttk.Treeview(win, columns=columns, show="headings", style="Treeview")
#         for col in columns:
#             tree.heading(col, text=col)
#             tree.column(col, width=120, anchor="center")
#
#         for s in suppliers:
#             tree.insert("", tk.END, values=(s["id"], s["name"], s.get("phone", ""), s.get("email", "")))
#
#         tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
#
#         def edit_selected_supplier():
#             selected = tree.selection()
#             if not selected:
#                 messagebox.showwarning("⚠ שגיאה", "יש לבחור ספק מהרשימה")
#                 return
#             item = tree.item(selected[0])
#             supplier_id = item["values"][0]
#             supplier = get_supplier_by_id(supplier_id)
#             if supplier:
#                 self.edit_supplier_form(supplier)
#             else:
#                 messagebox.showerror("שגיאה", "הספק לא נמצא")
#
#         btn_frame = ttk.Frame(win, style="TFrame")
#         btn_frame.pack(pady=10)
#
#         ttk.Button(btn_frame, text="✏️ ערוך ספק נבחר", style="Accent.TButton", command=edit_selected_supplier).pack()
#
#     def edit_supplier_form(self, supplier):
#         win = tk.Toplevel(self.root)
#         win.title("✏ עריכת ספק")
#         win.geometry("400x300")
#         win.configure(bg="#fff0f6")
#
#         ttk.Label(win, text="שם ספק:", style="TLabel").pack(pady=5)
#         name_entry = ttk.Entry(win, justify="right", style="TEntry")
#         name_entry.insert(0, supplier["name"])
#         name_entry.pack(pady=5)
#
#         ttk.Label(win, text="טלפון:", style="TLabel").pack(pady=5)
#         phone_entry = ttk.Entry(win, justify="right", style="TEntry")
#         phone_entry.insert(0, supplier.get("phone", ""))
#         phone_entry.pack(pady=5)
#
#         ttk.Label(win, text="אימייל:", style="TLabel").pack(pady=5)
#         email_entry = ttk.Entry(win, justify="right", style="TEntry")
#         email_entry.insert(0, supplier.get("email", ""))
#         email_entry.pack(pady=5)
#
#         def save_changes():
#             update_supplier(supplier["id"], {
#                 "name": name_entry.get(),
#                 "phone": phone_entry.get(),
#                 "email": email_entry.get()
#             })
#             messagebox.showinfo("הצלחה", "✅ הספק עודכן בהצלחה")
#             win.destroy()
#
#         ttk.Button(win, text="💾 שמור שינויים", style="Accent.TButton", command=save_changes).pack(pady=10)
#
#     def open_delete_supplier(self):
#         win = tk.Toplevel(self.root)
#         win.title("🗑 מחיקת ספק")
#         win.geometry("600x400")
#         win.configure(bg="#fff0f6")
#
#         suppliers = get_all_suppliers()
#         if not suppliers:
#             messagebox.showinfo("מידע", "אין ספקים ברשימה")
#             win.destroy()
#             return
#
#         columns = ("id", "name", "phone", "email")
#         tree = ttk.Treeview(win, columns=columns, show="headings", style="Treeview")
#         for col in columns:
#             tree.heading(col, text=col)
#             tree.column(col, width=120, anchor="center")
#
#         for s in suppliers:
#             tree.insert("", tk.END, values=(s["id"], s["name"], s.get("phone", ""), s.get("email", "")))
#
#         tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
#
#         def delete_selected_supplier():
#             selected = tree.selection()
#             if not selected:
#                 messagebox.showwarning("⚠ שגיאה", "יש לבחור ספק מהרשימה")
#                 return
#             item = tree.item(selected[0])
#             supplier_id = item["values"][0]
#             supplier_name = item["values"][1]
#
#             confirm = messagebox.askyesno("אישור מחיקה", f"האם אתה בטוח שברצונך למחוק את הספק '{supplier_name}'?")
#             if confirm:
#                 delete_supplier(supplier_id)
#                 messagebox.showinfo("הצלחה", f"🗑️ הספק '{supplier_name}' נמחק בהצלחה")
#                 tree.delete(selected[0])  # מסיר מה־Treeview
#
#         ttk.Button(win, text="🗑 מחק ספק נבחר", style="Accent.TButton", command=delete_selected_supplier).pack(pady=10)
#
#     def show_open_invitations_by_supplier(self):
#         def load_invitations(supplier_id):
#             invitations = get_open_supplier_invitations(supplier_id)
#             if not invitations:
#                 messagebox.showinfo("מידע", "אין הזמנות פתוחות לספק זה")
#                 return
#             self.show_list_window(f"📂 הזמנות פתוחות לספק {supplier_id}", invitations)
#
#         self.select_supplier_and_run(load_invitations)
#
#     def show_closed_unsupplied_invitations_by_supplier(self):
#         def load_invitations(supplier_id):
#             invitations = get_closed_unsupplied_invitations(supplier_id)
#             if not invitations:
#                 messagebox.showinfo("מידע", "אין הזמנות סגורות שלא סופקו לספק זה")
#                 return
#             self.show_list_window(f"📦 הזמנות סגורות שלא סופקו לספק {supplier_id}", invitations)
#
#         self.select_supplier_and_run(load_invitations)
#
#     def show_monthly_report_window(self, supplier_id, year, month):
#         # שליפה מהדאטה
#         rows = get_supplier_monthly_report(supplier_id, year, month)
#
#         # חלון חדש
#         report_window = tk.Toplevel(self.master)
#         report_window.title("דו\"ח חודשי")
#
#         # טבלה
#         columns = ("date", "product_name", "quantity", "total")
#         tree = ttk.Treeview(report_window, columns=columns, show="headings")
#
#         # כותרות בעברית
#         tree.heading("date", text="תאריך")
#         tree.heading("product_name", text="שם מוצר")
#         tree.heading("quantity", text="כמות")
#         tree.heading("total", text="סה\"כ")
#
#         # יישור לימין
#         tree.column("date", anchor="e", width=100)
#         tree.column("product_name", anchor="e", width=150)
#         tree.column("quantity", anchor="e", width=80)
#         tree.column("total", anchor="e", width=100)
#
#         # הכנסת נתונים לטבלה
#         for row in rows:
#             tree.insert(
#                 "", tk.END,
#                 values=(row["date"], row["product_name"], row["quantity"], row["total"])
#             )
#
#         # הוספת סיכום חודשי
#         total_sum = sum(row["total"] for row in rows)
#         tree.insert("", tk.END, values=("", "", "סה\"כ חודשי", total_sum))
#
#         tree.pack(fill=tk.BOTH, expand=True)
#
#     def select_supplier_and_run(self, callback):
#         win = tk.Toplevel(self.root)
#         win.title("בחר ספק")
#         win.geometry("400x150")
#         win.configure(bg="#fff0f6")
#
#         suppliers = get_all_suppliers()
#         supplier_names = [f'{s["name"]} (ID:{s["id"]})' for s in suppliers]
#
#         ttk.Label(win, text="בחר ספק:", style="TLabel").pack(pady=10)
#         supplier_cb = ttk.Combobox(win, values=supplier_names, state="readonly", width=30)
#         supplier_cb.pack(pady=5)
#
#         def on_select():
#             selected_index = supplier_cb.current()
#             if selected_index == -1:
#                 messagebox.showwarning("⚠ שגיאה", "יש לבחור ספק")
#                 return
#             supplier_id = suppliers[selected_index]["id"]
#             win.destroy()
#             callback(supplier_id)
#
#         ttk.Button(win, text="בחר", style="Accent.TButton", command=on_select).pack(pady=10)
#
#     def show_list_window(self, title, data):
#         win = tk.Toplevel(self.root)
#         win.title(title)
#         win.geometry("800x400")
#         win.configure(bg="#fff0f6")
#
#         tree = ttk.Treeview(win, columns=list(data[0].keys()), show="headings", style="Treeview")
#         for col in data[0].keys():
#             tree.heading(col, text=col)
#             tree.column(col, width=120, anchor="center")
#
#         for row in data:
#             tree.insert("", tk.END, values=list(row.values()))
#
#         tree.pack(fill=tk.BOTH, expand=True)
#
#     def show_supplier_catalog_window(self):
#         win = tk.Toplevel(self.root)
#         win.title("💲 מחירון ספקים")
#         win.geometry("900x500")
#         win.configure(bg="#fff0f6")
#
#         suppliers = get_all_suppliers()
#         supplier_names = [f'{s["name"]} (ID:{s["id"]})' for s in suppliers]
#         supplier_names.insert(0, "כל הספקים")
#
#         ttk.Label(win, text="בחר ספק:", style="TLabel").pack(pady=10)
#         supplier_cb = ttk.Combobox(win, values=supplier_names, state="readonly", width=40)
#         supplier_cb.pack(pady=5)
#         supplier_cb.current(0)
#
#         frame = ttk.Frame(win)
#         frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
#
#         tree = ttk.Treeview(frame)
#         tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
#
#         scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
#         tree.configure(yscrollcommand=scrollbar.set)
#         scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
#
#         def refresh_catalog():
#             selected_index = supplier_cb.current()
#             if selected_index == 0:
#                 self.show_full_catalog(tree)
#             else:
#                 supplier_id = suppliers[selected_index - 1]["id"]
#                 self.show_single_supplier_catalog(tree, supplier_id, win)
#
#         btn_frame = ttk.Frame(win)
#         btn_frame.pack(pady=5)
#
#         ttk.Button(btn_frame, text="➕ הוסף מוצר", style="Accent.TButton",
#                    command=lambda: self.open_add_catalog_entry_form(win, refresh_catalog)).pack(side=tk.LEFT, padx=10)
#         ttk.Button(btn_frame, text="🔄 טען מחירון", style="Accent.TButton", command=refresh_catalog).pack(side=tk.LEFT, padx=10)
#
#         refresh_catalog()
#
#     def open_add_catalog_entry_form(self, parent, refresh_callback):
#         win = tk.Toplevel(parent)
#         win.title("➕ הוספת מוצר למחירון")
#         win.geometry("400x300")
#         win.configure(bg="#fff0f6")
#
#         suppliers = get_all_suppliers()
#         supplier_names = [f'{s["name"]} (ID:{s["id"]})' for s in suppliers]
#
#         ttk.Label(win, text="בחר ספק:", style="TLabel").pack(pady=5)
#         supplier_cb = ttk.Combobox(win, values=supplier_names, state="readonly")
#         supplier_cb.pack(pady=5)
#         supplier_cb.current(0)
#
#         ttk.Label(win, text="קוד מוצר:", style="TLabel").pack(pady=5)
#         product_entry = ttk.Entry(win, justify="right", style="TEntry")
#         product_entry.pack(pady=5)
#
#         ttk.Label(win, text="מחיר:", style="TLabel").pack(pady=5)
#         price_entry = ttk.Entry(win, justify="right", style="TEntry")
#         price_entry.pack(pady=5)
#
#         def save_entry():
#             selected_index = supplier_cb.current()
#             if selected_index == -1:
#                 messagebox.showerror("שגיאה", "יש לבחור ספק")
#                 return
#
#             supplier_id = suppliers[selected_index]["id"]
#             product_id = product_entry.get().strip()
#             try:
#                 price = float(price_entry.get())
#             except ValueError:
#                 messagebox.showerror("שגיאה", "המחיר חייב להיות מספר תקין")
#                 return
#
#             if not product_id:
#                 messagebox.showerror("שגיאה", "יש להזין קוד מוצר")
#                 return
#
#             add_supplier_catalog_entry({
#                 "supplier_id": supplier_id,
#                 "product_id": product_id,
#                 "price": price
#             })
#             messagebox.showinfo("הצלחה", "✅ המוצר נוסף למחירון")
#             win.destroy()
#             refresh_callback()
#
#         ttk.Button(win, text="💾 שמור", style="Accent.TButton", command=save_entry).pack(pady=10)
#
#     def open_edit_catalog_entry_form(self, parent, entry, refresh_callback):
#         win = tk.Toplevel(parent)
#         win.title("✏ עריכת מוצר במחירון")
#         win.geometry("400x300")
#         win.configure(bg="#fff0f6")
#
#         suppliers = get_all_suppliers()
#         supplier_names = [f'{s["name"]} (ID:{s["id"]})' for s in suppliers]
#
#         ttk.Label(win, text="בחר ספק:", style="TLabel").pack(pady=5)
#         supplier_cb = ttk.Combobox(win, values=supplier_names, state="readonly")
#         supplier_cb.pack(pady=5)
#         for i, s in enumerate(suppliers):
#             if s["id"] == entry["supplier_id"]:
#                 supplier_cb.current(i)
#                 break
#
#         ttk.Label(win, text="קוד מוצר:", style="TLabel").pack(pady=5)
#         product_entry = ttk.Entry(win, justify="right", style="TEntry")
#         product_entry.insert(0, entry["product_id"])
#         product_entry.config(state="disabled")
#         product_entry.pack(pady=5)
#
#         ttk.Label(win, text="מחיר:", style="TLabel").pack(pady=5)
#         price_entry = ttk.Entry(win, justify="right", style="TEntry")
#         price_entry.insert(0, str(entry["price"]))
#         price_entry.pack(pady=5)
#
#         def save_changes():
#             selected_index = supplier_cb.current()
#             if selected_index == -1:
#                 messagebox.showerror("שגיאה", "יש לבחור ספק")
#                 return
#
#             supplier_id = suppliers[selected_index]["id"]
#             try:
#                 price = float(price_entry.get())
#             except ValueError:
#                 messagebox.showerror("שגיאה", "המחיר חייב להיות מספר תקין")
#                 return
#
#             update_supplier_catalog_entry(supplier_id, entry["product_id"], {"price": price})
#             messagebox.showinfo("הצלחה", "✅ המוצר עודכן בהצלחה")
#             win.destroy()
#             refresh_callback()
#
#         def delete_entry():
#             answer = messagebox.askyesno("אישור", "האם למחוק את המוצר מספק זה?")
#             if answer:
#                 delete_supplier_catalog_entry(supplier_id=entry["supplier_id"], product_id=entry["product_id"])
#                 messagebox.showinfo("הצלחה", "✅ המוצר נמחק")
#                 win.destroy()
#                 refresh_callback()
#
#         ttk.Button(win, text="💾 שמור שינויים", style="Accent.TButton", command=save_changes).pack(pady=5)
#         ttk.Button(win, text="🗑️ מחק מוצר", style="Danger.TButton", command=delete_entry).pack(pady=5)
#
#     def open_monthly_report_selector(self):
#         selector_win = tk.Toplevel(self.master)
#         selector_win.title("בחירת דו\"ח חודשי")
#
#         # בחירת ספק
#         tk.Label(selector_win, text="בחר ספק:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
#         suppliers = get_all_suppliers()  # פונקציה שמחזירה רשימת ספקים מהדאטה
#         supplier_var = tk.StringVar()
#         supplier_combo = ttk.Combobox(selector_win, textvariable=supplier_var,
#                                       values=[f"{s['id']} - {s['name']}" for s in suppliers])
#         supplier_combo.grid(row=0, column=1, padx=5, pady=5)
#
#         # בחירת שנה
#         tk.Label(selector_win, text="בחר שנה:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
#         year_var = tk.StringVar()
#         year_combo = ttk.Combobox(selector_win, textvariable=year_var,
#                                   values=[str(y) for y in range(2020, 2031)])
#         year_combo.grid(row=1, column=1, padx=5, pady=5)
#
#         # בחירת חודש
#         tk.Label(selector_win, text="בחר חודש:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
#         month_var = tk.StringVar()
#         month_combo = ttk.Combobox(selector_win, textvariable=month_var,
#                                    values=[str(m) for m in range(1, 13)])
#         month_combo.grid(row=2, column=1, padx=5, pady=5)
#
#         # כפתור הפעלת הדו"ח
#         btn = tk.Button(
#             selector_win,
#             text="📊 הצג דו\"ח",
#             command=lambda: self.show_monthly_report_window(
#                 supplier_var.get().split(" - ")[0],  # מוציא את ה-id מתוך ה-combobox
#                 year_var.get(),
#                 month_var.get()
#             )
#         )
#         btn.grid(row=3, column=0, columnspan=2, pady=10)
#
#     def show_single_supplier_catalog(self, tree, supplier_id, parent_win):
#         for i in tree.get_children():
#             tree.delete(i)
#
#         tree["columns"] = ("actions", "price", "product_name", "product_id")
#         tree["show"] = "headings"
#
#         tree.heading("actions", text="פעולות")
#         tree.heading("price", text="מחיר")
#         tree.heading("product_name", text="שם מוצר")
#         tree.heading("product_id", text="קוד מוצר")
#
#         tree.column("actions", width=150, anchor="center")
#         tree.column("price", width=100, anchor="center")
#         tree.column("product_name", width=350, anchor="center")
#         tree.column("product_id", width=80, anchor="center")
#
#         data = get_suppliers_catalog_by_supplier_id(supplier_id)
#         if not data:
#             messagebox.showinfo("ℹ מידע", "לא נמצאו רשומות למחירון הספק.")
#             return
#
#         for row in data:
#             tree.insert("", tk.END, values=("ערוך | מחק", row["price"], row["product_name"], row["product_id"]))
#
#         def on_tree_click(event):
#             region = tree.identify("region", event.x, event.y)
#             if region != "cell":
#                 return
#             col = tree.identify_column(event.x)
#             row_id = tree.identify_row(event.y)
#             if not row_id:
#                 return
#
#             item = tree.item(row_id)
#             values = item["values"]
#             product_id = values[3]  # תיקון כאן: קוד מוצר בעמודה הרביעית
#
#             if col == "#1":  # עמודת פעולות היא הראשונה
#                 bbox = tree.bbox(row_id, col)
#                 if not bbox:
#                     return
#                 x_click = event.x - bbox[0]
#                 half_width = bbox[2] / 2
#                 if x_click < half_width:
#                     self.open_edit_catalog_entry_form(parent_win, {
#                         "supplier_id": supplier_id,
#                         "product_id": product_id,
#                         "price": values[1]
#                     }, refresh_callback=lambda: self.show_single_supplier_catalog(tree, supplier_id, parent_win))
#                 else:
#                     answer = messagebox.askyesno("אישור", f"האם למחוק את המוצר {product_id} מספק זה?")
#                     if answer:
#                         delete_supplier_catalog_entry(supplier_id=supplier_id, product_id=product_id)
#                         messagebox.showinfo("הצלחה", "✅ המוצר נמחק")
#                         self.show_single_supplier_catalog(tree, supplier_id, parent_win)
#
#         tree.bind("<Button-1>", on_tree_click)
#
#     def show_full_catalog(self, tree):
#         for col in tree.get_children():
#             tree.delete(col)
#         tree.delete(*tree.get_children())
#
#         catalog = get_supplier_catalog()
#
#         if not catalog:
#             messagebox.showinfo("ℹ מידע", "המחירון ריק.")
#             return
#
#         products = sorted(set(row["product_id"] for row in catalog))
#         suppliers = sorted(set(row["supplier_id"] for row in catalog))
#
#         columns = [f"ספק {sid}" for sid in suppliers] + ["שם מוצר", "קוד מוצר"]
#         tree["columns"] = columns
#         tree["show"] = "headings"
#
#         for sid in suppliers:
#             tree.heading(f"ספק {sid}", text=f"ספק {sid}")
#             tree.column(f"ספק {sid}", width=100, anchor="center")
#
#         tree.heading("שם מוצר", text="שם מוצר")
#         tree.heading("קוד מוצר", text="קוד מוצר")
#         tree.column("שם מוצר", width=250, anchor="center")
#         tree.column("קוד מוצר", width=150, anchor="center")
#
#         price_map = {}
#         product_names = {}
#         for row in catalog:
#             key = (row["product_id"], row["supplier_id"])
#             price_map[key] = row["price"]
#             product_names[row["product_id"]] = row.get("product_name", "-")
#
#         for product in products:
#             row_values = []
#             for sid in suppliers:
#                 price = price_map.get((product, sid), "-")
#                 row_values.append(price)
#             row_values.append(product_names.get(product, "-"))
#             row_values.append(product)
#             tree.insert("", tk.END, values=row_values)
#
#         tree.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = SupplierApp(root)
#     app.mainloop()
# from kivy.uix.screenmanager import Screen
# from kivymd.uix.dialog import MDDialog
# from kivymd.uix.button import MDRaisedButton
# from kivymd.uix.textfield import MDTextField
# from kivymd.uix.boxlayout import MDBoxLayout
# from kivymd.uix.label import MDLabel
#
# from logic.suppliers import (
#     add_supplier, get_all_suppliers
# )
#
#
# class SuppliersScreen(Screen):
#     dialog = None
#
#     def open_add_supplier_form(self):
#         """פותח דיאלוג להוספת ספק חדש"""
#         if not self.dialog:
#             self.name_input = MDTextField(hint_text="שם ספק", font_name="HebrewFont")
#             self.phone_input = MDTextField(hint_text="טלפון", font_name="HebrewFont")
#             self.email_input = MDTextField(hint_text="אימייל", font_name="HebrewFont")
#
#             box = MDBoxLayout(orientation="vertical", spacing=10)
#             box.add_widget(self.name_input)
#             box.add_widget(self.phone_input)
#             box.add_widget(self.email_input)
#
#             self.dialog = MDDialog(
#                 title="➕ הוספת ספק",
#                 type="custom",
#                 content_cls=box,
#                 buttons=[
#                     MDRaisedButton(
#                         text="💾 שמור",
#                         font_name="HebrewFont",
#                         on_release=self.save_supplier
#                     )
#                 ]
#             )
#         self.dialog.open()
#
#     def save_supplier(self, *args):
#         """שמירת ספק חדש"""
#         add_supplier({
#             "name": self.name_input.text,
#             "phone": self.phone_input.text,
#             "email": self.email_input.text
#         })
#         self.dialog.dismiss()
#         self.dialog = None
#         self.show_message("✅ הספק נוסף בהצלחה")
#
#     def show_message(self, text):
#         """הצגת הודעה פשוטה בדיאלוג"""
#         MDDialog(
#             title="מידע",
#             text=text,
#             buttons=[MDRaisedButton(text="סגור", on_release=lambda x: self.close_dialog(x))]
#         ).open()
#
#     def close_dialog(self, instance):
#         instance.parent.parent.dismiss()
#
#     def show_suppliers_list(self):
#         """בינתיים רק מדגים טעינת רשימת ספקים"""
#         suppliers = get_all_suppliers()
#         msg = "\n".join([f"{s['id']} - {s['name']}" for s in suppliers]) or "אין ספקים"
#         self.show_message(msg)
# supplier_app.py
# -*- coding: utf-8 -*-
from kivy.uix.screenmanager import Screen
from kivymd.uix.datatables import MDDataTable
from kivymd.app import MDApp
from kivy.metrics import dp
from kivy.clock import Clock
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from logic.suppliers import get_all_suppliers,delete_supplier


# --- מסך הוספת / עריכת ספק ---
class SupplierScreen(Screen):
    def save_supplier(self):
        # דוגמה לשמירה
        name = self.ids.name_field.text
        phone = self.ids.phone_field.text
        email = self.ids.email_field.text
        # כאן תקראי לפונקציה שמכניסה ל-DB
        print("שומר ספק:", name, phone, email)
        self.manager.current = "suppliers_list"

    def cancel(self):
        self.manager.current = "suppliers_list"


# --- מסך רשימת ספקים ---
class SuppliersListScreen(Screen):
    def on_pre_enter(self, *args):
        Clock.schedule_once(lambda dt: self.refresh_suppliers(), 0.1)

    def refresh_suppliers(self):
        suppliers = get_all_suppliers() if 'get_all_suppliers' in globals() else []
        table = MDDataTable(
            size_hint=(1, 0.8),
            use_pagination=True,
            rows_num=10,
            column_data=[
                ("ID", dp(30)),
                ("שם", dp(40)),
                ("טלפון", dp(40)),
                ("אימייל", dp(60)),
            ],
            row_data=[(s["id"], s["name"], s.get("phone",""), s.get("email","")) for s in suppliers],
        )
        self.ids.content_box.clear_widgets()
        self.ids.content_box.add_widget(table)

class DeleteSupplierScreen(Screen):
    dialog = None

    def on_pre_enter(self, *args):
        from kivy.clock import Clock
        Clock.schedule_once(lambda dt: self.refresh_suppliers(), 0.1)

    def refresh_suppliers(self):
        suppliers = get_all_suppliers()
        self.table = MDDataTable(
            size_hint=(1, 0.8),
            use_pagination=True,
            rows_num=10,
            column_data=[
                ("ID", dp(30)),
                ("שם", dp(40)),
            ],
            row_data=[(s["id"], s["name"]) for s in suppliers],
        )
        self.ids.content_box.clear_widgets()
        self.ids.content_box.add_widget(self.table)

    def delete_selected(self):
        # שליפת השורה המסומנת בטבלה
        if not self.table.get_row_checks():
            MDApp.get_running_app().toast("לא נבחר ספק")
            return

        supplier_id = self.table.get_row_checks()[0][0]  # ה־ID מתוך השורה

        # דיאלוג אישור
        if not self.dialog:
            self.dialog = MDDialog(
                title="מחיקת ספק",
                text=f"אתה בטוח שברצונך למחוק את הספק {supplier_id}?",
                buttons=[
                    MDRaisedButton(
                        text="ביטול",
                        on_release=lambda x: self.dialog.dismiss()
                    ),
                    MDRaisedButton(
                        text="מחק",
                        on_release=lambda x: self.confirm_delete(supplier_id)
                    ),
                ],
            )
        self.dialog.open()

    def confirm_delete(self, supplier_id):
        delete_supplier(supplier_id)
        self.dialog.dismiss()
        MDApp.get_running_app().toast("הספק נמחק בהצלחה")
        self.refresh_suppliers()


# --- מסך קטלוג ---
class CatalogScreen(Screen):
    def on_pre_enter(self, *args):
        Clock.schedule_once(lambda dt: self.init_catalog(), 0.1)

    def init_catalog(self):
        app = MDApp.get_running_app()
        app.show_full_catalog(self.ids.table_box)

    def add_entry(self):
        app = MDApp.get_running_app()
        app.open_add_catalog_entry_form(lambda: self.refresh())

    def refresh(self):
        self.init_catalog()

    def show_all(self):
        app = MDApp.get_running_app()
        app.show_full_catalog(self.ids.table_box)

    def pick_supplier(self):
        app = MDApp.get_running_app()
        app.select_supplier_and_run(lambda sid: app.show_single_supplier_catalog(self.ids.table_box, sid))


# --- מסך גנרי לרשימות ---
class GenericListScreen(Screen):
    def set_data(self, title, rows):
        self.ids.topbar.title = title
        table = MDDataTable(
            size_hint=(1, 0.9),
            use_pagination=True,
            rows_num=10,
            column_data=[(k, dp(80)) for k in rows[0].keys()] if rows else [],
            row_data=[tuple(str(v) for v in r.values()) for r in rows],
        )
        self.ids.table_box.clear_widgets()
        self.ids.table_box.add_widget(table)


# --- מסך בחירת דו"ח חודשי ---
class MonthlyReportSelectorScreen(Screen):
    def init_inputs(self):
        self.ids.supplier_field.text = ""
        self.supplier_id = None

    def pick_supplier(self):
        app = MDApp.get_running_app()
        app.select_supplier_and_run(lambda sid: setattr(self, "supplier_id", sid) or setattr(self.ids.supplier_field, "text", str(sid)))

    def run_report(self):
        if not getattr(self, "supplier_id", None):
            MDApp.get_running_app().toast("בחר ספק")
            return
        year = int(self.ids.year_field.text or "0")
        month = int(self.ids.month_field.text or "0")
        MDApp.get_running_app().show_monthly_report_window(self.supplier_id, year, month)


# --- מסך דו"ח חודשי ---
class MonthlyReportScreen(Screen):
    def load_report(self, rows, supplier_id, year, month):
        self.ids.topbar.title = f"דוח {month}/{year} ספק {supplier_id}"
        table = MDDataTable(
            size_hint=(1, 0.9),
            use_pagination=True,
            rows_num=10,
            column_data=[(k, dp(80)) for k in rows[0].keys()] if rows else [],
            row_data=[tuple(str(v) for v in r.values()) for r in rows],
        )
        self.ids.table_box.clear_widgets()
        self.ids.table_box.add_widget(table)