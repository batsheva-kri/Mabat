from logic.utils import run_query
from datetime import datetime
def add_supplier(supplier):
    run_query(
        "INSERT INTO suppliers (name, phone, email,googleSheetLink) VALUES (?, ?, ?)",
        (supplier["name"], supplier.get("phone"), supplier.get("email"),supplier.get("link")),
        commit=True
    )
def update_supplier(supplier_id, updates):
    fields = []
    values = []
    for k, v in updates.items():
        fields.append(f"{k} = ?")
        values.append(v)
    values.append(supplier_id)
    q = f"UPDATE suppliers SET {', '.join(fields)} WHERE id = ?"
    run_query(q, tuple(values), commit=True)
def get_supplier_by_id(supplier_id):
    return run_query(
        "SELECT * FROM suppliers WHERE id = ?",
        (supplier_id,),
        fetchone=True
    )
def delete_supplier(supplier_id):
    run_query(
        "DELETE FROM suppliers WHERE id = ?",
        (supplier_id,),
        commit=True
    )
def get_supplier_catalog():
    query = """
    SELECT sc.product_id, p.name as product_name, sc.price, sc.supplier_id
    FROM suppliers_catalog sc
    JOIN products p ON sc.product_id = p.id
    """
    catalog = run_query(query, fetchall=True)
    return catalog
def add_supplier_invitations(customer_invitation_item_id=None, product_id=None, size=None, quantity=None):
    """
    מוסיפה הזמנת ספק.
    יכולה לעבוד בשני מצבים:
    1. מצב רגיל - מקבלת customer_invitation_item_id ושולפת פרטים.
    2. מצב ישיר - מקבלת product_id, size, quantity, ומכניסה עם customer_invitation_id = 0.
    """

    if customer_invitation_item_id is not None:
        # --- מצב 1: שליפה מטבלת customer_invitation_items ---
        item = run_query(
            """SELECT product_id, size, quantity, invitation_id
               FROM customer_invitation_items
               WHERE id = ?""",
            (customer_invitation_item_id,),
            fetchone=True
        )
        if not item:
            raise ValueError(f"פריט הזמנת לקוח עם ID {customer_invitation_item_id} לא נמצא")

        product_id = item["product_id"]
        size = item["size"]
        quantity = item["quantity"]
        customer_invitation_id = item["invitation_id"]

    else:
        # --- מצב 2: הכנסת פרטים ישירות ---
        if not (product_id and quantity is not None):
            raise ValueError("במצב ישיר חובה לספק product_id, size, quantity")
        customer_invitation_id = 0

    # שליפת הספק המועדף
    product = run_query(
        "SELECT preferred_supplier_id FROM products WHERE id = ?",
        (product_id,),
        fetchone=True
    )
    if not product:
        raise ValueError(f"מוצר {product_id} לא נמצא")
    supplier_id = product["preferred_supplier_id"]
    if not supplier_id:
        raise ValueError(f"למוצר {product_id} אין ספק מועדף")

    # הכנסת רשומה להזמנת ספק
    run_query(
        """INSERT INTO supplier_invitations
           (supplier_id, date_, supplied, product_id, size, quantity, customer_invitation_id, close)
           VALUES (?, ?, 0, ?, ?, ?, ?, 0)""",
        (
            supplier_id,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            product_id,
            size,
            quantity,
            customer_invitation_id
        ),
        commit=True
    )
def get_open_supplier_invitations(supplier_id):
    """
    מחזיר את כל ההזמנות מטבלת supplier_invitations
    שהשדה close = 0 (הזמנות פתוחות שלא נסגרו)
    """
    return run_query(
        "SELECT * FROM supplier_invitations WHERE supplier_id = ? AND close = 0",(supplier_id,),
        fetchall=True
    )
def get_closed_unsupplied_invitations(supplier_id):
    """
    מחזיר את כל ההזמנות שהן סגורות (close = 1)
    ועדיין לא סופקו (supplied = 0)
    """
    return run_query(
        "SELECT * FROM supplier_invitations WHERE supplier_id = ? AND close = 1 AND supplied = 0",(supplier_id,),
        fetchall=True
    )
def mark_supplied(invitation_id):
    run_query(
        "UPDATE supplier_invitations SET supplied = 1 WHERE id = ?",
        (invitation_id,),
        commit=True
    )
def mark_invitations_as_closed(invitations):
    """
    מקבלת רשימת הזמנות (מהפונקציה get_open_supplier_invitations)
    ומעדכנת את כולן ל-close = 1 (סגורות)
    """
    for inv in invitations:
        run_query(
            "UPDATE supplier_invitations SET close = 1 WHERE id = ?",
            (inv["id"],),
            commit=True
        )
def get_all_suppliers():
    query = """SELECT * FROM suppliers"""
    return run_query(query,fetchall=True)
def get_supplier_monthly_report(supplier_id, year, month):
    print("supplier_id", supplier_id)
    print("year",year)
    print("month",month)
    query = """
    SELECT sr.date_ AS date,
           p.name AS product_name,
           sr.count_ AS quantity,
           sr.calc AS total
    FROM supplier_reports sr
    JOIN products p ON sr.product_id = p.id
    WHERE sr.supplier_id = ?
      AND strftime('%Y', sr.date_) = ?
      AND strftime('%m', sr.date_) = ?
    ORDER BY sr.date_
    """
    ret = run_query(query, (supplier_id, str(year), f"{int(month):02d}"), fetchall=True)
    print(ret)
    return ret
def add_to_supplier_report(supplier_id,products):
    query = """
        INSERT INTO supplier_reports(supplier_id, _date, product_id, count, calc) VALUES (?,?,?,?,?)
    """
    for p in products:
        price = run_query("SELECT price FROM supplier_catalog WHERE supplier_id = ? AND product_id = ?",(supplier_id,p.id,),fetchall=True)
        now = datetime.now()
        run_query(
        query,
        (supplier_id, now, p.id,p.count,p.count*price),
        fetchall=True
    )
def get_suppliers_catalog_by_supplier_id(supplier_id):
    query = """SELECT sc.product_id, p.name as product_name, sc.price, sc.supplier_id
        FROM suppliers_catalog sc
        JOIN products p ON sc.product_id = p.id
        WHERE sc.supplier_id = ?"""
    return run_query(query,(supplier_id,),fetchall=True)
def add_supplier_catalog_entry(entry):
    print(entry["product_name"])
    existing = run_query("SELECT id FROM products WHERE name=?", (entry["product_name"],), fetchone=True)
    print(existing)
    if existing:
        product_id = existing["id"]
    else:
        # מוסיפים מוצר חדש
        run_query("INSERT INTO products (name) VALUES (?)", (entry["product_name"],), fetchone=True)
        product_id = run_query("SELECT id FROM products where name=?",(entry["product_name"],), fetchone=True)
        print(product_id)
        # שולפים את המזהה האחרון בצורה בטוחה
    # result = run_query("SELECT last_insert_rowid() AS id")
    # if result and len(result) > 0:
    #     product_id = result[0]["id"]
    # else:
    #     raise Exception("לא הצליח לשמור מוצר חדש ולקבל את המזהה שלו")

    # מוסיפים רשומה לקטלוג ספקים
    query = """
    INSERT INTO suppliers_catalog (supplier_id, product_id, price)
    VALUES (?, ?, ?)
    """
    run_query(query, (entry["supplier_id"], product_id, entry["price"]), commit=True)
def update_supplier_catalog_entry(supplier_id, product_id, updates):
    query = """
    INSERT INTO suppliers_catalog (supplier_id, product_id, price)
    VALUES (?, ?, ?)
    ON CONFLICT(supplier_id, product_id) DO UPDATE SET
        price = excluded.price
    """
    run_query(query, (supplier_id, product_id, updates["price"]), commit=True)
def delete_supplier_catalog_entry(supplier_id=None, product_id=None):
    if supplier_id and product_id:
        # מחיקת מוצר מספק ספציפי
        query = "DELETE FROM suppliers_catalog WHERE supplier_id = ? AND product_id = ?"
        run_query(query, (supplier_id, product_id), commit=True)
    elif product_id:
        # מחיקת מוצר מכל הספקים
        query = "DELETE FROM suppliers_catalog WHERE product_id = ?"
        run_query(query, (product_id,), commit=True)
    else:
        raise ValueError("צריך לספק לפחות product_id למחיקה")
def save_arrived_inventory( items,supplier_id):
    """
    שמירת מלאי שהגיע לדוח ספקים.

    :param supplier_id: מזהה הספק
    :param items: רשימה של מילונים {'product_id': int, 'count': int}
    """
    for item in items:
        product_id = item['product_id']
        count = item['count']

        # שולפים את המחיר מהטבלה suppliers_catalog
        row = run_query(
            "SELECT price FROM suppliers_catalog WHERE supplier_id = ? AND product_id = ?",
            (supplier_id, product_id),
            fetchone=True
        )
        if not row:
            raise ValueError(f"No price found for supplier {supplier_id} and product {product_id}")

        price = row['price']
        calc = price * count
        date_ = datetime.now().isoformat()

        # שמירת הנתונים בטבלת supplier_reports
        run_query(
            """
            INSERT INTO supplier_reports (supplier_id, date_, product_id, count_, calc)
            VALUES (?, ?, ?, ?, ?)
            """,
            (supplier_id, date_, product_id, count, calc),
            commit=True
        )
def create_supplier_invitations(supplier_id: int, customer_invitation_id: int, items: list[dict], notes: str = "", date_: str = None):
    """
    שומר רשומות לטבלת supplier_invitations.
    כל שורה בטבלה היא מוצר בודד בהזמנה לספק.

    items: list of dict, כל item = {
        "product_id": int,
        "size": str,
        "quantity": int
    }
    """
    if date_ is None:
        from datetime import datetime
        date_ = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    query = """
    INSERT INTO supplier_invitations
        (supplier_id, date_, notes, product_id, size, quantity, customer_invitation_id, supplied, close)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    for it in items:
        params = (
            supplier_id,
            date_,
            notes,
            it["product_id"],
            it.get("size", ""),
            it.get("qty", 1),
            customer_invitation_id,
            0,   # supplied (ברירת מחדל לא סופק)
            0    # close (ברירת מחדל לא סגור)
        )
        run_query(query, params, commit=True)
def get_open_orders(supplier_id=None):
    query = """
    SELECT si.id, s.name as supplier_name, si.date_ as date,
           p.name as product_name, si.quantity, sc.price, (si.quantity * sc.price) as total
    FROM supplier_invitations si
    JOIN suppliers s ON si.supplier_id = s.id
    JOIN products p ON si.product_id = p.id
    LEFT JOIN suppliers_catalog sc 
      ON sc.supplier_id = si.supplier_id AND sc.product_id = si.product_id
    WHERE si.close = 0
    """
    params = ()
    if supplier_id:
        query += " AND si.supplier_id = ?"
        params = (supplier_id,)
    return run_query(query, params, fetchall=True)
def get_closed_orders(supplier_id=None):
    query = """
    SELECT si.id, s.name as supplier_name, si.date_ as date,
           p.name as product_name, si.quantity, sc.price, (si.quantity * sc.price) as total,
           si.supplied
    FROM supplier_invitations si
    JOIN suppliers s ON si.supplier_id = s.id
    JOIN products p ON si.product_id = p.id
    LEFT JOIN suppliers_catalog sc 
      ON sc.supplier_id = si.supplier_id AND sc.product_id = si.product_id
    WHERE si.close = 1
    """
    params = ()
    if supplier_id:
        query += " AND si.supplier_id = ?"
        params = (supplier_id,)
    return run_query(query, params, fetchall=True)
def close_order(order_id):
    run_query("UPDATE supplier_invitations SET close = 1 WHERE id = ?", (order_id,), commit=True)
def reopen_order(order_id):
    run_query("UPDATE supplier_invitations SET close = 0 WHERE id = ?", (order_id,), commit=True)
