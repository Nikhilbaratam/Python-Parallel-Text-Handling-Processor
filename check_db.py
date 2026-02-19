import sqlite3

conn = sqlite3.connect("imdb_sentiment.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", cursor.fetchall())

cursor.execute("SELECT COUNT(*) FROM results")
print("Total rows stored:", cursor.fetchone())

conn.close()
