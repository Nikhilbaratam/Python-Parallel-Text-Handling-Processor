import sqlite3
import time
from multiprocessing import Pool, cpu_count


DB_NAME = "amazon_parallel.db"


def parse_line(line):
    if line.startswith("__label__2"):
        sentiment = "Positive"
        text = line.replace("__label__2", "").strip()
    elif line.startswith("__label__1"):
        sentiment = "Negative"
        text = line.replace("__label__1", "").strip()
    else:
        return None
    return (sentiment, text)


def init_db():
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
    conn.close()


def load_data():
    lines = []

    with open("train.ft.txt", "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            lines.append(line)

            if i >= 200_000:   # Smaller test for stability
                break

    return lines


if __name__ == "__main__":

    print("Starting parallel test...")

    init_db()

    print("Loading dataset...")
    lines = load_data()

    print("Lines loaded:", len(lines))
    print("CPU cores:", cpu_count())

    start = time.time()

    with Pool(cpu_count()) as p:
        results = p.map(parse_line, lines)

    cleaned = [r for r in results if r]

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.executemany(
        "INSERT INTO results (sentiment, text) VALUES (?, ?)",
        cleaned
    )

    conn.commit()
    conn.close()

    total_time = time.time() - start
    
    print("Parallel Processing Time:", total_time)