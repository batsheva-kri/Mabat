import flet as ft
from logic.customers import get_customer_by_id
from logic.inventory import get_all_products
from logic.orders import add_invitation_items, update_invitation, clear_invitation_items, \
    new_invitation, update_invitation_status, get_order_by_id, get_invitation_items_by_invitation_id
from logic.products import get_catalog_prices, get_product_name_by_id
from logic.suppliers import get_all_suppliers, create_supplier_invitations
from logic.users import get_all_users
import datetime
from temprint import generate_invoice_pdf

def NewInvitationPage(navigator, page, current_user, customer_id, is_new_invitation, edit, existing_invitation=None):
    page.snack_bar = ft.SnackBar(content=ft.Text(""), bgcolor=ft.Colors.RED)
    # יצירת עותק חדש אם ההזמנה קיימת אך לא פתוחה
    print("existing_invitation", existing_invitation)
    if edit and existing_invitation and existing_invitation["status"]:
        existing_invitation["status"] = "open"
    if existing_invitation and existing_invitation["status"] and existing_invitation["status"] != "open":
        edit = False
    if existing_invitation and not is_new_invitation and edit:
        new_inv = existing_invitation.copy()
        new_inv["created_by_user_id"] = int(current_user["id"]) if isinstance(current_user, dict) else None
        new_inv["date"] = datetime.datetime.now().isoformat()
        if existing_invitation.get("status") != "open":
            print("I do this")
            new_inv.pop("id", None)
            new_inv["created_by_user_id"] = int(current_user["id"]) if isinstance(current_user, dict) else None
            new_inv["date"] = datetime.datetime.now().isoformat()
            new_inv["status"] = "open"
            new_inv["shipped"] = 0
            new_inv["answered"] = 0
            new_inv["want_shipping"] = 0

        existing_invitation = new_inv

    # שליפת נתונים
    products = get_all_products()
    products_by_name = {p["name"]: p for p in products}
    product_names = list(products_by_name.keys())
    users = get_all_users()
    if existing_invitation:
        customer = get_customer_by_id(existing_invitation["customer_id"])
    else:
        customer = get_customer_by_id(customer_id)
    customer_name = customer[0]["name"]
    customer_phone = customer[0]["phone"]
    invitation_status = existing_invitation.get("status") if existing_invitation else "open"
    is_editable_items = (invitation_status == "open")
    is_editable_checkboxes = (invitation_status == "in_shop")
    if existing_invitation and existing_invitation.get("items"):
        for it in existing_invitation["items"]:
            product = products_by_name.get(it["product_name"])
            if product:
                prices = get_catalog_prices(product["id"], it.get("quantity", 1))
                it["unit_price"] = float(prices["unit_prices"]["price"])
                it["line_total"] = float(prices["total"])

    def refresh_page_with_new_invitation(new_inv):
        """טוען מחדש את הדף עם ההזמנה החדשה"""
        page.controls.clear()
        # קוראים שוב לפונקציה הראשית עם ההזמנה החדשה
        NewInvitationPage(
            navigator=navigator,
            page=page,
            current_user=current_user,
            customer_id=new_inv["customer_id"],
            is_new_invitation=False,
            edit=True,
            existing_invitation=new_inv
        )
        page.update()

    def go_previous_order(e):
        if not existing_invitation or "id" not in existing_invitation:
            return
        prev_id = existing_invitation["id"] - 1
        prev_inv = get_order_by_id(prev_id)
        if not prev_inv:
            page.snack_bar = ft.SnackBar(ft.Text(f"אין הזמנה עם ID {prev_id}"), bgcolor=ft.Colors.RED)
            page.snack_bar.open = True
            page.update()
            return

        # שליפת פריטים להזמנה החדשה
        items = get_invitation_items_by_invitation_id(prev_id)
        for item in items:
            item["product_name"] = get_product_name_by_id(item["product_id"])
        prev_inv["items"] = items
        refresh_page_with_new_invitation(prev_inv)

    def go_next_order(e):
        if not existing_invitation or "id" not in existing_invitation:
            return
        next_id = existing_invitation["id"] + 1
        next_inv = get_order_by_id(next_id)
        if not next_inv:
            page.snack_bar = ft.SnackBar(ft.Text(f"אין הזמנה עם ID {next_id}"), bgcolor=ft.Colors.RED)
            page.snack_bar.open = True
            page.update()
            return

        # שליפת פריטים להזמנה החדשה
        items = get_invitation_items_by_invitation_id(next_id)
        next_inv["items"] = items
        refresh_page_with_new_invitation(next_inv)

    # צ'קבוקסים
    answered_checkbox = ft.Checkbox(
        label="האם ענו?",
        value=bool(existing_invitation.get("answered", 0)) if existing_invitation else False,
        disabled=not is_editable_checkboxes
    )
    collected_checkbox = ft.Checkbox(
        label="נאסף",
        value=bool(existing_invitation.get("status") == "collected")if existing_invitation else False,
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
        disabled=not is_editable_checkboxes,
        visible=want_shipping_checkbox.value
    )

    # מיכל לפרטי משלוח
    def create_delivery_form():
        delivery_name = ft.TextField(label="שם המקבל", width=250 , value=customer_name)
        delivery_address = ft.TextField(label="כתובת", width=300)
        delivery_phone1 = ft.TextField(label="טלפון 1", width=180 , value=customer_phone)
        delivery_phone2 = ft.TextField(label="טלפון 2", width=180)
        delivery_notes = ft.TextField(label="הערות", multiline=True, width=400)
        delivery_paid = ft.Checkbox(label="שולם?")
        delivery_home = ft.Checkbox(label="משלוח עד הבית?")
        delivery_date = ft.TextField(label="תאריך משלוח", value=datetime.datetime.now().strftime("%Y-%m-%d"))

        return ft.Column([
            ft.Text("פרטי משלוח", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
            ft.Row([delivery_name, delivery_address]),
            ft.Row([delivery_phone1, delivery_phone2]),
            delivery_notes,
            ft.Row([delivery_paid, delivery_home, delivery_date])
        ])

    delivery_details_container = ft.Container(visible=want_shipping_checkbox.value and existing_invitation["shipped"] == 0)
    delivery_form = create_delivery_form()
    delivery_details_container.content = delivery_form

    # פונקציה לטיפול בכל שינוי בצ'קבוקסים
    def on_checkbox_change(e):
        if existing_invitation and existing_invitation.get("id"):
            # עדכון סטטוס בלבד, בלי לפגוע בפרטי ההזמנה האחרים
            update_invitation_status(
                existing_invitation["id"],
                call=int(answered_checkbox.value),
                delivery_requested=int(want_shipping_checkbox.value),
                delivery_sent=int(shipped_checkbox.value),
                collected = int(collected_checkbox.value)
            )

        delivery_details_container.visible = want_shipping_checkbox.value
        shipped_checkbox.visible = want_shipping_checkbox.value

        page.update()

    answered_checkbox.on_change = on_checkbox_change
    want_shipping_checkbox.on_change = on_checkbox_change
    shipped_checkbox.on_change = on_checkbox_change
    collected_checkbox.on_change = on_checkbox_change

    # שדות נוספים
    color_field = ft.TextField(
        label="צבע",
        value=existing_invitation.get("color", "") if existing_invitation else "",
        width=150,
        disabled=not is_editable_items
    )
    multifocal_field = ft.TextField(
        label="מולטיפוקל",
        value=existing_invitation.get("multifocal", "") if existing_invitation else "",
        width=150,
        disabled=not is_editable_items
    )
    notes_field = ft.TextField(
        label="הערות",
        multiline=True,
        value=existing_invitation.get("notes", "") if existing_invitation else "",
    )
    curvature_options = ["8.4", "8.5", "8.6", "8.7", "8.8", "8.9"]
    curvature_dropdown = ft.Dropdown(
        label="קימור",
        options=[ft.dropdown.Option(c, c) for c in curvature_options],
        value=str(existing_invitation.get("curvature")) if existing_invitation else None,
        width=120,
        disabled=not is_editable_items
    )
    prescription_dropdown = ft.Dropdown(
        label="סוג מרשם",
        options=[ft.dropdown.Option("עדשות", "עדשות"), ft.dropdown.Option("משקפיים", "משקפיים")],
        value=existing_invitation.get("prescription") if existing_invitation else None,
        width=150,
        disabled=not is_editable_items
    )
    user_dropdown = ft.Dropdown(
        label="עובד",
        options=[ft.dropdown.Option(str(u["id"]), u["user_name"]) for u in users],
        width=200,
        disabled=not is_editable_items
    )
    if isinstance(current_user, dict):
        user_dropdown.value = str(current_user["id"])
    elif isinstance(current_user, list) and len(current_user) == 1:
        user_dropdown.value = str(current_user[0]["id"])
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

    def collect_current_items():
        """אוסף את הנתונים הנוכחיים מכל השורות ב-products_column ומרכיב את רשימת items מחדש."""
        temp_items = []
        for ctrl in products_column.controls:
            if isinstance(ctrl, ft.Column) and len(ctrl.controls) > 1 and isinstance(ctrl.controls[1], ft.Row):
                # לקיחת שדות מתוך ה-Row: [name_var, quantity_var, size_var, supplier_var]
                row_controls = ctrl.controls[1].controls

                name = row_controls[0].value.strip()
                if not name:  # אם שם המוצר ריק, דלג על שורה זו
                    continue

                try:
                    quantity = int(row_controls[1].value or 1)
                except Exception:
                    quantity = 1
                size = row_controls[2].value.strip()

                if name in products_by_name:
                    product = products_by_name[name]
                    prices = get_catalog_prices(product["id"], quantity)
                    unit_price = float(prices["unit_prices"]["price"])
                    line_total = float(prices["total"])
                    supplier_id = int(row_controls[3].value) if row_controls[3].value else None

                    temp_items.append({
                        "label": ctrl.controls[0].value,  # כותרת השורה
                        "product_id": product["id"],
                        "product_name": name,
                        "quantity": quantity,
                        "size": size,
                        "unit_price": unit_price,
                        "line_total": line_total,
                        "supplier_id": supplier_id,
                        "supplied": 0  # הנחה ש-0 בזמן יצירה/עדכון טופס
                    })

        items.clear()
        items.extend(temp_items)
        if not items and existing_invitation and existing_invitation.get("items"):
            items.extend(existing_invitation["items"])
        return items

    def recompute_total():
        # הפעלת האיסוף המלא לפני החישוב
        current_items = collect_current_items()

        subtotal = sum(i.get('line_total', 0) for i in current_items)
        try:
            discount = float(discount_var.value or 0)
        except ValueError:
            discount = 0
        final_total = max(subtotal - discount, 0)
        total_var.value = f"סה\"כ: {subtotal:.2f}  |  לאחר הנחה: {final_total:.2f}"
        print("I update the total var")
        print(final_total)
        page.update()

    products_column = ft.Column(spacing=10)


    # טעינת פריטים קיימים (אם יש)
    def create_product_row(label: str, initial_item=None, readonly=False):
        if initial_item is None:
            initial_item = {}
        if "row_id" not in initial_item:
            initial_item["row_id"] = len(items)

        name_var = ft.TextField(
            label="מוצר", width=250,
            value=initial_item.get("product_name", "") if initial_item else "", disabled=readonly
        )
        quantity_var = ft.TextField(
            label="כמות", width=80,
            value=str(initial_item.get("quantity", 1)) if initial_item else "1",
            disabled=readonly
        )
        size_var = ft.TextField(
            label="מידה", width=80, value=initial_item.get("size", "") if initial_item else "",
            text_align=ft.TextAlign.RIGHT, disabled=readonly

        )
        suggestions_list = ft.Column()
        supplier_var = ft.Dropdown(width=200, options=[], value=None, disabled=readonly)
        price_text = ft.Text("מחיר יח': 0.00  | סה\"כ: 0.00")  # הצגת מחיר בשורה

        def update_supplier_dropdown(product_id=None):
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
            update_price()
            page.update()

        def update_price(e=None):
            name = name_var.value.strip()
            try:
                quantity = int(quantity_var.value or 1)
            except ValueError:
                quantity = 1
            size = size_var.value.strip()
            if name in products_by_name:
                product = products_by_name[name]
                prices = get_catalog_prices(product["id"], quantity)
                unit_price = float(prices["unit_prices"]["price"])
                line_total = float(prices["total"])
                price_text.value = f"מחיר יח': {unit_price:.2f}  | סה\"כ: {line_total:.2f}"

                # עדכון או הוספה ב-items (הלוגיקה נשארת כפי שתיקנת אותה)
                item_data = {
                    "label": label,
                    "product_name": name,
                    "quantity": quantity,
                    "size": size,
                    "unit_price": unit_price,
                    "line_total": line_total,
                    "supplier_id": None,  # יטופל בהמשך או בשמירה
                    "supplied": 0,
                    # שמירת ה-row_id לצורך עדכונים חוזרים
                    "row_id": initial_item["row_id"]
                }

                # עדכון או הוספה ב-items
                idx = initial_item["row_id"]

                # בדיקה אם האינדקס קיים: אם הוא קטן מהאורך הנוכחי של הרשימה, נאפשר עדכון.
                if idx < len(items):
                    items[idx].update(item_data)  # עדכן פריט קיים
                else:
                    # האינדקס אינו קיים (זהו פריט חדש שנוסף זה עתה ל-products_column) - יש להוסיף אותו.
                    items.append(item_data)
                    # עדכן את ה-row_id במילון ה-initial_item כך שיצביע על האינדקס החדש (במקרה של הוספת מוצר נוסף)
                    initial_item["row_id"] = len(items) - 1

            else:
                price_text.value = "מחיר יח': 0.00  | סה\"כ: 0.00"  # עדכון מחיר ל-0 אם שם המוצר לא קיים

            # 💡 הוספת הקריאה החסרה!
            recompute_total()
            page.update()

        name_var.on_change = lambda e: (update_suggestions(name_var.value), update_price())
        quantity_var.on_change = update_price

        row_container = ft.Column([
            ft.Text(label, weight=ft.FontWeight.BOLD),
            ft.Row([name_var, quantity_var, size_var, supplier_var], spacing=10),
            suggestions_list,
            price_text
        ])

        return row_container

    if existing_invitation:
        items_list.rows.clear()
        items.clear()
        for i, it in enumerate(existing_invitation.get("items", [])):
            unit_price = it.get("unit_price", it.get("price", 0))
            line_total = it.get("line_total", unit_price * it.get("quantity", 1))
            it["unit_price"] = unit_price
            it["line_total"] = line_total
            it["row_id"] = i
            items.append(it)

            # חישוב עמודת "סופק"
            supplied = it.get("supplied", 0)
            ordered = it.get("quantity", 0)
            if supplied == ordered:
                supplied_display = "✔️"
            else:
                supplied_display = f"{supplied} מתוך {ordered}"

            # בניית שורה
            items_list.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(it.get("label", ""))),
                    ft.DataCell(ft.Text(it.get("product_name", ""))),
                    ft.DataCell(ft.Text(str(it.get("quantity", 0)))),
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
        recompute_total()
    else:
        # ברירת מחדל – עין ימין ושמאל ריקות. כפתור שישתנה לטקסט עדכון רק אם existing_invitation
        right_eye_row = create_product_row("עין ימין", initial_item=None, readonly=not is_editable_items)
        left_eye_row = create_product_row("עין שמאל", initial_item=None, readonly=not is_editable_items)
        products_column.controls.extend([right_eye_row, left_eye_row])

    # כפתור להוספת מוצר נוסף — מוסתר אם ההזמנה לא ניתנת לעריכה
    def add_extra_product(e):
        new_row = create_product_row("מוצר נוסף", initial_item=None, readonly=not is_editable_items)
        products_column.controls.append(new_row)
        recompute_total()  # <-- כאן גם
        page.update()

    extra_button = ft.ElevatedButton("➕ הוסף מוצר נוסף"
                                     , on_click=add_extra_product, disabled=not is_editable_items)

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
            collect_current_items()
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
            "curvature": curvature_dropdown.value if curvature_dropdown.value else None,
            "prescription": prescription_dropdown.value if prescription_dropdown.value else None,
            "discount": float(discount_var.value or 0),
            "color": color_field.value or None,
            "multifocal": multifocal_field.value or None
        }
        if existing_invitation and existing_invitation["status"] != "open":
            invitation_id = existing_invitation["id"]
            if not edit:
                header["_date"] = existing_invitation["date"]
            update_invitation(invitation_id, header)
            # רק אם ההזמנה הייתה פתוחה נעדכן ונחליף את הפריטים
            if is_editable_items:
                clear_invitation_items(invitation_id)
                add_invitation_items(invitation_id, items)
                # ועדכן טבלה מקומית
                items_list.rows.clear()
                for i, it in enumerate(items):
                    supplied_display = "✔️" if it["supplied"] == it["quantity"] else f"{it['supplied']} מתוך {it['quantity']}"
                    items_list.rows.append(
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text(it.get("label", ""))),
                            ft.DataCell(ft.Text(it.get("product_name", ""))),
                            ft.DataCell(ft.Text(str(it.get("quantity", 0)))),
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
                        "quantity": it["quantity"]
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

        delivery_data = {}
        if want_shipping_checkbox.value:
            # קריאה לשדות מתוך delivery_form
            delivery_name = delivery_form.controls[1].controls[0].value.strip()
            delivery_address = delivery_form.controls[1].controls[1].value.strip()
            delivery_phone1 = delivery_form.controls[2].controls[0].value.strip()
            delivery_phone2 = delivery_form.controls[2].controls[1].value.strip()
            delivery_notes = delivery_form.controls[3].value.strip()
            paid = 1 if delivery_form.controls[4].controls[0].value else 0
            home_delivery = 1 if delivery_form.controls[4].controls[1].value else 0

            # שמירת משלוח במסד (רק אם כתובת וטלפון מלאים)
            if delivery_address and delivery_phone1:
                from logic.deliveries import add_delivery
                delivery_id = add_delivery(
                    name=delivery_name or customer_name,
                    address=delivery_address,
                    phone1=delivery_phone1,
                    phone2=delivery_phone2 or None,
                    paid=paid,
                    home_delivery=home_delivery,
                    created_by_user_id=int(user_dropdown.value),
                    notes=delivery_notes
                )
                update_invitation_status(
                    existing_invitation["id"],
                    delivery_sent= 1
                )
            # הכנת הנתונים להדפסה
            delivery_data = {
                "name": delivery_name,
                "address": delivery_address,
                "phone1": delivery_phone1,
                "phone2": delivery_phone2,
                "notes": delivery_notes,
                "paid": paid,
                "home_delivery": home_delivery,
                "created_at" : datetime.datetime.now().strftime("%Y-%m-%d")
            }
            existing_invitation["want_shipping"] = 1
            existing_invitation["shipped"] = 1
            existing_invitation["status"] = "collected"
        print(existing_invitation)
        update_invitation_status(invitation_id=existing_invitation["id"],
                                     delivery_requested= existing_invitation["want_shipping"],
                                     delivery_sent=existing_invitation["shipped"],
                                     collected=existing_invitation["status"])
        # קריאה ליצירת PDF
        pdf_file = generate_invoice_pdf(
            customer_name=customer_name,
            customer_phone=customer_phone,
            total_discount=float(discount_var.value or 0),
            existing_invitation=existing_invitation,
            output_file=f"{existing_invitation['id']}.pdf",
            created_by_user_name=current_user["user_name"],
            delivery_data=delivery_data
        )

        page.snack_bar = ft.SnackBar(ft.Text(f"PDF נוצר בהצלחה בשם {pdf_file}"), bgcolor=ft.Colors.GREEN)
        page.snack_bar.open = True
        page.update()
        navigator.go_home(current_user)
    saved_datetime_text = None

    def format_datetime(date_str):
        try:
            dt = datetime.datetime.fromisoformat(date_str)
            return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S")
        except Exception as e:
            print("Error parsing date:", e)
            return date_str, ""
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
    print("exs",existing_invitation)
    if existing_invitation:
        date = existing_invitation.get("date") or existing_invitation.get("date_")
        order_date, order_time = format_datetime(date)
    else:
        order_date, order_time = format_datetime(datetime.datetime.now().isoformat())
    # בסיום - כותרת, שדות הצ'קבוקסים והעמודה
    page.controls.clear()
    page.add(
        ft.Column([
            ft.Row([
                ft.Column([
                    ft.Row([
                        ft.Text(f"{customer_name}", size=20, weight=ft.FontWeight.BOLD),
                        ft.Text(f"📞 {customer_phone}", size=18, color=ft.Colors.BLUE),
                        ft.Text(f"תאריך: {order_date} ", size=20,color=ft.Colors.GREEN),
                        ft.Text(f" שעה: {order_time} ", size=20, color=ft.Colors.GREEN),
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ], alignment=ft.CrossAxisAlignment.END),
                ft.IconButton(icon=ft.Icons.ARROW_BACK, on_click=go_previous_order, tooltip="הזמנה קודמת"),
                ft.Text("הזמנה חדשה" if not existing_invitation else f"הזמנה: {existing_invitation.get('id', '')}",
                        size=22, weight=ft.FontWeight.BOLD),
                ft.IconButton(icon=ft.Icons.ARROW_FORWARD, on_click=go_next_order, tooltip="הזמנה הבאה"),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Row([answered_checkbox, collected_checkbox, want_shipping_checkbox, shipped_checkbox], spacing=20),
            delivery_details_container,
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
                ft.ElevatedButton("🖨️ הדפסה חשבונית", on_click=lambda e: print_invitation()),
                ft.ElevatedButton("💾 סגירת ההזמנה" if edit else " שמירת השינויים 💾",
                                  on_click=lambda e: save_invitation(close=True)),
                ft.ElevatedButton("💾 שמירת ההזמנה פתוחה", on_click=lambda e: save_invitation(close=False),
                                  disabled=(not is_editable_items)),
                ft.ElevatedButton("חזרה", on_click=lambda e: navigator.go_customer(current_user)),
                # כפתור חדש – חזרה להזמנות שסופקו, רק אם edit == False
                ft.ElevatedButton(
                    "📦 חזרה להזמנות שסופקו",
                    on_click=lambda e: navigator.go_invitations_supply(current_user),
                    visible=(not edit)
                )
            ], spacing=10)

        ], spacing=15)
    )
    page.update()
