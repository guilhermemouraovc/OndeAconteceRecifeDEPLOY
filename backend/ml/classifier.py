from pathlib import Path

import joblib

_ARTIFACT = Path(__file__).resolve().parent / "artifacts" / "free_paid_pipeline.joblib"


def _heuristic(text: str) -> dict:
    t = text.lower()
    free_hints = ("grátis", "gratuito", "gratuita", "entrada franca", "sem custo", "acesso livre")
    paid_hints = ("ingresso", "r$", "bilheteria", "sympla", "inteira", "meia", "pago")
    score_free = sum(1 for h in free_hints if h in t)
    score_paid = sum(1 for h in paid_hints if h in t)
    pago = 1 if score_paid > score_free else 0
    return {"pago": pago, "probabilidade_pago": 0.65 if pago else 0.35, "fonte": "heuristica"}


def predict_gratuito_pago(text: str) -> dict:
    """SCRUM-33: retorna se o texto sugere evento pago (1) ou gratuito (0)."""
    if not text or not str(text).strip():
        return {"pago": 0, "probabilidade_pago": 0.5, "fonte": "vazio"}

    if _ARTIFACT.exists():
        try:
            pipe = joblib.load(_ARTIFACT)
            proba = pipe.predict_proba([text])[0]
            pred = int(pipe.predict([text])[0])
            return {
                "pago": pred,
                "probabilidade_pago": float(proba[1]),
                "fonte": "modelo",
            }
        except Exception:
            return {**_heuristic(text), "fonte": "heuristica-fallback"}

    return {**_heuristic(text)}
