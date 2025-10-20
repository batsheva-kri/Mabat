import flet as ft
from logic.customers import get_customer_by_id
from logic.inventory import get_all_products
from logic.orders import add_invitation_items, create_invitation, update_invitation, clear_invitation_items, new_invitation
from logic.products import get_catalog_prices
from logic.suppliers import get_all_suppliers, create_supplier_invitations
from logic.users import get_all_users
import datetime
from temprint import generate_invoice_pdf

def NewInvitationPage(navigator, page, current_user, customer_id,is_new_invitation, existing_invitation=None):
    page.snack_bar = ft.SnackBar(content=ft.Text(""), bgcolor=ft.Colors.RED)
    print("existing_invitation",existing_invitation)
    # אם יש הזמנה קיימת אבל היא לא במצב open -> ניצור עותק חדש לעריכה
    if existing_invitation and existing_invitation.get("status") != "open" and is_new_invitation == False:
        new_inv = existing_invitation.copy()

        # איפוס שדות
        new_inv.pop("id", None)
        new_inv["created_by_user_id"] = int(current_user["id"]) if isinstance(current_user, dict) else None
        new_inv["date"] = datetime.datetime.now().isoformat()
        new_inv["notes"] = ""   # להשאיר ריק למילוי
        new_inv["status"] = "open"
        new_inv["shipped"] = 0
        new_inv["answered"] = 0
        new_inv["want_shipping"] = 0

        # אפס supplied בכל הפריטים
        new_items = []
        for it in new_inv.get("items", []):
            it = it.copy()
            it["supplied"] = 0
            new_items.append(it)
        new_inv["items"] = new_items

        existing_invitation = new_inv
    print("existing_invitation", existing_invitation)

    # נתוני מוצרים ומשתמשים
    products = get_all_products()
    products_by_name = {p["name"]: p for p in products}
    product_names = list(products_by_name.keys())
    users = get_all_users()
    customer = get_customer_by_id(customer_id)
    print(customer)
    # פרטי לקוח
    customer_name = customer[0]["name"]
    customer_phone = customer[0]["phone"]
    invitation_status = existing_invitation.get("status") if existing_invitation else "open"
    is_editable_items = (invitation_status == "open")
    is_editable_checkboxes = (invitation_status == "in_shop")
    print(existing_invitation)
    answered_checkbox = ft.Checkbox(
        label="האם ענו?",
        value=bool(existing_invitation.get("answered", 0)) if existing_invitation else False,
        disabled=not is_editable_checkboxes
    )
    want_shipping_checkbox = ft.Checkbox(
        label="משלוח?",
        value=bool(existing_invitation.get("want_shipping", 0)) if existing_invitation else False,
        disabled=not is_editable_checkboxes
    )
    shipped_checkbox = ft.Checkbox(
        label="נשלח?",
        value=bool(existing_invitation.get("shipped", 0)) if existing_invitation else False,
        disabled=not is_editable_checkboxes
    )
    shipped_checkbox.visible = want_shipping_checkbox.value
    color_field = ft.TextField(
        label="צבע",
        value=existing_invitation.get("color", "") if existing_invitation else "",
        width=150
    )

    multifocal_field = ft.TextField(
        label="מולטיפוקל",
        value=existing_invitation.get("multifocal", "") if existing_invitation else "",
        width=150
    )

    notes_field = ft.TextField(
        label="הערות",
        multiline=True,
        value=existing_invitation.get("notes", "") if existing_invitation else "",
        disabled=not is_editable_items
    )
    def request_shipping(invitation_id):
        print(f"REQUEST SHIPPING: invitation_id={invitation_id}")
    def on_shipped_change(e):
        shipped_checkbox.visible = True
        if shipped_checkbox.value:
            inv_id = existing_invitation.get("id") if existing_invitation else None
            request_shipping(inv_id)
        page.update()
    def on_want_shipping_change(e):
        shipped_checkbox.visible = want_shipping_checkbox.value
        page.update()
    want_shipping_checkbox.on_change = lambda e: on_want_shipping_change(e)
    shipped_checkbox.on_change = lambda e: on_shipped_change(e)
    curvature_options = ["8.4", "8.5", "8.6", "8.7", "8.8", "8.9"]
    curvature_dropdown = ft.Dropdown(
        label="קימור",
        options=[ft.dropdown.Option(c, c) for c in curvature_options],
        value=str(existing_invitation.get("curvature")) if existing_invitation and existing_invitation.get("curvature") else None,
        width=120
    )
    prescription_dropdown = ft.Dropdown(
        label="סוג מרשם",
        options=[
            ft.dropdown.Option("עדשות", "עדשות"),
            ft.dropdown.Option("משקפיים", "משקפיים")
        ],
        value=existing_invitation.get("prescription") if existing_invitation and existing_invitation.get(
            "prescription") else None,
        width=150
    )
    user_dropdown = ft.Dropdown(
        label="עובד",
        options=[ft.dropdown.Option(str(u["id"]), u["user_name"]) for u in users],
        width=200
    )
    if isinstance(current_user, dict):
        user_dropdown.value = str(current_user["id"])
    elif isinstance(current_user, list):
        if len(current_user) == 1:
            user_dropdown.value = str(current_user[0]["id"])
        else:
            user_dropdown.value = None

    items = []
    total_var = ft.Text(f"סה\"כ: 0.00")
    discount_var = ft.TextField(label="הנחה", width=100, value=str(existing_invitation.get("discount", 0) if existing_invitation else "0"))

    items_list = ft.DataTable(columns=[
        ft.DataColumn(ft.Text("תיאור")),
        ft.DataColumn(ft.Text("שם מוצר")),
        ft.DataColumn(ft.Text("כמות")),
        ft.DataColumn(ft.Text("מידה")),
        ft.DataColumn(ft.Text("מחיר יח'")),
        ft.DataColumn(ft.Text("סה\"כ")),
        ft.DataColumn(ft.Text("סופק"))  # עמודה חדשה
    ])

    def recompute_total():
        subtotal = sum(i.get('line_total', 0) for i in items)
        try:
            discount = float(discount_var.value or 0)
        except ValueError:
            discount = 0
        final_total = max(subtotal - discount, 0)
        total_var.value = f"סה\"כ: {subtotal:.2f}  |  לאחר הנחה: {final_total:.2f}"
        page.update()

    products_column = ft.Column(spacing=10)

    def create_product_row(label: str, initial_item=None, readonly=False):
        name_var = ft.TextField(label="מוצר", width=250, value=initial_item.get("product_name", "") if initial_item else "", disabled=readonly)
        qty_var = ft.TextField(label="כמות", width=80, value=str(initial_item.get("qty", 1)) if initial_item else "1", disabled=readonly)
        size_var = ft.TextField(label="מידה", width=80, value=initial_item.get("size", "") if initial_item else "", text_align=ft.TextAlign.RIGHT, disabled=readonly)
        suggestions_list = ft.Column()
        supplier_var = ft.Dropdown(width=200, options=[], value=None, disabled=readonly)

        def update_supplier_dropdown(product_id):
            suppliers = get_all_suppliers()
            supplier_var.options = [ft.dropdown.Option(str(s["id"]), s["name"]) for s in suppliers]
            if initial_item and initial_item.get("supplier_id"):
                supplier_var.value = str(initial_item["supplier_id"])
            else:
                product = products_by_name.get(name_var.value)
                if product:
                    preferred_supplier_id = product.get("preferred_supplier_id")
                    if preferred_supplier_id:
                        supplier_var.value = str(preferred_supplier_id)
                    elif suppliers:
                        supplier_var.value = str(suppliers[0]["id"])
            page.update()

        if initial_item:
            update_supplier_dropdown(initial_item.get("product_id"))

        def update_suggestions(query: str):
            suggestions_list.controls.clear()
            if query:
                matches = [p for p in product_names if query.lower() in p.lower()]
                for m in matches:
                    suggestions_list.controls.append(
                        ft.TextButton(text=m, on_click=lambda e, val=m: select_product(val))
                    )
            page.update()

        def select_product(val: str):
            name_var.value = val
            suggestions_list.controls.clear()
            product = products_by_name[val]
            update_supplier_dropdown(product["id"])
            page.update()

        name_var.on_change = lambda e: update_suggestions(name_var.value)

        def add_to_items_list(e=None, edit_row_id=None):
            if not is_editable_items:
                return
            name = name_var.value.strip()
            if name not in products_by_name:
                page.snack_bar = ft.SnackBar(ft.Text("מוצר לא מוכר"))
                page.snack_bar.open = True
                page.update()
                return
            product = products_by_name[name]
            try:
                qty = int(qty_var.value or 1)
            except ValueError:
                qty = 1
            size = size_var.value.strip()
            prices = get_catalog_prices(product["id"], qty)
            unit_price = float(prices["unit_prices"]["price"])
            line_total = float(prices["total"])

            preferred_supplier_id = product.get("preferred_supplier_id")
            supplier_id = int(supplier_var.value) if supplier_var.value else preferred_supplier_id

            if supplier_id is None:
                page.snack_bar = ft.SnackBar(ft.Text("לא נבחר ספק למוצר הזה!"))
                page.snack_bar.open = True
                page.update()
                return

            new_item = {
                "label": label,
                "product_id": product["id"],
                "product_name": name,
                "qty": qty,
                "size": size,
                "unit_price": unit_price,
                "line_total": line_total,
                "supplier_id": supplier_id,
                "supplied": 0
            }

            if initial_item and "row_id" in initial_item:
                supplied = new_item.get("supplied", 0)
                ordered = new_item.get("qty", 0)
                if supplied == ordered:
                    supplied_display = "✔️"
                else:
                    supplied_display = f"{supplied} מתוך {ordered}"

                idx = initial_item["row_id"]
                items[idx] = new_item
                items_list.rows[idx] = ft.DataRow(cells=[
                    ft.DataCell(ft.Text(label)),
                    ft.DataCell(ft.Text(name)),
                    ft.DataCell(ft.Text(str(qty))),
                    ft.DataCell(ft.Text(size)),
                    ft.DataCell(ft.Text(f"{unit_price:.2f}")),
                    ft.DataCell(ft.Text(f"{line_total:.2f}")),
                    ft.DataCell(ft.Text(supplied_display))
                ])

            else:
                new_item["row_id"] = len(items)
                items.append(new_item)

                supplied = new_item.get("supplied", 0)
                ordered = new_item.get("qty", 0)
                if supplied == ordered:
                    supplied_display = "✔️"
                else:
                    supplied_display = f"{supplied} מתוך {ordered}"

                items_list.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(new_item.get("label", ""))),
                        ft.DataCell(ft.Text(new_item["product_name"])),
                        ft.DataCell(ft.Text(str(new_item["qty"]))),
                        ft.DataCell(ft.Text(new_item["size"])),
                        ft.DataCell(ft.Text(f"{new_item['unit_price']:.2f}")),
                        ft.DataCell(ft.Text(f"{new_item['line_total']:.2f}")),
                        ft.DataCell(ft.Text(supplied_display))
                    ])
                )

            recompute_total()
            page.update()

        return ft.Column([
            ft.Text(label, weight=ft.FontWeight.BOLD),
            ft.Row([name_var, qty_var, size_var, supplier_var], spacing=10),
            suggestions_list,
            ft.ElevatedButton(f"➕ {label}", on_click=add_to_items_list, disabled=readonly)
        ])

        # טקסט בכפתור משתנה לפי מצב: אם זה הזמנה קיימת - כפתור יהיה "עדכן ..."
        if existing_invitation:
            action_btn_text = label.replace("הוסף מוצר", "עדכן ") if "הוסף מוצר" in label else f"עדכן {label}"
        else:
            action_btn_text = f"➕ {label}"

        action_button = ft.ElevatedButton(action_btn_text, on_click=add_to_items_list, disabled=not is_editable_items)

        return ft.Column([
            ft.Text(label, weight=ft.FontWeight.BOLD),
            ft.Row([name_var, qty_var, size_var, supplier_var], spacing=10),
            suggestions_list,
            action_button
        ])

    # טעינת פריטים קיימים (אם יש)
    if existing_invitation:
        items_list.rows.clear()
        items.clear()
        for i, it in enumerate(existing_invitation.get("items", [])):
            unit_price = it.get("unit_price", it.get("price", 0))
            line_total = it.get("line_total", unit_price * it.get("qty", 1))
            it["unit_price"] = unit_price
            it["line_total"] = line_total
            it["row_id"] = i
            items.append(it)

            # חישוב עמודת "סופק"
            supplied = it.get("supplied", 0)
            ordered = it.get("qty", 0)
            if supplied == ordered:
                supplied_display = "✔️"
            else:
                supplied_display = f"{supplied} מתוך {ordered}"

            # בניית שורה
            items_list.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(it.get("label", ""))),
                    ft.DataCell(ft.Text(it.get("product_name", ""))),
                    ft.DataCell(ft.Text(str(it.get("qty", 0)))),
                    ft.DataCell(ft.Text(it.get("size", ""))),
                    ft.DataCell(ft.Text(f"{unit_price:.2f}")),
                    ft.DataCell(ft.Text(f"{line_total:.2f}")),
                    ft.DataCell(ft.Text(supplied_display))
                ])
            )

            # הוספת שורת עריכה
            if is_editable_items:
                label = it.get("label") or (
                    "עדכן עין ימין" if i == 0 else "עדכן עין שמאל" if i == 1 else f"עדכן מוצר {i + 1}")
                row = create_product_row(label, initial_item=it, readonly=not is_editable_items)
                products_column.controls.append(row)

    else:
        # ברירת מחדל – עין ימין ושמאל ריקות. כפתור שישתנה לטקסט עדכון רק אם existing_invitation
        right_eye_row = create_product_row("עין ימין", initial_item=None, readonly=not is_editable_items)
        left_eye_row = create_product_row("עין שמאל", initial_item=None, readonly=not is_editable_items)
        products_column.controls.extend([right_eye_row, left_eye_row])

    # כפתור להוספת מוצר נוסף — מוסתר אם ההזמנה לא ניתנת לעריכה
    def add_extra_product(e):
        new_row = create_product_row("מוצר נוסף", initial_item=None, readonly=not is_editable_items)
        products_column.controls.append(new_row)
        page.update()

    extra_button = ft.ElevatedButton("➕ הוסף מוצר נוסף", on_click=add_extra_product, disabled=not is_editable_items)

    # שמירת הזמנה
    def save_invitation(close=True):
        # בדיקה אם נבחר משתמש
        if not user_dropdown.value:
            page.snack_bar = ft.SnackBar(ft.Text("חובה לבחור מי פתח את ההזמנה!"))
            page.snack_bar.open = True
            page.update()
            return

        created_by_user_id = int(user_dropdown.value)

        # אם ההזמנה פתוחה (או זו יצירה חדשה) — בונים items מתוך products_column
        if is_editable_items:
            items.clear()
            # לקרוא את השורות מה-products_column כמו קודם
            for ctrl in products_column.controls:
                if isinstance(ctrl, ft.Column):
                    # לקיחת שדות מתוך ה-Row
                    row_controls = ctrl.controls[1].controls  # [name_var, qty_var, size_var, supplier_var]
                    name = row_controls[0].value.strip()
                    try:
                        qty = int(row_controls[1].value or 1)
                    except Exception:
                        qty = 1
                    size = row_controls[2].value.strip()
                    supplier_id = int(row_controls[3].value) if row_controls[3].value else None

                    if name in products_by_name:
                        product = products_by_name[name]
                        prices = get_catalog_prices(product["id"], qty)
                        unit_price = float(prices["unit_prices"]["price"])
                        line_total = float(prices["total"])
                        items.append({
                            "label": ctrl.controls[0].value,  # כותרת השורה
                            "product_id": product["id"],
                            "product_name": name,
                            "qty": qty,
                            "size": size,
                            "unit_price": unit_price,
                            "line_total": line_total,
                            "supplier_id": supplier_id,
                            "supplied": 0
                        })

        # חישוב סכומים
        import datetime
        subtotal = sum(i.get('line_total', 0) for i in items)
        try:
            discount = float(discount_var.value or 0)
        except ValueError:
            discount = 0
        total_price = max(subtotal - discount, 0)
        status = "invented" if close else "open"

        # הכנת header כולל השדות החדשים שביקשת לשמור
        header = {
            "customer_id": customer_id,
            "created_by_user_id": created_by_user_id,
            "date_": datetime.datetime.now().isoformat(),
            "notes": notes_field.value or "",
            "total_price": total_price,
            "status": status if is_editable_items else (existing_invitation.get("status") if existing_invitation else status),
            "call": 1 if answered_checkbox.value else 0,
            "want_shipping": want_shipping_checkbox.value,
            "shipped": shipped_checkbox.value,
            "curvature": curvature_dropdown.value,
            "prescription": prescription_dropdown.value if prescription_dropdown.value else None,
            "discount": float(discount_var.value or 0),
            "color": color_field.value or None,
            "multifocal": multifocal_field.value or None
        }
        if existing_invitation and existing_invitation["status"] != "open":
            print(status == "open")
            print(status)
            invitation_id = existing_invitation["id"]
            update_invitation(invitation_id, header)
            # רק אם ההזמנה הייתה פתוחה נעדכן ונחליף את הפריטים
            if is_editable_items:
                clear_invitation_items(invitation_id)
                add_invitation_items(invitation_id, items)
                # ועדכן טבלה מקומית
                items_list.rows.clear()
                for i, it in enumerate(items):
                    supplied_display = "✔️" if it["supplied"] == it["qty"] else f"{it['supplied']} מתוך {it['qty']}"
                    items_list.rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(it.get("label", ""))),
                            ft.DataCell(ft.Text(it.get("product_name", ""))),
                            ft.DataCell(ft.Text(str(it.get("qty", 0)))),
                            ft.DataCell(ft.Text(it.get("size", ""))),
                            ft.DataCell(ft.Text(f"{it.get('unit_price', 0):.2f}")),
                            ft.DataCell(ft.Text(f"{it.get('line_total', 0):.2f}")),
                            ft.DataCell(ft.Text(supplied_display))
                        ])
                    )
        else:
            # יצירה חדשה
            invitation_id = new_invitation(header,items)

        # אם נבחר close וזו הזמנה פתוחה/שנוצרה עכשיו - יצירת הזמנות לספקים כמו קודם
        if close and is_editable_items:
            supplier_items_map = {}
            for it in items:
                supplier_id = it.get("supplier_id") or products_by_name[it["product_name"]].get("preferred_supplier_id")
                if supplier_id not in supplier_items_map:
                    supplier_items_map[supplier_id] = []
                supplier_items_map[supplier_id].append(it)

            for supplier_id, items_list_for_supplier in supplier_items_map.items():
                items_for_fn = []
                for it in items_list_for_supplier:
                    items_for_fn.append({
                        "product_name": it["product_name"],
                        "product_id": it["product_id"],
                        "size": it["size"],
                        "qty": it["qty"]
                    })

                create_supplier_invitations(
                    supplier_id=supplier_id,
                    customer_invitation_id=invitation_id,
                    items=items_for_fn,
                    notes=""
                )

        page.snack_bar = ft.SnackBar(ft.Text("ההזמנה נשמרה בהצלחה!"))
        page.snack_bar.open = True
        page.update()
        navigator.go_home(current_user)

    def print_invitation():
        if not existing_invitation:
            page.snack_bar = ft.SnackBar(ft.Text("אין הזמנה להדפסה!"))
            page.snack_bar.open = True
            page.update()
            return

        pdf_file = generate_invoice_pdf(
            customer_name=customer_name,
            customer_phone=customer_phone,
            total_discount=float(discount_var.value or 0),
            existing_invitation=existing_invitation,
            output_file=f"{existing_invitation['id']}.pdf",
            created_by_user_name=current_user["user_name"]
        )

        page.snack_bar = ft.SnackBar(ft.Text(f"PDF נוצר בהצלחה בשם {pdf_file}"), bgcolor=ft.Colors.GREEN)
        page.snack_bar.open = True
        page.update()
        navigator.go_home(current_user)
    saved_datetime_text = None
    if existing_invitation and existing_invitation.get("date"):
        try:
            saved_dt = datetime.datetime.fromisoformat(existing_invitation["date"])
            saved_datetime_text = ft.Text(
                f"תאריך שמירה: {saved_dt.strftime('%Y-%m-%d %H:%M:%S')}",
                size=16,
                color=ft.Colors.GREY
            )
        except Exception as e:
            print("Error parsing date:", e)
    # בסיום - כותרת, שדות הצ'קבוקסים והעמודה
    page.controls.clear()
    page.add(
        ft.Column([
            ft.Row([
                ft.Column([
                    ft.Row([
                        ft.Text(f"{customer_name}", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(f"📞 {customer_phone}", size=18, color=ft.Colors.BLUE),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ], alignment=ft.CrossAxisAlignment.END),
                ft.Text("הזמנה חדשה" if not existing_invitation else f"הזמנה: {existing_invitation.get('id', '')}",
                        size=22, weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            saved_datetime_text if saved_datetime_text else ft.Container(),
            ft.Row([answered_checkbox, want_shipping_checkbox, shipped_checkbox], spacing=20),
            ft.Row([curvature_dropdown, prescription_dropdown], spacing=20),
            multifocal_field,
            color_field,
            notes_field,
            user_dropdown,
            products_column,
            extra_button,
            items_list,
            ft.Row([discount_var, total_var], spacing=20),
            ft.Row([
                ft.ElevatedButton("🖨️ הדפסה חשבונית", on_click=lambda e:print_invitation()),
                ft.ElevatedButton("💾 סגירת ההזמנה", on_click=lambda e: save_invitation(close=True)),
                ft.ElevatedButton("💾 שמירת ההזמנה פתוחה", on_click=lambda e: save_invitation(close=False), disabled=(not is_editable_items)),
                ft.ElevatedButton("חזרה", on_click=lambda e: navigator.go_customer(current_user))
            ], spacing=10)
        ], spacing=15)
    )
    page.update()
