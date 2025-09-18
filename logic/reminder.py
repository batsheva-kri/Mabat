from datetime import datetime

from logic.utils import run_query


def check_or_create_reminder():
    """בודק אם צריך ליצור משימה חדשה, ומחזיר אותה אם לא בוצעה"""
    today = datetime.today()
    day = today.day
    month_year = today.strftime("%Y-%m")
    print(today)
    if day in (1, 15):
        print("this dayyyyyy")
        existing = run_query("SELECT * FROM reminders WHERE month_year=?", (month_year,), fetchone=True)
        print("not existing")
        if not existing:
            run_query(
                "INSERT INTO reminders (month_year, done) VALUES (?,0)",
                (month_year,),
                commit=True
            )

    return run_query(
        "SELECT * FROM reminders WHERE month_year=? AND done=0",
        (month_year,),
        fetchone=True
    )


def mark_done(month_year):
    run_query("UPDATE reminders SET done=1 WHERE month_year=?", (month_year,), commit=True)
