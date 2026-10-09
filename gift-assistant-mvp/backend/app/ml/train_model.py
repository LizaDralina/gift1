from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor

MODEL_PATH = Path(__file__).resolve().parent / "gift_ranker.joblib"


def train_and_save_model():
    data = pd.DataFrame([
        [3, 2500, 0.8, 1, 1, 1, 25, 0, 0.95],
        [1, 4500, 0.9, 1, 0, 1, 25, 0, 0.65],
        [0, 1200, 0.2, 0, 1, 0, 25, 0, 0.20],
        [2, 3200, 0.7, 1, 1, 1, 30, 0, 0.85],
        [1, 1800, 0.4, 1, 1, 0, 30, 0, 0.55],
        [0, 9000, 1.0, 0, 0, 0, 30, 12, 0.10],
    ], columns=[
        "interest_matches",
        "price",
        "price_position",
        "occasion_match",
        "relationship_match",
        "category_match",
        "recipient_age",
        "product_age_limit",
        "target_score",
    ])

    X = data.drop(columns=["target_score"])
    y = data["target_score"]

    model = GradientBoostingRegressor(random_state=42)
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    train_and_save_model()