from pathlib import Path
import joblib

MODEL_PATH = Path(__file__).resolve().parent / "gift_ranker.joblib"

_model = None

def load_model():
    global _model

    if _model is None and MODEL_PATH.exists():
        _model = joblib.load(MODEL_PATH)
        print(f"ML model loaded from: {MODEL_PATH}")

    if _model is None:
        print("ML model not found, fallback to heuristic scoring")

    return _model 