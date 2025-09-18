from .db import run_query, run_action
from datetime import datetime

def authenticate_by_password(password: str):
    users = run_query("SELECT * FROM users WHERE password_=?", (password,))
    if users:
        user = users[0]
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        run_action(
            "INSERT INTO worker_reports (user_id, date_, enter_time) VALUES (?, ?, ?)",
            (user["id"], now.split(" ")[0], now.split(" ")[1])
        )
        return user
    return None

def logout(user_id: int):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    run_action(
        "UPDATE worker_reports SET exit_time=? WHERE user_id=? AND exit_time IS NULL",
        (now.split(" ")[1], user_id)
    )
