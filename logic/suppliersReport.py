from logic.utils import run_query

def get_products_report(supplier_id, start_date, end_date):
    query = """
    SELECT si.product_id,
           p.name AS product_name,
           SUM(si.quantity) AS total_quantity
    FROM supplier_invitations si
    JOIN products p ON si.product_id = p.id
    WHERE si.close = 1
      AND (si.supplier_id = ? OR ? = 0)
      AND si.date_ BETWEEN ? AND ?
    GROUP BY si.product_id
    ORDER BY p.name
    """
    ret = run_query(query, (supplier_id, supplier_id, start_date, end_date), fetchall=True)
    return ret


def get_product_sizes_report(product_id, supplier_id, start_date, end_date):
    query = """
    SELECT si.size AS size,
           SUM(si.quantity) AS quantity
    FROM supplier_invitations si
    WHERE si.close = 1
      AND si.product_id = ?
      AND (si.supplier_id = ? OR ? = 0)
      AND si.date_ BETWEEN ? AND ?
    GROUP BY si.size
    ORDER BY size
    """
    ret = run_query(query, (product_id, supplier_id, supplier_id, start_date, end_date), fetchall=True)
    return ret
