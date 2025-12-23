import sqlite3
import os
import sys

# -----------------------------
# הגדרת מיקום ה-DB
# -----------------------------
db_dir = os.path.join(os.getenv("APPDATA"), "Mabat")
os.makedirs(db_dir, exist_ok=True)
DB_PATH = os.path.join(db_dir, "Mabat_db.db")
print("Using DB:", DB_PATH)
assert os.path.exists(DB_PATH), "DB file not found!"

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# -----------------------------
# אתחול חד פעמי: ממזג WAL אם קיים → עובר ל-DELETE
# -----------------------------
def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    try:
        wal_path = DB_PATH + "-wal"
        if os.path.exists(wal_path):
            print("Merging WAL → FULL checkpoint...")
            conn.execute("PRAGMA wal_checkpoint(FULL);")

        mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        if mode.upper() != "DELETE":
            print("Switching journal_mode to DELETE...")
            conn.execute("PRAGMA journal_mode=DELETE;")
    finally:
        conn.close()

initialize_database()

# -----------------------------
# פונקציה לחיבור נקי ל-DB
# -----------------------------
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=DELETE;")
    return conn

# -----------------------------
# ביצוע SELECT/שאילתות עם החזרת תוצאות
# -----------------------------
def run_query(query, params=(), fetchone=False, fetchall=False, commit=False):
    """
    - fetchone/fetchall מחזירים שורות SELECT
    - commit מבצע commit על INSERT/UPDATE/DELETE
    - בפעולת INSERT שמבוצעת עם commit – מחזיר lastrowid
    """
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            try:
                cur.execute(query, params)

                # במקרה של INSERT
                if query.strip().upper().startswith("INSERT") and commit:
                    conn.commit()
                    return cur.lastrowid

                # פעולות שינוי אחרות
                if commit:
                    conn.commit()

                # SELECT — שורה אחת
                if fetchone:
                    row = cur.fetchone()
                    return dict(row) if row else None

                # SELECT — כל השורות
                if fetchall:
                    rows = cur.fetchall()
                    return [dict(r) for r in rows] if rows else []

            finally:
                cur.close()

    except sqlite3.Error as e:
        print("SQL Error:", e)
        return []


# -----------------------------
# ביצוע פעולות ללא החזרת תוצאה
# -----------------------------

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
    """
    מבצע INSERT/UPDATE/DELETE ומבצע commit באופן בטוח
    """
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            try:
                cur.execute(query, params)
                conn.commit()
                print("Action executed:", query, "Params:", params)
            finally:
                cur.close()
    except sqlite3.Error as e:
        print("SQL Action failed:", e)
