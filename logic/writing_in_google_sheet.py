import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from logic.products import get_id_by_product_name, get_vista_name
# הגדרת ההרשאות
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "alien-drake-445721-e9-e11ed308249c.json", scope
)
client = gspread.authorize(creds)
def write(supplier_id,header:dict,items):
    from logic.suppliers import get_supplier_google_sheet_link
    sheet_url = get_supplier_google_sheet_link(supplier_id)
    spreadsheet = client.open_by_url(sheet_url[0]["googleSheetLink"])
    sheet = spreadsheet.worksheets()[-2]
    # פונקציה לעיבוד פריט
    def item_to_row(header, item):
        from logic.customers import get_customer_name_by_id
        customer_name = get_customer_name_by_id(header["customer_id"]) # אפשר להביא מה-DB לפי customer_id
        name = customer_name.get("name")
        notes = ""
        order_date = datetime.now().strftime("%d/%m/%Y")
        p = item['product_name']  # כאן אפשר לשים לוגיקה למציאת "הכי דומה"
        product_id = get_id_by_product_name(p)
        quantity = item['quantity']
        product_and_count = get_vista_name(product_id,quantity)
        if not product_and_count:
            notes = item['product_name']
            product = ""
        else:
            product = product_and_count["name"]
            quantity = product_and_count["count"]
        bc = header.get('curvature', "")

        # פיצול size
        size_parts = item['size'].split()
        number = size_parts[0] if len(size_parts) > 0 else ""
        cylinder = size_parts[1] if len(size_parts) > 1 else ""
        degrees = size_parts[2] if len(size_parts) > 2 else ""
        color = header.get('color', "")
        if color == None:
            color = ""
        multifokal = header.get('multifokal', "")
        if color == "":
            color_or_multifokal = multifokal
        else:
            color_or_multifokal = color
        prescription = "עדשות מגע" if header['prescription'] == "עדשות" else "משקפיים"
        status = "צריך להזמין"
        if notes != "":
            return [name, order_date, product, quantity, bc, number, cylinder, degrees, color_or_multifokal, prescription, status, notes ]
        return [name, order_date, product, quantity, bc, number, cylinder, degrees, color_or_multifokal, prescription, status]


    # לעבור על כל הפריטים ולכתוב ל-Sheet
    for item in items:
        row = item_to_row(header, item)
        sheet.append_row(row, value_input_option="USER_ENTERED")

def write_supplier2_google_sheet(supplier_id, header: dict, items):
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

        # הערות – אפשר למלא כאן מה שנוח לך
        notes = ""

        return [  order_date, product, number, cylinder, degrees, quantity, notes, "", "", name ]

    for item in items:
        row = item_to_row_supplier2(header, item)
        sheet.append_row(row, value_input_option="USER_ENTERED")
