# import flet as ft
# import pdfkit
# import os
# import webbrowser
# import tempfile
# from datetime import datetime
# from pathlib import Path
# from logic.db import run_query, run_action
#
# # --- DAL כמו ב deliveries.py ---
# def add_delivery(name, address, phone1, phone2=None, paid=False, home_delivery=False, created_by_user_id=None, notes=None):
#     run_action("""
#         INSERT INTO deliveries (name, address, phone1, phone2, paid, home_delivery, created_at, created_by_user_id, notes)
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
#     """, (
#         name, address, phone1, phone2,
#         1 if paid else 0,
#         1 if home_delivery else 0,
#         datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#         created_by_user_id, notes
#     ))
#     return run_query("SELECT last_insert_rowid() AS id")[0]["id"]
#
# def update_delivery(delivery_id, name, address, phone1, phone2=None, paid=False, home_delivery=False, notes=None):
#     run_action("""
#         UPDATE deliveries
#         SET name=?, address=?, phone1=?, phone2=?, paid=?, home_delivery=?, notes=?
#         WHERE id=?
#     """, (name, address, phone1, phone2, 1 if paid else 0, 1 if home_delivery else 0, notes, delivery_id))
#
# def delete_delivery(delivery_id):
#     run_action("DELETE FROM deliveries WHERE id=?", (delivery_id,))
#
# def get_deliveries(filter_paid=None, month_year=None, search_text=None):
#     query = "SELECT * FROM deliveries WHERE 1=1"
#     params = []
#     if filter_paid is not None:
#         query += " AND paid=?"
#         params.append(1 if filter_paid else 0)
#     if month_year:
#         year, month = month_year
#         query += " AND substr(created_at,1,7)=?"
#         params.append(f"{year:04d}-{month:02d}")
#     if search_text:
#         query += " AND (name LIKE ? OR phone1 LIKE ? OR phone2 LIKE ?)"
#         like_text = f"%{search_text}%"
#         params.extend([like_text, like_text, like_text])
#     query += " ORDER BY created_at DESC"
#     return run_query(query, tuple(params))
#
# def get_deliveries_this_month():
#     now = datetime.now()
#     return get_deliveries(month_year=(now.year, now.month))
#
# def get_delivery_by_id(delivery_id):
#     rows = run_query("SELECT * FROM deliveries WHERE id=?", (delivery_id,))
#     return rows[0] if rows else None
#
# # --- Paths / assets ---
# downloads_dir = str(Path.home() / "Downloads")
# os.makedirs(downloads_dir, exist_ok=True)
# ASSETS_DIR = "assets"
# logo_filename = "shop_bg.png"
# logo_path = os.path.join(ASSETS_DIR, logo_filename)
#
# # --- PDF helpers ---
# def _maybe_reshape_hebrew(text: str) -> str:
#     # פשוט מחזיר את הטקסט — ArialHeb + CSS RTL
#     return text or ""
#
# def _make_temp_pdf():
#     tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
#     tmp_name = tmp.name
#     tmp.close()
#     return tmp_name
#
# def export_single_pdf_preview(d, page):
#     tmp_path = _make_temp_pdf()
#     # HTML
#     html = f"""
#     <!DOCTYPE html>
#     <html lang="he" dir="rtl">
#     <head>
#     <meta charset="UTF-8">
#     <style>
#     @font-face {{
#         font-family: 'ArialHeb';
#         src: url('file:///{os.path.abspath(os.path.join(ASSETS_DIR,'arial.ttf'))}') format('truetype');
#     }}
#     body {{
#         font-family: 'ArialHeb', Arial, sans-serif;
#         margin: 20px;
#         background-color: #ffffff;
#         color: #333;
#     }}
#     .card {{
#         border:2px solid #52b69a;
#         border-radius:8px;
#         padding:15px;
#         margin-bottom:20px;
#     }}
#     .header {{ text-align:center; margin-bottom:20px; }}
#     .logo {{ width:140px; height:70px; }}
#     table {{
#         width:100%;
#         border-collapse:collapse;
#     }}
#     th, td {{
#         border:1px solid #eee;
#         padding:8px;
#         text-align:center;
#     }}
#     th {{ background-color:#52b69a; color:white; }}
#     tr:nth-child(even) {{ background-color:#f9f9f9; }}
#     tr:hover {{ background-color:#d2ebff; }}
#     </style>
#     </head>
#     <body>
#     <div class="card">
#         <div class="header">
#             <img src="file:///{logo_path}" class="logo"/>
#             <h3>משלוח #{d['id']} — {_maybe_reshape_hebrew(d.get('name'))}</h3>
#         </div>
#         <table>
#             <tr>
#                 <td>כתובת</td><td>{_maybe_reshape_hebrew(d.get('address'))}</td>
#                 <td>טלפון 1</td><td>{d.get('phone1')}</td>
#             </tr>
#             <tr>
#                 <td>טלפון 2</td><td>{d.get('phone2') or '-'}</td>
#                 <td>שולם</td><td>{"כן" if d.get("paid") else "לא"}</td>
#             </tr>
#             <tr>
#                 <td>עד הבית</td><td>{"כן" if d.get("home_delivery") else "לא"}</td>
#                 <td>תאריך</td><td>{d.get('created_at') or '-'}</td>
#             </tr>
#             <tr>
#                 <td colspan="4">הערות: {_maybe_reshape_hebrew(d.get('notes') or "-")}</td>
#             </tr>
#         </table>
#     </div>
#     </body>
#     </html>
#     """
#     options = {'enable-local-file-access': ''}
#     config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
#     pdfkit.from_string(html, tmp_path, configuration=config, options=options)
#
#     try:
#         page.launch_url(f"file://{os.path.abspath(tmp_path)}")
#     except Exception:
#         webbrowser.open_new(tmp_path)
#
#     page.snack_bar = ft.SnackBar(ft.Text("התצוגה נפתחה — מהחלון שנפתח ניתן לבצע הדפסה"))
#     page.snack_bar.open = True
#     page.update()
#
# def export_month_pdf_download(page, year=None, month=None):
#     now = datetime.now()
#     year = year or now.year
#     month = month or now.month
#     items = get_deliveries(month_year=(year, month))
#     fname = os.path.join(downloads_dir, f"deliveries_{year}_{month:02d}.pdf")
#
#     # HTML table
#     rows_html = ""
#     for d in items:
#         rows_html += f"""
#         <tr>
#             <td>{d['id']}</td>
#             <td>{_maybe_reshape_hebrew(d.get('name') or "-")}</td>
#             <td>{_maybe_reshape_hebrew(d.get('address') or "-")}</td>
#             <td>{d.get('phone1')}</td>
#             <td>{d.get('phone2') or "-"}</td>
#             <td>{"כן" if d.get("paid") else "לא"}</td>
#             <td>{"כן" if d.get("home_delivery") else "לא"}</td>
#             <td>{d.get('created_at') or "-"}</td>
#         </tr>
#         """
#
#     html = f"""
#     <!DOCTYPE html>
#     <html lang="he" dir="rtl">
#     <head>
#     <meta charset="UTF-8">
#     <style>
#     @font-face {{
#         font-family: 'ArialHeb';
#         src: url('file:///{os.path.abspath(os.path.join(ASSETS_DIR,'arial.ttf'))}') format('truetype');
#     }}
#     body {{ font-family: 'ArialHeb', Arial, sans-serif; margin:20px; }}
#     h2 {{ color:#52b69a; }}
#     table {{ width:100%; border-collapse:collapse; }}
#     th, td {{ border:1px solid #eee; padding:8px; text-align:center; }}
#     th {{ background-color:#52b69a; color:white; }}
#     tr:nth-child(even) {{ background-color:#f9f9f9; }}
#     tr:hover {{ background-color:#d2ebff; }}
#     </style>
#     </head>
#     <body>
#     <h2>דו"ח משלוחים לחודש {year}-{month:02d}</h2>
#     <table>
#         <tr>
#             <th>ID</th>
#             <th>שם</th>
#             <th>כתובת</th>
#             <th>טלפון1</th>
#             <th>טלפון2</th>
#             <th>שולם</th>
#             <th>עד הבית</th>
#             <th>תאריך</th>
#         </tr>
#         {rows_html}
#     </table>
#     <p>סה"כ משלוחים: {len(items)}</p>
#     </body>
#     </html>
#     """
#     options = {'enable-local-file-access': ''}
#     config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
#     pdfkit.from_string(html, fname, configuration=config, options=options)
#
#     page.snack_bar = ft.SnackBar(ft.Text(f"דו\"ח חודשי נשמר בתיקיית הורדות: {fname}"))
#     page.snack_bar.open = True
#     page.update()
#
#     return fname
# deliveries.py (גרסה עם pdfkit במקום ReportLab)
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

# --- DAL (Data Access Layer) ---
def add_delivery(name, address, phone1, phone2=None, paid=False, home_delivery=False, created_by_user_id=None, notes=None):
    run_action("""
        INSERT INTO deliveries (name, address, phone1, phone2, paid, home_delivery, created_at, created_by_user_id, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        name, address, phone1, phone2,
        1 if paid else 0,
        1 if home_delivery else 0,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        created_by_user_id, notes
    ))
    return run_query("SELECT last_insert_rowid() AS id")[0]["id"]

def update_delivery(delivery_id, name, address, phone1, phone2=None, paid=False, home_delivery=False, notes=None):
    run_action("""
        UPDATE deliveries
        SET name=?, address=?, phone1=?, phone2=?, paid=?, home_delivery=?, notes=?
        WHERE id=?
    """, (name, address, phone1, phone2, 1 if paid else 0, 1 if home_delivery else 0, notes, delivery_id))

def delete_delivery(delivery_id):
    run_action("DELETE FROM deliveries WHERE id=?", (delivery_id,))

def get_deliveries(filter_paid=None, month_year=None, search_text=None):
    query = "SELECT * FROM deliveries WHERE 1=1"
    params = []
    if filter_paid is not None:
        query += " AND paid=?"
        params.append(1 if filter_paid else 0)
    if month_year:
        year, month = month_year
        query += " AND substr(created_at,1,7)=?"
        params.append(f"{year:04d}-{month:02d}")
    if search_text:
        query += " AND (name LIKE ? OR phone1 LIKE ? OR phone2 LIKE ?)"
        like_text = f"%{search_text}%"
        params.extend([like_text, like_text, like_text])
    query += " ORDER BY created_at DESC"
    return run_query(query, tuple(params))

def get_deliveries_this_month():
    now = datetime.now()
    return get_deliveries(month_year=(now.year, now.month))

def get_delivery_by_id(delivery_id):
    rows = run_query("SELECT * FROM deliveries WHERE id=?", (delivery_id,))
    return rows[0] if rows else None

# --- Paths / assets ---
downloads_dir = str(Path.home() / "Downloads")
os.makedirs(downloads_dir, exist_ok=True)
ASSETS_DIR = "../../Mabat/assets"
logo_filename = "shop_bg.png"
logo_path = os.path.join(ASSETS_DIR, logo_filename)
arial_path = os.path.join(ASSETS_DIR, "arial.ttf")

# --- Helper functions ---
def _maybe_reshape_hebrew(text: str) -> str:
    return html.escape(text or "")

def _make_temp_pdf():
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp_name = tmp.name
    tmp.close()
    return tmp_name

def _open_file(path):
    try:
        webbrowser.open_new(f"file://{os.path.abspath(path)}")
    except Exception:
        pass

def _file_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

logo_b64 = _file_to_base64(logo_path)
font_b64 = _file_to_base64(arial_path)

# --- PDF functions (pdfkit) ---
# def export_single_pdf_preview(d, page):
#     print("I try to print pdf preview")
#     print("d ", d)
#     print("page ", page)
#     tmp_path = _make_temp_pdf()
#
#     html_content = f"""
#     <!DOCTYPE html>
#     <html lang="he" dir="rtl">
#     <head>
#     <meta charset="UTF-8">
#     <style>
#     @font-face {{
#         font-family: 'ArialHeb';
#         src: url(data:font/truetype;charset=utf-8;base64,{font_b64}) format('truetype');
#     }}
#     body {{
#         font-family: 'ArialHeb', Arial, sans-serif;
#         margin: 20px;
#         background-color: #ffffff;
#         color: #333;
#     }}
#     .card {{
#         border:2px solid #52b69a;
#         border-radius:8px;
#         padding:15px;
#         margin-bottom:20px;
#     }}
#     .header {{ text-align:center; margin-bottom:20px; }}
#     .logo {{ width:140px; height:70px; }}
#     table {{
#         width:100%;
#         border-collapse:collapse;
#     }}
#     th, td {{
#         border:1px solid #eee;
#         padding:8px;
#         text-align:center;
#     }}
#     th {{ background-color:#52b69a; color:white; }}
#     tr:nth-child(even) {{ background-color:#f9f9f9; }}
#     tr:hover {{ background-color:#d2ebff; }}
#     </style>
#     </head>
#     <body>
#     <div class="card">
#         <div class="header">
#             <img src="data:image/png;base64,{logo_b64}" class="logo"/>
#             <h3>משלוח #{d['id']} — {_maybe_reshape_hebrew(d.get('name'))}</h3>
#         </div>
#         <table>
#             <tr>
#                 <td>כתובת</td><td>{_maybe_reshape_hebrew(d.get('address'))}</td>
#                 <td>טלפון 1</td><td>{d.get('phone1')}</td>
#             </tr>
#             <tr>
#                 <td>טלפון 2</td><td>{d.get('phone2') or '-'}</td>
#                 <td>שולם</td><td>{"כן" if d.get("paid") else "לא"}</td>
#             </tr>
#             <tr>
#                 <td>עד הבית</td><td>{"כן" if d.get("home_delivery") else "לא"}</td>
#                 <td>תאריך</td><td>{d.get('created_at') or '-'}</td>
#             </tr>
#             <tr>
#                 <td colspan="4">הערות: {_maybe_reshape_hebrew(d.get('notes') or "-")}</td>
#             </tr>
#         </table>
#     </div>
#     </body>
#     </html>
#     """
#
#     options = {'enable-local-file-access': ''}
#     config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
#     pdfkit.from_string(html_content, tmp_path, configuration=config, options=options)
#
#     try:
#         page.launch_url(f"file://{os.path.abspath(tmp_path)}")
#     except Exception:
#         _open_file(tmp_path)
#
#     page.snack_bar = ft.SnackBar(ft.Text("התצוגה נפתחה — מהחלון שנפתח ניתן לבצע הדפסה"))
#     page.snack_bar.open = True
#     page.update()
def export_single_pdf_preview(d, page):
    from datetime import datetime
    import os
    import pdfkit
    import flet as ft

    # שם קובץ זמני
    tmp_path = os.path.join(os.getenv("TEMP", "."), f"delivery_{d['id']}.pdf")

    # בניית השורות לטבלה – שתי עמודות: שם שדה וערך
    rows_html = f"""
    <tr><td><b>שם</b></td><td>{_maybe_reshape_hebrew(d.get('name') or "-")}</td></tr>
    <tr><td><b>כתובת</b></td><td>{_maybe_reshape_hebrew(d.get('address') or "-")}</td></tr>
    <tr><td><b>טלפון 1</b></td><td>{d.get('phone1') or "-"}</td></tr>
    <tr><td><b>טלפון 2</b></td><td>{d.get('phone2') or "-"}</td></tr>
    <tr><td><b>שולם</b></td><td>{"כן" if d.get("paid") else "לא"}</td></tr>
    <tr><td><b>עד הבית</b></td><td>{"כן" if d.get("home_delivery") else "לא"}</td></tr>
    <tr><td><b>תאריך</b></td><td>{d.get('created_at') or "-"}</td></tr>
    <tr><td><b>הערות</b></td><td>{_maybe_reshape_hebrew(d.get('notes') or "-")}</td></tr>
    """

    # HTML מלא
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
    body {{
        font-family: 'ArialHeb', Arial, sans-serif;
        margin: 20px;
        background-color: #fff;
        color: #333;
    }}
    .logo {{
        width: 560px;
        height: 280x;
    }}
    h2 {{
        color: #52b69a;
        margin-bottom: 20px;
    }}
    table {{
        width: 60%;
        margin: 0 auto;
        border-collapse: collapse;
        font-size: 16px;
    }}
    th, td {{
        border: 1px solid #eee;
        padding: 10px;
        text-align: right;
    }}
    tr:nth-child(even) {{ background-color: #f9f9f9; }}
    tr:hover {{ background-color: #d2ebff; }}
    td:first-child {{
        width: 30%;
        background-color: #52b69a;
        color: white;
        font-weight: bold;
    }}
    </style>
    </head>
    <body>
        <div style="text-align:center; margin-bottom:20px;">
            <img src="data:image/png;base64,{logo_b64}" class="logo"/>
            <h2>משלוח #{d['id']} — {_maybe_reshape_hebrew(d.get('name'))}</h2>
        </div>
        <table>
            {rows_html}
        </table>
    </body>
    </html>
    """

    # יצירת PDF
    try:
        options = {'enable-local-file-access': ''}
        config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
        pdfkit.from_string(html_content, tmp_path, configuration=config, options=options)
        print("PDF created at:", tmp_path)
    except Exception as e:
        print("PDF generation failed:", e)
        return

    # הודעה למשתמש
    page.snack_bar = ft.SnackBar(ft.Text(f"התצוגה נוצרה — ניתן למצוא את הקובץ כאן: {tmp_path}"))
    page.snack_bar.open = True
    page.update()

    return tmp_path

def export_month_pdf_download(page, year=None, month=None):
    now = datetime.now()
    year = year or now.year
    month = month or now.month
    items = get_deliveries(month_year=(year, month))
    fname = os.path.join(downloads_dir, f"deliveries_{year}_{month:02d}.pdf")

    rows_html = ""
    for d in items:
        rows_html += f"""
        <tr>
            <td>{d['id']}</td>
            <td>{_maybe_reshape_hebrew(d.get('name') or "-")}</td>
            <td>{_maybe_reshape_hebrew(d.get('address') or "-")}</td>
            <td>{d.get('phone1')}</td>
            <td>{d.get('phone2') or "-"}</td>
            <td>{"כן" if d.get("paid") else "לא"}</td>
            <td>{"כן" if d.get("home_delivery") else "לא"}</td>
            <td>{d.get('created_at') or "-"}</td>
        </tr>
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
    body {{ font-family: 'ArialHeb', Arial, sans-serif; margin:20px; }}
    h2 {{ color:#52b69a; }}
    .logo {{ width:140px; height:70px; }}
    table {{ width:100%; border-collapse:collapse; }}
    th, td {{ border:1px solid #eee; padding:8px; text-align:center; }}
    th {{ background-color:#52b69a; color:white; }}
    tr:nth-child(even) {{ background-color:#f9f9f9; }}
    tr:hover {{ background-color:#d2ebff; }}
    </style>
    </head>
    <body>
    <div style="text-align:center; margin-bottom:20px;">
        <img src="data:image/png;base64,{logo_b64}" class="logo"/>
        <h2>דו"ח משלוחים לחודש {year}-{month:02d}</h2>
    </div>
    <table>
        <tr>
            <th>ID</th><th>שם</th><th>כתובת</th><th>טלפון1</th>
            <th>טלפון2</th><th>שולם</th><th>עד הבית</th><th>תאריך</th>
        </tr>
        {rows_html}
    </table>
    <p>סה"כ משלוחים: {len(items)}</p>
    </body>
    </html>
    """

    options = {'enable-local-file-access': ''}
    config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
    pdfkit.from_string(html_content, fname, configuration=config, options=options)

    page.snack_bar = ft.SnackBar(ft.Text(f"דו\"ח חודשי נשמר בתיקיית הורדות: {fname}"))
    page.snack_bar.open = True
    page.update()

    return fname
