from logic.utils import run_query
from logic.suppliers import mark_supplied
from logic.orders import get_order_by_id
from datetime import datetime

def handle_supplied_item(invitation_id, qty):
    """
    כשהמוצר סופק ע"י ספק:
    1. מסמן בטבלת supplier_invitations שהמוצר סופק
    2. מסמן את המוצר בהזמנת הלקוח כ'סופק' (supplied = 1)
    3. מעדכן את הסטטוס שלו ל'in_shop'
    4. פותח את ההזמנה של הלקוח בממשק (אם קיים navigator)
    """

    # --- שלב 1: סימון ההזמנה כסופקה ---
    mark_supplied(invitation_id,qty)
    # --- שלב 2: שליפת הנתונים ---
    supplier_inv = run_query(
        "SELECT product_id, customer_invitation_id FROM supplier_invitations WHERE id = ?",
        (invitation_id,),
        fetchone=True
    )
    if not supplier_inv:
        raise ValueError(f"לא נמצאה הזמנת ספק עם ID {invitation_id}")

    product_id = supplier_inv["product_id"]
    customer_invitation_id = supplier_inv["customer_invitation_id"]

    if not customer_invitation_id or customer_invitation_id == 0:
        print("ההזמנה הזו אינה מקושרת להזמנת לקוח, אין מה לעדכן.")
        return

    # --- שלב 3: סימון המוצר בהזמנת הלקוח כ'סופק' ---
    run_query(
        """
        UPDATE customer_invitation_items
        SET supplied = ?
        WHERE invitation_id = ? AND product_id = ?
        """,
        (qty,customer_invitation_id, product_id),
        commit=True
    )

    # --- שלב 4: עדכון סטטוס המוצר ל-in_shop ---
    unsupplied_items = run_query(
        """
        SELECT COUNT(*) as cnt
        FROM customer_invitation_items
        WHERE invitation_id = ? AND supplied < ?
        """,
        (customer_invitation_id,qty,),
        fetchone=True
    )

    if unsupplied_items and unsupplied_items["cnt"] == 0:
        # כל המוצרים סופקו – עדכון סטטוס ההזמנה
        run_query(
            """
            UPDATE customer_invitations
            SET status = 'in_shop'
            WHERE id = ?
            """,
            (customer_invitation_id,),
            commit=True
        )
        print(f"הזמנה {customer_invitation_id} כל המוצרים סופקו – סטטוס עודכן ל-in_shop")
    else:
        print(f"הזמנה {customer_invitation_id} עדיין לא סופקה במלואה – סטטוס לא עודכן")


    print(f"מוצר {product_id} עודכן כסופק ונמצא בחנות להזמנה {customer_invitation_id}")
    return customer_invitation_id