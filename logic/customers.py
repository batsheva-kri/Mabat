from logic.utils import run_query

def get_all_customers():
    query = """SELECT * FROM customers"""
    return run_query(query, fetchall=True)
def search_customer_by_name(name):
    query = """
    SELECT id, name, phone, email
    FROM customers
    WHERE name LIKE ?
    ORDER BY name
    """
    params = (f"%{name}%",)
    return run_query(query, params,fetchall=True)
def search_customer_by_phone(phone):
    query = """
    SELECT id, name, phone, email
    FROM customers
    WHERE phone LIKE ?
    ORDER BY phone
    """
    params = (f"%{phone}%",)
    return run_query(query, params,fetchall=True)
def get_orders_for_customer(customer_id):
    query = """
    SELECT ci.* ,
            ci.id AS invitation_id,
           ci.date_ AS date,
           ci.status AS status,
           cii.id AS item_id,
           cii.product_id,
           p.name AS product_name,
           cii.size,
           cii.quantity AS quantity,
           cii.price AS unit_price,
           cii.supplied
    FROM customer_invitations ci
    JOIN customer_invitation_items cii ON ci.id = cii.invitation_id
    JOIN products p ON cii.product_id = p.id
    WHERE ci.customer_id = ?
    ORDER BY ci.date_ DESC, ci.id DESC
    """
    rows = run_query(query, (customer_id,), fetchall=True)

    # לאחד לפי הזמנה
    invitations = {}
    for r in rows:
        inv_id = r["invitation_id"]
        if inv_id not in invitations:
            invitations[inv_id] = {
                "id": inv_id,
                "date": r["date"],
                "status": r["status"],
                "notes": r["notes"],
                "total_price": r["total_price"],
                "answered": r["call"],
                "created_by_user_id": r["created_by_user_id"],
                "want_shipping": r["delivery_requested"],
                "shipped": r["delivery_sent"],
                "curvature": r["curvature"],
                "prescription": r["prescription"],
                "items": []
            }
        invitations[inv_id]["items"].append({
            "product_id": r["product_id"],
            "product_name": r["product_name"],
            "quantity": r["quantity"],
            "size": r["size"],
            "unit_price": r["unit_price"],
            "line_total": r["unit_price"] * r["quantity"],
            "supplied": r["supplied"]
        })
    return list(invitations.values())
def add_customer(name: str, phone: str, email: str = None, notes: str = None) -> int:
    """
    מוסיף לקוח חדש לטבלת customers ומחזיר את המזהה (id).
    עובד עם run_query בדיוק כמו בשאר הפונקציות שלך.
    """
    params = (name, phone, email, notes)
    try:
        row = run_query("""
            INSERT INTO customers (name, phone, email, notes)
            VALUES (?, ?, ?, ?)
            RETURNING id
        """, params, fetchone=True)
        return row["id"] if isinstance(row, dict) else row[0]
    except Exception:
        # תאימות לאחור: הוספה רגילה ואז שליפת last_insert_rowid()
        run_query("""
            INSERT INTO customers (name, phone, email, notes)
            VALUES (?, ?, ?, ?)
        """, params)
        row = run_query("SELECT last_insert_rowid() AS id", (), fetchone=True)
        return row["id"] if isinstance(row, dict) else row[0]
def get_customer_by_id(customer_id):
    print("customer_id",customer_id)
    return run_query("SELECT * FROM customers WHERE id = ?", (customer_id,), fetchall=True)
def get_customer_name_by_id(id):
    return run_query("SELECT name FROM customers WHERE id = ?",(id,),fetchone=True)