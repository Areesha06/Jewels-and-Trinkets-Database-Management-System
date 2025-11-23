from django.db import connection

def custom_sql_select(query):
    with connection.cursor() as cursor:
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

        

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
    