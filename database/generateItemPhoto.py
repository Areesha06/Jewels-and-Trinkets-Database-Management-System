import sqlite3

conn = sqlite3.connect("dbDummy.sqlite3")
cur = conn.cursor()

cur.execute("SELECT item_id FROM Items")
ids = [row[0] for row in cur.fetchall()]

with open("1.jpg", "rb") as f:
    img_data = f.read()

for item_id in ids:
    cur.execute("UPDATE Items SET image = ? WHERE item_id = ?", (img_data, item_id))

conn.commit()
conn.close()
