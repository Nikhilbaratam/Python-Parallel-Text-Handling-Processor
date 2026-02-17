import os
from multiprocessing import Pool, cpu_count
import sqlite3

KEYWORDS = ["python", "parallel", "multiprocessing", "error"]

def process_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        text = f.read().lower()

    results = []
    for word in KEYWORDS:
        results.append((os.path.basename(filepath), word, text.count(word)))

    return results


def store_results(data):
    conn = sqlite3.connect("processor.db")
    cursor = conn.cursor()

    cursor.executemany(
        "INSERT INTO results (filename, keyword, count) VALUES (?, ?, ?)",
        data
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":

    folder = "texts"
    files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith(".txt")]

    with Pool(cpu_count()) as pool:
        mapped_results = pool.map(process_file, files)

    flat_results = [item for sublist in mapped_results for item in sublist]

    store_results(flat_results)

    print("Processing complete.")
