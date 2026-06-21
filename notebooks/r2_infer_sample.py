"""Load a trained R2 dual-head model and predict suicide-risk level for a sample post-sequence.

Usage:
    .venv-voice/bin/python notebooks/r2_infer_sample.py [path/to/best_model.pt]

Reconstructs the architecture WITHOUT downloading the encoder weights (AutoModel.from_config),
then loads the checkpoint — so inference needs no network once the checkpoint is local.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer

# import the model/dataset code from the training script (sibling file)
_spec = importlib.util.spec_from_file_location(
    "r2_mod", Path(__file__).parent / "r2-suicide-risk-dualhead.py")
r2 = importlib.util.module_from_spec(_spec)
sys.modules["r2_mod"] = r2          # register so @dataclass introspection works
_spec.loader.exec_module(r2)


def load_model(ckpt_path: str):
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    cfg = r2.Config()
    cfg.model_name = ckpt["model_name"]
    cfg.n_classes = ckpt["n_classes"]
    cfg.use_features = ckpt["use_features"]
    model = r2.HierarchicalDualHead(cfg, pretrained=False)   # structure only, no download
    model.load_state_dict(ckpt["state_dict"])
    model.eval()
    tok = AutoTokenizer.from_pretrained(cfg.model_name)
    return model, tok, cfg, ckpt["label_names"]


@torch.no_grad()
def predict(model, tok, cfg, posts: list[str]):
    posts = posts[-cfg.seq_len:]
    n = len(posts)
    padded = posts + [""] * (cfg.seq_len - n)
    enc = tok(padded, truncation=True, max_length=cfg.max_length,
              padding="max_length", return_tensors="pt")
    valid = torch.zeros(1, cfg.seq_len, dtype=torch.bool); valid[0, :n] = True
    feats = torch.from_numpy(r2.stat_features(posts, cfg.seq_len)).unsqueeze(0)
    coral, cls = model(enc["input_ids"].unsqueeze(0), enc["attention_mask"].unsqueeze(0),
                       valid, torch.zeros(1, cfg.seq_len), feats)
    p = 0.5 * r2.coral_to_probs(coral, cfg.n_classes) + 0.5 * F.softmax(cls, dim=-1)
    return p.squeeze(0).numpy()


if __name__ == "__main__":
    ckpt_path = sys.argv[1] if len(sys.argv) > 1 else "r2_out/best_model.pt"
    model, tok, cfg, names = load_model(ckpt_path)
    print(f">>> loaded {ckpt_path}  (encoder={cfg.model_name}, cv_macro_f1 in ckpt)")

    sample = [
        "Lately I just feel empty, like nothing I do matters anymore.",
        "I keep thinking everyone would be better off without me here.",
        "I've started giving away my things and writing letters to people.",
        "Last year I tried to end it but they found me in time.",
        "I don't know how much longer I can keep pretending I'm okay.",
    ]
    probs = predict(model, tok, cfg, sample)
    pred = int(np.argmax(probs))
    print(">>> sample post-sequence (5 posts):")
    for p in sample:
        print("    -", p)
    print(f">>> predicted risk level: {pred} = {names[pred]}")
    print(">>> class probabilities:")
    for i, nm in enumerate(names):
        print(f"    {i} {nm:10s}: {probs[i]:.3f}")
