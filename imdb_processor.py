import pandas as pd
import sqlite3
import datetime
import re

# ---------------------------
# Rule-based scoring dictionary
# ---------------------------
SCORES = {

    # Strong Positive
    "masterpiece": 4,
    "outstanding": 3,
    "excellent": 3,
    "brilliant": 3,
    "fantastic": 3,

    # Moderate Positive
    "amazing": 2,
    "great": 2,
    "good": 1,
    "enjoyable": 2,
    "interesting": 1,
    "love": 2,
    "liked": 1,

    # Neutral-ish
    "okay": 0,
    "average": 0,

    # Moderate Negative
    "bad": -1,
    "boring": -2,
    "dull": -2,
    "slow": -1,
    "weak": -1,
    "disappointing": -2,

    # Strong Negative
    "worst": -3,
    "terrible": -3,
    "awful": -3,
    "horrible": -3,
    "waste": -3,
    "hate": -2
}


# ---------------------------
# Database Setup
# ---------------------------
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


# ---------------------------
# Score Calculation
# ---------------------------
NEGATIONS = {"not", "no", "never", "none"}

def calculate_score(text):
    words = re.findall(r"\b\w+\b", str(text).lower())

    score = 0
    negate = False

    for word in words:

        if word in NEGATIONS:
            negate = True
            continue

        word_score = SCORES.get(word, 0)

        if negate:
            word_score *= -1   # Reverse polarity
            negate = False

        score += word_score

    if score > 0:
        sentiment = "Positive"
    elif score < 0:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"

    return score, sentiment



# ---------------------------
# Store Results
# ---------------------------
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


# ---------------------------
# Main Execution
# ---------------------------
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
        print("Error occurred:", e)
