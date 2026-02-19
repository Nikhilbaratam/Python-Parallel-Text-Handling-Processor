import pandas as pd
import sqlite3
import datetime
import re

SCORES = {
    "good": 1,
    "great": 2,
    "excellent": 3,
    "amazing": 2,
    "happy": 1,
    "bad": -1,
    "poor": -2,
    "terrible": -3,
    "boring": -2,
    "sad": -1
}

def init_db():
    conn = sqlite3.connect("imdb_sentiment.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        score INTEGER,
        sentiment TEXT,
        timestamp TEXT
    )
    """)

    conn.commit()
    conn.close()


def calculate_score(text):
    words = re.findall(r"\b\w+\b", str(text).lower())

    score = 0
    for word in words:
        score += SCORES.get(word, 0)

    if score > 0:
        sentiment = "Positive"
    elif score < 0:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return score, sentiment


def store_result(text, score, sentiment):
    conn = sqlite3.connect("imdb_sentiment.db")
    cursor = conn.cursor()

    timestamp = str(datetime.datetime.now())

    cursor.execute(
        "INSERT INTO results (text, score, sentiment, timestamp) VALUES (?, ?, ?, ?)",
        (text, score, sentiment, timestamp)
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":

    init_db()

    try:
        print("Reading dataset...")

        df = pd.read_csv("IMDB.csv")

        print("Total records:", len(df))

        for review in df['review']:
            score, sentiment = calculate_score(review)
            store_result(review, score, sentiment)

        print("Dataset processed successfully.")

    except Exception as e:
        print("Error:", e)

