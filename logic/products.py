from logic.utils import run_query

def get_all_products_for_invitation():
    query = """
    SELECT id, name
    FROM products
    WHERE status = 'invitation'
    ORDER BY name
    """
    res = run_query(query, fetchall=True)
    print(res)
    return res

def get_catalog_prices(product_id, amount):
    query = """
    SELECT price, price_3, price_6, price_12
    FROM catalog
    WHERE product_id = ?
    """
    params = (product_id,)
    row = run_query(query, params, fetchone=True)

    if not row:
        return None  # לא נמצא מוצר

    # נבנה מילון מהשורה
    prices = dict(row)

    # ודא שהשדות קיימים
    price = prices.get("price")
    price_3 = prices.get("price_3")
    price_6 = prices.get("price_6")
    price_12 = prices.get("price_12")

    # השלמות חוסרים
    if not price_3:
        price_3 = price * 3
    if not price_6:
        price_6 = price_3 * 2 if price_3 else price * 6
    if not price_12:
        price_12 = price_6 * 2 if price_6 else price_3 * 4 if price_3 else price * 12

    # נעדכן חזרה במילון
    prices["price_3"] = price_3
    prices["price_6"] = price_6
    prices["price_12"] = price_12

    # חישוב מחיר סופי לפי כמות
    if amount >= 12:
        total = price_12 * (amount // 12) + (amount % 12) * price
    elif amount >= 6:
        total = price_6 * (amount // 6) + (amount % 6) * price
    elif amount >= 3:
        total = price_3 * (amount // 3) + (amount % 3) * price
    else:
        total = price * amount

    return {
        "unit_prices": prices,
        "total": total
    }

