"""Kaggle kernel — frozen utterance-level feature extraction for the ViEmoSpeech benchmark.

Runs ONCE on a GPU kernel (P100/T4) over the private dataset clips and writes one
`.npz` per backbone ({ids, X}) to /kaggle/working, which is then pulled back and fed
to the local `run_benchmark.py`. Frozen backbones only (no fine-tune).

Backbones (utterance vector per clip):
  - wavlm-large     : microsoft/wavlm-large, mean-pool last_hidden_state -> 1024
  - emotion2vec-s   : ASLP-lab/Emotion2Vec-S via fairseq, out["utt_x"]   -> 768
  - emotion2vec     : iic/emotion2vec_base via FunASR, granularity=utterance -> 768
  - mfcc            : MFCC(20)+delta+delta2 mean+std (parity with the local baseline) -> 120

Each backbone is GUARDED: a failed install/load skips that arm, never kills the kernel
(fairseq is the fragile one — see the pinned install below).

DO NOT RUN until the corpus is human-labeled (per docs/tasks/viemospeech-benchmark-survey.md
decision 2026-07-13); this only produces *features*, which are label-agnostic, but we
keep one push→run for the final labels to avoid drift.

Dataset input:  /kaggle/input/viemospeech-pilot/{manifest.csv, clips/*.wav}
Output:         /kaggle/working/{wavlm-large,emotion2vec-s,emotion2vec,mfcc}.npz

Setup cell (run before this script, in a separate cell so a fairseq failure is isolated):

    # fairseq for emotion2vec-S (pinned; upstream archived Mar-2026 + breaks on modern pip)
    !pip install -q "pip<24.1"
    !pip install -q "omegaconf==2.0.6" "hydra-core==1.0.7" "PyYAML==5.4.1"
    !pip install -q "fairseq==0.12.2" || echo "fairseq install failed -> emotion2vec-s arm will skip"
    !pip install -q funasr modelscope || echo "funasr skip -> base emotion2vec arm will skip"
    # sparse-fetch only the data2vec user-dir (4 small .py) for emotion2vec-S
    !git clone --depth 1 --filter=blob:none --sparse https://github.com/zxzhao0/C2SER.git
    !cd C2SER && git sparse-checkout set Emotion2Vec-S/examples/data2vec
    # emotion2vec-S checkpoint (~1.13 GB)
    from huggingface_hub import hf_hub_download
    hf_hub_download("ASLP-lab/Emotion2Vec-S", "checkpoint.pt", local_dir="e2vs_ckpt")
"""

from __future__ import annotations

import csv
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf
import torch

IN = Path("/kaggle/input/viemospeech-pilot")
OUT = Path("/kaggle/working")
SR = 16000
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_clips() -> tuple[list[str], list[np.ndarray]]:
    rows = [r for r in csv.DictReader((IN / "manifest.csv").open(encoding="utf-8"))
            if r["is_clean"].lower() == "true"]
    ids, wavs = [], []
    for r in rows:
        wav, sr = sf.read(IN / r["clip"])
        if wav.ndim > 1:
            wav = wav.mean(1)
        assert sr == SR, f"{r['clip']} sr={sr}"
        ids.append(f"{r['ep']}::{r['id']}")
        wavs.append(wav.astype(np.float32))
    print(f"loaded {len(ids)} clean clips")
    return ids, wavs


# ---- backbone extractors: each returns a list of (dim,) utterance vectors ----

def extract_wavlm(wavs: list[np.ndarray]) -> np.ndarray:
    # Per-clip (bs=1) so there is no padding and mean-pool over time is exact.
    from transformers import AutoFeatureExtractor, WavLMModel
    fe = AutoFeatureExtractor.from_pretrained("microsoft/wavlm-large")
    model = WavLMModel.from_pretrained("microsoft/wavlm-large").to(DEVICE).eval()
    out = []
    with torch.no_grad():
        for w in wavs:
            enc = fe(w, sampling_rate=SR, return_tensors="pt")
            enc = {k: v.to(DEVICE) for k, v in enc.items()}
            h = model(**enc).last_hidden_state          # (1, T, 1024)
            out.append(h.mean(1).float().cpu().numpy()[0])
    return np.stack(out)


def extract_emotion2vec_s(wavs: list[np.ndarray]) -> np.ndarray:
    import fairseq

    @dataclass
    class UserDirModule:
        user_dir: str

    fairseq.utils.import_user_module(UserDirModule("C2SER/Emotion2Vec-S/examples/data2vec"))
    model, _, _ = fairseq.checkpoint_utils.load_model_ensemble_and_task(
        ["e2vs_ckpt/checkpoint.pt"])
    model = model[0].to(DEVICE).eval()
    out = []
    with torch.no_grad():
        for w in wavs:
            x = torch.tensor(w, device=DEVICE).unsqueeze(0)     # (1, T)
            r = model.extract_features(x)
            out.append(r["utt_x"].cpu().numpy()[0])             # (768,)
    return np.stack(out)


def extract_emotion2vec(wavs: list[np.ndarray]) -> np.ndarray:
    from funasr import AutoModel as FunASR
    try:
        model = FunASR(model="iic/emotion2vec_base", hub="hf", disable_update=True)
    except Exception:
        from huggingface_hub import snapshot_download
        model = FunASR(model=snapshot_download("emotion2vec/emotion2vec_base"),
                       disable_update=True)
    out = []
    for w in wavs:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
            sf.write(tf.name, w, SR)
            path = tf.name
        r = model.generate(path, granularity="utterance", extract_embedding=True)
        out.append(np.asarray(r[0]["feats"], dtype=np.float32))  # (768,)
        os.remove(path)
    return np.stack(out)


def extract_mfcc(wavs: list[np.ndarray]) -> np.ndarray:
    import torchaudio
    mf = torchaudio.transforms.MFCC(
        sample_rate=SR, n_mfcc=20,
        melkwargs={"n_fft": 400, "hop_length": 160, "n_mels": 40})
    out = []
    for w in wavs:
        m = mf(torch.tensor(w).unsqueeze(0)).squeeze(0)
        d1 = torchaudio.functional.compute_deltas(m)
        d2 = torchaudio.functional.compute_deltas(d1)
        feat = torch.cat([m, d1, d2], 0)
        out.append(torch.cat([feat.mean(1), feat.std(1)]).numpy())
    return np.stack(out)


EXTRACTORS = {
    "wavlm-large": extract_wavlm,
    "emotion2vec-s": extract_emotion2vec_s,
    "emotion2vec": extract_emotion2vec,
    "mfcc": extract_mfcc,
}


def main() -> None:
    ids, wavs = load_clips()
    for name, fn in EXTRACTORS.items():
        try:
            print(f"\n[{name}] extracting...")
            X = fn(wavs).astype(np.float32)
            np.savez(OUT / f"{name}.npz", ids=np.array(ids), X=X)
            print(f"[{name}] wrote {name}.npz X={X.shape}")
            torch.cuda.empty_cache()
        except Exception as e:
            print(f"[{name}] SKIPPED -> {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
