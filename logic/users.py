from logic.utils import run_query

def get_all_users():
    query = """
    SELECT id, user_name
    FROM users
    ORDER BY user_name
    """
    return run_query(query, fetchall=True)

def get_user_by_id(user_id):
    query = """
    SELECT id, user_name
    FROM users
    WHERE id = ?
    """
    params = (user_id,)
    return run_query(query, params, fetchone=True)
