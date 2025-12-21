from logic.db import resource_path
from logic.orders import get_order_by_id
from logic.products import get_product_name_by_id
from logic.utils import run_query
from datetime import datetime
import flet as ft

from logic.writing_in_google_sheet import write, write_supplier2_google_sheet

def add_supplier(supplier):
    run_query(
        "INSERT INTO suppliers (name, phone, email,googleSheetLink) VALUES (?, ?, ?,?)",
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
    print("I am in add_supplier_invitations")
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
    print("supplier_id", supplier_id)
    if supplier_id == 5:#ויסטה
        header = {
            "customer_id": 0,
            "date_": datetime.now().isoformat(),
            "notes": "",
            "prescription": "עדשות" ,
        }
        product_name = get_product_name_by_id(product_id)
        items = [{
            "product_name": product_name,
            "product_id": product_id,
            "size": size,
            "quantity": quantity
        }]

        print("I go and write in the googlesheet")
        write(supplier_id,header,items)
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
        "SELECT * FROM supplier_invitations WHERE supplier_id = ? AND close = 1 AND supplied < quantity",(supplier_id,),
        fetchall=True
    )
def mark_supplied(invitation_id, supplied):
    # שולפים את ההזמנה
    inv = run_query(
        "SELECT quantity, supplied FROM supplier_invitations WHERE id = ?",
        (invitation_id,),
        fetchone=True
    )
    if inv:
        quantity = inv["quantity"]
        total_supplied = inv["supplied"] + int(supplied)

        # לא לעבור על הכמות שהוזמנה
        if total_supplied > quantity:
            total_supplied = quantity
        now =datetime.now().isoformat()
        run_query(
            "UPDATE supplier_invitations SET supplied = ?, supplying_date = ? WHERE id = ?",
            (total_supplied, now, invitation_id),
            commit=True
        )

        # אם כל הכמות סופקה — נסגור את ההזמנה
        if total_supplied >= quantity:
            run_query(
                "UPDATE supplier_invitations SET close = 1 WHERE id = ?",
                (invitation_id,),
                commit=True
            )
            print(f"הזמנת ספק {invitation_id} נסגרה (כל הכמות סופקה)")
        else:
            print(f"הזמנת ספק {invitation_id} פתוחה – סופק {total_supplied}/{quantity}")
    else:
        print(f"⚠️ לא נמצאה הזמנת ספק עם id={invitation_id}")
def get_all_suppliers():
    from logic.utils import run_query
    return run_query("SELECT * FROM suppliers",(),fetchall=True)
def get_supplier_monthly_report(supplier_id, year, month):
    from logic.utils import run_query
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
    return ret
def add_to_supplier_report(supplier_id, products):
    from logic.utils import run_query
    print("alllllllllllllll",run_query("SELECT * FROM suppliers_catalog", fetchall=True))
    query = """
        INSERT INTO supplier_reports(supplier_id, date_ , product_id, count_ , calc) VALUES (?,?,?,?,?)
    """
    print("supplier_id",supplier_id)
    for p in products:
        price_row = run_query(
            "SELECT price FROM suppliers_catalog WHERE supplier_id = ? AND product_id = ?",
            (supplier_id, p["id"]),
            fetchone=True, commit=True
        )

        print("price_row:", price_row)

        price = price_row["price"] if price_row else None
        print("price:", price)
        print("count", p["count"])
        print("count type", type(p["count"]))

        now = datetime.now()

        run_query(
            query,
            (supplier_id, now, p["id"], p["count"], float(p["count"]) * price),
            fetchall=False
        )
def cancel_s_invitation(customer_inv_id):
    run_query(
        "UPDATE supplier_invitations SET supplied = quantity, close = 1 WHERE customer_invitation_id = ?",
        (customer_inv_id,),
        commit=True
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
        run_query("INSERT INTO products (name) VALUES (?)", (entry["product_name"],), fetchone=True, commit=True)
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
def save_arrived_inventory(items, supplier_id, page=None):
    """
    שמירת מלאי שהגיע לדוח ספקים.
    :param supplier_id: מזהה הספק
    :param items: רשימה של מילונים {'product_id': int, 'count': int, 'size': int}
    :param page: אובייקט הדף של Flet, אם רוצים להציג הודעות
    """
    warnings = []  # רשימת התראות
    print("item", items)
    for item in items:
        product_id = item['product_id']
        count = item['count']
        size = item['size']
        name = get_product_name_by_id(product_id)
        # שולפים את המחיר מהטבלה suppliers_catalog
        row = run_query(
            "SELECT price FROM suppliers_catalog WHERE supplier_id = ? AND product_id = ?",
            (supplier_id, product_id),
            fetchone=True
        )
        if not row:
            # אם לא נמצא מחיר – גם זו סיבה לאזהרה
            warnings.append(f"מוצר {name} לא מופיע בקטלוג של ספק {supplier_id}")
            continue

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
        # בדיקה אם המוצר היה מוזמן
        invitation_id = get_supplier_invitation(supplier_id, product_id, size)
        if invitation_id is not None:
            mark_supplied(invitation_id["id"], count)
        else:
            supplier = get_supplier_by_id(supplier_id)
            # המוצר לא הוזמן → נוסיף לרשימת ההתראות
            warnings.append(f"המוצר {name} בכמות {count} במידה {size} לא הוזמן מהספק {supplier['name']}")
    if page and warnings:
        msg = "\n".join(warnings)
        snack = ft.SnackBar(
            content=ft.Text(f"התראה:\n{msg}", color="red"),
            bgcolor="#FFF8E1",
            open=True,
            duration=20000  # כמה זמן יישאר על המסך (במילי־שניות)
        )

        # הוספה לשכבת overlay כדי שיוצג בפועל
        page.overlay.append(snack)
        page.update()
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
    header = get_order_by_id(customer_invitation_id)
    print("I am in create_supplier_invitations function")
    try:
        print("HEADER:", header)
        if supplier_id == 6:
            write_supplier2_google_sheet(supplier_id, header, items)
        else:
            write(supplier_id, header, items)

    except Exception as e:
        print("ERROR writing to Google Sheets:", e)
        raise  # מחזירים החריגה לפונקציה שקראה לנו

    print("I am in create_supplier_invitations function, and I wrote in the sheet")
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
            it.get("quantity", 1),
            customer_invitation_id,
            0,   # supplied (ברירת מחדל לא סופק)
            0    # close (ברירת מחדל לא סגור)
        )
        run_query(query, params, commit=True)
def get_open_orders(supplier_id=None):
    query = """
    SELECT si.id, s.name as supplier_name,c.name as customer_name, si.date_ as date, ci.total_price AS total,
           p.name as product_name, si.quantity, sc.price, (si.quantity * sc.price) as total,si.size as size
           FROM customers c JOIN customer_invitations ci ON c.id = ci.customer_id 
    JOIN supplier_invitations si ON ci.id = si.customer_invitation_id
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
    SELECT si.id, s.name as supplier_name, si.date_ as date,c.name as customer_name, ci.total_price AS total,
           p.name as product_name, si.quantity, sc.price, (si.quantity * sc.price) as total,si.size as size,
           si.supplied, supplying_date
     FROM customers c JOIN customer_invitations ci ON c.id = ci.customer_id 
    JOIN supplier_invitations si ON ci.id = si.customer_invitation_id
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
    run_query("UPDATE supplier_invitations SET close = 1 AND supplying_date = ? WHERE id = ?",
              (datetime.now().isoformat(), order_id,), commit=True)
def reopen_order(order_id):
    run_query("UPDATE supplier_invitations SET close = 0 WHERE id = ?", (order_id,), commit=True)
def get_supplier_google_sheet_link(id):
    return run_query("SELECT googleSheetLink FROM suppliers WHERE id = ?",(id,), fetchall=True)
def get_supplier_invitation(supplier_id, product_id, size=None):

    # שליפת כל ההזמנות הפתוחות של הספק למוצר
    query = """
        SELECT id FROM supplier_invitations
        WHERE supplier_id = ? AND product_id =?
          AND close = 0
    """
    params = [supplier_id, product_id]

    if size:
        query += " AND size = ?"
        params.append(size)

    query += " ORDER BY id"
    print("query", query)
    print("params",params)
    ret =  run_query(query, tuple(params), fetchone=True)
    print("ret", ret)
    return ret
import threading
import pdfkit
import os
from pathlib import Path
import html
import base64

# --- Paths / assets ---
downloads_dir = str(Path.home() / "Downloads")
os.makedirs(downloads_dir, exist_ok=True)
ASSETS_DIR = "../../Mabat/assets"
logo_path = resource_path("assets/shop_bg.png")
arial_path = resource_path("assets/arial.ttf")

# --- Base64 ---
def _file_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_b64 = _file_to_base64(logo_path)
font_b64 = _file_to_base64(arial_path)

def _maybe_reshape_hebrew(text: str) -> str:
    return html.escape(text or "")

# --- גרסה בטוחה ל-Flet ---
def export_supplier_monthly_pdf(page, supplier_id, year, month):
    print("I am hear 😉😉😉")
    supplier = get_supplier_by_id(supplier_id)
    """
    ייצוא דוח חודשי של ספק בודד ל-PDF, בצורה לא חוסמת את ה-UI
    """
    def task():
        try:
            print("Fetching report...")
            data = get_supplier_monthly_report(supplier_id, year, month)
            print("DATA:", data)
            if not data:
                page.snack_bar = ft.SnackBar(ft.Text("לא נמצאו נתונים לספק ולחודש"))
                page.snack_bar.open = True
                page.update()
                return

            print("Generating PDF...")
            fname = os.path.join(downloads_dir, f"supplier_{supplier['name']}_{int(year)}_{int(month):02d}.pdf")

            total_month = 0
            rows_html = ""
            grouped = {}
            for row in data:
                day = row["date"].split("T")[0] if "T" in row["date"] else row["date"]
                product = row["product_name"]
                quantity = row["quantity"]
                total = row["total"]

                if day not in grouped:
                    grouped[day] = {}
                if product not in grouped[day]:
                    grouped[day][product] = {"quantity": 0, "total": 0}

                grouped[day][product]["quantity"] += quantity
                grouped[day][product]["total"] += total

            for day, products in sorted(grouped.items()):
                daily_total = sum(p["total"] for p in products.values())
                total_month += daily_total

                item_rows = ""
                for product_name, info in products.items():
                    item_rows += f"""
                                   <tr>
                                       <td>{_maybe_reshape_hebrew(product_name)}</td>
                                       <td>{info['quantity']}</td>
                                       <td>{info['total']:.2f} ₪</td>
                                   </tr>
                               """
                rows_html += f"""
                              <h3 style='color:#1b4332; margin-top:30px;'>תאריך: {day}</h3>
                              <table>
                                  <tr><th>שם מוצר</th><th>כמות</th><th>סה"כ</th></tr>
                                  {item_rows}
                                  <tr style="background-color:#ddd;">
                                      <td colspan="2"><b>סה"כ ליום</b></td>
                                      <td><b>{daily_total:.2f} ₪</b></td>
                                  </tr>
                              </table>
                              """
            html_content = f"""
                       <!DOCTYPE html>
                       <html lang="he" dir="rtl">
                       <head>
                           <meta charset="UTF-8">
                           <style>
                           @font-face {{
                               font-family: 'ArialHeb';
                               src: url(data:font/truetype;charset=utf-8;base64,{font_b64}) format('truetype');
                           }}
                           body {{ font-family: 'ArialHeb', Arial, sans-serif; margin:30px; color:#333; }}
                           .logo {{ width:200px; margin-bottom:20px; }}
                           h2 {{ color:#52b69a; text-align:center; }}
                           table {{ width:90%; margin:0 auto 20px auto; border-collapse:collapse; font-size:15px; }}
                           th, td {{ border:1px solid #eee; padding:8px 10px; text-align:center; }}
                           th {{ background-color:#52b69a; color:white; }}
                           tr:nth-child(even) {{ background-color:#f9f9f9; }}
                           </style>
                       </head>
                       <body>
                           <div style="text-align:center;">
                               <img src="data:image/png;base64,{logo_b64}" class="logo"/>
                               <h2>דו"ח ספק חודשי — {supplier['name']}</h2>
                               <p>שנה: {year}, חודש: {month}</p>
                           </div>
                           {rows_html}
                           <h2 style="color:#2a9d8f;">סה"כ חודשי: {total_month:.2f} ₪</h2>
                       </body>
                       </html>
                       """
            options = {'enable-local-file-access': ''}
            config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
            pdfkit.from_string(html_content, fname, configuration=config, options=options)
            print("PDF generated at:", fname)
            page.snack_bar = ft.SnackBar(ft.Text(f"דוח נשמר בהצלחה: {fname}"))
            page.snack_bar.open = True
            page.update()
        except Exception as e:
            print("Exception:", e)
            page.snack_bar = ft.SnackBar(ft.Text(f"שגיאה ביצירת PDF: {e}"))
            page.snack_bar.open = True
            page.update()

    # הפעלת יצירת PDF ב-Thread נפרד
    threading.Thread(target=task).start()
