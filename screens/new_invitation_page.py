from os import close
from typing import final
import tempfile
import os
import time
import flet as ft
from logic.customers import get_customer_by_id
from logic.deliveries import add_delivery
from logic.inventory import get_all_products
from logic.orders import add_invitation_items, update_invitation, clear_invitation_items, \
    new_invitation, update_invitation_status, get_order_by_id, get_invitation_items_by_invitation_id, \
    cancel_c_invitation, delete_invitation
from logic.products import get_catalog_prices, get_product_name_by_id, get_order_total
from logic.suppliers import get_all_suppliers, create_supplier_invitations, cancel_s_invitation
from logic.users import get_all_users
import datetime
from printing import print_pdf_async
from temprint import generate_invoice_pdf

def NewInvitationPage(navigator, page, current_user, customer_id, is_new_invitation, edit, existing_invitation=None,
                      copy=False):
    print("existing_invitation", existing_invitation)
    page.snack_bar = ft.SnackBar(content=ft.Text(""), bgcolor=ft.Colors.RED)
    def show_dialog(title, message):
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[ft.TextButton("אישור", on_click=lambda e: close_dialog())],
            actions_alignment=ft.MainAxisAlignment.END
        )

        def close_dialog():
            dlg.open = False
            page.update()

        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    # --- לוגיקת סטטוס ועותק ---
    if edit and existing_invitation and existing_invitation.get("status"):
        existing_invitation["status"] = "open"
    if existing_invitation and existing_invitation.get("status") and existing_invitation["status"] != "open":
        edit = False

    if existing_invitation and not is_new_invitation and edit:
        new_inv = existing_invitation.copy()
        if copy:
            new_inv["created_by_user_id"] = int(current_user["id"]) if isinstance(current_user, dict) else None
            new_inv["date"] = datetime.datetime.now().isoformat()
            new_inv.pop("id", None)
            new_inv["status"] = "open"
            new_inv["shipped"] = 0
            new_inv["answered"] = 0
            new_inv["want_shipping"] = 0
        existing_invitation = new_inv

    # שליפת נתונים
    products = get_all_products()
    products_by_name = {p["name"].strip(): p for p in products}
    product_names = list(products_by_name.keys())
    users = get_all_users()

    if existing_invitation:
        customer = get_customer_by_id(existing_invitation["customer_id"])
    else:
        customer = get_customer_by_id(customer_id)
        if isinstance(customer, list): customer = customer[0]

    if isinstance(customer, list): customer = customer[0]
    customer_name = customer["name"]
    customer_phone = customer["phone"]

    invitation_status = existing_invitation.get("status") if existing_invitation else "open"
    is_editable_items = (invitation_status == "open")
    is_editable_checkboxes = (invitation_status == "in_shop")

    # פירוק מידות לפריטים קיימים
    if existing_invitation and existing_invitation.get("items"):
        for it in existing_invitation["items"]:
            raw_size = it.get("size", "")
            sphere, cylinder, axis = "", "", ""
            if isinstance(raw_size, str) and raw_size:
                parts = raw_size.split()
                if len(parts) >= 1: sphere = parts[0]
                if len(parts) >= 2: cylinder = parts[1]
                if len(parts) >= 3: axis = parts[2]
            it["size"], it["cyl"], it["ax"] = sphere, cylinder, axis
            product = products_by_name.get(it["product_name"])
            if product:
                prices = get_catalog_prices(product["id"], it.get("quantity", 1))
                it["unit_price"] = float(prices["unit_prices"]["price"])
                it["line_total"] = float(prices["total"])

    def refresh_page_with_new_invitation(new_inv):
        page.controls.clear()
        NewInvitationPage(navigator, page, current_user, new_inv["customer_id"], False, True, new_inv)
        page.update()

        # --- פונקציות ניווט מתוקנות ---
    def go_previous_order(e):
        if not existing_invitation or "id" not in existing_invitation: return
        current_id = existing_invitation["id"]

        prev_id = current_id - 1
        prev_inv = None

        # חיפוש אחורה עד שמוצאים הזמנה או מגיעים ל-0
        while prev_id > 0:
            prev_inv = get_order_by_id(prev_id)
            if prev_inv:
                break
            prev_id -= 1

        if not prev_inv:
            page.snack_bar.content = ft.Text("לא נמצאו הזמנות קודמות")
            page.snack_bar.open = True
            page.update()
            return

        items_fetched = get_invitation_items_by_invitation_id(prev_id)
        for item in items_fetched:
            item["product_name"] = get_product_name_by_id(item["product_id"])
        prev_inv["items"] = items_fetched
        refresh_page_with_new_invitation(prev_inv)

    def go_next_order(e):
        if not existing_invitation or "id" not in existing_invitation: return
        current_id = existing_invitation["id"]

        next_id = current_id + 1
        next_inv = None

        # חיפוש קדימה (מגבילים ל-100 קפיצות כדי לא להיתקע בלולאה אינסופית אם אין יותר הזמנות)
        for _ in range(100):
            next_inv = get_order_by_id(next_id)
            if next_inv:
                break
            next_id += 1

        if not next_inv:
            page.snack_bar.content = ft.Text("לא נמצאו הזמנות נוספות")
            page.snack_bar.open = True
            page.update()
            return

        items_fetched = get_invitation_items_by_invitation_id(next_id)
        for item in items_fetched:
            item["product_name"] = get_product_name_by_id(item["product_id"])
        next_inv["items"] = items_fetched
        refresh_page_with_new_invitation(next_inv)

    # --- צ'קבוקסים ופרטי משלוח ---
    answered_checkbox = ft.Checkbox(label="האם ענו?", value=bool(
        existing_invitation.get("answered", 0)) if existing_invitation else False, disabled=not is_editable_checkboxes)
    collected_checkbox = ft.Checkbox(label="נאסף", value=bool(
        existing_invitation.get("status") == "collected") if existing_invitation else False,
                                     disabled=not is_editable_checkboxes)
    want_shipping_checkbox = ft.Checkbox(label="משלוח?", value=bool(
        existing_invitation.get("want_shipping", 0)) if existing_invitation else False,
                                         disabled=not is_editable_checkboxes)
    shipped_checkbox = ft.Checkbox(label="נשלח?",
                                   value=bool(existing_invitation.get("shipped", 0)) if existing_invitation else False,
                                   disabled=not is_editable_checkboxes, visible=want_shipping_checkbox.value)
    delivery_name_field = ft.TextField(label="שם המקבל", width=250, value=customer_name)
    delivery_address_field = ft.TextField(label="כתובת", width=300)
    delivery_phone1_field = ft.TextField(label="טלפון 1", width=180, value=customer_phone)
    delivery_phone2_field = ft.TextField(label="טלפון 2", width=180)
    delivery_notes_field = ft.TextField(label="הערות", multiline=True, width=400)
    delivery_paid_checkbox = ft.Checkbox(label="שולם?")
    delivery_home_checkbox = ft.Checkbox(label="משלוח עד הבית?")
    delivery_date_field = ft.TextField(label="תאריך משלוח", value=datetime.datetime.now().strftime("%Y-%m-%d"))
    def create_delivery_form():
        return ft.Column([
            ft.Text("פרטי משלוח", size=18, weight="bold", color="blue"),
            ft.Row([delivery_name_field, delivery_address_field]),
            ft.Row([delivery_phone1_field, delivery_phone2_field]),
            delivery_notes_field,
            ft.Row([delivery_paid_checkbox, delivery_home_checkbox, delivery_date_field])
        ])

    delivery_details_container = ft.Container(
        visible=want_shipping_checkbox.value and (existing_invitation["shipped"] == 0 if existing_invitation else True))
    delivery_form = create_delivery_form()
    delivery_details_container.content = delivery_form

    def on_checkbox_change(e):
        if existing_invitation and existing_invitation.get("id"):
            update_invitation_status(existing_invitation["id"], call=int(answered_checkbox.value),
                                     delivery_requested=int(want_shipping_checkbox.value),
                                     delivery_sent=int(shipped_checkbox.value), collected=int(collected_checkbox.value))
            existing_invitation.update(
                {"answered": int(answered_checkbox.value), "want_shipping": int(want_shipping_checkbox.value),
                 "shipped": int(shipped_checkbox.value), "collected": int(collected_checkbox.value)})
        delivery_details_container.visible = want_shipping_checkbox.value
        shipped_checkbox.visible = want_shipping_checkbox.value
        page.update()

    answered_checkbox.on_change = on_checkbox_change
    want_shipping_checkbox.on_change = on_checkbox_change
    shipped_checkbox.on_change = on_checkbox_change
    collected_checkbox.on_change = on_checkbox_change

    # שדות נוספים
    color_field = ft.TextField(label="צבע", value=existing_invitation.get("color", "") if existing_invitation else "",
                               width=150, disabled=not is_editable_items)
    multifocal_field = ft.TextField(label="מולטיפוקל",
                                    value=existing_invitation.get("multifocal", "") if existing_invitation else "",
                                    width=150, disabled=not is_editable_items)
    notes_field = ft.TextField(label="הערות", multiline=True,
                               value=existing_invitation.get("notes", "") if existing_invitation else "")
    curvature_dropdown = ft.Dropdown(label="קימור", options=[ft.dropdown.Option(c, c) for c in
                                                             ["8.4", "8.5", "8.6", "8.7", "8.8", "8.9"]],
                                     value=str(existing_invitation.get("curvature")) if existing_invitation else None,
                                     width=120, disabled=not is_editable_items)
    prescription_dropdown = ft.Dropdown(label="סוג מרשם", options=[ft.dropdown.Option("עדשות", "עדשות"),
                                                                   ft.dropdown.Option("משקפיים", "משקפיים")],
                                        value=existing_invitation.get("prescription") if existing_invitation else None,
                                        width=150, disabled=not is_editable_items)
    user_dropdown = ft.Dropdown(label="עובד", options=[ft.dropdown.Option(str(u["id"]), u["user_name"]) for u in users],
                                width=200, disabled=not is_editable_items)

    if isinstance(current_user, dict): user_dropdown.value = str(current_user["id"])

    products_column = ft.Column(spacing=10)
    items = []
    total_var = ft.Text(f"סה\"כ: 0.00")

    def collect_current_items():
        temp_items = []
        for ctrl in products_column.controls:
            if isinstance(ctrl, ft.Column) and len(ctrl.controls) > 1 and isinstance(ctrl.controls[1], ft.Row):
                row_controls = ctrl.controls[1].controls
                name = row_controls[0].value.strip()
                if not name: continue
                try:
                    quantity = int(row_controls[1].value or 1)
                except:
                    quantity = 1
                size = f"{row_controls[2].value.strip()} {row_controls[3].value.strip()} {row_controls[4].value.strip()}"
                if name in products_by_name:
                    p = products_by_name[name]
                    prices = get_catalog_prices(p["id"], quantity)
                    print(f"row_control {row_controls}")
                    temp_items.append({"label": ctrl.controls[0].value, "product_id": p["id"], "product_name": name,
                                       "quantity": quantity, "size": size,
                                       "unit_price": float(prices["unit_prices"]["price"]),
                                       "line_total": float(prices["total"]),
                                       "supplier_id": int(row_controls[5].value) if row_controls[5].value else None,
                                       "supplied": 0})
        items.clear()
        items.extend(temp_items)
        if not items and existing_invitation and existing_invitation.get("items"): items.extend(
            existing_invitation["items"])
        return items

    def bring_discount():
        collect_current_items()
        print("I send hear")
        total_price = get_order_total(items)
        if existing_invitation is not None:
            lastPrice = existing_invitation["total_price"]
            existing_invitation["discount"] = total_price - lastPrice
            total_var.value = f"סה\"כ לאחר חבילות והנחה: {lastPrice:.2f}"
            page.update()

    bring_discount()
    discount_var = ft.TextField(label="הנחה", width=100,
                                value=str(existing_invitation.get("discount", 0) if existing_invitation else "0"))

    def recompute_total():
        collect_current_items()
        total_price = get_order_total(items)
        try:
            discount = float(discount_var.value or 0)
        except:
            discount = 0
        final_total = max(total_price - discount, 0)
        if existing_invitation is not None: existing_invitation["discount"] = total_price - discount
        total_var.value = f"סה\"כ לאחר חבילות והנחה: {final_total:.2f}"
        page.update()

    discount_var.on_change = lambda e: recompute_total()

    # --- טבלת פריטים שסופקו ---
    items_list = ft.DataTable(
        columns=[ft.DataColumn(ft.Text("תיאור")), ft.DataColumn(ft.Text("שם מוצר")), ft.DataColumn(ft.Text("כמות")),
                 ft.DataColumn(ft.Text("מידה")), ft.DataColumn(ft.Text("מחיר יח'")), ft.DataColumn(ft.Text("סה\"כ")),
                 ft.DataColumn(ft.Text("סופק"))])

    def create_product_row(label: str, initial_item=None, readonly=False):
        if initial_item is None: initial_item = {}
        if "row_id" not in initial_item: initial_item["row_id"] = len(items)

        name_var = ft.TextField(label="מוצר", width=250, value=initial_item.get("product_name", ""), disabled=readonly)
        quantity_var = ft.TextField(label="כמות", width=80, value=str(initial_item.get("quantity", 1)),
                                    disabled=readonly)
        size_var = ft.TextField(label="מידה", width=80, value=initial_item.get("size", ""), text_align="right",
                                disabled=readonly)
        cyl_var = ft.TextField(label="צילינדר", width=80, value=initial_item.get("cyl", ""), text_align="right",
                               disabled=readonly)
        ax_var = ft.TextField(label="זווית", width=80, value=initial_item.get("ax", ""), text_align="right",
                              disabled=readonly)
        suggestions_list = ft.Column()
        supplier_var = ft.Dropdown(width=200, disabled=readonly)
        price_text = ft.Text("מחיר יח': 0.00 | סה\"כ: 0.00")

        def update_supplier_dropdown(product_id=None):
            suppliers = get_all_suppliers()
            supplier_var.options = [ft.dropdown.Option(str(s["id"]), s["name"]) for s in suppliers]
            if initial_item.get("supplier_id"):
                supplier_var.value = str(initial_item["supplier_id"])
            elif product_id:
                pref = products_by_name.get(name_var.value, {}).get("preferred_supplier_id")
                if pref: supplier_var.value = str(pref)
            page.update()

        if initial_item: update_supplier_dropdown(initial_item.get("product_id"))

        def update_price(e=None):
            name = name_var.value.strip()
            qty = int(quantity_var.value or 1)
            if name in products_by_name:
                p = products_by_name[name]
                prices = get_catalog_prices(p["id"], qty)
                price_text.value = f"מחיר יח': {prices['unit_prices']['price']:.2f} | סה\"כ: {prices['total']:.2f}"
            recompute_total()
            refresh_items_table()

        name_var.on_change = lambda e: (
            suggestions_list.controls.clear(),
            [suggestions_list.controls.append(ft.TextButton(text=m, on_click=lambda _, v=m: (
            setattr(name_var, 'value', v), suggestions_list.controls.clear(),
            update_supplier_dropdown(products_by_name[v]["id"]), update_price(), page.update())))
             for m in product_names if name_var.value.lower() in m.lower()][:5] if name_var.value else None,
            update_price(), page.update()
        )
        for v in [quantity_var, size_var, cyl_var, ax_var]: v.on_change = update_price

        return ft.Column([ft.Text(label, weight="bold"),
                          ft.Row([name_var, quantity_var, size_var, cyl_var, ax_var, supplier_var], spacing=10),
                          suggestions_list, price_text])

    def refresh_items_table():
        # איסוף הנתונים המעודכנים מהשדות במסך
        current_items = collect_current_items()
        items_list.rows.clear()

        for i, it in enumerate(current_items):
            supplied_display = "✔️" if it.get("supplied") == it.get(
                "quantity") else f"{it.get('supplied', 0)} מתוך {it.get('quantity', 0)}"

            items_list.rows.append(ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(it.get("label", ""))),
                    ft.DataCell(ft.Text(it.get("product_name", ""))),
                    ft.DataCell(ft.Text(str(it.get("quantity", 0)))),
                    ft.DataCell(ft.Text(it.get("size", ""))),
                    ft.DataCell(ft.Text(f"{it.get('unit_price', 0):.2f}")),
                    ft.DataCell(ft.Text(f"{it.get('line_total', 0):.2f}")),
                    ft.DataCell(ft.Text(supplied_display))
                ]
            ))
        page.update()

    # טעינת פריטים קיימים ל-DataTable ולעריכה
    if existing_invitation:
        items_list.rows.clear()
        items.clear()
        for i, it in enumerate(existing_invitation.get("items", [])):
            it["row_id"] = i
            items.append(it)
            supplied_display = "✔️" if it.get("supplied") == it.get(
                "quantity") else f"{it.get('supplied', 0)} מתוך {it.get('quantity', 0)}"
            items_list.rows.append(ft.DataRow(
                cells=[ft.DataCell(ft.Text(it.get("label", ""))), ft.DataCell(ft.Text(it.get("product_name", ""))),
                       ft.DataCell(ft.Text(str(it.get("quantity", 0)))),
                       ft.DataCell(ft.Text(f"{it.get('size', '')} {it.get('cyl', '')} {it.get('ax', '')}")),
                       ft.DataCell(ft.Text(f"{it.get('unit_price', 0):.2f}")),
                       ft.DataCell(ft.Text(f"{it.get('line_total', 0):.2f}")), ft.DataCell(ft.Text(supplied_display))]))
            if is_editable_items:
                products_column.controls.append(create_product_row(it.get("label") or f"מוצר {i + 1}", initial_item=it,
                                                                   readonly=not is_editable_items))
        recompute_total()
    else:
        products_column.controls.extend([create_product_row("עין ימין"), create_product_row("עין שמאל")])

        # --- פונקציית השמירה המלאה ---
    def save_invitation(close=True, old=False, event=None):
        if event and event.control:
            event.control.disabled = True
            page.update()

        if not user_dropdown.value:
            show_dialog("שגיאה", "חובה לבחור עובד!")
            if event and event.control:
                event.control.disabled = False
                page.update()
            return

        if is_editable_items:
            collect_current_items()

        # --- בדיקה שכל הפריטים כוללים ספק ---
        for item in items:
            if item.get("supplier_id") is None:
                show_dialog("חסר נתון", f"חובה לבחור ספק עבור המוצר: {item.get('product_name', 'לא ידוע')}")
                if event and event.control:
                    event.control.disabled = False
                    page.update()
                return
        # ------------------------------------

        subtotal = sum(i.get('line_total', 0) for i in items)
        discount = float(discount_var.value or 0)
        total_price = max(subtotal - discount, 0)

        header = {
            "customer_id": customer_id,
            "created_by_user_id": int(user_dropdown.value),
            "date_": datetime.datetime.now().isoformat(),
            "notes": notes_field.value or "",
            "total_price": total_price,
            "status": "old" if old else ("invented" if close else "open"),
            "call": 1 if answered_checkbox.value else 0,
            "want_shipping": want_shipping_checkbox.value,
            "shipped": shipped_checkbox.value,
            "curvature": curvature_dropdown.value,
            "prescription": prescription_dropdown.value,
            "discount": discount,
            "color": color_field.value,
            "multifocal": multifocal_field.value
        }

        try:
            print("existing_invitation",existing_invitation)
            if existing_invitation and not close:
                if old:
                    for i in items: i["supplied"] = i["quantity"]
                print("items bhjyh", items)
                inv_id = existing_invitation["id"]
                update_invitation(inv_id, header)
                if is_editable_items:
                    clear_invitation_items(inv_id)
                    add_invitation_items(inv_id, items)
            else:
                if old:
                    for i in items: i["supplied"] = i["quantity"]
                print("items", items)
                invitation_id = new_invitation(header, items)
                if close and is_editable_items:
                    create_supplier_invitations(invitation_id, items)
            navigator.go_home(current_user)
        except Exception as ex:
            if event and event.control:
                event.control.disabled = False
                page.update()
            show_dialog("שגיאה", str(ex))

    def print_invitation():
        if not existing_invitation or not existing_invitation.get("id"):
            show_dialog("שגיאה", "יש לשמור את ההזמנה לפני ההדפסה!")
            return

        # חילוץ נתונים בסיסיים
        inv_id = existing_invitation["id"]
        total_price = existing_invitation.get('total_price', 0)
        delivery_data = {}

        # טיפול בלוגיקת משלוח
        if want_shipping_checkbox.value:
            # שליפה בטוחה מהמשתנים הישירים
            d_name = delivery_name_field.value.strip() or customer_name
            d_address = delivery_address_field.value.strip()
            d_phone1 = delivery_phone1_field.value.strip()
            d_phone2 = delivery_phone2_field.value.strip()
            d_notes = delivery_notes_field.value.strip()
            is_paid = delivery_paid_checkbox.value
            is_home = delivery_home_checkbox.value

            # בדיקת חובה: כתובת וטלפון
            if not d_address or not d_phone1:
                show_dialog("פרטים חסרים", "עבור משלוח חובה להזין כתובת וטלפון!")
                return

            try:
                # שמירה לטבלת deliveries
                add_delivery(
                    name=d_name,
                    address=d_address,
                    phone1=d_phone1,
                    phone2=d_phone2 if d_phone2 else None,
                    cash=is_paid,
                    cash_amount=total_price,
                    home_delivery=is_home,
                    created_by_user_id=int(user_dropdown.value or current_user["id"]),
                    notes=d_notes
                )

                # עדכון אובייקט מקומי לטובת ה-PDF
                delivery_data = {
                    "name": d_name,
                    "address": d_address,
                    "phone1": d_phone1,
                    "phone2": d_phone2,
                    "notes": d_notes,
                    "paid": is_paid,
                    "home_delivery": is_home,
                    "created_at": datetime.datetime.now().strftime("%d/%m/%Y")
                }

                # עדכון סטטוס בתוך האובייקט הקיים
                existing_invitation["want_shipping"] = 1
                existing_invitation["shipped"] = 1
                existing_invitation["status"] = "collected"  # נחשב כנאסף ברגע שיצא למשלוח

            except Exception as e:
                print(f"Error saving delivery: {e}")
                show_dialog("שגיאה בשמירת משלוח", str(e))
                return

        # עדכון סטטוס ההזמנה ב-DB (גם אם אין משלוח)
        try:
            update_invitation_status(
                invitation_id=inv_id,
                call=int(answered_checkbox.value),
                delivery_requested=int(existing_invitation.get("want_shipping", 0)),
                delivery_sent=int(existing_invitation.get("shipped", 0)),
                collected=1 if existing_invitation.get("status") == "collected" else 0
            )
        except Exception as e:
            print(f"Error updating status: {e}")
        # 3. בניית שם הקובץ והנתיב המלא שלו
        inv_id = existing_invitation.get('id', 'temp')
        # 4. קריאה לפונקציית יצירת ה-PDF עם הנתיב המלא
        try:
            # 1. יצירת נתיב לקובץ זמני (הוא נשמר בתיקיית ה-Temp של Windows)
            # הקובץ לא נמחק אוטומטית עדיין, אנחנו רק מקבלים נתיב בטוח לכתיבה
            temp_dir = tempfile.gettempdir()
            file_name = f"inv_temp_{inv_id}.pdf"
            full_pdf_path = os.path.join(temp_dir, file_name)

            # 2. יצירת ה-PDF בנתיב הזמני
            pdf_file = generate_invoice_pdf(
                customer_name=customer_name,
                customer_phone=customer_phone,
                total_discount=float(discount_var.value or 0),
                existing_invitation=existing_invitation,
                output_file=full_pdf_path,
                created_by_user_name=current_user["user_name"] if isinstance(current_user, dict) else "User",
                delivery_data=delivery_data
            )

            # 3. שליחה להדפסה
            print_pdf_async(full_pdf_path)

            # 4. מחיקת הקובץ לאחר השהיה קלה
            # אנחנו צריכים לתת למערכת זמן לשלוח את הקובץ לתור ההדפסה לפני שמוחקים
            def delete_after_delay(path, delay=10):
                time.sleep(delay)
                try:
                    if os.path.exists(path):
                        os.remove(path)
                        print(f"Temporary file deleted: {path}")
                except Exception as e:
                    print(f"Error deleting temp file: {e}")

            import threading
            threading.Thread(target=delete_after_delay, args=(full_pdf_path,), daemon=True).start()

            # הצגת הודעה למשתמש
            page.snack_bar.content = ft.Text("ההדפסה נשלחה בהצלחה!")
            page.snack_bar.bgcolor = ft.Colors.GREEN
            page.snack_bar.open = True
            page.update()

            navigator.go_home(current_user)

        except Exception as e:
            print("error message:", e)
            show_dialog("שגיאה", f"שגיאה בתהליך ההדפסה: {e}")
    def delete_the_invitation():
        if not existing_invitation or not existing_invitation.get('id'):
            return

        def handle_confirm_delete(e):
            # מחיקה וניווט
            delete_invitation(existing_invitation.get('id'))
            dlg.open = False
            page.update()
            navigator.go_home(current_user)

        def handle_cancel(e):
            dlg.open = False
            page.update()

        # יצירת דיאלוג אישור מותאם
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("אישור מחיקה"),
            content=ft.Text(f"האם אתה בטוח שברצונך למחוק את הזמנה {existing_invitation.get('id')}? פעולה זו אינה ניתנת לביטול."),
            actions=[
                ft.TextButton("כן, מחק", on_click=handle_confirm_delete, style=ft.ButtonStyle(color=ft.Colors.RED)),
                ft.TextButton("ביטול", on_click=handle_cancel),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.overlay.append(dlg)
        dlg.open = True
        page.update()
    date_val = datetime.datetime.now().isoformat()
    if existing_invitation:
        date_val = existing_invitation.get("date") or existing_invitation.get("date_") or date_val
    try:
        dt = datetime.datetime.fromisoformat(date_val)
        order_date, order_time = dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S")
    except:
        order_date, order_time = date_val, ""

    isClose = True
    if existing_invitation and "id" in existing_invitation and not (existing_invitation.get("status") == "open"):
        isClose = False

    page.controls.clear()
    page.add(ft.Column([
        ft.Row([
            ft.Column([ft.Row(
                [ft.Text(customer_name, size=20, weight="bold"), ft.Text(f"📞 {customer_phone}", size=18, color="blue"),
                 ft.Text(f"תאריך: {order_date}", color="green"), ft.Text(f"שעה: {order_time}", color="green")])]),
            ft.IconButton(ft.Icons.ARROW_BACK, on_click=go_previous_order),
            ft.Text("הזמנה חדשה" if not existing_invitation else f"הזמנה: {existing_invitation.get('id', '')}", size=22,
                    weight="bold"),
            ft.IconButton(ft.Icons.ARROW_FORWARD, on_click=go_next_order),
        ], alignment="spaceBetween"),
        delivery_details_container,
        ft.Row([curvature_dropdown, prescription_dropdown, multifocal_field, color_field, user_dropdown,
                ft.Row([answered_checkbox, collected_checkbox, want_shipping_checkbox, shipped_checkbox], spacing=20)],
               spacing=20),
        notes_field, products_column,
        ft.ElevatedButton("➕ הוסף מוצר נוסף", on_click=lambda _: (
        products_column.controls.append(create_product_row("מוצר נוסף")), page.update()),
                          disabled=not is_editable_items),
        items_list,
        ft.Row([discount_var, total_var], spacing=20),
        ft.Row([
            ft.ElevatedButton("🖨️ הדפסה חשבונית", on_click=lambda _: print_invitation(), bgcolor="blue", color="white"),            ft.ElevatedButton("💾 סגירת ההזמנה" if isClose else "שמירת שינויים 💾",
                              on_click=lambda e: save_invitation(close=isClose, event=e), bgcolor="#52b79a",
                              color="white"),
            ft.ElevatedButton("💾 שמירת ההזמנה פתוחה", on_click=lambda e: save_invitation(close=False, event=e),
                              bgcolor="#8ecae6", color="white", disabled=not is_editable_items),
            ft.ElevatedButton("❌ ביטול ההזמנה", on_click=lambda _: (
            cancel_c_invitation(existing_invitation["id"]), navigator.go_customer(current_user)), bgcolor="pink",
                              visible=not is_editable_items),
            ft.ElevatedButton("הזמנה ישנה⏱️", on_click=lambda e: save_invitation(close=False, old=True, event=e),
                              bgcolor="#52b69a", color="white"),
            ft.ElevatedButton("מחיקת הזמנה🆑 ️", on_click=lambda e: delete_the_invitation(),
                              bgcolor="#52b62a", color="white", visible=not is_editable_items),
            ft.ElevatedButton("חזרה⬅️", on_click=lambda _: navigator.go_customer(current_user), bgcolor="#f28c7d",
                              color="white"),
        ], spacing=10)
    ], spacing=15, scroll="auto"))
    page.update()