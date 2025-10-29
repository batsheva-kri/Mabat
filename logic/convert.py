import math

from logic.utils import run_query


def _fmt_number_trim(x):
    """פורמט מספר כך שיסיר אפסים מיותרים: 6.00 -> '6', 6.50 -> '6.5', 6.25 -> '6.25'"""
    if x is None:
        return None
    s = f"{x:.2f}"
    s = s.rstrip('0').rstrip('.')
    return s

def _round_down_allowed_cylinder(cyl):
    """
    עבור ערך צילינדר (חיובי או שלילי), נמצא את הערך המותאם 'למטה' לפי הסדרה 0.75,1.25,1.75,...
    מחזיר מחרוזת עם סימן שלילי (כמו '-1.25') כי DB שומר כך בד"כ.
    אם abs(cyl) < 0.75 => נחזיר None (לא מתייחסים לצילינדר/זוית).
    """
    if cyl is None:
        return None
    sign = -1 if cyl < 0 else 1
    a = abs(cyl)
    if a < 0.75:
        return None
    # סדרת המינים: 0.75 + 0.5 * n
    # נבחר את הערך הגדול ביותר שאינו> a (round down)
    n = math.floor((a - 0.75) / 0.5)
    val = 0.75 + 0.5 * n
    if val <= 0:
        val = 0.75
    val = round(val, 2)
    val = val * sign
    return _fmt_number_trim(val)

def _angle_options_from(angle):
    """
    קבלת רשימת זויות אפשריות לפי הכללים:
    - angle <= 2 -> 180
    - 2 < angle < 6 -> 10
    - אחרת עיגול לעשרות; אם הספרה היחידות == 5 -> נחזיר גם תחתון וגם עליון
    - גבול עליון 180 (ואחריו 0)
    """
    if angle is None:
        return [None]
    try:
        a = int(round(angle))
    except Exception:
        return [None]
    if a <= 2:
        return [180]
    if a < 6:
        return [10]
    # עכשיו מעל/שווה 6
    tens = (a // 10) * 10
    rem = a % 10
    opts = []
    if rem == 5:
        opts.append(tens)
        up = min(tens + 10, 180)
        if up not in opts:
            opts.append(up)
    elif rem < 5:
        opts.append(tens)
    else:
        opts.append(min(tens + 10, 180))
    # הסרת ערכים לא תקינים (0-180). לפי הכלל: מעל 180 -> 0 (לא נחזור על זה כאן).
    opts = [o for o in opts if 0 <= o <= 180]
    return opts if opts else [None]

def customer_size_to_possible_arrived(customer_size_str):
    """
    מקבל מחרוזת size מהלקוח (למשל "6.50 -1.25 10" או "7.25" וכו')
    מחזיר רשימת מחרוזות אפשריות של מה שהספק יכול להביא (פורמט זהה לזה ששמור ב־DB).
    הכללים מבוססים על ההוראות שסיפקת.
    """
    if not customer_size_str:
        return []

    parts = customer_size_str.strip().split()
    # פירוק
    try:
        base_size = float(parts[0])
    except Exception:
        return []
    cyl = None
    ang = None
    if len(parts) > 1:
        try:
            cyl = float(parts[1])
        except Exception:
            cyl = None
    if len(parts) > 2:
        try:
            ang = int(float(parts[2]))
        except Exception:
            ang = None

    # 1) המרת גודל לפי טווחים:
    adjusted = base_size
    if 4 < base_size < 6.25:
        adjusted = base_size - 0.25
    elif 6.25 <= base_size < 8:
        adjusted = base_size - 0.5
    elif 8.25 <= base_size < 10:
        adjusted = base_size - 0.75
    elif base_size >= 10:
        adjusted = base_size - 1.0
    # שים לב: על 6 יש רק קפיצות של 0.5 — לכן אם adjusted > 6 ונקבל ערך שלא על חצי
    size_options = []
    if adjusted > 6:
        # אם אינו כפולה של 0.5, נחזיר גם את הקרוב התחתון וגם העליון (לפי תיאורך)
        dbl = adjusted * 2
        if abs(dbl - round(dbl)) < 1e-9:
            size_options = [adjusted]
        else:
            lower = math.floor(dbl) / 2.0
            upper = math.ceil(dbl) / 2.0
            # יכול להיות lower == upper, נדאג לייחוד
            size_options = sorted(set([round(lower, 2), round(upper, 2)]))
    else:
        # אם adjusted <= 6, ניתן להחזיר את הערך כמו שהוא (כולל רבעים)
        size_options = [round(adjusted, 2)]

    # 2) צילינדר: אם קטן מ-0.75 -> מתעלמים מצילינדר + זוית
    cyl_opt = _round_down_allowed_cylinder(cyl)  # נותן מחרוזת כמו '-1.25' או None
    # 3) זויות:
    angle_opts = _angle_options_from(ang) if cyl_opt is not None else [None]

    results = []
    for s in size_options:
        s_str = _fmt_number_trim(s)
        if cyl_opt is None:
            # ללא צילינדר וללא זוית
            results.append(s_str)
        else:
            for ao in angle_opts:
                if ao is None:
                    results.append(f"{s_str} {cyl_opt}")
                else:
                    results.append(f"{s_str} {cyl_opt} {ao}")

    # הסרת כפילויות ושמירה על סדר
    seen = set()
    ordered = []
    for r in results:
        if r not in seen:
            seen.add(r)
            ordered.append(r)
    return ordered

# ---------------- הפונקציה הראשית ----------------
def get_supplier_invitation(
    supplier_id,
    product_name,
    size=None,
    cylinder=None,
    angle=None,
    color=None,
    multifocal=None,
    curvature=None
):
    """
    זרימת בדיקה לפי ההיגיון שסיכמנו:
    - המוצר שהגיע נתון בפרמטרים size,cylinder,angle (כבר אחרי המרה).
    - עבור כל הזמנת ספק פתוחה לאותו product_id נשאב את כל שורות הלקוח שמתאימות ל־product_id.
    - עבור כל שורת לקוח נחשב את כל המחרוזות האפשריות שיכולות להתאים (customer_size_to_possible_arrived),
      ואז נבדוק האם המחרוזת שהגיעה (combined) קיימת ברשימה הזו.
    - צבע/מולטיפוקל/קימור נבדקים רק אם הוזנו לפונקציה (לא נבדקים אם None/ריק).
    """
    # בונים מחרוזת הגיע (כפי שהשתמשת בעבר)
    arrived_combined = " ".join(filter(None, [size, cylinder, angle]))

    # שליפת כל ההזמנות הפתוחות של הספק למוצר (ללא LIMIT)
    query = """
        SELECT id, product_id, size FROM supplier_invitations
        WHERE supplier_id = ?
          AND product_id = (SELECT id FROM products WHERE name = ?)
          AND close = 0
        ORDER BY id
    """
    params = [supplier_id, product_name]
    inv_list = run_query(query, tuple(params), fetchall=True)
    # print("inv_list:", inv_list)

    for inv in inv_list:
        supplier_inv_id = inv['id']
        product_id = inv['product_id']

        # נשלוף את ההזמנות של הלקוחות שיש להן אותו product_id
        # נוסיף תנאים על color/multifocal/curvature רק אם הם הוזנו
        cust_query = """
            SELECT ci.id AS cust_inv_id, cii.id AS item_id, cii.size AS cust_size
            FROM customer_invitations ci
            JOIN customer_invitation_items cii ON ci.id = cii.invitation_id
            WHERE cii.product_id = ?
        """
        cust_params = [product_id]

        if color is not None and color != "":
            cust_query += " AND ci.color = ?"
            cust_params.append(color)
        if multifocal is not None and multifocal != "":
            cust_query += " AND ci.multifocal = ?"
            cust_params.append(multifocal)
        if curvature is not None and curvature != "":
            cust_query += " AND ci.curvature = ?"
            cust_params.append(curvature)

        # ניתן למיין לפי עדיפויות אם יש צורך; כרגע פשוט נחדיר את כל התוצאות
        cust_rows = run_query(cust_query, tuple(cust_params), fetchall=True)

        # עבור כל שורת לקוח נחשב את המחרוזות האפשריות ונשווה ל-arrived_combined
        for row in cust_rows:
            cust_size_str = row.get("cust_size")
            possible_arrived = customer_size_to_possible_arrived(cust_size_str)
            # אם המוצר שהגיע קיים ברשימת האפשרויות -> זו התאמה
            if arrived_combined in possible_arrived:
                return supplier_inv_id

    # אם לא מצאנו התאמה בכל הזמנות הספק
    return None
# import math
# from logic.utils import run_query
#
# def _fmt_number_trim(x):
#     if x is None:
#         return None
#     s = f"{x:.2f}"
#     return s.rstrip('0').rstrip('.')
#
# def _round_down_allowed_cylinder(cyl):
#     if cyl is None:
#         return None
#     sign = -1 if cyl < 0 else 1
#     a = abs(cyl)
#     if a < 0.75:
#         return None
#     n = math.floor((a - 0.75) / 0.5)
#     val = 0.75 + 0.5 * n
#     val = round(val, 2) * sign
#     return _fmt_number_trim(val)
#
# def _angle_options_from(angle):
#     if angle is None:
#         return [None]
#     try:
#         a = int(round(angle))
#     except Exception:
#         return [None]
#     if a <= 2:
#         return [180]
#     if a < 6:
#         return [10]
#     tens = (a // 10) * 10
#     rem = a % 10
#     opts = []
#     if rem == 5:
#         opts.extend([tens, min(tens + 10, 180)])
#     elif rem < 5:
#         opts.append(tens)
#     else:
#         opts.append(min(tens + 10, 180))
#     return [o for o in opts if 0 <= o <= 180]
#
# def customer_size_to_possible_arrived(customer_size_str):
#     if not customer_size_str:
#         return []
#
#     parts = customer_size_str.strip().split()
#     try:
#         base_size = float(parts[0])
#     except Exception:
#         return []
#
#     cyl = float(parts[1]) if len(parts) > 1 else None
#     ang = float(parts[2]) if len(parts) > 2 else None
#
#     # המרת מידה לפי טווחים
#     adjusted = base_size
#     if 4 < base_size < 6.25:
#         adjusted = base_size - 0.25
#     elif 6.25 <= base_size < 8:
#         adjusted = base_size - 0.5
#     elif 8.25 <= base_size < 10:
#         adjusted = base_size - 0.75
#     elif base_size >= 10:
#         adjusted = base_size - 1.0
#
#     # יצירת אפשרויות מידה
#     size_options = []
#     if adjusted > 6:
#         dbl = adjusted * 2
#         if abs(dbl - round(dbl)) < 1e-9:
#             size_options = [adjusted]
#         else:
#             lower = math.floor(dbl) / 2.0
#             upper = math.ceil(dbl) / 2.0
#             size_options = sorted(set([round(lower, 2), round(upper, 2)]))
#     else:
#         size_options = [round(adjusted, 2)]
#
#     cyl_opt = _round_down_allowed_cylinder(cyl)
#     angle_opts = _angle_options_from(ang) if cyl_opt is not None else [None]
#
#     results = []
#     for s in size_options:
#         s_str = _fmt_number_trim(s)
#         if cyl_opt is None:
#             results.append(s_str)
#         else:
#             for ao in angle_opts:
#                 if ao is None:
#                     results.append(f"{s_str} {cyl_opt}")
#                 else:
#                     results.append(f"{s_str} {cyl_opt} {ao}")
#
#     return list(dict.fromkeys(results))  # הסרת כפילויות תוך שמירה על סדר
#
#
# # ---------------- הפונקציה הראשית ----------------
# def get_supplier_invitation(
#     supplier_id,
#     product_name,
#     size=None,
#     cylinder=None,
#     angle=None,
#     color=None,
#     multifocal=None,
#     curvature=None
# ):
#     """
#     לוגיקה מאוחדת:
#     1. ננסה קודם למצוא התאמה מדויקת להזמנה פתוחה של ספק לפי המוצר, הגודל והמאפיינים.
#     2. אם לא נמצא, נחשב התאמות לפי המרה על הזמנות הלקוחות בלבד.
#     """
#     combined = " ".join(filter(None, [size, cylinder, angle])) if (size or cylinder or angle) else None
#     arrived_combined = combined  # מחרוזת המוצר שהגיע
#
#     # --- שלב 1: בדיקה ישירה של התאמה להזמנת ספק ---
#     query = """
#         SELECT id, product_id, size FROM supplier_invitations
#         WHERE supplier_id = ?
#           AND product_id = (SELECT id FROM products WHERE name = ?)
#           AND close = 0
#     """
#     params = [supplier_id, product_name]
#
#     if color:
#         query += " AND color = ?"
#         params.append(color)
#     if multifocal:
#         query += " AND multifocal = ?"
#         params.append(multifocal)
#     if curvature:
#         query += " AND curvature = ?"
#         params.append(curvature)
#     if combined:
#         query += " AND size = ?"
#         params.append(combined)
#
#     query += " ORDER BY id"
#
#     inv_list = run_query(query, tuple(params), fetchall=True)
#
#     # אם נמצא התאמה מדויקת, נחזיר מיד
#     if inv_list:
#         return inv_list[0]["id"]
#
#     # --- שלב 2: התאמה לפי המרת מידה של הלקוחות ---
#     # שליפת כל ההזמנות הפתוחות של הספק לאותו מוצר (בלי LIMIT)
#     inv_query = """
#         SELECT id, product_id FROM supplier_invitations
#         WHERE supplier_id = ?
#           AND product_id = (SELECT id FROM products WHERE name = ?)
#           AND close = 0
#         ORDER BY id
#     """
#     invs = run_query(inv_query, (supplier_id, product_name), fetchall=True)
#
#     for inv in invs:
#         supplier_inv_id = inv["id"]
#         product_id = inv["product_id"]
#
#         cust_query = """
#             SELECT ci.id AS cust_inv_id, cii.id AS item_id, cii.size AS cust_size
#             FROM customer_invitations ci
#             JOIN customer_invitation_items cii ON ci.id = cii.invitation_id
#             WHERE cii.product_id = ?
#         """
#         cust_params = [product_id]
#
#         if color:
#             cust_query += " AND ci.color = ?"
#             cust_params.append(color)
#         if multifocal:
#             cust_query += " AND ci.multifocal = ?"
#             cust_params.append(multifocal)
#         if curvature:
#             cust_query += " AND ci.curvature = ?"
#             cust_params.append(curvature)
#
#         cust_rows = run_query(cust_query, tuple(cust_params), fetchall=True)
#
#         for row in cust_rows:
#             cust_size_str = row.get("cust_size")
#             possible_arrived = customer_size_to_possible_arrived(cust_size_str)
#             if arrived_combined in possible_arrived:
#                 return supplier_inv_id
#
#     # אם לא נמצאה שום התאמה
#     return None
