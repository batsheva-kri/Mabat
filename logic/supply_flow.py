from logic.convert import get_supplier_invitation
from logic.orders import get_order_by_id, get_invitation_items_by_invitation_id
from logic.products import get_product_name_by_id, get_id_by_product_name
from logic.utils import run_query
from logic.suppliers import mark_supplied, add_to_supplier_report


def handle_supplied_item(invitation_id,
                         quantity,customer_invitation_item_id,
                         supplier_id,
                         product_name,
                         leftover = None,
                         size=None,
                         cylinder=None,
                         angle=None,
                         color=None,
                         multifocal=None,
                         curvature=None
                         ):
    """
    כשמוצר סופק ע"י ספק:
    1. מסמן בטבלת supplier_invitations שהמוצר סופק
    2. מסמן את המוצר בהזמנת הלקוח כ'סופק' (supplied)
    3. מעדכן את הסטטוס ל'in_shop' אם כל הפריטים סופקו
    4. פותח את פרטי ההזמנה בממשק (אם navigator קיים)
    5. אם סופק יותר מהכמות שהוזמנה, מחפש הזמנה נוספת לעדכון
    """

    # --- שלב 1: סימון ההזמנה כסופקה ---
    mark_supplied(invitation_id, quantity)
    p_id = get_id_by_product_name(product_name)
    print("supplier_id =", supplier_id, type(supplier_id))
    print("p_id =", p_id, type(p_id))
    add_to_supplier_report(supplier_id, [{"id": p_id["id"], "count": quantity}])
    # --- שלב 2: שליפת הנתונים ---
    supplier_inv = run_query(
        "SELECT product_id, customer_invitation_id, size FROM supplier_invitations WHERE id = ?",
        (invitation_id,),
        fetchone=True
    )
    if not supplier_inv:
        raise ValueError(f"לא נמצאה הזמנת ספק עם ID {invitation_id}")

    product_id = supplier_inv["product_id"]
    customer_invitation_id = supplier_inv["customer_invitation_id"]
    size = supplier_inv["size"]

    if not customer_invitation_id or customer_invitation_id == 0:
        print("ההזמנה אינה מקושרת להזמנת לקוח, אין מה לעדכן.")
        return

    # --- שלב 3: שליפת השורה המדויקת לעדכון ---
    current_item = run_query(
        """
        SELECT id, quantity, supplied
        FROM customer_invitation_items
        WHERE id = ?
        ORDER BY id
        LIMIT 1
        """,
        (customer_invitation_item_id,),
        fetchone=True
    )
    if not current_item:
        print(f"לא נמצא פריט {product_id} במידה {size} בהזמנה {customer_invitation_id}")
        return

    item_id = current_item["id"]
    total_supplied_now = min(quantity, current_item["quantity"] - current_item["supplied"])
    leftover = quantity - total_supplied_now
    print("leftover", leftover)
    inv = run_query("SELECT supplied, quantity FROM customer_invitation_items WHERE id =?",(item_id,),fetchone=True)
    if inv["supplied"] + total_supplied_now < inv["quantity"]:
        run_query(
            """
            UPDATE customer_invitation_items
            SET supplied = 
            WHERE id = ? 
            """,
            (inv["quantity"], item_id),
            commit=True
        )
    # עדכון כמות שסופקה בשורה המדויקת בלבד
    run_query(
        """
        UPDATE customer_invitation_items
        SET supplied = supplied + ?
        WHERE id = ? 
        """,
        (total_supplied_now, item_id),
        commit=True
    )

    # --- עדכון סטטוס ההזמנה הראשונית אם כל הפריטים סופקו ---
    unsupplied_items = run_query(
        """
        SELECT COUNT(*) as cnt
        FROM customer_invitation_items
        WHERE invitation_id = ? AND supplied < quantity
        """,
        (customer_invitation_id,),
        fetchone=True
    )

    if unsupplied_items and unsupplied_items["cnt"] == 0:
        run_query(
            "UPDATE customer_invitations SET status='in_shop' WHERE id=?",
            (customer_invitation_id,),
            commit=True
        )
        print(f"הזמנה {customer_invitation_id} – כל המוצרים סופקו, סטטוס עודכן ל-in_shop")
    else:
        print(f"הזמנה {customer_invitation_id} – עדיין לא סופקה במלואה")

    # --- שלב 4: טיפול בעודפים והקצאות נוספות ---
    # הוספת ההזמנה הראשונית ל-results
    results = [{
        "customer_invitation_id": customer_invitation_id,
        "product_id": product_id,
        "size": size,
        "supplied": total_supplied_now,
        "note": f" {customer_invitation_id}  עודכן בהזמנה "
    }]

    while leftover > 0:
        print("leftover in the loop ", leftover)
        next_item = get_supplier_invitation(supplier_id,
                                            product_name,
                                            size,
                                            cylinder,
                                            angle,
                                            color = color if color else None,
                                            multifocal = multifocal if multifocal else None,
                                            curvature = curvature if curvature else None)
        if not next_item:
            # אין הזמנות נוספות → עודף מיותר
            results.append({
                "customer_invitation_id": None,
                "product_id": product_id,
                "size": size,
                "supplied": leftover,
                "note": "עודף – מיותר"
            })
            print(f"עודף של {leftover} יחידות – אין הזמנה נוספת, מצוין כ'עודף'")
            leftover = 0
            break

        next_results, leftoverSub  = handle_supplied_item(next_item["supplier_inv_id"],
                            leftover,
                            next_item["customer_invitation_item_id"],
                            supplier_id,
                            product_name,
                            leftover=leftover,
                            size=size,
                            cylinder=cylinder,
                            angle=angle,
                            color = color if color else None,
                            multifocal = multifocal if multifocal else None,
                            curvature = curvature if curvature else None)
        if next_results:
            results.extend(next_results)
        leftover = leftoverSub
        print("leftover after callback", leftover)


    leftoverSub = leftover
    if results:
        return results,leftoverSub
    else:
        print(f"מוצר {product_id} עודכן כסופק בהזמנה {customer_invitation_id}")
        return customer_invitation_id,leftoverSub
