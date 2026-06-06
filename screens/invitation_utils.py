import datetime


def format_datetime(date_str):
    """מפרמט מחרוזת תאריך לתצוגה של תאריך ושעה בנפרד"""
    try:
        if not date_str:
            return "", ""
        dt = datetime.datetime.fromisoformat(date_str)
        return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M:%S")
    except Exception:
        return date_str, ""


def parse_size_parts(raw_size):
    """מפרק מחרוזת מידה (Size) לשלושה חלקים: ספירה, צילינדר וזווית"""
    sphere, cylinder, axis = "", "", ""
    if isinstance(raw_size, str) and raw_size:
        parts = raw_size.split()
        if len(parts) >= 1: sphere = parts[0]
        if len(parts) >= 2: cylinder = parts[1]
        if len(parts) >= 3: axis = parts[2]
    return sphere, cylinder, axis


def prepare_invitation_copy(existing_invitation, current_user, copy=False):
    """מכין עותק של הזמנה קיימת לצרכי עריכה או שכפול"""
    if not existing_invitation:
        return None

    new_inv = existing_invitation.copy()
    user_id = int(current_user["id"]) if isinstance(current_user, dict) else None

    if copy:
        new_inv.pop("id", None)
        new_inv["created_by_user_id"] = user_id
        new_inv["date"] = datetime.datetime.now().isoformat()
        new_inv["status"] = "open"
        new_inv["shipped"] = 0
        new_inv["answered"] = 0
        new_inv["want_shipping"] = 0

    return new_inv