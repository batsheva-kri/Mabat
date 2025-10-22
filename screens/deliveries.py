# deliveries.py
import flet as ft
import os
import webbrowser
import tempfile
from datetime import datetime
from pathlib import Path
from logic.db import run_query, run_action

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

# --- Optional bidi/reshaper for correct Hebrew shaping ---
try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    _BIDI_AVAILABLE = True
except Exception:
    _BIDI_AVAILABLE = False

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
ASSETS_DIR = "assets"
logo_filename = "shop_bg.png"
logo_path = os.path.join(ASSETS_DIR, logo_filename)
arial_filename = "arial.ttf"  # צפי: אם יש פונט אריאל בקובץ זה ב-ASSETS
arial_path = os.path.join(ASSETS_DIR, arial_filename)

# register Arial if exists
_FONT_NAME = "Helvetica"
if os.path.exists(arial_path):
    try:
        pdfmetrics.registerFont(TTFont("ArialHeb", arial_path))
        _FONT_NAME = "ArialHeb"
    except Exception as ex:
        print("Failed to register Arial font:", ex)
        _FONT_NAME = "Helvetica"
else:
    # keep Helvetica; we'll show SnackBar if needed from UI
    _FONT_NAME = "Helvetica"

# helper: reshape hebrew text if bidi libs are available
def _maybe_reshape_hebrew(text: str) -> str:
    if not text:
        return ""
    if _BIDI_AVAILABLE:
        try:
            reshaped = arabic_reshaper.reshape(text)
            bidi_text = get_display(reshaped)
            return bidi_text
        except Exception:
            return text
    else:
        return text

# --- PDF helpers ---
def _make_temp_pdf_canvas():
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp_name = tmp.name
    tmp.close()
    c = canvas.Canvas(tmp_name, pagesize=A4)
    return c, tmp_name

def _open_file(path):
    # try Flet's launch_url in production; fallback to webbrowser
    try:
        # Flet's page.launch_url can't be used here (no page reference), caller should call page.launch_url
        webbrowser.open_new(f"file://{os.path.abspath(path)}")
    except Exception:
        try:
            webbrowser.open_new(path)
        except Exception:
            pass

def export_single_pdf_preview(d, page):
    """
    משתמש בזה לצורך תצוגת משלוח בודד — יוצר PDF זמני, שומר, ופותח לתצוגה (לא שמירת קבועה ב-Downloads).
    המשתמש יוכל להדפיס מהצופה.
    """
    # create canvas on temp file
    c, tmp_path = _make_temp_pdf_canvas()
    width, height = A4
    y = height - 40

    # draw turquoise rounded rectangle center (visual card)
    rect_w = width - 120
    rect_h = 220
    rect_x = 60
    rect_y = y - rect_h
    c.setStrokeColor(colors.Color(82/255, 182/255, 154/255))
    c.setFillColor(colors.white)
    c.roundRect(rect_x, rect_y, rect_w, rect_h, 8, fill=1, stroke=1)

    # logo (large, bottom of page inside rect)
    if os.path.exists(logo_path):
        try:
            img = ImageReader(logo_path)
            # draw logo at bottom center of card
            logo_w = 140
            logo_h = 70
            c.drawImage(img, rect_x + (rect_w - logo_w)/2, rect_y + 10, width=logo_w, height=logo_h, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    # header text on top-right inside card
    header_x = rect_x + rect_w - 20
    text_x_label = header_x
    text_x_value = rect_x + 110  # align values a bit to the left

    c.setFont(_FONT_NAME, 16)
    header = f"משלוח #{d['id']} — {d['name']}"
    c.drawRightString(text_x_label, y - 20, _maybe_reshape_hebrew(header))
    y_text = y - 50

    # details lines
    details = [
        ("כתובת", d.get("address") or "-"),
        ("טלפון 1", d.get("phone1") or "-"),
        ("טלפון 2", d.get("phone2") or "-"),
        ("שולם", "כן" if d.get("paid") else "לא"),
        ("עד הבית", "כן" if d.get("home_delivery") else "לא"),
        ("תאריך", d.get("created_at") or "-"),
        ("הערות", d.get("notes") or "-"),
    ]

    c.setFont(_FONT_NAME, 12)
    for label, val in details:
        # label on right, value slightly to left
        c.drawRightString(text_x_label, y_text, _maybe_reshape_hebrew(f"{label}:"))
        c.drawRightString(text_x_value, y_text, _maybe_reshape_hebrew(str(val)))
        y_text -= 20

    c.showPage()
    c.save()

    # open preview using Flet page.launch_url to ensure consistent behavior
    try:
        page.launch_url(f"file://{os.path.abspath(tmp_path)}")
    except Exception:
        # fallback
        _open_file(tmp_path)

    # snack
    page.snack_bar = ft.SnackBar(ft.Text("התצוגה נפתחה — מהחלון שנפתח ניתן לבצע הדפסה"))
    page.snack_bar.open = True
    page.update()

def export_month_pdf_download(page, year=None, month=None):
    """
    יצירת דו"ח חודשי ושמירתו בתיקיית ההורדות (Downloads).
    מחזיר את הנתיב של הקובץ.
    """
    now = datetime.now()
    year = year or now.year
    month = month or now.month

    items = get_deliveries(month_year=(year, month))
    fname = os.path.join(downloads_dir, f"deliveries_{year}_{month:02d}.pdf")
    doc = canvas.Canvas(fname, pagesize=A4)
    width, height = A4
    y = height - 40

    # title box
    title_x = width - 40
    doc.setFont(_FONT_NAME, 18)
    doc.drawRightString(title_x, y, _maybe_reshape_hebrew(f"דו\"ח משלוחים לחודש {year}-{month:02d}"))
    y -= 30

    # logo
    if os.path.exists(logo_path):
        try:
            img = ImageReader(logo_path)
            doc.drawImage(img, 40, y - 70, width=120, height=60, preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    # table
    data = [[
        _maybe_reshape_hebrew("ID"),
        _maybe_reshape_hebrew("שם"),
        _maybe_reshape_hebrew("כתובת"),
        _maybe_reshape_hebrew("טלפון1"),
        _maybe_reshape_hebrew("טלפון2"),
        _maybe_reshape_hebrew("שולם"),
        _maybe_reshape_hebrew("עד הבית"),
        _maybe_reshape_hebrew("תאריך"),
    ]]
    for d in items:
        data.append([
            str(d["id"]),
            _maybe_reshape_hebrew(d.get("name") or "-"),
            _maybe_reshape_hebrew(d.get("address") or "-"),
            d.get("phone1") or "-",
            d.get("phone2") or "-",
            "כן" if d.get("paid") else "לא",
            "כן" if d.get("home_delivery") else "לא",
            d.get("created_at") or "-"
        ])

    table = Table(data, colWidths=[40, 90, 140, 70, 70, 40, 60, 90], repeatRows=1)
    style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.Color(82/255, 182/255, 154/255)),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ])
    # zebra rows
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.add('BACKGROUND', (0,i), (-1,i), colors.whitesmoke)
    table.setStyle(style)

    w, h = table.wrapOn(doc, width-80, height-180)
    # draw table from top (y - header)
    table.drawOn(doc, 40, y - h)

    # total count
    doc.setFont(_FONT_NAME, 12)
    doc.drawRightString(width - 40, y - h - 20, _maybe_reshape_hebrew(f"סה\"כ משלוחים: {len(items)}"))

    doc.save()

    # notify user (snack) and open download folder
    page.snack_bar = ft.SnackBar(ft.Text(f"דו\"ח חודשי נשמר בתיקיית הורדות: {fname}"))
    page.snack_bar.open = True
    page.update()

    return fname

# --- UI (Flet screen) ---
def DeliveriesScreen(page, navigator, user):
    page.title = "מעקב משלוחים"
    page.scroll = "always"
    page.rtl = True

    # create refs/controls
    search_field = ft.Ref[ft.TextField]()
    only_unpaid = ft.Ref[ft.Checkbox]()
    month_picker = ft.Ref[ft.Dropdown]()
    data_table = ft.Ref[ft.DataTable]()

    # month picker options (year-1 .. year+1)
    now = datetime.now()
    month_options = []
    for y in range(now.year-1, now.year+1):
        for m in range(1, 13):
            month_options.append(ft.dropdown.Option(f"{y}-{m:02d}"))

    month_picker_control = ft.Dropdown(width=140, options=month_options, value=f"{now.year}-{now.month:02d}")
    month_picker.current = month_picker_control

    # helper: load table (dynamic search & filter)
    def load_table(e=None):
        paid_filter = None if not only_unpaid.current.value else False
        month_val = month_picker.current.value
        if month_val:
            year, month = map(int, month_val.split("-"))
            month_filter = (year, month)
        else:
            month_filter = None
        search_val = search_field.current.value.strip() if search_field.current.value else None

        rows_raw = get_deliveries(filter_paid=paid_filter, month_year=month_filter, search_text=search_val)
        rows = []
        for i, d in enumerate(rows_raw):
            paid_text = "✓" if d["paid"] else ""
            home_text = "כן" if d["home_delivery"] else "לא"
            created = d.get("created_at") or ""
            # capture id in lambda default parameter
            actions = ft.Row([
                ft.IconButton(icon=ft.Icons.EDIT, tooltip="ערוך", on_click=lambda e, did=d["id"]: open_edit(did)),
                ft.IconButton(icon=ft.Icons.DELETE, tooltip="מחק", on_click=lambda e, did=d["id"]: confirm_delete(did)),
                ft.IconButton(icon=ft.Icons.PRINT, tooltip="הדפס (תצוגה)", on_click=lambda e, did=d["id"]: export_single_pdf_preview(get_delivery_by_id(did), page)),
            ])
            rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(d["id"]))),
                    ft.DataCell(ft.Text(d["name"])),
                    ft.DataCell(ft.Text(d["address"] or "-")),
                    ft.DataCell(ft.Text(d["phone1"] or "-")),
                    ft.DataCell(ft.Text(d["phone2"] or "-")),
                    ft.DataCell(ft.Text(paid_text)),
                    ft.DataCell(ft.Text(home_text)),
                    ft.DataCell(ft.Text(created)),
                    ft.DataCell(actions),
                ], color="#f8f8f8" if i % 2 == 0 else "#ffffff")
            )

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("שם", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("כתובת", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("טלפון 1", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("טלפון 2", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("שולם", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("עד הבית", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("תאריך", weight=ft.FontWeight.BOLD)),
                ft.DataColumn(ft.Text("פעולות", weight=ft.FontWeight.BOLD)),
            ],
            rows=rows,
            heading_row_color="#52b69a",
            border=ft.border.all(1, ft.Colors.GREY_300),
            column_spacing=12,
            divider_thickness=1,
            data_row_min_height=56,
            expand=True
        )

        if data_table.current:
            try:
                page.controls.remove(data_table.current)
            except ValueError:
                pass
        data_table.current = table
        page.controls.append(table)
        page.update()

    # dialogs (edit/add)
    def open_edit(delivery_id=None):
        if delivery_id:
            d = get_delivery_by_id(delivery_id)
            if not d:
                page.snack_bar = ft.SnackBar(ft.Text("משלוח לא נמצא"))
                page.snack_bar.open = True
                page.update()
                return
            name_val, addr_val, p1_val, p2_val = d["name"], d["address"] or "", d["phone1"] or "", d["phone2"] or ""
            paid_val, home_val, notes_val = bool(d["paid"]), bool(d["home_delivery"]), d.get("notes") or ""
        else:
            name_val = addr_val = p1_val = p2_val = notes_val = ""
            paid_val = home_val = False

        name_field = ft.TextField(label="שם", value=name_val, width=400)
        address_field = ft.TextField(label="כתובת", value=addr_val, width=400, multiline=True)
        phone1_field = ft.TextField(label="טלפון 1", value=p1_val)
        phone2_field = ft.TextField(label="טלפון 2", value=p2_val)
        paid_cb = ft.Checkbox(label="שולם", value=paid_val)
        home_cb = ft.Checkbox(label="עד הבית", value=home_val)
        notes_field = ft.TextField(label="הערות", value=notes_val, multiline=True, width=400)

        def close():
            page.overlay.clear()
            page.update()

        def save(e):
            try:
                if delivery_id:
                    update_delivery(delivery_id, name_field.value, address_field.value, phone1_field.value, phone2_field.value, paid_cb.value, home_cb.value, notes_field.value)
                    page.snack_bar = ft.SnackBar(ft.Text("המשלוח עודכן"))
                else:
                    add_delivery(name_field.value, address_field.value, phone1_field.value, phone2_field.value, paid_cb.value, home_cb.value, user["id"], notes_field.value)
                    page.snack_bar = ft.SnackBar(ft.Text("משלוח נוסף"))
                page.snack_bar.open = True
                page.update()
                close()
                load_table()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"שגיאה בשמירה: {ex}"))
                page.snack_bar.open = True
                page.update()

        dlg = ft.Container(
            content=ft.Column([
                ft.Text("עריכת משלוח" if delivery_id else "הוספת משלוח", size=20, weight=ft.FontWeight.BOLD),
                name_field, address_field,
                ft.Row([phone1_field, phone2_field], spacing=10),
                ft.Row([paid_cb, home_cb], spacing=20),
                notes_field,
                ft.Row([
                    ft.ElevatedButton("שמור", on_click=save, bgcolor="#52b69a", color="white"),
                    ft.ElevatedButton("ביטול", on_click=lambda e: close(), bgcolor="#f28c7d", color="white"),
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=12)
            ], spacing=10),
            padding=20, bgcolor="#ffffff", border_radius=12
        )
        page.overlay.clear()
        page.overlay.append(dlg)
        page.update()

    def confirm_delete(delivery_id):
        def do_delete(e):
            try:
                delete_delivery(delivery_id)
                page.snack_bar = ft.SnackBar(ft.Text("המשלוח נמחק"))
                page.snack_bar.open = True
                page.update()
                page.overlay.clear()
                load_table()
            except Exception as ex:
                page.snack_bar = ft.SnackBar(ft.Text(f"שגיאה במחיקה: {ex}"))
                page.snack_bar.open = True
                page.update()

        dlg = ft.Container(
            content=ft.Column([
                ft.Text("מחק משלוח", size=18, weight=ft.FontWeight.BOLD),
                ft.Text("האם למחוק את המשלוח?"),
                ft.Row([
                    ft.ElevatedButton("מחק", on_click=do_delete, bgcolor="#f28c7d", color="white"),
                    ft.ElevatedButton("ביטול", on_click=lambda e: page.overlay.clear(), bgcolor="#888", color="white")
                ], alignment=ft.MainAxisAlignment.CENTER, spacing=12)
            ], spacing=10),
            padding=20, bgcolor="#ffffff", border_radius=12
        )
        page.overlay.clear()
        page.overlay.append(dlg)
        page.update()

    # export monthly with selected month from dropdown
    def on_export_month(e):
        # parse selected month
        month_val = month_picker.current.value
        if month_val:
            y, m = map(int, month_val.split("-"))
        else:
            now = datetime.now()
            y, m = now.year, now.month
        path = export_month_pdf_download(page, year=y, month=m)
        # try to open the folder containing the file (optional)
        try:
            folder = os.path.dirname(path)
            # open folder in file explorer
            if os.name == 'nt':
                os.startfile(folder)
        except Exception:
            pass

    # --- Build UI ---
    search_field_control = ft.TextField(ref=search_field, label="חיפוש לפי שם / טלפון", width=300, on_change=load_table)
    only_unpaid_control = ft.Checkbox(ref=only_unpaid, label="הצג רק לא שולם", value=False, on_change=load_table)

    controls = ft.Column([
        ft.Row([ft.Text("מעקב משלוחים", size=28, weight=ft.FontWeight.BOLD, color="#52b69a")]),
        ft.Row([
            search_field_control,
            only_unpaid_control,
            month_picker_control,
            ft.ElevatedButton("➕ הוסף משלוח", on_click=lambda e: open_edit(None), bgcolor="#52b69a", color="white"),
            ft.ElevatedButton("ייצוא דוח חודשי PDF", on_click=on_export_month, bgcolor="#4d96ff", color="white"),
            ft.ElevatedButton("חזור", on_click=lambda e: navigator.go_home(user), bgcolor="#f28c7d", color="white"),
        ], alignment=ft.MainAxisAlignment.CENTER, spacing=12),
    ], spacing=12, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    page.controls.clear()
    page.add(controls)
    load_table()

    # if Arial not registered, tell user via snack
    if _FONT_NAME != "ArialHeb" and _BIDI_AVAILABLE is False:
        # only notify once
        page.snack_bar = ft.SnackBar(ft.Text("לשיפור תמיכת עברית בפורמטים PDF מומלץ: להתקין 'arial.ttf' בתיקיית assets ו-'python-bidi' + 'arabic-reshaper' בסביבת הפייתון."))
        page.snack_bar.open = True
        page.update()

    page.update()