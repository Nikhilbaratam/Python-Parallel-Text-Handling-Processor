import sqlite3

conn = sqlite3.connect("processor.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM results")
print(cursor.fetchall())

conn.close()
