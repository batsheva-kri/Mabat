from logic.convert import get_supplier_invitation
from logic.orders import get_order_by_id, get_invitation_items_by_invitation_id
from logic.products import get_product_name_by_id, get_id_by_product_name
from logic.utils import run_query
from logic.suppliers import mark_supplied, add_to_supplier_report
import flet as ft

def _to_float_safe(x):
    if x is None:
        return None
    try:
        return float(x)
    except Exception:
        try:
            return float(str(x).split()[0])
        except Exception:
            return None
def parse_size(size_str):
        if not size_str:
            return None, None, None

        parts = str(size_str).split()
        if len(parts) == 1:
            # רק Sphere
            return _to_float_safe(parts[0]), None, None

        if len(parts) == 2:
            # Sphere + Cylinder
            return _to_float_safe(parts[0]), _to_float_safe(parts[1]), None

        if len(parts) >= 3:
            # Sphere + Cylinder + Axis
            return _to_float_safe(parts[0]), _to_float_safe(parts[1]), _to_float_safe(parts[2])

def get_open_invitations():
    # שולף את כל פריטי ההזמנות הפתוחות, עם פרטי ההזמנה והלקוח, פעם אחת בלבד לכל פריט
    invitations = run_query("""
        SELECT 
            inv.id,
            ci.id as inv_item_id,
            inv.customer_id,
            ci.product_id,
            ci.size,
            si.supplier_id,
            ci.quantity - ci.supplied AS quantity_remaining,
            c.name AS customer_name,
            p.name AS product_name,
            inv.color,
            inv.multifokal,
            inv.curvature
        FROM customer_invitation_items ci
        JOIN customer_invitations inv ON ci.invitation_id = inv.id
        LEFT JOIN (
            SELECT customer_invitation_id, MIN(supplier_id) AS supplier_id
            FROM supplier_invitations
            GROUP BY customer_invitation_id
        ) si ON si.customer_invitation_id = inv.id
        JOIN customers c ON inv.customer_id = c.id
        JOIN products p ON ci.product_id = p.id
        WHERE inv.status = 'invented'
          AND ci.supplied < ci.quantity
    """, fetchall=True)

    for inv in invitations:
        sphere, cyl, axis = parse_size(inv["size"])
        inv["size"] = sphere
        inv["cylinder"] = cyl
        inv["angle"] = axis
        # אם השדות חסרים, מגדירים "-"
        inv["color"] = inv.get("color") or "-"
        inv["multifokal"] = inv.get("multifokal") or "-"
        inv["curvature"] = inv.get("curvature") or "-"

    return invitations
def handle_supplied_item(page,
                         invitation_id,
                         quantity,
                         customer_invitation_item_id,
                         supplier_id,
                         product_name,
                         quantity_var=None,
                         leftover=None,
                         size=None,
                         cylinder=None,
                         angle=None,
                         color=None,
                         multifocal=None,
                         curvature=None):
    """
    כשמוצר סופק ע"י ספק:
    - מסמן את המוצר כסופק עד לכמות שנותרה
    - אם הכמות שהוזנה גבוהה, מפיק leftover ומעדכן את תיבת הכמות
    - מציג דיאלוג אזהרה במקום print
    - רק לאחר שכל העודפים הוקצו, ניתן לפתוח את ההזמנה
    """
    def show_dialog(title, message):
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text(title),
            content=ft.Text(message),
            actions=[
                ft.TextButton("אישור", on_click=lambda e: close_dialog())
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        def close_dialog():
            dlg.open = False
            page.update()

        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    # --- שליפת השורה המדויקת לעדכון ---
    current_item = run_query(
        "SELECT id, quantity, supplied FROM customer_invitation_items WHERE id = ? LIMIT 1",
        (customer_invitation_item_id,),
        fetchone=True
    )
    if not current_item:
        show_dialog("שגיאה", f"לא נמצא פריט {customer_invitation_item_id} בהזמנה {invitation_id}")
        return

    item_id = current_item["id"]
    quantity_remaining = int(current_item["quantity"]) - int(current_item["supplied"])
    total_supplied_now = min(int(quantity), quantity_remaining)
    leftover = int(quantity) - total_supplied_now

    # --- עדכון supplied ---
    new_supplied = int(current_item["supplied"]) + total_supplied_now
    run_query(
        "UPDATE customer_invitation_items SET supplied = ? WHERE id = ?",
        (new_supplied, item_id),
        commit=True
    )

    # --- אם נשאר עודף, עדכון תיבת הכמות והצגת אזהרה ---
    if leftover > 0 and quantity_var:
        quantity_var.value = str(leftover)
        show_dialog("עודף כמות", f"נשארו {leftover} יחידות שיש לבחור להזמנה אחרת.")

    # --- עדכון סטטוס ההזמנה הראשונית אם כל הפריטים סופקו ---
    unsupplied_items = run_query(
        "SELECT COUNT(*) as cnt FROM customer_invitation_items WHERE invitation_id = ? AND supplied < quantity",
        (invitation_id,),
        fetchone=True
    )
    if unsupplied_items and unsupplied_items["cnt"] == 0:
        run_query(
            "UPDATE customer_invitations SET status='in_shop' WHERE id=?",
            (invitation_id,),
            commit=True
        )
    # --- החזרת leftover כדי להמשיך להקצות עודפים ---
    results = [{
        "customer_invitation_id": invitation_id,
        "product_id": product_name,
        "size": size,
        "supplied": total_supplied_now,
        "note": f"הזמנה {invitation_id} עודכנה בכמות {total_supplied_now}"
    }]

    return results, leftover

# def handle_supplied_item(invitation_id,
#                          quantity, customer_invitation_item_id,
#                          supplier_id,
#                          product_name,
#                          leftover=None,
#                          size=None,
#                          cylinder=None,
#                          angle=None,
#                          color=None,
#                          multifocal=None,
#                          curvature=None):
#     """
#     כשמוצר סופק ע"י ספק:
#     1. מסמן בטבלת supplier_invitations שהמוצר סופק
#     2. מסמן את המוצר בהזמנת הלקוח כ'סופק' (supplied)
#     3. מעדכן את הסטטוס ל'in_shop' אם כל הפריטים סופקו
#     4. פותח את פרטי ההזמנה בממשק (אם navigator קיים)
#     5. אם סופק יותר מהכמות שהוזמנה, מחפש הזמנה נוספת לעדכון
#     """
#     print("quantity", quantity)
#     print("invitation_id", invitation_id)
#
#     # --- שלב 1: סימון ההזמנה כסופקה ---
#     mark_supplied(invitation_id, quantity)
#     p_id = get_id_by_product_name(product_name)
#     print("p_id", p_id)
#     add_to_supplier_report(supplier_id, [{"id": p_id["id"], "count": quantity}])
#
#     # --- שלב 2: שליפת הנתונים ---
#     supplier_inv = run_query(
#         "SELECT product_id, customer_invitation_id, size FROM supplier_invitations WHERE customer_invitation_id = ?",
#         (invitation_id,),
#         fetchone=True
#     )
#     print("supplier_inv", supplier_inv)
#     if not supplier_inv:
#         raise ValueError(f"לא נמצאה הזמנת ספק עם ID {invitation_id}")
#
#     product_id = supplier_inv["product_id"]
#     customer_invitation_id = supplier_inv["customer_invitation_id"]
#     size = supplier_inv["size"]
#
#     if not customer_invitation_id or customer_invitation_id == 0:
#         print("ההזמנה אינה מקושרת להזמנת לקוח, אין מה לעדכן.")
#         return
#
#     # --- שלב 3: שליפת השורה המדויקת לעדכון ---
#     current_item = run_query(
#         """
#         SELECT id, quantity, supplied
#         FROM customer_invitation_items
#         WHERE id = ?
#         LIMIT 1
#         """,
#         (customer_invitation_item_id,),
#         fetchone=True
#     )
#     if not current_item:
#         print(f"לא נמצא פריט {product_id} במידה {size} בהזמנה {customer_invitation_id}")
#         return
#     print("current_item", current_item)
#
#     item_id = current_item["id"]
#     total_supplied_now = min(int(quantity), int(current_item["quantity"]) - int(current_item["supplied"]))
#     print("1", current_item["quantity"])
#     print("2", current_item["supplied"])
#     leftover = int(quantity) - total_supplied_now
#     print("leftover", leftover)
#
#     # --- עדכון supplied מתוקן ---
#     inv = run_query(
#         "SELECT supplied, quantity FROM customer_invitation_items WHERE id = ?",
#         (item_id,),
#         fetchone=True
#     )
#     new_supplied = min(int(inv["supplied"]) + total_supplied_now, int(inv["quantity"]))
#     run_query(
#         """
#         UPDATE customer_invitation_items
#         SET supplied = ?
#         WHERE id = ?
#         """,
#         (new_supplied, item_id),
#         commit=True
#     )
#
#     # --- עדכון סטטוס ההזמנה הראשונית אם כל הפריטים סופקו ---
#     unsupplied_items = run_query(
#         """
#         SELECT COUNT(*) as cnt
#         FROM customer_invitation_items
#         WHERE invitation_id = ? AND supplied < quantity
#         """,
#         (customer_invitation_id,),
#         fetchone=True
#     )
#
#     if unsupplied_items and unsupplied_items["cnt"] == 0:
#         run_query(
#             "UPDATE customer_invitations SET status='in_shop' WHERE id=?",
#             (customer_invitation_id,),
#             commit=True
#         )
#         print(f"הזמנה {customer_invitation_id} – כל המוצרים סופקו, סטטוס עודכן ל-in_shop")
#     else:
#         print(f"הזמנה {customer_invitation_id} – עדיין לא סופקה במלואה")
#
#     # --- שלב 4: טיפול בעודפים והקצאות נוספות ---
#     results = [{
#         "customer_invitation_id": customer_invitation_id,
#         "product_id": product_id,
#         "size": size,
#         "supplied": total_supplied_now,
#         "note": f" {customer_invitation_id} עודכן בהזמנה "
#     }]
#     print("results", results)
#
#     while leftover > 0:
#         print("leftover in the loop", leftover)
#         next_item = get_supplier_invitation(
#             supplier_id,
#             product_name,
#             size,
#             cylinder,
#             angle,
#             color=color if color else None,
#             multifocal=multifocal if multifocal else None,
#             curvature=curvature if curvature else None
#         )
#         if not next_item:
#             results.append({
#                 "customer_invitation_id": None,
#                 "product_id": product_id,
#                 "size": size,
#                 "supplied": leftover,
#                 "note": "עודף – מיותר"
#             })
#             print(f"עודף של {leftover} יחידות – אין הזמנה נוספת, מצוין כ'עודף'")
#             leftover = 0
#             break
#
#         next_results, leftoverSub = handle_supplied_item(
#             next_item["supplier_inv_id"],
#             leftover,
#             next_item["customer_invitation_item_id"],
#             supplier_id,
#             product_name,
#             leftover=leftover,
#             size=size,
#             cylinder=cylinder,
#             angle=angle,
#             color=color if color else None,
#             multifocal=multifocal if multifocal else None,
#             curvature=curvature if curvature else None
#         )
#         if next_results:
#             results.extend(next_results)
#         leftover = leftoverSub
#         print("leftover after callback", leftover)
#
#     leftoverSub = leftover
#     if results:
#         return results, leftoverSub
#     else:
#         print(f"מוצר {product_id} עודכן כסופק בהזמנה {customer_invitation_id}")
#         return customer_invitation_id, leftoverSub
#
