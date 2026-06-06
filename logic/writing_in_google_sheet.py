import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

from logic.db import resource_path
from logic.products import get_id_by_product_name, get_vista_name
# הגדרת ההרשאות
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
json_path = resource_path("alien-drake-445721-e9-e11ed308249c.json")
creds = ServiceAccountCredentials.from_json_keyfile_name(
    json_path, scope
)
client = gspread.authorize(creds)


def write(supplier_id, header: dict, item):
    print(">>> Entering regular write function for supplier_id:", supplier_id)
    print("Header:", header)
    print("Item:", item)

    from logic.suppliers import get_supplier_google_sheet_link
    sheet_url = get_supplier_google_sheet_link(supplier_id)
    spreadsheet = client.open_by_url(sheet_url[0]["googleSheetLink"])

    # בוחרים גיליון לפי חודש ושנה
    if supplier_id != 6:
        now = datetime.now()
        month = now.month
        year_short = str(now.year)[-2:]
        possible_names = [f"{month:02d}.{year_short}", f"{month}.{year_short}"]

        # אם לא נמצא, מחפשים חודש קודם
        if month > 1:
            prev_month = month - 1
            possible_names.extend([f"{prev_month:02d}.{year_short}", f"{prev_month}.{year_short}"])

        # מנסים למצוא גיליון קיים
        sheet = None
        for name in possible_names:
            try:
                sheet = spreadsheet.worksheet(name)
                print(f">>> Found sheet: {name}")
                break
            except:
                continue

        # אם לא מצאנו עדיין, לוקחים את האחרון
        if not sheet:
            sheet = spreadsheet.worksheets()[-1]
            print(f">>> Sheet not found in list, using last sheet: {sheet.title}")
    else:
        # במקרה הזה ספק 6 לא מגיע לכאן בכלל
        return

    # פונקציה לעיבוד פריט
    def item_to_row(header, item):
        from logic.customers import get_customer_name_by_id
        customer_name = get_customer_name_by_id(header["customer_id"])
        name = customer_name.get("name")
        notes = header.get('notes','')
        order_date = datetime.now().strftime("%d/%m/%Y")
        p = item['product_name']
        product_id = get_id_by_product_name(p)
        quantity = item['quantity']
        bc = header.get('curvature', "")
        size_parts = item['size'].split()
        number = size_parts[0] if len(size_parts) > 0 else ""
        cylinder = size_parts[1] if len(size_parts) > 1 else ""
        degrees = size_parts[2] if len(size_parts) > 2 else ""
        color = header.get('color', "") or ""
        multifokal = header.get('multifokal', "")
        color_or_multifokal = multifokal if color == "" else color
        prescription = "עדשות מגע" if header['prescription'] == "עדשות" else "משקפיים"
        status = "צריך להזמין"
        print(f"notes {notes}")
        if notes != "":
            return [name, order_date, p, quantity, bc, number, cylinder, degrees, color_or_multifokal,
                    prescription, status, notes]
        return [name, order_date, p, quantity, bc, number, cylinder, degrees, color_or_multifokal, prescription,
                status]

    # כותבים את כל הפריטים לגיליון
    row = item_to_row(header, item)
    row = [str(x) if x is not None else "" for x in row]
    print(">>> Row to append:", row, "Length:", len(row))
    # במקום append_row, נמצא את השורה הפנויה הראשונה ונכתוב אליה ישירות מתוך עמודה A
    try:
        # מוצא את מספר השורה האחרונה שיש בה תוכן + 1
        next_row = len(sheet.get_all_values()) + 1

        # מגדיר טווח שמתחיל תמיד בעמודה A (למשל A85)
        range_to_update = f"A{next_row}"

        # מעדכן את השורה החל מעמודה A
        sheet.update(range_to_update, [row], value_input_option="USER_ENTERED")

        print(f"✅ Row updated successfully at {range_to_update}")
    except Exception as e:
        print("❌ Exception while updating row:", e)
        raise


def write_supplier2_google_sheet(supplier_id, header: dict, item):
    print(">>> Entering supplier2 sheet write function for supplier_id:", supplier_id)
    print("Header:", header)
    print("Item:", item)
    from logic.suppliers import get_supplier_google_sheet_link
    sheet_url = get_supplier_google_sheet_link(supplier_id)
    sheet = client.open_by_url(sheet_url[0]["googleSheetLink"]).sheet1

    def item_to_row_supplier2(header, item):
        from logic.customers import get_customer_name_by_id
        customer_name = get_customer_name_by_id(header["customer_id"])  # אפשר להביא מה-DB לפי customer_id
        name = customer_name.get("name")
        order_date = datetime.now().strftime("%d/%m/%Y")
        product = item['product_name']
        if product == "אואזיס":
            product = "אואסיס בודד"
        quantity = item['quantity']

        # פיצול size
        size_parts = item['size'].split()
        number = size_parts[0] if len(size_parts) > 0 else ""
        cylinder = size_parts[1] if len(size_parts) > 1 else ""
        degrees = size_parts[2] if len(size_parts) > 2 else ""
        notes = header.get('notes',"")

        return [  order_date, product, number, cylinder, degrees, quantity, notes, "", "", name ]

    row = item_to_row_supplier2(header, item)
    row = [str(x) if x is not None else "" for x in row]
    print(">>> Row to append:", row, "Length:", len(row))
    try:
        sheet.append_row(row, value_input_option="USER_ENTERED")
        print("✅ Row appended successfully")
    except Exception as e:
        import traceback
        print("❌ Exception while appending row:", e)
        print("Full traceback:")
        traceback.print_exc()
        print(">>> Check row for invalid characters or length over limit")
        print("Row length (characters):", sum(len(str(x)) for x in row))
        raise


