from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    auc,
    confusion_matrix,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_recall_curve,
    precision_score,
    r2_score,
    recall_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler

BASE_DIR = Path(__file__).resolve().parent
DATA_EVENTS = BASE_DIR / "data" / "dashboard_eventos.csv"
DATA_MOVEMENT = BASE_DIR / "data" / "dashboard_horarios.csv"


@dataclass
class ClassifierResult:
    metrics: dict[str, Any]
    confusion: list[list[int]]
    roc: dict[str, Any]
    pr: dict[str, Any]
    feature_importance: list[dict[str, Any]]


@lru_cache
def load_dashboard_data() -> dict[str, Any]:
    events_raw = _read_csv_safe(DATA_EVENTS)
    movement_raw = _read_csv_safe(DATA_MOVEMENT)

    events = normalize_events(events_raw)
    movement = normalize_movement(movement_raw)

    regression = build_regression(movement)
    classification = build_classification(events)
    clusters = build_clusters(events)

    return {
        "events": events.to_dict(orient="records"),
        "movement": movement.to_dict(orient="records"),
        "stats": build_exploration(events),
        "regression": regression,
        "classification": classification,
        "clusters": clusters,
        "version": 1,
    }


def _read_csv_safe(path: Path) -> pd.DataFrame:
    for encoding in ("utf-8-sig", "utf-8", "latin1"):
        try:
            return pd.read_csv(path, encoding=encoding)
        except UnicodeDecodeError:
            continue
    return pd.read_csv(path)


def normalize_events(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["inicio_dt"] = pd.to_datetime(
        out["data"].astype(str).str.strip() + " " + out["horario"].astype(str).str.strip(),
        errors="coerce",
    )
    out["inicio_iso"] = out["inicio_dt"].dt.strftime("%Y-%m-%dT%H:%M:%S")
    out["preco"] = pd.to_numeric(out["preco_ingresso"], errors="coerce")
    out["gratuito"] = out["gratuito"].astype(str).str.lower().isin(["true", "1", "sim", "yes"])
    out["categoria"] = out["tipo"].fillna("Outros").astype(str)
    out["source"] = out["plataforma"].fillna("Fonte desconhecida").astype(str)
    out["hour"] = out["inicio_dt"].dt.hour + out["inicio_dt"].dt.minute.fillna(0) / 60.0
    out["weekday"] = out["dia_semana"].fillna("Sem data").astype(str)
    out["publico_estimado"] = pd.to_numeric(out["publico_estimado"], errors="coerce")
    out["lat"] = pd.to_numeric(out["latitude"], errors="coerce")
    out["lng"] = pd.to_numeric(out["longitude"], errors="coerce")
    id_base = out["id_evento"] if "id_evento" in out.columns else pd.Series(index=out.index, dtype="object")
    out["id"] = id_base.fillna(pd.Series(out.index.astype(str), index=out.index)).astype(str)
    out["titulo"] = out["nome"].fillna("Evento sem título").astype(str)
    out["descricao"] = out.get("descricao", "").astype(str) if "descricao" in out.columns else ""
    out["local"] = out.get("local", "").astype(str) if "local" in out.columns else ""
    return out.dropna(subset=["inicio_dt", "publico_estimado", "preco"])


def normalize_movement(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["hora"] = pd.to_numeric(out["hora"], errors="coerce")
    out["movimentacao_pct"] = pd.to_numeric(out["movimentacao_pct"], errors="coerce")
    out["dia_semana"] = out["dia_semana"].astype(str)
    out["bairro"] = out["bairro"].astype(str)
    out["horario_label"] = out["horario_label"].astype(str)
    return out.dropna(subset=["hora", "movimentacao_pct"])


def build_exploration(events: pd.DataFrame) -> dict[str, Any]:
    total = len(events)
    categories = events["categoria"].value_counts().head(10)
    neighborhoods = events["bairro"].value_counts().head(10)
    by_day = (
        events.groupby("weekday")["publico_estimado"]
        .mean()
        .reindex(["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"])
        .fillna(0)
    )
    price_bins = histogram(events["preco"].tolist(), bins=8)
    public_values = events["publico_estimado"].tolist()
    price_values = events["preco"].tolist()
    corr_price_public = safe_corr(price_values, public_values)
    corr_price_hour = safe_corr(events["preco"].tolist(), events["hour"].tolist())
    corr_hour_public = safe_corr(events["hour"].tolist(), public_values)

    return {
        "total": total,
        "free_count": int(events["gratuito"].sum()),
        "avg_price": float(events["preco"].mean()),
        "avg_public": float(events["publico_estimado"].mean()),
        "top_categories": to_count_list(categories),
        "top_neighborhoods": to_count_list(neighborhoods),
        "by_day": [{"label": idx, "value": float(val)} for idx, val in by_day.items()],
        "price_bins": price_bins,
        "correlations": {
            "price_public": corr_price_public,
            "price_hour": corr_price_hour,
            "hour_public": corr_hour_public,
        },
        "descriptive": {
            "price": events["preco"].describe().to_dict(),
            "public": events["publico_estimado"].describe().to_dict(),
        },
    }


def build_regression(movement: pd.DataFrame) -> dict[str, Any] | None:
    if movement.empty:
        return None

    X = movement[["hora"]].to_numpy()
    y = movement["movimentacao_pct"].to_numpy()
    if len(np.unique(X)) < 2:
        return None

    model = LinearRegression()
    model.fit(X, y)
    pred = model.predict(X)
    residuals = y - pred
    return {
        "points": [
            {
                "hora": float(hora),
                "movimentacao_pct": float(mov),
                "pred": float(pred_val),
                "residual": float(res),
            }
            for hora, mov, pred_val, res in zip(movement["hora"], y, pred, residuals)
        ],
        "slope": float(model.coef_[0]),
        "intercept": float(model.intercept_),
        "r2": float(r2_score(y, pred)),
        "mae": float(mean_absolute_error(y, pred)),
        "rmse": float(np.sqrt(mean_squared_error(y, pred))),
        "predictions": [float(v) for v in pred],
        "residuals": [float(v) for v in residuals],
        "hours": [float(v) for v in movement["hora"]],
    }


def build_classification(events: pd.DataFrame) -> dict[str, Any] | None:
    if events.empty:
        return None

    df = events.copy()
    df["alto_publico"] = (df["publico_estimado"] > df["publico_estimado"].median()).astype(int)

    for src, dst in [
        ("categoria", "categoria_enc"),
        ("bairro", "bairro_enc"),
        ("source", "source_enc"),
        ("weekday", "weekday_enc"),
    ]:
        enc = LabelEncoder()
        df[dst] = enc.fit_transform(df[src].astype(str))

    X = df[["categoria_enc", "bairro_enc", "source_enc", "weekday_enc", "preco"]].to_numpy()
    y = df["alto_publico"].to_numpy()
    stratify = y if len(np.unique(y)) > 1 else None

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=42, stratify=stratify)

    scaler = StandardScaler()
    X_tr_s = scaler.fit_transform(X_tr)
    X_te_s = scaler.transform(X_te)

    rf = RandomForestClassifier(n_estimators=150, random_state=42, max_depth=6)
    rf.fit(X_tr, y_tr)
    y_pred_rf = rf.predict(X_te)
    y_prob_rf = rf.predict_proba(X_te)[:, 1]

    lr = LogisticRegression(max_iter=2000, random_state=42)
    lr.fit(X_tr_s, y_tr)
    y_pred_lr = lr.predict(X_te_s)
    y_prob_lr = lr.predict_proba(X_te_s)[:, 1]

    feat_names = ["Categoria", "Bairro", "Fonte", "Dia", "Preço"]
    return {
        "median_public": float(df["publico_estimado"].median()),
        "models": {
            "Random Forest": classifier_result(y_te, y_pred_rf, y_prob_rf, rf.feature_importances_, feat_names),
            "Regressao Logistica": classifier_result(
                y_te,
                y_pred_lr,
                y_prob_lr,
                [0.0] * len(feat_names),
                feat_names,
            ),
        },
    }


def classifier_result(y_true, y_pred, y_prob, feature_importances, feat_names) -> dict[str, Any]:
    cm = confusion_matrix(y_true, y_pred)
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    prec, rec, _ = precision_recall_curve(y_true, y_prob)
    tn, fp, fn, tp = cm.ravel().tolist()
    return {
        "support": int(len(y_true)),
        "baseline_rate": float(np.mean(y_true)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "counts": {"tp": int(tp), "tn": int(tn), "fp": int(fp), "fn": int(fn)},
        "confusion_matrix": cm.tolist(),
        "roc": {"points": [{"fpr": float(a), "tpr": float(b)} for a, b in zip(fpr, tpr)], "auc": float(auc(fpr, tpr))},
        "pr": {"points": [{"recall": float(a), "precision": float(b)} for a, b in zip(rec, prec)], "auc": float(auc(rec, prec))},
        "feature_importance": [
            {"label": label, "value": float(value)} for label, value in sorted(zip(feat_names, feature_importances), key=lambda item: item[1])
        ],
    }


def build_clusters(events: pd.DataFrame) -> dict[str, Any] | None:
    pts = events[["hour", "preco"]].dropna()
    if len(pts) < 3:
        return None
    k = min(3, len(pts))
    model = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = model.fit_predict(pts.to_numpy())
    return {
        "points": [
            {
                "hour": float(hour),
                "preco": float(price),
                "cluster": int(cluster),
            }
            for (hour, price), cluster in zip(pts.to_numpy(), labels)
        ],
        "centroids": [{"hour": float(c[0]), "preco": float(c[1])} for c in model.cluster_centers_],
    }


def histogram(values: list[float], bins: int = 8) -> list[dict[str, Any]]:
    clean = [float(v) for v in values if pd.notna(v)]
    if not clean:
        return []
    min_v = min(clean)
    max_v = max(clean)
    if min_v == max_v:
        return [{"label": f"{round(min_v)} - {round(max_v)}", "count": len(clean), "share": 1.0}]

    size = (max_v - min_v) / bins
    buckets = [{"start": min_v + i * size, "end": min_v + (i + 1) * size, "count": 0} for i in range(bins)]
    for value in clean:
        idx = min(bins - 1, max(0, int((value - min_v) // size)))
        buckets[idx]["count"] += 1
    total = sum(bucket["count"] for bucket in buckets) or 1
    return [
        {
            "label": f"{round(bucket['start'])} - {round(bucket['end'])}",
            "count": int(bucket["count"]),
            "share": float(bucket["count"] / total),
        }
        for bucket in buckets
    ]


def to_count_list(series: pd.Series) -> list[dict[str, Any]]:
    total = int(series.sum()) or 1
    return [
        {"label": str(idx), "count": int(value), "share": float(value / total)}
        for idx, value in series.items()
    ]


def safe_corr(xs: list[float], ys: list[float]) -> float:
    x = pd.Series(xs, dtype="float64")
    y = pd.Series(ys, dtype="float64")
    return float(x.corr(y)) if x.notna().sum() > 1 and y.notna().sum() > 1 else 0.0
