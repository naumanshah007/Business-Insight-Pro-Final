# nlp_tasks.py

from textblob import TextBlob

def analyze_sentiment_vader(text):
    """
    Returns a sentiment polarity score: -1 (negative) to 1 (positive).
    """
    if not text or not isinstance(text, str) or not text.strip():
        return 0.0
    return TextBlob(text).sentiment.polarity
