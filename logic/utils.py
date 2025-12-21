# # import os
# # import sqlite3
# #
# # BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # תיקיית logic
# # DB_PATH = os.path.join(BASE_DIR, "..", "Mabat_db.db")
# # DB_PATH = os.path.normpath(DB_PATH)
# #
# # def run_query(query, params=(), fetchone=False, fetchall=False, commit=False):
# #     with sqlite3.connect(DB_PATH) as conn:
# #         conn.row_factory = sqlite3.Row
# #         cur = conn.cursor()
# #         cur.execute(query, params)
# #         if commit:
# #             conn.commit()
# #         if fetchone:
# #             row = cur.fetchone()
# #             return dict(row) if row else None
# #         if fetchall:
# #             rows = cur.fetchall()
# #             return [dict(r) for r in rows]
# #     return None
# import os
# import sqlite3
# from datetime import datetime
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # תיקיית logic
# DB_PATH = os.path.join(BASE_DIR, "..", "Mabat_db.db")
# DB_PATH = os.path.normpath(DB_PATH)
#
# def run_query(query, params=(), fetchone=False, fetchall=False, commit=False, return_lastrowid=False):
#     import sqlite3
#     with sqlite3.connect(DB_PATH, timeout=10) as conn:
#         conn.row_factory = sqlite3.Row
#         cur = conn.cursor()
#         try:
#             cur.execute(query, params)
#             if commit:
#                 conn.commit()
#                 if return_lastrowid:
#                     return cur.lastrowid  # מחזיר את ה-ID שנוצר
#             if fetchone:
#                 row = cur.fetchone()
#                 return dict(row) if row else None
#             if fetchall:
#                 rows = cur.fetchall()
#                 return [dict(r) for r in rows]
#         finally:
#             cur.close()
#     return None
#
#
# def insert_worker_entry(user_id: int):
#     """מכניס שורה חדשה לדו"ח עובדים כשעובד מתחבר"""
#     now = datetime.now()
#     run_query(
#         """
#         INSERT INTO worker_reports (user_id, date_, enter_time)
#         VALUES (?, ?, ?)
#         """,
#         (user_id, now.date().isoformat(), now.strftime("%H:%M:%S")),
#         commit=True
#     )
#
# def update_worker_exit(user_id: int):
#     """מעדכן שורת דו"ח עובדים קיימת כשעובד מתנתק"""
#     now = datetime.now()
#     run_query(
#         """
#         UPDATE worker_reports
#         SET exit_time = ?
#         WHERE user_id = ? AND date_ = ? AND exit_time IS NULL
#         """,
#         (now.strftime("%H:%M:%S"), user_id, now.date().isoformat()),
#         commit=True
#     )
#
# def get_all_employees():
#         return run_query("SELECT id, user_name, role FROM users", fetchall=True)
#
# def get_employee_monthly_hours(employee_id: int, month: int, year: int):
#     """מחזיר את שעות העובד לחודש ושנה מסוימים על בסיס enter_time ו-exit_time"""
#     query = """
#         SELECT date_, enter_time, exit_time
#         FROM worker_reports
#         WHERE user_id = ?
#           AND strftime('%m', date_) = ?
#           AND strftime('%Y', date_) = ?
#     """
#     month_str = f"{month:02d}"
#     year_str = str(year)
#     rows = run_query(query, (employee_id, month_str, year_str), fetchall=True)
#
#     results = []
#     if rows:
#         for r in rows:
#             enter = r["enter_time"]
#             exit_ = r["exit_time"]
#             if enter and exit_:
#                 # חישוב שעות
#                 fmt = "%H:%M:%S"
#                 t_enter = datetime.strptime(enter, fmt)
#                 t_exit = datetime.strptime(exit_, fmt)
#                 diff = t_exit - t_enter
#                 hours = round(diff.total_seconds() / 3600, 2)  # שעות עם 2 ספרות אחרי הנקודה
#             else:
#                 hours = 0
#             results.append({"date": r["date_"], "hours": hours})
#     return results
import os
import sqlite3
from datetime import datetime

from logic.db import get_connection

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # תיקיית logic
# DB_PATH = os.path.join(BASE_DIR, "..", "Mabat_db.db")
# DB_PATH = os.path.normpath(DB_PATH)

def run_query(query, params=(), fetchone=False, fetchall=False, commit=False):
    """
    מבצע שאילתה על מסד הנתונים.
    - fetchone/fetchall מחזירים שורות SELECT
    - commit מבצע commit על INSERT/UPDATE/DELETE
    - מחזיר lastrowid במקרה של INSERT רגיל
    - מחזיר את התוצאה במקרה של INSERT ... RETURNING
    """
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(query, params)

        # אם השאילתה משנה נתונים
        if commit:
            conn.commit()

        # אם זה SELECT / RETURNING
        if fetchone:
            row = cur.fetchone()
            return dict(row) if row else None
        if fetchall:
            rows = cur.fetchall()
            return [dict(r) for r in rows]

        # במקרה של INSERT רגיל בלי RETURNING
        if query.strip().upper().startswith("INSERT") and "RETURNING" not in query.upper() and commit:
            return cur.lastrowid

    except sqlite3.Error as e:
        print("SQL Error:", e)
        return None
    finally:
        cur.close()
        conn.close()

def insert_worker_entry(user_id: int):
    """מכניס שורה חדשה לדו"ח עובדים כשעובד מתחבר"""
    now = datetime.now()
    run_query(
        """
        INSERT INTO worker_reports (user_id, date_, enter_time)
        VALUES (?, ?, ?)
        """,
        (user_id, now.date().isoformat(), now.strftime("%H:%M:%S")),
        commit=True
    )

def update_worker_exit(user_id: int):
    """מעדכן שורת דו"ח עובדים קיימת כשעובד מתנתק"""
    now = datetime.now()
    run_query(
        """
        UPDATE worker_reports
        SET exit_time = ?
        WHERE user_id = ? AND date_ = ? AND exit_time IS NULL
        """,
        (now.strftime("%H:%M:%S"), user_id, now.date().isoformat()),
        commit=True
    )

def get_all_employees():
        return run_query("SELECT id, user_name, role FROM users", fetchall=True)

def get_employee_monthly_hours(employee_id: int, month: int, year: int):
    """מחזיר את שעות העובד לחודש ושנה מסוימים על בסיס enter_time ו-exit_time"""
    query = """
        SELECT date_, enter_time, exit_time
        FROM worker_reports
        WHERE user_id = ? 
          AND strftime('%m', date_) = ? 
          AND strftime('%Y', date_) = ?
    """
    month_str = f"{month:02d}"
    year_str = str(year)
    rows = run_query(query, (employee_id, month_str, year_str), fetchall=True)

    results = []
    if rows:
        for r in rows:
            enter = r["enter_time"]
            exit_ = r["exit_time"]
            if enter and exit_:
                # חישוב שעות
                fmt = "%H:%M:%S"
                t_enter = datetime.strptime(enter, fmt)
                t_exit = datetime.strptime(exit_, fmt)
                diff = t_exit - t_enter
                hours = round(diff.total_seconds() / 3600, 2)  # שעות עם 2 ספרות אחרי הנקודה
            else:
                hours = 0
            results.append({"date": r["date_"], "hours": hours})
    return results