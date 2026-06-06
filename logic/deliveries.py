import flet as ft
import os
import webbrowser
import tempfile
from datetime import datetime
from pathlib import Path
from logic.db import run_query, run_action
import pdfkit
import base64
import html

from printing import print_pdf_async


# --- DAL ---
def _delete_after_delay(file_path, delay=20):
    """מוחק את הקובץ אחרי השהייה כדי לאפשר למ מדפסת לסיים לקרוא אותו"""
    import threading
    import time
    def task():
        time.sleep(delay)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"--- Temporary file deleted: {file_path} ---")
        except Exception as e:
            print(f"Could not delete temp file: {e}")

    # הרצה ב-Thread נפרד כדי לא לעצור את התוכנה
    threading.Thread(target=task, daemon=True).start()
def add_delivery(name, address, phone1, phone2=None,
                 cash=False, cash_amount=0, home_delivery=False,
                 created_by_user_id=None, notes=None):
    print("ksmcksmcksmcks  ", name, address, phone1, phone2,
                 cash, cash_amount, home_delivery,
                 created_by_user_id, notes)
    run_action("""
        INSERT INTO deliveries
        (name, address, phone1, phone2, cash, cash_amount,
         home_delivery, created_at, created_by_user_id, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name, address, phone1, phone2,
        1 if cash else 0,
        cash_amount,
        1 if home_delivery else 0,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        created_by_user_id,
        notes
    ))

    return run_query("SELECT last_insert_rowid() AS id")[0]["id"]


def update_delivery(delivery_id, name, address, phone1, phone2=None,
                    cash=False, cash_amount=0, home_delivery=False, notes=None):

    run_action("""
        UPDATE deliveries
        SET name=?, address=?, phone1=?, phone2=?, cash=?, cash_amount=?,
            home_delivery=?, notes=?
        WHERE id=?
    """, (name, address, phone1, phone2,
          1 if cash else 0, cash_amount,
          1 if home_delivery else 0,
          notes, delivery_id))


def delete_delivery(delivery_id):
    run_action("DELETE FROM deliveries WHERE id=?", (delivery_id,))


def get_deliveries(filter_paid=None, month_year=None, search_text=None):
    query = "SELECT * FROM deliveries WHERE 1=1"
    params = []

    if month_year:
        year, month = month_year
        query += " AND substr(created_at,1,7)=?"
        params.append(f"{year:04d}-{month:02d}")

    if search_text:
        query += " AND (name LIKE ? OR phone1 LIKE ? OR phone2 LIKE ?)"
        like = f"%{search_text}%"
        params.extend([like, like, like])

    query += " ORDER BY created_at DESC"
    return run_query(query, tuple(params))


def get_delivery_by_id(delivery_id):
    rows = run_query("SELECT * FROM deliveries WHERE id=?", (delivery_id,))
    return rows[0] if rows else None


# --- Paths / Assets ---
# downloads_dir = str(Path.home() / "Downloads")
# os.makedirs(downloads_dir, exist_ok=True)
#
# ASSETS_DIR = "../../Mabat/assets"
# logo_path = os.path.join(ASSETS_DIR, "shop_bg.png")
# arial_path = os.path.join(ASSETS_DIR, "arial.ttf")

import os
import tempfile
from pathlib import Path

# --- Paths / Assets ---

# 1. יצירת נתיב לתיקייה זמנית של המערכת (מקום נסתר עם הרשאות כתיבה)
# tempfile.gettempdir() מחזיר נתיב כמו C:\Users\User\AppData\Local\Temp
temp_base = Path(tempfile.gettempdir()) / "Mabat_Temp_Invoices"

# 2. יצירת התיקייה הזמנית במידה והיא לא קיימת
os.makedirs(str(temp_base), exist_ok=True)

# 3. הגדרת המשתנה לשימוש בשאר הפונקציות
output_base_path = str(temp_base)

# הדפסת הנתיב למסוף (Console) כדי שתוכלי להעתיק ולראות שהקובץ שם
print(f"--- קבצים זמניים נשמרים בנתיב: {output_base_path} ---")

# --- שאר הנתיבים שלך (לוגו ופונטים נשארים כרגיל) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.normpath(os.path.join(BASE_DIR, "..", "assets"))

logo_path = os.path.join(ASSETS_DIR, "shop_bg.png")
arial_path = os.path.join(ASSETS_DIR, "arial.ttf")

def get_deliveries_by_range(start_year, start_month, end_year, end_month):
    start = f"{start_year:04d}-{start_month:02d}"
    end = f"{end_year:04d}-{end_month:02d}"

    query = """
        SELECT *
        FROM deliveries
        WHERE substr(created_at,1,7) BETWEEN ? AND ?
        ORDER BY created_at ASC
    """
    return run_query(query, (start, end))



def export_range_summary_pdf(page, sy, sm, ey, em):
    items = get_deliveries_by_range(sy, sm, ey, em)

    total = len(items)
    home = sum(1 for d in items if d["home_delivery"])
    not_home = total - home

    price_home = 25
    price_regular = 20
    total_price = home * price_home + not_home * price_regular

    rows_html = ""
    for d in items:
        rows_html += f"""
        <tr>
            <td>{_maybe_reshape_hebrew(d['name'])}</td>
            <td>{_maybe_reshape_hebrew(d['address'])}</td>
            <td>{"כן" if d['home_delivery'] else "לא"}</td>
            <td>{d['created_at']}</td>
        </tr>
        """

    # שימוש בנתיב הזמני הנסתר
    fname = os.path.join(
        output_base_path,
        f"range_report_{sy}_{sm}.pdf"
    )

    html_content = f"""
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <style>
            body{{font-family:'ArialHeb';margin:20px}}
            table{{width:100%;border-collapse:collapse}}
            th,td{{border:1px solid #ddd;padding:8px;text-align:center}}
            th{{background:#52b69a;color:white}}
        </style>
    </head>
    <body>
        <div style="text-align:center;margin-bottom:20px">
             <img src="data:image/png;base64,{logo_b64}" width="200">
             <h2>דו"ח משלוחים {sy}/{sm:02d} – {ey}/{em:02d}</h2>
        </div>
        <table>
            <tr>
                <th>שם</th>
                <th>כתובת</th>
                <th>עד הבית</th>
                <th>תאריך</th>
            </tr>
            {rows_html}
        </table>
        <hr>
        <p>סה״כ משלוחים: <b>{total}</b></p>
        <p>סה״כ עד הבית: <b>{home}</b></p>
        <p>סה״כ לא עד הבית: <b>{not_home}</b></p>
        <h3>סה״כ לתשלום: {total_price} ₪</h3>
    </body>
    </html>
    """

    options = {"enable-local-file-access": ""}
    config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

    # יצירת הקובץ
    pdfkit.from_string(html_content, fname, configuration=config, options=options)

    # הדפסה
    print_pdf_async(fname)

    # מחיקה אוטומטית מהתיקייה הנסתרת בעוד 20 שניות
    _delete_after_delay(fname)

    page.snack_bar = ft.SnackBar(ft.Text("דו״ח טווח נשלח להדפסה"))
    page.snack_bar.open = True
    page.update()








def _maybe_reshape_hebrew(text): return html.escape(text or "")
def _make_temp_pdf():
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    name = tmp.name
    tmp.close()
    return name

def _open_file(path):
    try: webbrowser.open_new(f"file://{os.path.abspath(path)}")
    except: pass

def _file_to_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_b64 = _file_to_b64(logo_path)
font_b64 = _file_to_b64(arial_path)

# --- Single PDF ---
def export_single_pdf_print(d, page):
    # שימוש בנתיב הזמני הנסתר
    fname = os.path.join(
        output_base_path,
        f"delivery_label_{d['id']}.pdf"
    )

    html_content = f"""
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <style>
            @font-face {{
                font-family:'ArialHeb';
                src:url(data:font/truetype;charset=utf-8;base64,{font_b64}) format('truetype');
            }}
            body {{ font-family:'ArialHeb'; margin:0; padding:0; }}
            .page {{ width:210mm; height:297mm; position:relative; }}
            .label {{ position:absolute; top:10mm; right:10mm; width:105mm; height:148mm; border:3px solid #40E0D0; padding:10mm; box-sizing:border-box; }}
            .header {{ text-align:center; margin-bottom:8px; }}
            .header img {{ width:120px; }}
            table {{ width:100%; border-collapse:collapse; font-size:13px; }}
            td {{ border:1px solid #ddd; padding:5px; }}
            td:first-child {{ background:#52b69a; color:white; font-weight:bold; width:35%; }}
        </style>
    </head>
    <body>
        <div class="page">
            <div class="label">
                <div class="header"><img src="data:image/png;base64,{logo_b64}"></div>
                <table>
                    <tr><td>שם</td><td>{_maybe_reshape_hebrew(d['name'])}</td></tr>
                    <tr><td>כתובת</td><td>{_maybe_reshape_hebrew(d['address'])}</td></tr>
                    <tr><td>טלפון</td><td>{d['phone1']}</td></tr>
                    <tr><td>תשלום</td><td>{"מזומן" if d['cash'] else "אשראי"}</td></tr>
                    <tr><td>סכום</td><td>{d['cash_amount'] if d['cash'] else "-"}</td></tr>
                    <tr><td>עד הבית</td><td>{"כן" if d['home_delivery'] else "לא"}</td></tr>
                    <tr><td>הערות</td><td>{_maybe_reshape_hebrew(d['notes'])}</td></tr>
                </table>
            </div>
        </div>
    </body>
    </html>
    """

    options = {
        "page-size": "A4",
        "margin-top": "0mm", "margin-bottom": "0mm", "margin-left": "0mm", "margin-right": "0mm",
        "enable-local-file-access": ""
    }

    config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")

    # יצירת הקובץ
    pdfkit.from_string(html_content, fname, configuration=config, options=options)

    # הדפסה
    print_pdf_async(fname)

    # מחיקה אוטומטית מהתיקייה הנסתרת בעוד 20 שניות
    _delete_after_delay(fname)

    page.snack_bar = ft.SnackBar(ft.Text("התווית נשלחה להדפסה"))
    page.snack_bar.open = True
    page.update()

    return fname