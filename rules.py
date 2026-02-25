# Pattern-based rules (high priority)
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