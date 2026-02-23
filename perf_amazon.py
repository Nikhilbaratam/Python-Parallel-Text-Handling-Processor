import sqlite3
import time

DB_NAME = "amazon_perf.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sentiment TEXT,
    text TEXT
)
""")
conn.commit()


def parse_line(line):
    if line.startswith("__label__2"):
        sentiment = "Positive"
        text = line.replace("__label__2", "").strip()
    elif line.startswith("__label__1"):
        sentiment = "Negative"
        text = line.replace("__label__1", "").strip()
    else:
        return None

    return sentiment, text


print("Reading dataset...")

start = time.time()

data = []

with open("train.ft.txt", "r", encoding="utf-8") as f:
    for i, line in enumerate(f):

        parsed = parse_line(line)
        if parsed:
            data.append(parsed)

        if i >= 1_000_000:
            break


print("Inserting into database...")

cursor.executemany(
    "INSERT INTO results (sentiment, text) VALUES (?, ?)",
    data
)

conn.commit()

insert_time = time.time() - start
print("Insert Time:", insert_time)


print("\nQuery WITHOUT index...")

start_q = time.time()

cursor.execute("SELECT COUNT(*) FROM results WHERE sentiment='Positive'")
cursor.fetchone()

no_index_time = time.time() - start_q
print("Query Time (No Index):", no_index_time)


print("\nCreating index...")

cursor.execute("CREATE INDEX idx_sentiment ON results(sentiment)")
conn.commit()


print("Query WITH index...")

start_q = time.time()

cursor.execute("SELECT COUNT(*) FROM results WHERE sentiment='Positive'")
cursor.fetchone()

index_time = time.time() - start_q
print("Query Time (With Index):", index_time)


print("\nImprovement:", no_index_time - index_time)

conn.close()