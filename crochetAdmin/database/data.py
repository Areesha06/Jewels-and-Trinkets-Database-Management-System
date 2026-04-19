from django.db import connection
import urllib.request
import urllib.error
import base64
import io

"""
Data-access helpers for the crochetAdmin app.

This module is intentionally aligned with:
- The database schema defined in `database/schema.txt`
- The helper patterns used in `crochetStore/database/data.py`

Key conventions from `schema.txt`:
- Table names: Users, Items, ItemsQuant, Category, SubCategory, Orders, OrderItems, Cart, Wishlist, Complaint, Address, UserAddress
- Primary keys: user_id, item_id, itemQuant_id, cat_id, subcat_id, order_id, orderItem_id, cart_id, wishlist_id, complaint_id, addr_id

Note: The `image` column in Items table is BLOB (binary data), not a URL string.
"""


def custom_sql_select(query):
    """
    Run a raw SELECT query and return a list of dicts.
    Use only for internal/admin tooling where `query` is trusted.
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


# ---------------------------------------------------------------------------
# User helpers (table: Users)
# ---------------------------------------------------------------------------

def login_sql_select(email, password):
    """
    Admin / staff login using the shared `Users` table.
    Uses the same table/columns as defined in `schema.txt`.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM Users WHERE email = %s AND password = %s",
            [email, password],
        )
        columns = [col[0] for col in cursor.description]
        login_data = [dict(zip(columns, row)) for row in cursor.fetchall()]

        if login_data:
            return login_data[0]
        return False


def register_sql_insert(name, email, password, role="customer"):
    """
    Insert a new user row into `Users`.
    Default role is 'customer', but admin/staff roles can be passed explicitly.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO Users (name, email, password, role) VALUES (%s, %s, %s, %s)",
            [name, email, password, role],
        )
        connection.commit()
        return cursor.lastrowid


def get_user_by_email(email):
    """
    Fetch a single user row by email from `Users`.
    Returns a dict if found, otherwise None.
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Users WHERE email = %s", [email])
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return rows[0] if rows else None


def get_user_by_id(user_id):
    """
    Fetch a single user row by user_id from `Users`.
    Returns a dict if found, otherwise None.
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Users WHERE user_id = %s", [user_id])
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return rows[0] if rows else None


def register_user_if_new(name, email, password, role="customer"):
    """
    Insert a user only if the email does not already exist.
    Returns the new user_id when created, or None if duplicate.
    """
    existing = get_user_by_email(email)
    if existing:
        return None
    return register_sql_insert(name, email, password, role=role)


def update_profile_sql(user_id, name=None, email=None, phone=None):
    """
    Update the `Users` table for a given user_id.
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


# ---------------------------------------------------------------------------
# Item / inventory helpers (Items, ItemsQuant, Category, SubCategory)
# ---------------------------------------------------------------------------

def get_items_by_ids(item_ids):
    """
    Return a list of Items rows (as dicts) for the given item_ids.
    Uses parametrised SQL to avoid injection.
    """
    if not item_ids:
        return []

    placeholders = ",".join(["%s"] * len(item_ids))
    sql = f"SELECT * FROM Items WHERE item_id IN ({placeholders})"

    with connection.cursor() as cursor:
        cursor.execute(sql, list(item_ids))
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def fetch_items(category=None, subcategory=None):
    """
    Return items optionally filtered by category and/or subcategory.
    Joins Items, Category, SubCategory according to the schema.
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
    Fetch a single item by its id using parametrised SQL.
    Returns a dict or None if not found.
    Note: image field is BLOB, not URL.
    """
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Items WHERE item_id = %s", [item_id])
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return rows[0] if rows else None


def url_to_blob(image_url):
    """
    Download an image from a URL and convert it to BLOB (bytes) for SQLite storage.
    Returns bytes if successful, None if failed.
    """
    if not image_url or not image_url.strip():
        return None
    
    image_url = image_url.strip()
    
    # Handle data URIs (base64 encoded images)
    if image_url.startswith('data:image'):
        try:
            # Format: data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...
            header, encoded = image_url.split(',', 1)
            return base64.b64decode(encoded)
        except Exception:
            return None
    
    # Handle file:// URLs (local files)
    if image_url.startswith('file://'):
        try:
            file_path = image_url.replace('file://', '')
            with open(file_path, 'rb') as f:
                return f.read()
        except Exception:
            return None
    
    # Handle http:// and https:// URLs
    if image_url.startswith('http://') or image_url.startswith('https://'):
        try:
            req = urllib.request.Request(image_url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            with urllib.request.urlopen(req, timeout=10) as response:
                return response.read()
        except (urllib.error.URLError, urllib.error.HTTPError, Exception):
            return None
    
    # Try as local file path (relative or absolute)
    try:
        with open(image_url, 'rb') as f:
            return f.read()
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Order / Cart / Wishlist / Complaint helpers (admin‑side reporting)
# ---------------------------------------------------------------------------

def get_all_orders():
    """
    Fetch all orders with basic user information.
    Useful for an admin dashboard list.
    """
    sql = """
        SELECT o.*, u.name AS customer_name, u.email AS customer_email
        FROM Orders o
        LEFT JOIN Users u ON o.user_id = u.user_id
        ORDER BY o.order_date DESC
    """
    return custom_sql_select(sql)


def get_order_details(order_id):
    """
    Fetch a single order with its items and related info.
    Joins Orders, OrderItems, ItemsQuant, Items.
    """
    sql = """
        SELECT 
            o.*, 
            oi.orderItem_id,
            oi.quantity,
            oi.price,
            iq.itemQuant_id,
            iq.color,
            iq.stock,
            iq.description AS item_description,
            i.itemName,
            i.basePrice,
            i.image
        FROM Orders o
        LEFT JOIN OrderItems oi ON o.order_id = oi.order_id
        LEFT JOIN ItemsQuant iq ON oi.itemQuant_id = iq.itemQuant_id
        LEFT JOIN Items i ON iq.item_id = i.item_id
        WHERE o.order_id = %s
        ORDER BY oi.orderItem_id
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [order_id])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_complaints(status=None):
    """
    Fetch complaints, optionally filtered by status.
    Joins Complaint with User.
    """
    sql = """
        SELECT c.*, u.name AS user_name, u.email AS user_email
        FROM Complaint c
        LEFT JOIN Users u ON c.user_id = u.user_id
    """
    params = []
    if status:
        sql += " WHERE c.status = %s"
        params.append(status)

    sql += " ORDER BY c.created_at DESC"

    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def update_complaint_status(complaint_id, status):
    """
    Update the status of a complaint (e.g., 'open', 'in_progress', 'resolved').
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE Complaint SET status = %s WHERE complaint_id = %s",
            [status, complaint_id],
        )
        connection.commit()
        return cursor.rowcount > 0


def get_inventory_snapshot():
    """
    High‑level stock snapshot combining Items and ItemsQuant.
    Useful for an admin 'inventory' view.
    
    Note: image field is BLOB, not included here. Use image serving endpoint.
    """
    sql = """
        SELECT 
            i.item_id,
            i.itemName,
            i.basePrice,
            iq.itemQuant_id,
            iq.color,
            iq.stock,
            iq.description,
            CASE WHEN i.image IS NOT NULL THEN 1 ELSE 0 END AS has_image
        FROM Items i
        LEFT JOIN ItemsQuant iq ON i.item_id = iq.item_id
        ORDER BY i.item_id, iq.itemQuant_id
    """
    return custom_sql_select(sql)


# ---------------------------------------------------------------------------
# Admin CRUD helpers
# ---------------------------------------------------------------------------

def list_users():
    """
    Lightweight listing of users for the admin Users tab.
    """
    sql = """
        SELECT user_id, name, email, role, phone, created_at
        FROM Users
        ORDER BY created_at DESC
    """
    return custom_sql_select(sql)


def update_user(user_id, name, email, role, phone=None):
    """
    Update core user fields (name, email, role, phone).
    """
    fields = ["name = %s", "email = %s", "role = %s"]
    values = [name, email, role]
    if phone is not None:
        fields.append("phone = %s")
        values.append(phone)

    values.append(user_id)
    sql = f"UPDATE Users SET {', '.join(fields)} WHERE user_id = %s"

    with connection.cursor() as cursor:
        cursor.execute(sql, values)
        connection.commit()
        return cursor.rowcount > 0


def list_products():
    """
    Aggregate-level product listing for the Products table in admin UI.
    Combines Items with a single stock/description snapshot from ItemsQuant.
    
    Note: image field is BLOB, not included in this query for performance.
    Use get_product_image(item_id) or the image serving endpoint to display images.
    """
    sql = """
        SELECT
            i.item_id,
            i.itemName,
            i.basePrice,
            COALESCE(SUM(iq.stock), 0) AS total_stock,
            CASE WHEN i.image IS NOT NULL THEN 1 ELSE 0 END AS has_image
        FROM Items i
        LEFT JOIN ItemsQuant iq ON i.item_id = iq.item_id
        GROUP BY i.item_id, i.itemName, i.basePrice
        ORDER BY i.item_id DESC
    """
    return custom_sql_select(sql)


def get_product(item_id):
    """
    Fetch a single product with one associated ItemsQuant row (if any).
    """
    sql = """
        SELECT
            i.item_id,
            i.itemName,
            i.basePrice,
            i.image,
            iq.itemQuant_id,
            iq.color,
            iq.stock,
            iq.description
        FROM Items i
        LEFT JOIN ItemsQuant iq ON i.item_id = iq.item_id
        WHERE i.item_id = %s
        ORDER BY iq.itemQuant_id
        LIMIT 1
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [item_id])
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return rows[0] if rows else None


def save_product(item_id, name, price, stock, short_desc, full_desc, image_url, color="default"):
    """
    Create or update a product using Items and a single ItemsQuant row.
    - If item_id is None/0: create new Items and ItemsQuant.
    - If item_id exists: update Items and upsert a single ItemsQuant.
    
    The image_url parameter can be:
    - A URL (http://, https://) - will be downloaded and stored as BLOB
    - A local file path - will be read and stored as BLOB
    - A data URI (data:image/...) - will be decoded and stored as BLOB
    - Empty/None - will store NULL
    
    The image column in Items table is BLOB, not a URL string.
    """
    description = (short_desc or "").strip()
    if full_desc:
        if description:
            description += " - " + full_desc.strip()
        else:
            description = full_desc.strip()

    # Convert image URL to BLOB
    image_blob = url_to_blob(image_url) if image_url else None

    with connection.cursor() as cursor:
        if not item_id:
            # Create new item
            cursor.execute(
                "INSERT INTO Items (itemName, basePrice, image) VALUES (%s, %s, %s)",
                [name, price, image_blob],
            )
            item_id = cursor.lastrowid

            cursor.execute(
                """
                INSERT INTO ItemsQuant (item_id, color, stock, description)
                VALUES (%s, %s, %s, %s)
                """,
                [item_id, color, stock, description],
            )
        else:
            # Update existing item
            # Only update image if a new one was provided
            if image_blob is not None:
                cursor.execute(
                    "UPDATE Items SET itemName = %s, basePrice = %s, image = %s WHERE item_id = %s",
                    [name, price, image_blob, item_id],
                )
            else:
                # Keep existing image if no new URL provided
                cursor.execute(
                    "UPDATE Items SET itemName = %s, basePrice = %s WHERE item_id = %s",
                    [name, price, item_id],
                )

            # Try to update an existing variant; if none, create one.
            cursor.execute(
                "SELECT itemQuant_id FROM ItemsQuant WHERE item_id = %s ORDER BY itemQuant_id LIMIT 1",
                [item_id],
            )
            row = cursor.fetchone()
            if row:
                item_quant_id = row[0]
                cursor.execute(
                    """
                    UPDATE ItemsQuant
                    SET color = %s, stock = %s, description = %s
                    WHERE itemQuant_id = %s
                    """,
                    [color, stock, description, item_quant_id],
                )
            else:
                cursor.execute(
                    """
                    INSERT INTO ItemsQuant (item_id, color, stock, description)
                    VALUES (%s, %s, %s, %s)
                    """,
                    [item_id, color, stock, description],
                )

        connection.commit()
        return item_id


def delete_product(item_id):
    """
    Delete a product and all dependent rows to satisfy foreign keys.

    Order of deletion (per schema.txt):
    - OrderItems, Cart, Wishlist (depend on ItemsQuant)
    - ItemsQuant (depends on Items)
    - SubCategory (depends on Items)
    - Items (root row)
    """
    with connection.cursor() as cursor:
        # Find all itemQuant_ids for this item
        cursor.execute(
            "SELECT itemQuant_id FROM ItemsQuant WHERE item_id = %s",
            [item_id],
        )
        quant_ids = [row[0] for row in cursor.fetchall()]

        if quant_ids:
            placeholders = ",".join(["%s"] * len(quant_ids))

            # Delete from OrderItems, Cart, Wishlist first (FK -> itemQuant_id)
            cursor.execute(
                f"DELETE FROM OrderItems WHERE itemQuant_id IN ({placeholders})",
                quant_ids,
            )
            cursor.execute(
                f"DELETE FROM Cart WHERE itemQuant_id IN ({placeholders})",
                quant_ids,
            )
            cursor.execute(
                f"DELETE FROM Wishlist WHERE itemQuant_id IN ({placeholders})",
                quant_ids,
            )

        # Delete quantity variants
        cursor.execute("DELETE FROM ItemsQuant WHERE item_id = %s", [item_id])

        # Remove category links
        cursor.execute("DELETE FROM SubCategory WHERE item_id = %s", [item_id])

        # Finally delete the item itself
        cursor.execute("DELETE FROM Items WHERE item_id = %s", [item_id])

        connection.commit()
        # cursor.rowcount here is from the last statement; treat any deletion as success
        return True


def update_order_status(order_id, status):
    """
    Update the status of an order in the Orders table.
    """
    with connection.cursor() as cursor:
        cursor.execute(
            "UPDATE Orders SET order_status = %s WHERE order_id = %s",
            [status, order_id],
        )
        connection.commit()
        return cursor.rowcount > 0


# ---------------------------------------------------------------------------
# Dashboard Statistics
# ---------------------------------------------------------------------------

def get_pending_orders_count():
    """Count orders with status 'Processing'."""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) as count FROM Orders WHERE order_status = 'Processing'"
        )
        row = cursor.fetchone()
        return row[0] if row else 0


def get_low_stock_count(threshold=10):
    """Count items with total stock below threshold."""
    sql = """
        SELECT COUNT(DISTINCT i.item_id) as count
        FROM Items i
        LEFT JOIN ItemsQuant iq ON i.item_id = iq.item_id
        GROUP BY i.item_id
        HAVING COALESCE(SUM(iq.stock), 0) < %s
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [threshold])
        row = cursor.fetchone()
        return row[0] if row else 0


def get_todays_sales():
    """Get total sales revenue for today."""
    sql = """
        SELECT COALESCE(SUM(totalPrice), 0) AS total
        FROM Orders
        WHERE DATE(order_date) = DATE('now');
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchone()
        return float(row[0]) if row and row[0] else 0.0


def get_custom_requests_count():
    """Count complaints/requests awaiting review."""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) as count FROM Complaint WHERE status = 'open' OR status = 'pending'"
        )
        row = cursor.fetchone()
        return row[0] if row else 0


# ---------------------------------------------------------------------------
# Category Management
# ---------------------------------------------------------------------------

def list_categories():
    """List all categories."""
    sql = "SELECT cat_id, categoryName FROM Category ORDER BY categoryName"
    return custom_sql_select(sql)


def get_or_create_category(category_name):
    """Get category by name, or create if doesn't exist."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT cat_id FROM Category WHERE categoryName = %s", [category_name])
        row = cursor.fetchone()
        if row:
            return row[0]
        cursor.execute("INSERT INTO Category (categoryName) VALUES (%s)", [category_name])
        connection.commit()
        return cursor.lastrowid


def get_product_categories(item_id):
    """Get categories and subcategories for a product."""
    sql = """
        SELECT c.cat_id, c.categoryName, s.subcat_id, s.subCatName
        FROM SubCategory s
        JOIN Category c ON s.cat_id = c.cat_id
        WHERE s.item_id = %s
    """
    return custom_sql_select(sql)


def assign_product_to_category(item_id, category_name, subcategory_name=None):
    """Assign a product to a category/subcategory."""
    cat_id = get_or_create_category(category_name)
    subcat_name = subcategory_name or category_name
    
    with connection.cursor() as cursor:
        # Check if already exists
        cursor.execute(
            "SELECT subcat_id FROM SubCategory WHERE cat_id = %s AND item_id = %s",
            [cat_id, item_id]
        )
        existing = cursor.fetchone()
        
        if existing:
            # Update existing
            cursor.execute(
                "UPDATE SubCategory SET subCatName = %s WHERE subcat_id = %s",
                [subcat_name, existing[0]]
            )
        else:
            # Insert new
            cursor.execute(
                "INSERT INTO SubCategory (cat_id, item_id, subCatName) VALUES (%s, %s, %s)",
                [cat_id, item_id, subcat_name]
            )
        connection.commit()


# ---------------------------------------------------------------------------
# Reports
# ---------------------------------------------------------------------------

def get_sales_summary():
    """Get sales summary with top-selling products."""
    sql = """
        SELECT 
            i.item_id,
            i.itemName,
            SUM(oi.quantity) as total_sold,
            SUM(oi.price * oi.quantity) as total_revenue
        FROM OrderItems oi
        JOIN ItemsQuant iq ON oi.itemQuant_id = iq.itemQuant_id
        JOIN Items i ON iq.item_id = i.item_id
        GROUP BY i.item_id, i.itemName
        ORDER BY total_sold DESC
        LIMIT 10
    """
    return custom_sql_select(sql)


def get_inventory_value():
    """Calculate total inventory value."""
    sql = """
        SELECT 
            COALESCE(SUM(i.basePrice * iq.stock), 0) as total_value
        FROM Items i
        JOIN ItemsQuant iq ON i.item_id = iq.item_id
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchone()
        return float(row[0]) if row and row[0] else 0.0


# ---------------------------------------------------------------------------
# User Order History
# ---------------------------------------------------------------------------

def get_user_order_history(user_id):
    """Get order history for a specific user."""
    sql = """
        SELECT 
            o.order_id,
            o.order_date,
            o.order_status,
            o.totalPrice
        FROM Orders o
        WHERE o.user_id = %s
        ORDER BY o.order_date DESC
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [user_id])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]


def get_user_order_stats(user_id):
    """Get order statistics for a user."""
    sql = """
        SELECT 
            COUNT(*) as total_orders,
            SUM(CASE WHEN order_status = 'Processing' THEN 1 ELSE 0 END) as pending_orders,
            COALESCE(SUM(totalPrice), 0) as total_revenue
        FROM Orders
        WHERE user_id = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, [user_id])
        columns = [col[0] for col in cursor.description]
        row = cursor.fetchone()
        if row:
            return dict(zip(columns, row))
        return {"total_orders": 0, "pending_orders": 0, "total_revenue": 0.0}

