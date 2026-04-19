from django.db import connection


def custom_sql_select(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def login_sql_select(email, password):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Users WHERE email = %s AND password = %s", [email, password])
        columns = [col[0] for col in cursor.description]
        login_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        if login_data != []:
            return login_data[0]
        else:
            return False


def register_sql_insert(name, email, password, phone=None):
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO Users (name, email, phone, password, role) VALUES (%s, %s, %s, %s, 'customer')",
            [name, email, phone, password],
        )
        connection.commit()
        return cursor.lastrowid


def get_user_by_email(email):
    """
    Fetch a single user row by email.
    Returns a dict if found, otherwise None.
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Users WHERE email = %s", [email])
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return rows[0] if rows else None


def get_user_by_id(user_id):
    """
    Fetch a single user row by user_id.
    Returns a dict if found, otherwise None.
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Users WHERE user_id = %s", [user_id])
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return rows[0] if rows else None


def register_user_if_new(name, email, password, phone=None):
    """
    Insert a user only if the email does not already exist.
    Returns the new user_id when created, or None if duplicate.
    """
    existing = get_user_by_email(email)
    if existing:
        return None
    return register_sql_insert(name, email, password, phone)


def update_profile_sql(user_id, name=None, email=None, phone=None):
    """
    Update the User table for a given user_id.
    Only updates fields that are not None.
    """
    fields = []
    values = []

    if name is not None:
        fields.append("name = %s")
        values.append(name)
    if email is not None:
        fields.append("email = %s")
        values.append(email)
    if phone is not None:
        fields.append("phone = %s")
        values.append(phone)

    if not fields:
        return False  # nothing to update

    values.append(user_id)  # for WHERE clause

    sql = f"UPDATE Users SET {', '.join(fields)} WHERE user_id = %s"

    with connection.cursor() as cursor:
        cursor.execute(sql, values)
        connection.commit()
        return cursor.rowcount > 0  # True if at least 1 row updated


def get_items_by_ids(item_ids):
    """
    Return a list of Items rows (as dicts) for the given item_ids.
    Uses parameterised SQL to avoid injection.
    """
    if not item_ids:
        return []

    placeholders = ",".join(["%s"] * len(item_ids))
    sql = f"SELECT * FROM Items WHERE item_id IN ({placeholders})"

    with connection.cursor() as cursor:
        cursor.execute(sql, list(item_ids))
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_user_addresses(user_id):
    """
    Return all addresses for a given user_id using Address and UserAddress tables.
    """
    sql = """
        SELECT a.addr_id, a.province, a.city, a.area, a.houseNumber
        FROM Address a
        INNER JOIN UserAddress ua ON a.addr_id = ua.addr_id
        WHERE ua.user_id = %s
        ORDER BY a.addr_id
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [user_id])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def create_address(province, city, area, house_number):
    """
    Insert a new address and return its addr_id.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO Address (province, city, area, houseNumber) VALUES (%s, %s, %s, %s)",
            [province, city, area, house_number],
        )
        connection.commit()
        return cursor.lastrowid


def link_user_address(user_id, addr_id):
    """
    Link a user to an address in UserAddress table.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO UserAddress (user_id, addr_id) VALUES (%s, %s)",
            [user_id, addr_id],
        )
        connection.commit()


def delete_user_address(user_id, addr_id):
    """
    Remove a mapping from UserAddress and, for simplicity, delete the address row.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM UserAddress WHERE user_id = %s AND addr_id = %s",
            [user_id, addr_id],
        )
        cursor.execute("DELETE FROM Address WHERE addr_id = %s", [addr_id])
        connection.commit()


def fetch_items(category=None, subcategory=None):
    """
    Return items optionally filtered by category and/or subcategory.
    Uses joins with parameters to avoid SQL injection.
    """
    sql = """
        SELECT i.* FROM Items i
        LEFT JOIN SubCategory s ON i.item_id = s.item_id
        LEFT JOIN Category c ON s.cat_id = c.cat_id
    """
    conditions = []
    params = []

    if category:
        conditions.append("c.categoryName = %s")
        params.append(category)
    if subcategory:
        conditions.append("s.subCatName = %s")
        params.append(subcategory)

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    sql += " GROUP BY i.item_id"

    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_item_by_id(item_id):
    """
    Fetch a single item by its id using parameterised SQL.
    Returns a dict or None if not found.
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Items WHERE item_id = %s", [item_id])
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return rows[0] if rows else None


def get_user_orders(user_id):
    """
    Fetch basic order history for a user from the Orders table.
    Returns a list of dicts with order_id, order_date, order_status, totalPrice.
    """
    sql = """
        SELECT order_id, order_date, order_status, totalPrice
        FROM Orders
        WHERE user_id = %s
        ORDER BY order_date DESC, order_id DESC
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [user_id])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

