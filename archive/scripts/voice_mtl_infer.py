#!/usr/bin/env python
"""Local sample test for the voice-MTL-heads artifact (3 heads).

Loads a pulled `artifact_<backbone>/` bundle (config.json + mtl_head.pt), runs the frozen
backbone on one wav to get FRAME-level features, and applies the shared SUPERB trunk + the
three heads to print: emotion (8-way), affect (valence/arousal), and crisis probability vs
the recall-floor-tuned threshold. Mirrors the kernel's c3/c4 path. A single clip is fed
un-padded, so every frame is valid and the masked-mean reduces to a plain mean.

Usage:
    PYTHONPATH=src .venv-voice/bin/python scripts/voice_mtl_infer.py \
        kaggle/voice/pebble-voice-mtl-heads/out/artifact_wavlm-large sample.wav

Env: .venv-voice (py3.12, torch 2.2.2 CPU). WavLM works out of the box; the emotion2vec
backbone needs `funasr` installed locally (else use the wavlm-large bundle).
"""
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
import torch.nn as nn
import torch.nn.functional as F
import torchaudio

SR = 16000


class MTLHead(nn.Module):
    def __init__(self, dim, n_emo, hid):
        super().__init__()
        self.pre = nn.Linear(dim, hid)
        self.emo = nn.Linear(hid, n_emo)
        self.reg = nn.Linear(hid, 2)
        self.safe = nn.Linear(hid, 1)

    def forward(self, x):                  # x (1, T, dim), all frames valid
        z = F.relu(self.pre(x)).mean(1)    # mean-pool over time
        return self.emo(z), self.reg(z), self.safe(z).squeeze(-1)


def load_wav(path):
    wav, sr = sf.read(path, dtype="float32")
    if wav.ndim > 1:
        wav = wav.mean(axis=1)
    if sr != SR:
        wav = torchaudio.functional.resample(torch.from_numpy(wav), sr, SR).numpy()
    return wav.astype(np.float32)


def feat_wavlm(wav, hf_id):
    from transformers import AutoFeatureExtractor, WavLMModel
    fe = AutoFeatureExtractor.from_pretrained(hf_id)
    model = WavLMModel.from_pretrained(hf_id).eval()
    enc = fe([wav], sampling_rate=SR, return_tensors="pt", padding=True)
    with torch.no_grad():
        h = model(**enc).last_hidden_state          # (1, T, 1024)
    return h.float().numpy()


def feat_emotion2vec(wav, hf_id):
    from funasr import AutoModel as FunASR
    import os, tempfile
    model = FunASR(model=hf_id, hub="hf", disable_update=True)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
        sf.write(tf.name, wav, SR); path = tf.name
    r = model.generate(path, granularity="frame", extract_embedding=True, output_dir=None)
    os.remove(path)
    return np.asarray(r[0]["feats"], dtype=np.float32)[None, :, :]   # (1, T, 768)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    bundle, wav_path = Path(sys.argv[1]), sys.argv[2]
    cfg = json.loads((bundle / "config.json").read_text())
    wav = load_wav(wav_path)

    if cfg["backbone"] == "emotion2vec":
        X = feat_emotion2vec(wav, cfg["backbone_hf_id"])
    else:
        X = feat_wavlm(wav, cfg["backbone_hf_id"])

    emotions = cfg["emotions"]
    head = MTLHead(cfg["embed_dim"], len(emotions), cfg["head_dim"])
    head.load_state_dict(torch.load(bundle / "mtl_head.pt", map_location="cpu"))
    head.eval()
    with torch.no_grad():
        emo_logits, reg, safe_logit = head(torch.tensor(X, dtype=torch.float))
    probs = torch.softmax(emo_logits, dim=-1).squeeze(0).numpy()
    valence, arousal = reg.squeeze(0).tolist()
    crisis_p = torch.sigmoid(safe_logit).item()
    tau = cfg["crisis_tau"]

    order = np.argsort(probs)[::-1]
    print(f"backbone={cfg['backbone']} ({cfg['backbone_hf_id']})  wav={wav_path}")
    print(f"EMOTION : {emotions[order[0]]}  (p={probs[order[0]]:.3f})")
    print("  top-3 :", ", ".join(f"{emotions[i]}={probs[i]:.3f}" for i in order[:3]))
    print(f"AFFECT  : valence={valence:+.2f}  arousal={arousal:+.2f}  (proxy V/A, [-1,1])")
    flag = "CRISIS" if crisis_p >= tau else "ok"
    print(f"CRISIS  : p={crisis_p:.3f}  tau(recall>={cfg['recall_floor']})={tau:.3f}  -> {flag}")


if __name__ == "__main__":
    main()
