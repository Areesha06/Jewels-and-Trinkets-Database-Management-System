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

def register_sql_insert(name, email, password):
    with connection.cursor() as cursor:
        cursor.execute("INSERT INTO Users (name, email, password) VALUES (%s, %s, %s)", [name, email, password])
        connection.commit()
        return cursor.lastrowid


def update_profile_sql(user_id, name=None, email=None, phone=None):
    """
    Update the Users table for a given user_id.
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

        

def create_dummy_db():
    with connection.cursor() as cursor:
        cursor.execute("""
                       CREATE TABLE users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        age INTEGER
                        );
                    """)
        cursor.execute("""
                    INSERT INTO users (name, email, age)
                    VALUES
                    ('Bob', 'bob@example.com', 30),
                    ('Charlie', 'charlie@example.com', 22);

                    """)
        # cursor.execute("UPDATE bar SET foo = 1 WHERE baz = %s", [self.baz])
        # cursor.execute("SELECT foo FROM bar WHERE baz = %s", [self.baz])
        row = cursor.fetchall()
        #print(row)

    return row


def create_initial_db():

    with open("crochet.sql", "r", encoding="utf-8") as file:
        sql_script = file.read()

    with connection.cursor() as cursor:
        # Split commands by semicolon (for MySQL, executescript() is not available)
        for statement in sql_script.split(';'):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
    
    with open("data.sql", "r", encoding="utf-8") as file:
        sql_script = file.read()

    with connection.cursor() as cursor:
        # Split commands by semicolon (for MySQL, executescript() is not available)
        for statement in sql_script.split(';'):
            statement = statement.strip()
            if statement:
                cursor.execute(statement)
    
    connection.commit()
    connection.close()
    