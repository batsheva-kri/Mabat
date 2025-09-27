import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "Mabat_db.db")  # מיקום קובץ DB
print("DB_PATH:", DB_PATH)

# def run_query(query, params=()):
#     print("Running SQL Query:", query, "Params:", params)
#     try:
#         conn = get_connection()
#         cursor = conn.cursor()
#         cursor.execute(query, params)
#         rows = cursor.fetchall()
#         print("Query returned", len(rows), "rows")
#         return [dict(row) for row in rows]
#     except sqlite3.Error as e:
#         print("SQL Query failed:", e)
#         return []
#     finally:
#         conn.close()
def get_connection():
    """יוצר חיבור למסד הנתונים עם timeout ומוודא מצב WAL"""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5)
    conn.row_factory = sqlite3.Row
    # הפעלת WAL mode לשיפור עבודה במקביל
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn
def run_query(query, params=()):
    print("Running SQL Query:", query, "Params:", params)
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        print("Query returned", len(rows), "rows")
        return [dict(row) for row in rows]
    except sqlite3.Error as e:
        print("SQL Query failed:", e)
        return []
    finally:
        conn.close()

def run_action(query, params=()):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()

    conn.close()