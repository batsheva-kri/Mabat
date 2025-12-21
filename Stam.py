import flet as ft
from logic.customers import get_customer_by_id
from logic.inventory import get_all_products
from logic.orders import add_invitation_items, update_invitation, clear_invitation_items, \
    new_invitation, update_invitation_status, get_order_by_id, get_invitation_items_by_invitation_id, cancel_c_invitation
from logic.products import get_catalog_prices, get_product_name_by_id
from logic.suppliers import get_all_suppliers, create_supplier_invitations, cancel_s_invitation
from logic.users import get_all_users
import datetime
from temprint import generate_invoice_pdf

def NewInvitationPage(navigator, page, current_user, customer_id, is_new_invitation, edit, existing_invitation=None):

    if edit and existing_invitation and existing_invitation["status"]:
        existing_invitation["status"] = "open"
    if existing_invitation and existing_invitation["status"] and existing_invitation["status"] != "open":
        edit = False
    if existing_invitation and not is_new_invitation and edit:
        new_inv = existing_invitation.copy()
        new_inv["created_by_user_id"] = int(current_user["id"]) if isinstance(current_user, dict) else None
        new_inv["date"] = datetime.datetime.now().isoformat()
        if existing_invitation.get("status") != "open":
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
            raw_size = it.get("size", "")

            sphere = ""
            cylinder = ""
            axis = ""

            if isinstance(raw_size, str) and raw_size:
                parts = raw_size.split()
                if len(parts) >= 1:
                    sphere = parts[0]
                if len(parts) >= 2:
                    cylinder = parts[1]
                if len(parts) >= 3:
                    axis = parts[2]

            # שמירה בתוך הפריט:
            it["size"] = sphere
            it["cyl"] = cylinder
            it["ax"] = axis
            product = products_by_name.get(it["product_name"])
            if product:
                prices = get_catalog_prices(product["id"], it.get("quantity", 1))
                it["unit_price"] = float(prices["unit_prices"]["price"])
                it["line_total"] = float(prices["total"])

    items = []
    total_var = ft.Text(f"סה\"כ: 0.00")
    discount_var = ft.TextField(label="הנחה", width=100, value=str(existing_invitation.get("discount", 0) if existing_invitation else "0"))
    discount_var.on_change = lambda e: recompute_total()
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
                size = f"{row_controls[2].value.strip()} {row_controls[3].value.strip()} {row_controls[4].value.strip()}"

                if name in products_by_name:
                    product = products_by_name[name]
                    prices = get_catalog_prices(product["id"], quantity)
                    unit_price = float(prices["unit_prices"]["price"])
                    line_total = float(prices["total"])
                    supplier_id = int(row_controls[5].value) if row_controls[5].value else None

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
        cyl_var = ft.TextField(
            label="צילינדר", width=80, value=initial_item.get("cyl", "") if initial_item else "",
            text_align=ft.TextAlign.RIGHT, disabled=readonly

        )
        ax_var = ft.TextField(
            label="זווית", width=80, value=initial_item.get("ax", "") if initial_item else "",
            text_align=ft.TextAlign.RIGHT, disabled=readonly

        )

        suggestions_list = ft.Column()
        supplier_var = ft.Dropdown(width=200, options=[], value=None, disabled=readonly)
        price_text = ft.Text("מחיר יח': 0.00  | סה\"כ: 0.00")  # הצגת מחיר בשורה
        if initial_item:
            update_supplier_dropdown(initial_item.get("product_id"))


        def update_price(e=None):
            name = name_var.value.strip()
            try:
                quantity = int(quantity_var.value or 1)
            except ValueError:
                quantity = 1
            cyl = cyl_var.value.strip()
            ax = ax_var.value.strip()
            size1 = size_var.value.strip()
            size = f"{size1} {cyl} {ax}"
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
            ft.Row([name_var, quantity_var, size_var, cyl_var, ax_var, supplier_var], spacing=10),
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
            size = it.get("size", "") +" " + it.get("cyl", "") +" " + it.get("ax", "")
            # בניית שורה
            items_list.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(it.get("label", ""))),
                    ft.DataCell(ft.Text(it.get("product_name", ""))),
                    ft.DataCell(ft.Text(str(it.get("quantity", 0)))),
                    ft.DataCell(ft.Text(size)),
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
        if existing_invitation and close:
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

            try:
                for supplier_id, items_list_for_supplier in supplier_items_map.items():
                    items_for_fn = []
                    for it in items_list_for_supplier:
                        items_for_fn.append({
                            "product_name": it["product_name"],
                            "product_id": it["product_id"],
                            "size": it["size"],
                            "quantity": it["quantity"]
                        })
                header["status"] = "open"
                update_invitation(invitation_id, header)
                return
        page.snack_bar = ft.SnackBar(ft.Text("ההזמנה נשמרה בהצלחה!"))
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
                ft.ElevatedButton(
                    "❌ ביטול ההזמנה",
                    on_click=lambda e: cancel_invitation(),
                    visible=(not is_editable_items)
                ),
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
