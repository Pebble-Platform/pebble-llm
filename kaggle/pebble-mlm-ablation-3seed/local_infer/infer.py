"""Local CPU inference for the shipped Pebble model (pebble_model.pt).

Rebuilds the MultiTask architecture from s5 using the LOCAL NeoBERT code
(model.py, xformers SwiGLU swapped for a pure-torch equivalent), then loads the
fine-tuned state_dict. No GPU, no xformers, no trust_remote_code download —
encoder weights live inside the ckpt.

Usage:
    python infer.py                       # built-in demo sentences
    python infer.py "your sentence here"  # analyze the given sentence(s)
"""
import sys, warnings
warnings.filterwarnings("ignore")
import torch
import torch.nn as nn
from transformers import AutoTokenizer
from model import NeoBERT, NeoBERTConfig

HERE = sys.path[0]
CKPT = f"{HERE}/../output_v4/pebble_model.pt"
DEVICE = torch.device("cpu")

ck = torch.load(CKPT, map_location="cpu", weights_only=False)
EMO_NAMES, MAX_LEN = ck["emo_names"], ck["max_len"]
N_EMO = len(EMO_NAMES)
print(f"ckpt: arm={ck['arm']} seed={ck['seed']} | {N_EMO} emotions | max_len={MAX_LEN}")


class Head(nn.Module):
    def __init__(s, h, out, d=256, p=0.1):
        super().__init__()
        s.net = nn.Sequential(nn.Dropout(p), nn.Linear(h, d), nn.GELU(), nn.Dropout(p), nn.Linear(d, out))
    def forward(s, x): return s.net(x)


class MultiTask(nn.Module):
    def __init__(s, cfg):
        super().__init__()
        s.encoder = NeoBERT(cfg)
        h = cfg.hidden_size
        s.emotion_head, s.score_head = Head(h, N_EMO), Head(h, 1)
    def forward(s, ids, attn):
        cls = s.encoder(input_ids=ids, attention_mask=attn).last_hidden_state[:, 0, :]
        return s.emotion_head(cls), torch.sigmoid(s.score_head(cls)).squeeze(-1)


import json
cfg = NeoBERTConfig(**{k: v for k, v in json.load(open(f"{HERE}/config.json")).items()
                       if k in ("hidden_size", "num_hidden_layers", "num_attention_heads",
                                "intermediate_size", "norm_eps", "vocab_size", "pad_token_id", "max_length")})
tok = AutoTokenizer.from_pretrained(HERE)  # local tokenizer files (bert-base-uncased)
model = MultiTask(cfg).to(DEVICE)
missing, unexpected = model.load_state_dict(ck["state_dict"], strict=False)
print(f"load_state_dict: missing={len(missing)} unexpected={len(unexpected)}")
if missing:    print("  missing[:8]:", missing[:8])
if unexpected: print("  unexpected[:8]:", unexpected[:8])
model.eval()


@torch.no_grad()
def analyze(text, topk=3):
    e = tok([text], truncation=True, max_length=MAX_LEN, padding="max_length", return_tensors="pt")
    el, sp = model(e["input_ids"].to(DEVICE), e["attention_mask"].to(DEVICE))
    probs = torch.softmax(el.float(), -1).cpu().numpy()[0]
    sev = float(sp.float().cpu().numpy()[0])
    top = probs.argsort()[::-1][:topk]
    return {"severity": round(sev, 3),
            "emotions": [(EMO_NAMES[i], round(float(probs[i]), 3)) for i in top]}


if __name__ == "__main__":
    TESTS = sys.argv[1:] or [
        "I just got promoted, best day of my life!",
        "the meeting is at 3pm tomorrow",
        "why does everyone always ignore me",
        "I can't do this anymore, nothing matters",
        "I'm so scared something bad will happen",
    ]
    print("\n================= INFERENCE =================")
    for t in TESTS:
        r = analyze(t)
        top = ", ".join(f"{e}:{p}" for e, p in r["emotions"])
        print(f"severity={r['severity']:.3f} | {top}   <= {t!r}")
