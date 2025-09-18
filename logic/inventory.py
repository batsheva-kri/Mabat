from datetime import datetime
from decimal import Decimal

from logic.suppliers import add_supplier_invitations
from logic.utils import run_query

def get_all_suppliers():
    query = "SELECT id, name FROM suppliers ORDER BY name"
    return run_query(query, fetchall=True)
def get_categories():
    return run_query("SELECT id, name FROM categories ORDER BY name", fetchall=True)

# def get_products_by_category_status(category_id =-1, status="inventory"):
#     print(category_id, status)
#     query = """
#     SELECT id, name, status, category_id
#     FROM products"""
#     if category_id !=-1:
#         query += """
#         \n WHERE category_id = ? AND status = ?
#         ORDER BY name
#         """
#         print(query)
#         print(type(query))
#         ret = run_query(query, (category_id, status,), fetchall=True)
#     else:
#         query += """ \nWHERE status = ?
#         ORDER BY name"""
#         print(query)
#         print(type(query))
#         ret = run_query(query, (status,), fetchall=True)
#     print("response", ret)
#     return ret

def get_category_name(category_id):
    query = "SELECT name FROM categories WHERE id = ?"
    row = run_query(query, (category_id,), fetchone=True)
    return row["name"] if row else "קטגוריה לא ידועה"
def get_inventory_products(category_id):
    query = """
        SELECT id, name, status, category_id
        FROM products
        WHERE status = 'inventory' AND category_id = ?
        ORDER BY name
    """
    return run_query(query,(category_id,) ,fetchall=True)
def get_invitation_products():
    query = """
        SELECT id, name, status, category_id
        FROM products
        WHERE status = 'inventory'
        ORDER BY name
    """
    return run_query(query, fetchall=True)
def get_all_products():
    query = """
        SELECT id, name, status, category_id
        FROM products
        ORDER BY name
    """
    return run_query(query, fetchall=True)
def format_size(d: Decimal) -> str:
    # מפיק מחרוזת נוחה: 0.5, 1, 1.25 וכו'
    return format(d.normalize(), 'f').rstrip('0').rstrip('.') if '.' in format(d.normalize(), 'f') else format(d.normalize(), 'f')

def sizes_for_category(category_id):
    sizes = []
    if category_id in (1, 2):
        s = Decimal("0.5")
        while s <= Decimal("6"):
            sizes.append(format_size(s))
            s += Decimal("0.25")
        s = Decimal("6.5")
        while s <= Decimal("12"):
            sizes.append(format_size(s))
            s += Decimal("0.5")
    else:
        # ברירת מחדל: נוכל להחזיר אותו טווח (או להחזיר ריק)
        s = Decimal("0.5")
        while s <= Decimal("12"):
            sizes.append(format_size(s))
            if s < Decimal("6"):
                s += Decimal("0.25")
            else:
                s += Decimal("0.5")
    return sizes
# --- שמירת מספר ערכים (dictionary) בבת אחת ---
def save_existing_inventory(entries,stam=None):
    for product_id, size, quantity in entries:
        if quantity is None or str(quantity).strip() == "":
            continue
        try:
            q = int(quantity)
        except Exception:
            q = 0
        if size == -1:
            required = run_query(
           "SELECT required_count FROM required_stock WHERE product_id = ?",
           (product_id,),
            fetchone=True
            )
        else:
            # --- בדיקה מול required_stock ---
            required = run_query(
                "SELECT required_count FROM required_stock WHERE product_id = ? AND size = ?",
                (product_id, str(size)),
                fetchone=True
            )
        if required:
            missing = required["required_count"] - quantity
            if missing > 0:
                # שולחים להזמנת ספק במצב ישיר
                add_supplier_invitations(
                    product_id=product_id,
                    size=str(size),
                    quantity=missing
                )
def process_inventory_input(entries):
    """
    entries: [(product_id, size, quantity), ...]
    משווה מול required_stock ושולח לספק במידת הצורך
    """
    for product_id, size, quantity in entries:
        if quantity is None or str(quantity).strip() == "":
            continue
        try:
            q = int(quantity)
        except Exception:
            q = 0

        required = run_query(
            "SELECT required_count FROM required_stock WHERE product_id = ? AND size = ?",
            (product_id, str(size)),
            fetchone=True
        )
        if required:
            missing = required["required_count"] - q
            if missing > 0:
                add_supplier_invitations(
                    product_id=product_id,
                    size=str(size),
                    quantity=missing
                )
