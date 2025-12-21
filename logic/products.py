from logic.utils import run_query

def get_all_products_for_invitation():
    query = """
    SELECT id, name
    FROM products
    WHERE status = 'invitation'
    ORDER BY name
    """
    res = run_query(query, fetchall=True)
    return res

def get_catalog_prices(product_id, amount):
    print("I am hear👋👋")
    query = """
    SELECT price, price_3, price_6, price_12, preferred_supplier_id
    FROM products
    WHERE id = ?
    """
    row = run_query(query, (product_id,),fetchone=True)
    print("row",row)
    if not row:
        return None  # לא נמצא מוצר
    print("row",row)
    prices = dict(row)
    price = prices.get("price")
    price_3 = prices.get("price_3") or price * 6      # 3 זוגות = 6 יחידות
    price_6 = prices.get("price_6") or price * 12     # 6 זוגות = 12 יחידות
    price_12 = prices.get("price_12") or price * 24   # 12 זוגות = 24 יחידות

    # פונקציה לחישוב מחיר לפי חבילות
    total = calculate_total_price(amount, price, price_3, price_6, price_12)
    print("prices",prices)
    print("total", total)
    return {
        "unit_prices": prices,
        "total": total
    }
def calculate_total_price(amount, price, price_3, price_6, price_12):
    total = 0
    remaining = amount
    for pack_size, pack_price in [(24, price_12), (12, price_6), (6, price_3), (1, price)]:
        if remaining >= pack_size:
            n_packs = remaining // pack_size
            total += n_packs * pack_price
            remaining -= n_packs * pack_size
    return total

def get_order_total(items):
    """
    items = רשימה של dict עם product_id ו-quantity
    מחשבת את המחיר הכולל לכל ההזמנה לפי חבילות.
    """
    from logic.db import run_query
    # מיזוג כמויות לפי מוצר
    quantities_by_product = {}
    for it in items:
        pid = it["product_id"]
        quantities_by_product[pid] = quantities_by_product.get(pid, 0) + it["quantity"]
    print("quantities_by_product", quantities_by_product)
    total = 0
    for pid, total_amount in quantities_by_product.items():
        prices = run_query(
            "SELECT * FROM products WHERE id = ?",
            (pid,),fetchall=True
        )
        if not prices:
            continue
        print("prices", prices)
        price = prices[0]["price"]
        price_3 = prices[0].get("price_3") or price * 6
        price_6 = prices[0].get("price_6") or price * 12
        price_12 = prices[0].get("price_12") or price * 24
        print("price", price)
        print("price_3", price)
        print("price_6", price)
        print("price_12", price)
        print("total_amount", total_amount)
        # שימוש בפונקציה לחישוב לפי חבילות
        total += calculate_total_price(total_amount, price, price_3, price_6, price_12)
        print("total", total)
    return total

def get_product_name_by_id(product_id):
    print("product_id", product_id)
    name = run_query("SELECT name FROM products WHERE id = ?",(product_id,),fetchone=True)
    print("name", name)
    return name["name"]
def get_id_by_product_name(product_name):
    return run_query("SELECT id FROM products WHERE name = ?",(product_name,),fetchone=True)
def get_vista_name(product_id, total_units):

    p_id = product_id["id"]
    # שולף מהטבלה את כל סוגי הקופסאות והשם המתאים
    packages = run_query("""
        SELECT package_name, units_per_box 
        FROM name_products_to_vista
        WHERE product_code = ? 
        ORDER BY units_per_box DESC
    """, (p_id,),fetchall=True)
    if not packages:
        return None
    name = packages[0]["package_name"].split()[0] if packages[0]["package_name"] else ""
    if len(packages) < 1:
        return {"name": f"{name}בודד ", "count": total_units}
    # נבדוק אם אפשר לחלק בדיוק
    fits_exactly = any(total_units % p["units_per_box"] == 0 for p in packages)

    # אם לא מתחלק בדיוק - נחשב הכל כבודדים
    if not fits_exactly:
        return {"name": f"{name} בודד", "count": total_units}

    # נבדוק אם הכמות מתחלקת בצורה מדויקת לאחת מהקופסאות
    for pkg in packages:
        box_size = pkg["units_per_box"]
        if total_units % box_size == 0:
            num_boxes = total_units // box_size
            return {"name": pkg["package_name"], "count": num_boxes}

