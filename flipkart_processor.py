import pandas as pd
import sqlite3
import datetime
import re

PATTERN_RULES = [
    (r"very good|really good|excellent product|highly recommend|worth buying", 3),
    (r"awesome|amazing product|works perfectly|super quality", 4),

    (r"very bad|not good|poor quality|waste of money|do not buy", -3),
    (r"worst product|totally disappointed|stopped working|bad experience", -4),
]

WORD_SCORES = {
    "good": 1,
    "nice": 1,
    "excellent": 2,
    "amazing": 2,
    "perfect": 2,

    "bad": -1,
    "poor": -2,
    "worst": -3,
    "waste": -2,
    "disappointed": -2
}

NEGATIONS = {"not", "no", "never"}
INTENSIFIERS = {"very", "extremely", "really"}

def init_db():
    conn = sqlite3.connect("flipkart_sentiment.db")
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

    text = str(text).lower()
    score = 0

    for pattern, value in PATTERN_RULES:
        if re.search(pattern, text):
            score += value

    words = re.findall(r"\b\w+\b", text)

    negate = False
    boost = 1

    for word in words:

        if word in NEGATIONS:
            negate = True
            continue

        if word in INTENSIFIERS:
            boost = 2
            continue

        word_score = WORD_SCORES.get(word, 0)

        if negate:
            word_score *= -1
            negate = False

        score += word_score * boost
        boost = 1

    if score > 1:
        sentiment = "Positive"
    elif score < -1:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return score, sentiment

def store_result(text, score, sentiment):
    conn = sqlite3.connect("flipkart_sentiment.db")
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
        print("Reading Flipkart dataset...")

        df = pd.read_csv(
            "flipkart_product.csv",
            encoding="latin1",
            engine="python",          # ⭐ CRITICAL FIX
            on_bad_lines="skip"       # ⭐ Prevent early stop
        )

        print("Total records:", len(df))

        for review in df['Review']:
            score, sentiment = calculate_score(review)
            store_result(review, score, sentiment)

        print("Dataset processed successfully.")

    except Exception as e:
        print("Error occurred:", e)