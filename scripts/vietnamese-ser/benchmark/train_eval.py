"""Shared MTL probe + train/eval loop for the ViEmoSpeech benchmark (M2).

One trainer every feature-vector method reports through, so the results table is
apples-to-apples. Input = a frozen utterance feature matrix X (N, dim) + a Fold of
targets; the probe is a small shared trunk with three heads:
  - emotion  : 7-way, class-weighted cross-entropy      -> macro-F1
  - valence  : regression, CCC loss (1 - CCC)           -> CCC
  - arousal  : regression, CCC loss                      -> CCC
  - distress : binary, BCE (pos_weight)                 -> recall

Feature-agnostic: the caller decides what X is — MFCC(mean+std), WavLM(mean-pool),
emotion2vec-S(utt_x), PhoBERT(CLS), or concat([text, audio]) for fusion. Frozen
backbones only (constraint) -> the backbone never appears here, just its features.

torch is the only heavy dep; runs on CPU for the probe (features are precomputed).
"""

from __future__ import annotations

import numpy as np
import torch
import torch.nn as nn
from data import EMOTIONS
from metrics import ccc, distress_metrics, emotion_metrics

N_EMO = len(EMOTIONS)


def ccc_loss(pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
    """1 - Lin's CCC, differentiable (RJCMA/MSP objective)."""
    pm, tm = pred.mean(), target.mean()
    pv, tv = pred.var(unbiased=False), target.var(unbiased=False)
    cov = ((pred - pm) * (target - tm)).mean()
    denom = pv + tv + (pm - tm) ** 2
    return 1 - (2 * cov / denom.clamp_min(1e-8))


class Probe(nn.Module):
    def __init__(self, dim: int, hidden: int = 256, p: float = 0.3):
        super().__init__()
        self.trunk = nn.Sequential(nn.Linear(dim, hidden), nn.ReLU(), nn.Dropout(p))
        self.emotion = nn.Linear(hidden, N_EMO)
        self.va = nn.Linear(hidden, 2)       # valence, arousal (scaled to 1..5)
        self.distress = nn.Linear(hidden, 1)

    def forward(self, x):
        h = self.trunk(x)
        va = torch.sigmoid(self.va(h)) * 4 + 1   # -> [1,5]
        return self.emotion(h), va, self.distress(h).squeeze(-1)


def _standardize(xtr: np.ndarray, xte: np.ndarray):
    mu, sd = xtr.mean(0), xtr.std(0) + 1e-6
    return (xtr - mu) / sd, (xte - mu) / sd


def train_eval_once(x_train, train_fold, x_test, test_fold, *, seed=0,
                    epochs=60, lr=1e-3, wd=1e-4, hidden=256,
                    w_emo=1.0, w_va=1.0, w_dist=1.0, device="cpu") -> dict:
    torch.manual_seed(seed)
    np.random.seed(seed)
    xtr, xte = _standardize(np.asarray(x_train, np.float32), np.asarray(x_test, np.float32))
    dev = torch.device(device)
    Xtr = torch.tensor(xtr, device=dev)
    Xte = torch.tensor(xte, device=dev)
    emo = torch.tensor(train_fold.emotion, device=dev)
    val = torch.tensor(train_fold.valence, device=dev)
    aro = torch.tensor(train_fold.arousal, device=dev)
    dis = torch.tensor(train_fold.distress.astype(np.float32), device=dev)

    cw = torch.tensor(train_fold.class_weights(), device=dev)
    n_pos = max(int(train_fold.distress.sum()), 1)
    pos_w = torch.tensor([(len(train_fold) - n_pos) / n_pos], device=dev)
    ce = nn.CrossEntropyLoss(weight=cw)
    bce = nn.BCEWithLogitsLoss(pos_weight=pos_w)

    model = Probe(Xtr.shape[1], hidden=hidden).to(dev)
    opt = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=wd)
    model.train()
    for _ in range(epochs):
        opt.zero_grad()
        e_logit, va, d_logit = model(Xtr)
        loss = (w_emo * ce(e_logit, emo)
                + w_va * (ccc_loss(va[:, 0], val) + ccc_loss(va[:, 1], aro))
                + w_dist * bce(d_logit, dis))
        loss.backward()
        opt.step()

    model.eval()
    with torch.no_grad():
        e_logit, va, d_logit = model(Xte)
    emo_pred = [EMOTIONS[i] for i in e_logit.argmax(1).cpu().numpy()]
    m = emotion_metrics(test_fold.emotion_name, emo_pred)
    va = va.cpu().numpy()
    return {
        "macro_f1": m["macro_f1"], "accuracy": m["accuracy"],
        "per_class_f1": m["per_class_f1"], "support": m["support"],
        "ccc_valence": ccc(test_fold.valence, va[:, 0]),
        "ccc_arousal": ccc(test_fold.arousal, va[:, 1]),
        **{f"distress_{k}": v for k, v in
           distress_metrics(test_fold.distress, (d_logit.cpu().numpy() > 0)).items()},
    }


def train_eval(x_train, train_fold, x_test, test_fold, *, seeds=(0, 1, 2), **kw) -> dict:
    """Run over seeds, return mean±std of the scalar metrics."""
    runs = [train_eval_once(x_train, train_fold, x_test, test_fold, seed=s, **kw)
            for s in seeds]
    scalars = ["macro_f1", "accuracy", "ccc_valence", "ccc_arousal",
               "distress_recall", "distress_precision"]
    agg = {k: (float(np.mean([r[k] for r in runs])),
               float(np.std([r[k] for r in runs]))) for k in scalars}
    agg["support"] = runs[0]["support"]
    agg["per_class_f1_mean"] = {c: float(np.mean([r["per_class_f1"][c] for r in runs]))
                                for c in runs[0]["per_class_f1"]}
    return agg


def _selftest() -> None:
    # random features must give ~chance macro-F1 and near-0 CCC — sanity, not skill.
    from data import load_fold
    tr, te = load_fold("fold1", "train"), load_fold("fold1", "test")
    rng = np.random.default_rng(0)
    dim = 64
    xtr = rng.standard_normal((len(tr), dim)).astype(np.float32)
    xte = rng.standard_normal((len(te), dim)).astype(np.float32)
    out = train_eval(xtr, tr, xte, te, seeds=(0,), epochs=10)
    print("random-feature sanity:", {k: v for k, v in out.items()
                                      if k in ("macro_f1", "ccc_valence", "distress_recall")})
    assert out["macro_f1"][0] < 0.4, "random features should be near chance"
    print("train_eval self-test OK")


if __name__ == "__main__":
    _selftest()
