from . import _register
import pandas as pd
import plotly.express as px
from textblob import TextBlob
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import sys
import os

# Add parent directory to path to import genai_client
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from genai_client import analyze_customer_sentiment

@_register("sentiment_analysis")
def sentiment_question(df):
    """
    Analyzes customer sentiment and highlights negative feedback topics.
    Returns a dict: {'summary', 'fig', 'table'}
    """
    # Try to find a review-like column
    review_cols = [c for c in df.columns if any(k in c.lower() for k in ["feedback", "review", "comment", "text"])]
    if not review_cols:
        return {"summary": "❌ No column found for customer feedback or reviews.", "fig": None, "table": None}
    
    text_col = review_cols[0]
    reviews = df[text_col].dropna().astype(str)

    # Score sentiment using TextBlob
    sentiments = reviews.apply(lambda x: TextBlob(x).sentiment.polarity)
    result_df = pd.DataFrame({text_col: reviews, "Sentiment Score": sentiments})

    # Visualize sentiment distribution
    fig = px.histogram(
        result_df,
        x="Sentiment Score",
        nbins=20,
        color_discrete_sequence=["#636EFA"],
        title="💬 Customer Sentiment Distribution"
    )
    fig.update_layout(
        xaxis_title="Sentiment Score (Polarity)",
        yaxis_title="Number of Reviews",
        plot_bgcolor="#f9f9f9",
        paper_bgcolor="#f9f9f9",
        title_x=0.5
    )

    # Topic modeling for negative reviews (polarity < -0.1)
    negative_reviews = reviews[sentiments < -0.1]
    topics_summary = ""
    topics_table = None

    if not negative_reviews.empty:
        vectorizer = CountVectorizer(stop_words="english", max_features=500)
        X = vectorizer.fit_transform(negative_reviews)

        n_topics = min(3, X.shape[0])
        if n_topics > 1:
            lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
            lda.fit(X)
            topic_words = []
            for idx, topic in enumerate(lda.components_):
                top_words = [vectorizer.get_feature_names_out()[i] for i in topic.argsort()[-7:][::-1]]
                topic_words.append(", ".join(top_words))
            topics_table = pd.DataFrame({"Negative Feedback Topics": topic_words})
            topics_summary = " | ".join(topic_words)
        else:
            topics_summary = "📉 Not enough strongly negative feedback to extract common topics."
    else:
        topics_summary = "✅ No strongly negative reviews detected."

    # Prepare comprehensive sentiment data for GenAI analysis
    sentiment_stats = {
        "total_reviews": len(reviews),
        "positive_reviews": len(sentiments[sentiments > 0.1]),
        "negative_reviews": len(sentiments[sentiments < -0.1]),
        "neutral_reviews": len(sentiments[(sentiments >= -0.1) & (sentiments <= 0.1)]),
        "avg_sentiment_score": round(sentiments.mean(), 3),
        "sentiment_std": round(sentiments.std(), 3),
        "positive_percentage": round(len(sentiments[sentiments > 0.1]) / len(reviews) * 100, 1),
        "negative_percentage": round(len(sentiments[sentiments < -0.1]) / len(reviews) * 100, 1),
        "top_negative_themes": topics_summary.split(" | ") if topics_table is not None else [],
        "sentiment_distribution": {
            "very_positive": len(sentiments[sentiments > 0.5]),
            "positive": len(sentiments[(sentiments > 0.1) & (sentiments <= 0.5)]),
            "neutral": len(sentiments[(sentiments >= -0.1) & (sentiments <= 0.1)]),
            "negative": len(sentiments[(sentiments >= -0.5) & (sentiments < -0.1)]),
            "very_negative": len(sentiments[sentiments < -0.5])
        }
    }
    
    # Generate GenAI-powered sentiment insights
    try:
        genai_sentiment_analysis = analyze_customer_sentiment(sentiment_stats, "retail")
        summary = f"### 💬 AI-Powered Customer Sentiment Analysis\n\n{genai_sentiment_analysis}"
    except Exception as e:
        # Fallback to enhanced static analysis
        summary = (
            "### 💬 Customer Sentiment Analysis\n\n"
            f"**Analysis Summary:** Analyzed feedback from **{len(reviews)}** customers using advanced NLP techniques.\n\n"
            f"**Sentiment Distribution:**\n"
            f"- 🟢 **Positive**: {sentiment_stats['positive_percentage']}% ({sentiment_stats['positive_reviews']} reviews)\n"
            f"- 🟡 **Neutral**: {round(sentiment_stats['neutral_reviews'] / len(reviews) * 100, 1)}% ({sentiment_stats['neutral_reviews']} reviews)\n"
            f"- 🔴 **Negative**: {sentiment_stats['negative_percentage']}% ({sentiment_stats['negative_reviews']} reviews)\n\n"
            f"**Key Metrics:**\n"
            f"- Average sentiment score: **{sentiment_stats['avg_sentiment_score']}** (range: -1 to +1)\n"
            f"- Sentiment consistency: **{sentiment_stats['sentiment_std']}** standard deviation\n\n"
            + (f"**🔍 Top Negative Themes:** {topics_summary}" if topics_table is not None else "**✅ No major negative themes identified**") + "\n\n"
            "**Action Items:**\n"
            "1. Address negative feedback themes systematically\n"
            "2. Leverage positive feedback for marketing\n"
            "3. Monitor sentiment trends over time\n\n"
            "*Note: Enhanced AI sentiment analysis temporarily unavailable. Showing detailed statistical analysis.*"
        )

    return {
        "summary": summary,
        "fig": fig,
        "table": topics_table if topics_table is not None else result_df.head(10)
    }
