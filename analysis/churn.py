from . import _register
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.ensemble import RandomForestClassifier

@_register("churn_prediction")
def churn_question(df, **kwargs):
    """
    Predicts customer churn using RandomForest.
    Attempts to automatically detect churn column from known keywords.
    """

    # Step 1: Identify churn target column
    churn_keywords = [
        "churn", "is_churn", "churned", "exited", "left", "attrition",
        "cancel", "cancelled", "closed", "lost", "inactive"
    ]
    candidate_targets = [
        col for col in df.columns
        if any(kw in col.lower() for kw in churn_keywords)
        and df[col].nunique() <= 3
    ]

    # Fallback: pick other binary columns
    if not candidate_targets:
        for col in df.columns:
            if (
                df[col].nunique() <= 3
                and col.lower() not in ['product', 'customerid', 'date', 'amount', 'price', 'cost']
            ):
                candidate_targets.append(col)

    if not candidate_targets:
        return {
            "summary": "❌ No binary churn column found. Try adding a column like 'churn', 'exited', or 'cancelled'.",
            "fig": None,
            "table": None
        }

    target = candidate_targets[0]

    # Step 2: Prepare target
    df = df.dropna(subset=[target])
    if df[target].dtype == object:
        df[target] = df[target].map({"Yes": 1, "No": 0, "yes": 1, "no": 0})
    df[target] = pd.to_numeric(df[target], errors='coerce')
    df = df.dropna(subset=[target])
    df[target] = df[target].astype(int)

    # Step 3: Prepare features
    X = df.drop(columns=[target])
    X = pd.get_dummies(X, drop_first=True)
    y = df[target]

    if X.shape[0] < 10 or X.shape[1] == 0:
        return {
            "summary": "❌ Not enough data to train a churn model. Try uploading more complete records.",
            "fig": None,
            "table": None
        }

    # Step 4: Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # Step 5: Train Model
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)

    # Step 6: Evaluation
    accuracy = accuracy_score(y_test, y_pred)
    report_df = pd.DataFrame(classification_report(y_test, y_pred, output_dict=True)).transpose()
    churn_rate = round(y.mean() * 100, 1)

    # Step 7: Confusion Matrix Plot
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots()
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax)
    ax.set_xlabel('Predicted')
    ax.set_ylabel('Actual')
    ax.set_title('Churn Prediction: Confusion Matrix')

    buf = BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    fig_data = base64.b64encode(buf.read()).decode("utf-8")
    fig_html = f"![Confusion Matrix](data:image/png;base64,{fig_data})"

    # Step 8: Return
    return {
        "summary": (
            f"### 🔄 Churn Prediction Summary (Target: `{target}`)\n\n"
            f"- ✅ **Model Accuracy**: **{accuracy:.2%}**\n"
            f"- 📉 **Churn Rate**: **{churn_rate}%**\n"
            f"- 🧠 RandomForest model trained to detect at-risk customers.\n\n"
            f"#### 🔎 Confusion Matrix\n{fig_html}\n\n"
            f"#### 📋 Classification Report"
        ),
        "fig": None,
        "table": report_df.round(2)
    }
