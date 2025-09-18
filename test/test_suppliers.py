from logic.suppliers import add_supplier, update_supplier, get_supplier_by_id, delete_supplier, get_supplier_catalog, add_supplier_catalog_entry, update_supplier_catalog_entry, delete_supplier_catalog_entry,add_supplier_invitations, mark_supplied


print("\n--- בדיקות פונקציות ניהול ספקים ---")

# 1. הוספת ספק
print("\n1. הוספת ספק:")
add_supplier({
    "Id": 1,
    "Name": "ספק עדשות בע\"מ",
    "Phone": "03-1234567",
    "Email": "supplier@example.com"
})
print("ספק נוסף בהצלחה.")

# 2. שליפת ספק
print("\n2. שליפת ספק לפי ID:")
supplier = get_supplier_by_id(1)
print(supplier)

# 3. עדכון ספק
print("\n3. עדכון ספק:")
update_supplier(1, {"Phone": "03-7654321"})
print("אחרי עדכון:", get_supplier_by_id(1))

# 4. הוספת פריט למחירון ספק
print("\n4. הוספת פריט למחירון:")
add_supplier_catalog_entry({
    "Supplier_id": 1,
    "Product_id": 101,
    "Price": 250
})
print(get_supplier_catalog(1))

# 5. עדכון מחיר במחירון
print("\n5. עדכון מחיר במחירון:")
update_supplier_catalog_entry(1, 101, {"Price": 260})
print(get_supplier_catalog(1))

# 6. מחיקת פריט מהמחירון
print("\n6. מחיקת פריט מהמחירון:")
delete_supplier_catalog_entry(1, 101)
print(get_supplier_catalog(1))

# 7. בדיקת הזמנות ספקים
print("\n7. הוספת הזמנה לספק (דורש שהמוצר יופיע ב-Products עם ספק מועדף):")
# לשם בדיקה, נכניס ידנית מוצר לספק
from dal.suppliers_dal import load_data, save_data
data = load_data()
data["Products"].append({
    "Id": 5001,
    "Name": "עדשה חודשית",
    "Suppliers_priority_id": 1
})
save_data(data)

add_supplier_invitations([5001])
print("הזמנות ספקים אחרי הוספה:", load_data()["Supplier_invitations"])

# 8. סימון כ- supplied
print("\n8. סימון הזמנה שסופקה:")
if load_data()["Supplier_invitations"]:
    inv_id = load_data()["Supplier_invitations"][0]["Id"]
    mark_supplied(inv_id)
    print(load_data()["Supplier_invitations"])
else:
    print("אין הזמנות לספק.")

# 9. מחיקת ספק
print("\n9. מחיקת ספק:")
delete_supplier(1)
print(load_data()["Suppliers"])
