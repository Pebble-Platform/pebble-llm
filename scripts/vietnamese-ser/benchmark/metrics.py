"""Shared evaluation metrics for the ViEmoSpeech benchmark (M1).

One module every method reports through, so numbers are comparable:
- emotion: macro-F1 (headline), per-class F1, accuracy.
- valence / arousal: CCC (Lin's concordance) — the objective from RJCMA/MSP.
- distress: recall + precision (small-support proxy, reported with a caveat).

Dependency-light (numpy only). No sklearn, to keep the Kaggle stack thin.
"""

from __future__ import annotations

import numpy as np

EMOTIONS = ["neutral", "anger", "joy", "sadness", "fear_anxiety", "disgust", "surprise"]


def per_class_f1(y_true: list[str], y_pred: list[str], labels: list[str]) -> dict[str, float]:
    out = {}
    yt = np.asarray(y_true)
    yp = np.asarray(y_pred)
    for c in labels:
        tp = int(np.sum((yt == c) & (yp == c)))
        fp = int(np.sum((yt != c) & (yp == c)))
        fn = int(np.sum((yt == c) & (yp != c)))
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        out[c] = (2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0
    return out


def emotion_metrics(y_true: list[str], y_pred: list[str],
                    labels: list[str] = EMOTIONS) -> dict:
    f1 = per_class_f1(y_true, y_pred, labels)
    yt = np.asarray(y_true)
    yp = np.asarray(y_pred)
    # macro-F1 over classes actually PRESENT in y_true (small-test honesty)
    present = [c for c in labels if np.any(yt == c)]
    macro = float(np.mean([f1[c] for c in present])) if present else 0.0
    acc = float(np.mean(yt == yp)) if len(yt) else 0.0
    return {"macro_f1": macro, "accuracy": acc, "per_class_f1": f1,
            "present_classes": present, "support": {c: int(np.sum(yt == c)) for c in labels}}


def ccc(y_true: list[float], y_pred: list[float]) -> float:
    """Lin's Concordance Correlation Coefficient."""
    x = np.asarray(y_true, dtype=float)
    y = np.asarray(y_pred, dtype=float)
    if len(x) < 2:
        return 0.0
    mx, my = x.mean(), y.mean()
    vx, vy = x.var(), y.var()
    cov = np.mean((x - mx) * (y - my))
    denom = vx + vy + (mx - my) ** 2
    return float(2 * cov / denom) if denom else 0.0


def distress_metrics(y_true: list[bool], y_pred: list[bool]) -> dict:
    yt = np.asarray(y_true, dtype=bool)
    yp = np.asarray(y_pred, dtype=bool)
    tp = int(np.sum(yt & yp))
    fp = int(np.sum(~yt & yp))
    fn = int(np.sum(yt & ~yp))
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    return {"recall": rec, "precision": prec, "n_positive": int(yt.sum())}


def _selftest() -> None:
    yt = ["anger", "joy", "neutral", "anger"]
    yp = ["anger", "neutral", "neutral", "anger"]
    m = emotion_metrics(yt, yp)
    assert abs(m["accuracy"] - 0.75) < 1e-9, m
    assert set(m["present_classes"]) == {"anger", "joy", "neutral"}
    assert abs(ccc([1, 2, 3], [1, 2, 3]) - 1.0) < 1e-9
    d = distress_metrics([True, False, True], [True, False, False])
    assert d["recall"] == 0.5 and d["n_positive"] == 2, d
    print("metrics self-test OK")


if __name__ == "__main__":
    _selftest()
