import pandas as pd
import sqlite3
import re
import time
from multiprocessing import Pool, cpu_count

DB_NAME = "flipkart_sentiment.db"

# ---------------------------
# Pattern Rules (Your Version)
# ---------------------------
PATTERN_RULES = [

    # STRONG POSITIVE
    (r"highly recommend|must buy|worth every penny|value for money", 4),
    (r"excellent product|superb product|loved the product|very satisfied", 4),
    (r"best purchase|works perfectly|awesome product|great quality", 3),
    (r"good quality|nice product|happy with the product", 2),

    # STRONG NEGATIVE
    (r"waste of money|do not buy|not worth|very disappointed", -4),
    (r"worst product|poor quality|stopped working|defective product", -4),
    (r"bad experience|totally useless|very bad|extremely bad", -3),
    (r"damaged product|received damaged|fake product", -3),

    # DELIVERY / SERVICE
    (r"late delivery|delivery was late|poor delivery", -2),
    (r"fast delivery|quick delivery|delivered on time", 2),

    # PERFORMANCE SIGNALS
    (r"works great|works fine|working perfectly", 3),
    (r"not working|does not work|stopped working", -3),

    # EXPECTATION MATCH
    (r"as expected|met expectations", 2),
    (r"not as expected|did not meet expectations", -2),
]

# ---------------------------
# Word Scores (Your Version)
# ---------------------------
WORD_SCORES = {

    # Positive Words
    "good": 1,
    "nice": 1,
    "excellent": 2,
    "amazing": 2,
    "perfect": 2,
    "satisfied": 2,
    "happy": 1,
    "love": 2,
    "great": 2,
    "awesome": 2,
    "best": 2,

    # Negative Words
    "bad": -1,
    "poor": -2,
    "worst": -3,
    "waste": -2,
    "disappointed": -2,
    "defective": -2,
    "damaged": -2,
    "useless": -2,
    "hate": -2,
    "problem": -1,
    "issue": -1
}

NEGATIONS = {"not", "no", "never", "none"}
INTENSIFIERS = {"very", "extremely", "really", "too"}

# ---------------------------
# Database Setup
# ---------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        score INTEGER,
        sentiment TEXT
    )
    """)

    conn.commit()
    conn.close()

# ---------------------------
# Score Logic
# ---------------------------
def calculate_score(text):

    original_text = str(text)
    text = original_text.lower()
    score = 0

    # Pattern rules (high priority)
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

    return (original_text[:80], score, sentiment)

# ---------------------------
# Store Results
# ---------------------------
def store_results(rows):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.executemany(
        "INSERT INTO results (text, score, sentiment) VALUES (?, ?, ?)",
        rows
    )

    conn.commit()
    conn.close()

# ---------------------------
# Main Program
# ---------------------------
if __name__ == "__main__":

    print("Starting Flipkart Parallel Sentiment Test...")

    init_db()

    print("Reading dataset...")
    df = pd.read_csv("flipkart_product.csv", encoding="latin1", engine="python")

    reviews = df['Review'].dropna().tolist()

    print("Total reviews:", len(reviews))
    print("CPU cores:", cpu_count())

    start = time.time()

    with Pool(cpu_count()) as pool:
        results = pool.map(calculate_score, reviews)

    store_results(results)

    total_time = time.time() - start

    print("\nSample Scores:")
    for r in results[:5]:
        print("Score:", r[1], "| Sentiment:", r[2])
        print("Text:", r[0])
        print("-" * 60)

    print("\nParallel Processing Time:", total_time)