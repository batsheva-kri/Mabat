from logic.db import run_action
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
def customer_exists_by_name(name: str) -> bool:
    row = run_query("SELECT id FROM customers WHERE name = ?", (name,), fetchone=True)
    return row is not None
def customer_exists_by_phone(phone: str) -> bool:
    row = run_query("SELECT id FROM customers WHERE phone = ?", (phone,), fetchone=True)
    return row is not None
def get_customer_by_phone(phone):
    return run_query("SELECT name FROM customers WHERE phone = ?", (phone,), fetchone=True)

class PhoneAlreadyExists(Exception):
    pass
def add_customer(name: str, phone: str, phone2:str , address: str, email: str = None, notes: str = None, allow_duplicate_name=False) -> int:
    # בדיקת טלפון — לא לאפשר
    if customer_exists_by_phone(phone):
        raise PhoneAlreadyExists("קיים כבר לקוח עם מספר טלפון זהה")

    # בדיקת שם — רק אם לא מאשרים כפילויות
    if not allow_duplicate_name and customer_exists_by_name(name):
        # נודיע למעלה שקיים שם, אבל כן נאפשר אם המשתמש ביקש
        return -1  # יחזר לסמן "שם קיים" אבל לא למנוע
    print("I try to add")
    # הכנסת הלקוח
    params = (name, phone, phone2, address,  email, notes)
    run_action("""
        INSERT INTO customers (name, phone, phone2, address, email, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, params)
    row = run_query("SELECT id FROM customers WHERE phone = ?", (phone,),fetchone=True)
    print("It's run")
    print("row",row)
    return row["id"]

def get_customer_by_id(customer_id):
    print("customer_id",customer_id)
    return run_query("SELECT * FROM customers WHERE id = ?", (customer_id,), fetchall=True)
def get_customer_name_by_id(id):
    return run_query("SELECT name FROM customers WHERE id = ?",(id,),fetchone=True)
def update_customer(customer_id, customer_details):
    run_query( "UPDATE customers SET name = ?, phone = ?,phone2 = ?, address = ?, email = ?, notes = ? WHERE id = ?",
               (customer_details["name"], customer_details["phone"],customer_details["phone2"],customer_details["address"],
                customer_details["email"] , customer_details["notes"], customer_id),commit=True)
def delete_customer(cust_id):
    run_query("DELETE FROM customers WHERE id = ?", (cust_id,),commit=True)

def get_item(inv_id):
    return run_query("SELECT cii.*, customer_id FROM customer_invitation_items cii JOIN customer_invitations ci WHERE cii.id=?", (inv_id,), fetchone=True)