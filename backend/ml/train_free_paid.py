"""
SCRUM-33: treina classificador gratuito/pago (TF-IDF + regressão logística).
Execute: python -m ml.train_free_paid
"""

from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "sample_training.csv"
ARTIFACT = Path(__file__).resolve().parent / "artifacts" / "free_paid_pipeline.joblib"


def main() -> None:
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(CSV_PATH)
    X = df["texto"].astype(str)
    y = df["pago"].astype(int)

    pipe = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1, max_df=0.95)),
            ("clf", LogisticRegression(max_iter=200, class_weight="balanced")),
        ]
    )
    pipe.fit(X, y)
    joblib.dump(pipe, ARTIFACT)
    print(f"Modelo salvo em {ARTIFACT}")


if __name__ == "__main__":
    main()
