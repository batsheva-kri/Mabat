import datetime

from logic.utils import run_query
from logic.writing_in_google_sheet import write

def get_order_by_id(customer_invitation_id):
    return run_query("SELECT * FROM  customer_invitations WHERE id =?",(customer_invitation_id,),fetchone=True)
def new_invitation(header: dict ,items: list[dict]):
    invitation_id = create_invitation(header)
    add_invitation_items(invitation_id, items)
    return invitation_id
def create_invitation(header: dict):
    print(header.get("curvature"))
    print(header.get("curvature") is None)
    print(type(header.get("curvature")))
    curvature_val = header.get("curvature")

    # 💡 הוספת בדיקה למחרוזת "None" (או "none", למקרה הצורך)
    if curvature_val is None or curvature_val == "None":
        print("I am in. Using SHORT query (omitting curvature).")
        print("I am in")
        query = """
        INSERT INTO customer_invitations
            (customer_id, created_by_user_id, date_, notes, total_price, status, call, delivery_requested, delivery_sent, prescription,color,multifokal)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            header.get("customer_id"),
            header.get("created_by_user_id"),
            header.get("date_"),
            header.get("notes"),
            header.get("total_price"),
            header.get("status"),
            header.get("call",0),
            header.get("want_shipping", 0),   # תואם ל-delivery_requested
            header.get("shipped", 0),         # תואם ל-delivery_sent
            header.get("prescription"),
            header.get("color"),
            header.get("multifokal")
        )
    else:
        query = """
               INSERT INTO customer_invitations
                   (customer_id, created_by_user_id, date_, notes, total_price, status, call, delivery_requested, delivery_sent, curvature, prescription,color,multifokal)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
               """
        params = (
            header.get("customer_id"),
            header.get("created_by_user_id"),
            header.get("date_"),
            header.get("notes"),
            header.get("total_price"),
            header.get("status"),
            header.get("call", 0),
            header.get("want_shipping", 0),  # תואם ל-delivery_requested
            header.get("shipped", 0),  # תואם ל-delivery_sent
            header.get("curvature"),
            header.get("prescription"),
            header.get("color"),
            header.get("multifokal")
        )
    invitation_id = run_query(query, params, commit=True)
    print(invitation_id)
    return invitation_id
def add_invitation_items(invitation_id: int, items: list[dict]):
    """
    מוסיף פריטים להזמנה
    כל item = {product_id, quantity, size, unit_price, line_total, supplied}
    """
    query = """
    INSERT INTO customer_invitation_items
        (invitation_id, product_id, quantity, size, price, supplied)
    VALUES (?, ?, ?, ?, ?, ?)
    """
    for it in items:
        params = (
            invitation_id,
            it["product_id"],
            it["quantity"],
            it["size"],
            it["unit_price"],
            it["supplied"],
        )
        run_query(query, params, commit=True)  # בהנחה ש־run_query נמצאת בקובץ db.py
def update_invitation(invitation_id: int, header: dict):
    """
    מעדכן את פרטי ההזמנה בטבלת customer_invitations אם ההזמנה קיימת
    """
    existing = run_query(
        "SELECT id FROM customer_invitations WHERE id = ?",
        (invitation_id,),
        fetchone=True
    )
    if not existing:
        return False

    query = """
        UPDATE customer_invitations
        SET customer_id = ?,
            created_by_user_id = ?,
            date_ = ?,
            notes = ?,
            total_price = ?,
            status = ?,
            call = ?,
            delivery_requested = ?,
            delivery_sent = ?,
            curvature = ?,
            prescription = ?,
            color = ?,
            multifokal = ?
        WHERE id = ?
    """
    params = (
        header.get("customer_id"),
        header.get("created_by_user_id"),
        header.get("date_"),
        header.get("notes"),
        header.get("total_price"),
        header.get("status"),
        header.get("call"),
        header.get("want_shipping", 0),
        header.get("shipped", 0),
        header.get("curvature"),
        header.get("prescription"),
        header.get("color"),
        header.get("multifokal"),
        invitation_id
    )
    run_query(query, params, commit=True)
    return True
# פונקציה חדשה לעדכון שדות סטטוס בלבד
def update_invitation_status(invitation_id: int, call=None, delivery_requested=None, delivery_sent=None, collected= None):
    """
    עדכון שדות סטטוס בלבד בהזמנה.
    """
    existing = run_query(
        "SELECT id FROM customer_invitations WHERE id = ?",
        (invitation_id,),
        fetchone=True
    )
    if not existing:
        return False

    updates = []
    params = []

    if call is not None:
        updates.append("call = ?")
        updates.append("answering_date = ?")
        params.append(call)
        params.append(datetime.datetime.now().isoformat())
    if delivery_requested is not None:
        updates.append("delivery_requested = ?")
        params.append(delivery_requested)
    if delivery_sent is not None:
        updates.append("delivery_sent = ?")
        params.append(delivery_sent)
    if collected is not None:
        updates.append("status = ?")
        if collected == "collected":
            params.append("collected")
        else:
            params.append("in_shop")

    if not updates:
        return True  # אין מה לעדכן

    query = f"UPDATE customer_invitations SET {', '.join(updates)} WHERE id = ?"
    params.append(invitation_id)

    run_query(query, tuple(params), commit=True)
    return True
def clear_invitation_items(invitation_id: int):
    """
    מוחק את כל הפריטים הקשורים להזמנה מהטבלה customer_invitation_items אם ההזמנה קיימת
    :param invitation_id: מזהה ההזמנה
    :return: True אם נמחקו פריטים, False אם ההזמנה לא קיימת
    """
    existing = run_query(
        "SELECT id FROM customer_invitations WHERE id = ?",
        (invitation_id,),
        fetchone=True
    )
    if not existing:
        return False

    query = "DELETE FROM customer_invitation_items WHERE invitation_id = ?"
    run_query(query, (invitation_id,), commit=True)
    return True
def get_latest_orders(limit=1500):
    """
    מחזירה רשימה של ההזמנות האחרונות של כל הלקוחות.
    כל הזמנה כוללת:
    - פרטי ההזמנה
    - פרטי הלקוח
    - פרטי הפריטים (items) עם line_total
    - שדות נוספים: created_by_user_id, call
    """
    # שליפה של ההזמנות האחרונות עם פרטי לקוח
    invitations_query = """
        SELECT ci.*, c.name AS customer_name, c.phone AS customer_phone
        FROM customer_invitations ci
        JOIN customers c ON c.id = ci.customer_id
        ORDER BY ci.date_ DESC
        LIMIT ?
    """
    invitations = run_query(invitations_query, (limit,), fetchall=True)

    latest_orders = []

    for inv in invitations:
        # שליפה של כל הפריטים להזמנה זו
        items_query = """
            SELECT cii.id, cii.invitation_id, p.name AS product_name, p.id as product_id, cii.quantity AS quantity,
                   cii.size, cii.price as unit_price, cii.supplied
            FROM customer_invitation_items cii
            JOIN products p ON p.id = cii.product_id
            WHERE cii.invitation_id = ?
        """
        items = run_query(items_query, (inv["id"],), fetchall=True)

        # חישוב line_total לכל פריט
        for item in items:
            item["line_total"] = item["quantity"] * item["unit_price"] if item["unit_price"] is not None else 0
            item["supplied"] =item["supplied"]

        # הכנה של אובייקט הזמנה
        order = {
            "id": inv["id"],
            "customer_id": inv["customer_id"],
            "date": inv["date_"],
            "status": inv["status"],
            "notes": inv["notes"],
            "total_price": inv["total_price"],
            "answered": inv.get("call", 0),
            "created_by_user_id": inv.get("created_by_user_id"),
            "want_shipping": inv.get("delivery_requested"),
            "shipped":inv.get("delivery_sent"),
            "curvature":inv.get("curvature"),
            "prescription":inv.get("prescription"),
            "color" :inv.get("color"),
            "multifokal":inv.get("multifokal"),
            "items": items
        }

        # פרטי לקוח
        customer = {
            "id": inv["customer_id"],
            "name": inv["customer_name"],
            "phone": inv["customer_phone"]
        }

        latest_orders.append({
            "customer": customer,
            "order": order
        })

    return latest_orders
def auto_save_field(invitation_id, field, value):
    query = f"UPDATE customer_invitations SET {field} = ? WHERE id = ?"
    run_query(query, (value, invitation_id), commit=True)
    print(f"עודכן {field} ל-{value} להזמנה {invitation_id}")
def get_invitation_items_by_invitation_id(customer_invitation_id):
    invitations = run_query("SELECT * FROM  customer_invitation_items WHERE invitation_id =?", (customer_invitation_id,),fetchall=True)
    print("invitations", invitations)
    return invitations