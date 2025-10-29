from logic.orders import get_order_by_id, get_invitation_items_by_invitation_id
from logic.products import get_product_name_by_id
from logic.utils import run_query
from logic.suppliers import mark_supplied

# def handle_supplied_item(invitation_id, quantity):
#     """
#     כשהמוצר סופק ע"י ספק:
#     1. מסמן בטבלת supplier_invitations שהמוצר סופק
#     2. מסמן את המוצר בהזמנת הלקוח כ'סופק' (supplied = 1)
#     3. מעדכן את הסטטוס שלו ל'in_shop'
#     4. פותח את ההזמנה של הלקוח בממשק (אם קיים navigator)
#     """
#
#     # --- שלב 1: סימון ההזמנה כסופקה ---
#     mark_supplied(invitation_id,quantity)
#     # --- שלב 2: שליפת הנתונים ---
#     supplier_inv = run_query(
#         "SELECT product_id, customer_invitation_id, size FROM supplier_invitations WHERE id = ?",
#         (invitation_id,),
#         fetchone=True
#     )
#     if not supplier_inv:
#         raise ValueError(f"לא נמצאה הזמנת ספק עם ID {invitation_id}")
#
#     product_id = supplier_inv["product_id"]
#     customer_invitation_id = supplier_inv["customer_invitation_id"]
#     size = supplier_inv["size"]
#
#     if not customer_invitation_id or customer_invitation_id == 0:
#         print("ההזמנה הזו אינה מקושרת להזמנת לקוח, אין מה לעדכן.")
#         return
#
#     # --- שלב 3: סימון המוצר בהזמנת הלקוח כ'סופק' ---
#     run_query(
#         """
#         UPDATE customer_invitation_items
#         SET supplied = ?
#         WHERE invitation_id = ? AND product_id = ? AND size = ?
#         """,
#         (quantity,customer_invitation_id, product_id, size),
#         commit=True
#     )
#
#     # --- שלב 4: עדכון סטטוס המוצר ל-in_shop ---
#     unsupplied_items = run_query(
#         """
#         SELECT COUNT(*) as cnt
#         FROM customer_invitation_items
#         WHERE invitation_id = ? AND supplied < ?
#         """,
#         (customer_invitation_id,quantity,),
#         fetchone=True
#     )
#
#     if unsupplied_items and unsupplied_items["cnt"] == 0:
#         # כל המוצרים סופקו – עדכון סטטוס ההזמנה
#         run_query(
#             """
#             UPDATE customer_invitations
#             SET status = 'in_shop'
#             WHERE id = ?
#             """,
#             (customer_invitation_id,),
#             commit=True
#         )
#         print(f"הזמנה {customer_invitation_id} כל המוצרים סופקו – סטטוס עודכן ל-in_shop")
#     else:
#         print(f"הזמנה {customer_invitation_id} עדיין לא סופקה במלואה – סטטוס לא עודכן")
#
#
#     print(f"מוצר {product_id} עודכן כסופק ונמצא בחנות להזמנה {customer_invitation_id}")
#     return customer_invitation_id


# def handle_supplied_item(invitation_id, quantity, navigator=None, current_user=None):
#     """
#     כשמוצר סופק ע"י ספק:
#     1. מסמן בטבלת supplier_invitations שהמוצר סופק
#     2. מסמן את המוצר בהזמנת הלקוח כ'סופק' (supplied)
#     3. מעדכן את הסטטוס ל'in_shop' אם כל הפריטים סופקו
#     4. פותח את פרטי ההזמנה בממשק (אם navigator קיים)
#     5. אם הסופק יותר מהכמות שהוזמנה, מחפש הזמנה נוספת לעדכון
#     """
#
#     # --- שלב 1: סימון ההזמנה כסופקה ---
#     mark_supplied(invitation_id, quantity)
#
#     # --- שלב 2: שליפת הנתונים ---
#     supplier_inv = run_query(
#         "SELECT product_id, customer_invitation_id, size FROM supplier_invitations WHERE id = ?",
#         (invitation_id,),
#         fetchone=True
#     )
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
#     # --- שלב 3: שליפת כמות נוכחית וסימון כ'סופק' ---
#     current_item = run_query(
#         """
#         SELECT quantity, supplied
#         FROM customer_invitation_items
#         WHERE invitation_id = ? AND product_id = ? AND size = ?
#         """,
#         (customer_invitation_id, product_id, size),
#         fetchone=True
#     )
#     if not current_item:
#         print(f"לא נמצא פריט {product_id} במידה {size} בהזמנה {customer_invitation_id}")
#         return
#
#     total_supplied_now = min(quantity, current_item["quantity"] - current_item["supplied"])
#     leftover = quantity - total_supplied_now
#
#     # עדכון כמות שסופקה בהזמנה זו
#     run_query(
#         """
#         UPDATE customer_invitation_items
#         SET supplied = supplied + ?
#         WHERE invitation_id = ? AND product_id = ? AND size = ?
#         """,
#         (total_supplied_now, customer_invitation_id, product_id, size),
#         commit=True
#     )
#
#     # --- שלב 4: עדכון סטטוס ההזמנה אם כל הפריטים סופקו ---
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
#             """
#             UPDATE customer_invitations
#             SET status = 'in_shop'
#             WHERE id = ?
#             """,
#             (customer_invitation_id,),
#             commit=True
#         )
#         print(f"הזמנה {customer_invitation_id} – כל המוצרים סופקו, סטטוס עודכן ל-in_shop")
#     else:
#         print(f"הזמנה {customer_invitation_id} – עדיין לא סופקה במלואה")
#
#     # --- שלב 5: פתיחת ההזמנה בממשק ---
#     if navigator and current_user:
#         customer_invitation = get_order_by_id(customer_invitation_id)
#         items_list = get_invitation_items_by_invitation_id(customer_invitation_id)
#         customer_invitation["items"] = [items_list] if isinstance(items_list, dict) else items_list
#         for inv_item in customer_invitation["items"]:
#             inv_item["product_name"] = get_product_name_by_id(inv_item["product_id"])
#         navigator.go_new_invitation(
#             current_user,
#             customer_invitation["customer_id"],
#             is_new_invitation=True,
#             existing_invitation=customer_invitation,
#             edit=False
#         )
#
#     # --- שלב 6: טיפול בכמות עודפת ---# --- שלב 6: טיפול בכמות עודפת ---
#     # --- שלב 6: טיפול בכמות עודפת ---
#     if leftover > 0:
#         next_item = run_query(
#             """
#             SELECT invitation_id
#             FROM customer_invitation_items
#             WHERE product_id = ? AND size = ? AND supplied < quantity
#             ORDER BY invitation_id
#             LIMIT 1
#             """,
#             (product_id, size),
#             fetchone=True
#         )
#         if next_item:
#             print(f"עודף של {leftover} יחידות, ניתן להקצות להזמנה הבאה (ID {next_item['invitation_id']})")
#             return {
#                 "customer_invitation_id": next_item["invitation_id"],
#                 "product_id": product_id,
#                 "size": size,
#                 "supplied": leftover,
#                 "note": ""
#             }
#         else:
#             print(f"עודף של {leftover} יחידות – אין הזמנה נוספת, מצוין כ'עודף'")
#             return {
#                 "customer_invitation_id": None,
#                 "product_id": product_id,
#                 "size": size,
#                 "supplied": leftover,
#                 "note": "עודף – מיותר"
#             }
#
#     print(f"מוצר {product_id} עודכן כסופק בהזמנה {customer_invitation_id}")
#     return customer_invitation_id




# def handle_supplied_item(invitation_id, quantity):
#     """
#     כשמוצר סופק ע"י ספק:
#     1. מסמן בטבלת supplier_invitations שהמוצר סופק
#     2. מסמן את המוצר בהזמנת הלקוח כ'סופק'
#     3. מעדכן סטטוס להזמנה אם נשלמה
#     4. אם יש עודף – מחזיר מידע על עודפים
#     """
#
#     # --- שלב 1: סימון ההזמנה כסופקה ---
#     mark_supplied(invitation_id, quantity)
#
#     # --- שלב 2: שליפת נתוני הזמנת ספק ---
#     supplier_inv = run_query(
#         "SELECT product_id, customer_invitation_id, size FROM supplier_invitations WHERE id = ?",
#         (invitation_id,),
#         fetchone=True
#     )
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
#     # --- שלב 3: עדכון כמות שסופקה ---
#     current_item = run_query(
#         """
#         SELECT quantity, supplied
#         FROM customer_invitation_items
#         WHERE invitation_id = ? AND product_id = ? AND size = ?
#         """,
#         (customer_invitation_id, product_id, size),
#         fetchone=True
#     )
#     if not current_item:
#         print(f"לא נמצא פריט {product_id} במידה {size} בהזמנה {customer_invitation_id}")
#         return
#
#     total_supplied_now = min(quantity, current_item["quantity"] - current_item["supplied"])
#     leftover = quantity - total_supplied_now
#
#     run_query(
#         """
#         UPDATE customer_invitation_items
#         SET supplied = supplied + ?
#         WHERE invitation_id = ? AND product_id = ? AND size = ?
#         """,
#         (total_supplied_now, customer_invitation_id, product_id, size),
#         commit=True
#     )
#
#     # --- שלב 4: עדכון סטטוס ההזמנה אם כל הפריטים סופקו ---
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
#             "UPDATE customer_invitations SET status = 'in_shop' WHERE id = ?",
#             (customer_invitation_id,),
#             commit=True
#         )
#         print(f"הזמנה {customer_invitation_id} – כל המוצרים סופקו, סטטוס עודכן ל-in_shop")
#     else:
#         print(f"הזמנה {customer_invitation_id} – עדיין לא סופקה במלואה")
#
#     # --- שלב 5: טיפול בעודפים ---
#     if leftover > 0:
#         next_item = run_query(
#             """
#             SELECT invitation_id
#             FROM customer_invitation_items
#             WHERE product_id = ? AND size = ? AND supplied < quantity
#             ORDER BY invitation_id
#             LIMIT 1
#             """,
#             (product_id, size),
#             fetchone=True
#         )
#         if next_item:
#             print(f"עודף של {leftover} יחידות, ניתן להקצות להזמנה הבאה (ID {next_item['invitation_id']})")
#             return {
#                 "customer_invitation_id": next_item["invitation_id"],
#                 "product_id": product_id,
#                 "size": size,
#                 "supplied": leftover,
#                 "note": ""
#             }
#         else:
#             print(f"עודף של {leftover} יחידות – אין הזמנה נוספת, מצוין כ'עודף'")
#             return {
#                 "customer_invitation_id": None,
#                 "product_id": product_id,
#                 "size": size,
#                 "supplied": leftover,
#                 "note": "עודף – מיותר"
#             }
#
#     print(f"מוצר {product_id} עודכן כסופק בהזמנה {customer_invitation_id}")
#     return customer_invitation_id

# def handle_supplied_item(invitation_id, quantity, navigator=None, current_user=None):
#     """
#     כשמוצר סופק ע"י ספק:
#     1. מסמן בטבלת supplier_invitations שהמוצר סופק
#     2. מסמן את המוצר בהזמנת הלקוח כ'סופק' (supplied)
#     3. מעדכן את הסטטוס ל'in_shop' אם כל הפריטים סופקו
#     4. פותח את פרטי ההזמנה בממשק (אם navigator קיים)
#     5. אם סופק יותר מהכמות שהוזמנה, מחפש הזמנה נוספת לעדכון
#     """
#
#     # --- שלב 1: סימון ההזמנה כסופקה ---
#     mark_supplied(invitation_id, quantity)
#
#     # --- שלב 2: שליפת הנתונים ---
#     supplier_inv = run_query(
#         "SELECT product_id, customer_invitation_id, size FROM supplier_invitations WHERE id = ?",
#         (invitation_id,),
#         fetchone=True
#     )
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
#     # --- שלב 3: שליפת כמות נוכחית וסימון כ'סופק' ---
#     current_item = run_query(
#         """
#         SELECT quantity, supplied
#         FROM customer_invitation_items
#         WHERE invitation_id = ? AND product_id = ? AND size = ?
#         """,
#         (customer_invitation_id, product_id, size),
#         fetchone=True
#     )
#     if not current_item:
#         print(f"לא נמצא פריט {product_id} במידה {size} בהזמנה {customer_invitation_id}")
#         return
#
#     total_supplied_now = min(quantity, current_item["quantity"] - current_item["supplied"])
#     leftover = quantity - total_supplied_now
#
#     # עדכון כמות שסופקה בהזמנה זו
#     run_query(
#         """
#         UPDATE customer_invitation_items
#         SET supplied = supplied + ?
#         WHERE invitation_id = ? AND product_id = ? AND size = ?
#         """,
#         (total_supplied_now, customer_invitation_id, product_id, size),
#         commit=True
#     )
#
#     # --- שלב 4: עדכון סטטוס ההזמנה אם כל הפריטים סופקו ---
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
#             """
#             UPDATE customer_invitations
#             SET status = 'in_shop'
#             WHERE id = ?
#             """,
#             (customer_invitation_id,),
#             commit=True
#         )
#         print(f"הזמנה {customer_invitation_id} – כל המוצרים סופקו, סטטוס עודכן ל-in_shop")
#     else:
#         print(f"הזמנה {customer_invitation_id} – עדיין לא סופקה במלואה")
#
#     # --- שלב 5: טיפול בעודפים (מוגדל – מספר הקצאות ברצף) ---
#     results = []
#     results = []
#     while leftover > 0:
#         next_item = run_query(
#             """
#             SELECT invitation_id, quantity, supplied
#             FROM customer_invitation_items
#             WHERE product_id = ? AND size = ? AND supplied < quantity
#             ORDER BY invitation_id
#             LIMIT 1
#             """,
#             (product_id, size),
#             fetchone=True
#         )
#
#         if next_item:
#             inv_id = next_item["invitation_id"]
#             can_supply = next_item["quantity"] - next_item["supplied"]
#             supply_now = min(leftover, can_supply)
#
#             run_query(
#                 """
#                 UPDATE customer_invitation_items
#                 SET supplied = supplied + ?
#                 WHERE invitation_id = ? AND product_id = ? AND size = ?
#                 """,
#                 (supply_now, inv_id, product_id, size),
#                 commit=True
#             )
#
#             print(f"עודף של {supply_now} יחידות נותב להזמנה {inv_id}")
#             results.append({
#                 "customer_invitation_id": inv_id,
#                 "product_id": product_id,
#                 "size": size,
#                 "supplied": supply_now,
#                 "note": f"עודף נותב להזמנה {inv_id}"
#             })
#
#             leftover -= supply_now
#
#     # אם לא היו עודפים בכלל → נפתח את ההזמנה כרגיל
#     if navigator and current_user and not results:
#         customer_invitation = get_order_by_id(customer_invitation_id)
#         items_list = get_invitation_items_by_invitation_id(customer_invitation_id)
#         customer_invitation["items"] = [items_list] if isinstance(items_list, dict) else items_list
#         for inv_item in customer_invitation["items"]:
#             inv_item["product_name"] = get_product_name_by_id(inv_item["product_id"])
#         navigator.go_new_invitation(
#             current_user,
#             customer_invitation["customer_id"],
#             is_new_invitation=True,
#             existing_invitation=customer_invitation,
#             edit=False
#         )
#
#     # החזרה לכל שימוש אחר (למשל ל־add_to_over_supplied)
#     if results:
#         return results
#     else:
#         print(f"מוצר {product_id} עודכן כסופק בהזמנה {customer_invitation_id}")
#         return customer_invitation_id


def handle_supplied_item(invitation_id, quantity, navigator=None, current_user=None):
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
        WHERE invitation_id = ? AND product_id = ? AND size = ?
        ORDER BY id
        LIMIT 1
        """,
        (customer_invitation_id, product_id, size),
        fetchone=True
    )
    if not current_item:
        print(f"לא נמצא פריט {product_id} במידה {size} בהזמנה {customer_invitation_id}")
        return

    item_id = current_item["id"]
    total_supplied_now = min(quantity, current_item["quantity"] - current_item["supplied"])
    leftover = quantity - total_supplied_now

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
        "note": "עודכן בהזמנה ראשונית"
    }]

    while leftover > 0:
        next_item = run_query(
            """
            SELECT invitation_id, product_id, size, quantity, supplied
            FROM customer_invitation_items
            WHERE product_id = ? AND size = ? AND supplied < quantity
            ORDER BY invitation_id
            LIMIT 1
            """,
            (product_id, size),
            fetchone=True
        )

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

        inv_id = next_item["invitation_id"]
        can_supply = next_item["quantity"] - next_item["supplied"]
        supply_now = min(leftover, can_supply)

        # ⚠️ כאן צריך להפעיל את mark_supplied על ההזמנה הבאה
        mark_supplied(inv_id, supply_now)

        # עדכון כמות שסופקה בהזמנה הנוכחית
        run_query(
            """
            UPDATE customer_invitation_items
            SET supplied = supplied + ?
            WHERE invitation_id = ? AND product_id = ? AND size = ?
            """,
            (supply_now, inv_id, product_id, size),
            commit=True
        )

        # בדיקה ועדכון סטטוס ההזמנה אם כל הפריטים סופקו
        unsupplied = run_query(
            """
            SELECT COUNT(*) as cnt
            FROM customer_invitation_items
            WHERE invitation_id = ? AND supplied < quantity
            """,
            (inv_id,),
            fetchone=True
        )
        if unsupplied["cnt"] == 0:
            run_query(
                "UPDATE customer_invitations SET status='in_shop' WHERE id=?",
                (inv_id,),
                commit=True
            )
            print(f"הזמנה {inv_id} – כל המוצרים סופקו, סטטוס עודכן ל-in_shop")
        else:
            print(f"הזמנה {inv_id} – עדיין לא סופקה במלואה")

        results.append({
            "customer_invitation_id": inv_id,
            "product_id": product_id,
            "size": size,
            "supplied": supply_now,
            "note": f"עודף נותב להזמנה {inv_id}"
        })

        leftover -= supply_now

    # --- שלב 5: פתיחת ההזמנה בממשק אם navigator קיים ---
    if navigator and current_user and not results:
        customer_invitation = get_order_by_id(customer_invitation_id)
        items_list = get_invitation_items_by_invitation_id(customer_invitation_id)
        customer_invitation["items"] = [items_list] if isinstance(items_list, dict) else items_list
        for inv_item in customer_invitation["items"]:
            inv_item["product_name"] = get_product_name_by_id(inv_item["product_id"])
        navigator.go_new_invitation(
            current_user,
            customer_invitation["customer_id"],
            is_new_invitation=True,
            existing_invitation=customer_invitation,
            edit=False
        )

    # החזרה לכל שימוש אחר (למשל ל־add_to_over_supplied)
    if results:
        return results
    else:
        print(f"מוצר {product_id} עודכן כסופק בהזמנה {customer_invitation_id}")
        return customer_invitation_id
