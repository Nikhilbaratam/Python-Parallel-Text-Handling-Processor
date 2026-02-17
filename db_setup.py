import sqlite3

conn = sqlite3.connect("processor.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    keyword TEXT,
    count INTEGER
)
""")

conn.commit()
conn.close()

print("Database ready.")
