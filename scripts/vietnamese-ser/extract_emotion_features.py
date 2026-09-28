"""Extract the two feature sets change 015 analyses, one row per human-clean clip.

  * eGeMAPSv02 functionals (88 hand-crafted acoustic features, openSMILE) — the
    interpretable set: prosody / voice quality / spectral.
  * Frozen WavLM-Large hidden states from EVERY layer (embedding output + 24
    transformer layers = 25), mean-pooled over time — for the layer-wise probe.
    Layer 24 is ``last_hidden_state``, i.e. the exact feature the baseline kernel
    (vnser-train.py) trains on.

Same clip filter as build_kaggle_gold.py (human ``emotion``, not rejected, not multi —
I3), restricted to the two series of the baseline (SERIES, preregistration §2), read straight from state.db and episodes/<epKey>/clips/*.wav: nothing is copied or
uploaded. Features only, no raw audio and no transcript text in the output (I1). Output
lands under data/** (gitignored); each stage is skipped if its file already exists, so an
interrupted run resumes.

This script makes NO analysis choice (speaker normalisation, folds, statistics): it
stores raw features + the metadata the pre-registered analysis needs
(docs/spec/changes/015-emotion-acoustic-features/preregistration.md).

Usage (from repo root):
  PYTHONIOENCODING=utf-8 PYTHONPATH=scripts/vietnamese-ser \
    .venv-vnser/Scripts/python.exe scripts/vietnamese-ser/extract_emotion_features.py
  # smoke: --limit 5 --out data/vietnamese-ser/features/015-smoke
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import soundfile as sf
from labeler_store import read_records

ROOT = Path(__file__).resolve().parents[2]
EPISODES = ROOT / "data" / "vietnamese-ser" / "episodes"
OUT = ROOT / "data" / "vietnamese-ser" / "features" / "015"
BACKBONE = "microsoft/wavlm-large"
SR = 16000
# Fixed clip set (preregistration §2): the two series the baseline evaluates on. A series
# labelled later (cay-tao-no-hoa, 6 clips on 2026-09-27) would become a near-empty LOSO fold.
SERIES = ("chay-tron-thanh-xuan", "ve-nha-di-con")
META = [
    "key",
    "ep",
    "id",
    "series",
    "speaker",
    "gender",
    "age_group",
    "dialect",
    "dur",
    "emotion",
    "valence",
    "arousal",
    "annotator",
    "ts",
]


def clean_clips(limit: int | None) -> pd.DataFrame:
    rows = []
    for r in read_records(EPISODES):
        if not r.get("emotion") or r.get("rejected") or r.get("multi"):
            continue
        if r["epKey"].split("/")[0] not in SERIES:
            continue
        wav = EPISODES / r["epKey"] / "clips" / f"{r['id']}.wav"
        if not wav.is_file():
            continue
        rows.append(
            {
                "key": f"{r['epKey']}/{r['id']}",
                "ep": r["epKey"],
                "id": r["id"],
                "series": r["epKey"].split("/")[0],
                # `speaker` is mixed: a human-assigned cast name, OR a raw pyannote id
                # ("SPEAKER_07") that is only unique WITHIN one episode; empty where unset.
                "speaker": r.get("speaker") or "",
                "gender": r.get("gender") or "",
                "age_group": r.get("age_group") or "",
                "dialect": r.get("dialect") or "",
                "dur": round(sf.info(wav).duration, 3),
                "emotion": r["emotion"],
                "valence": r.get("valence"),
                "arousal": r.get("arousal"),
                "annotator": r.get("annotator", ""),
                "ts": r.get("ts", ""),
                "_wav": wav,
            }
        )
    df = pd.DataFrame(rows).sort_values("key").reset_index(drop=True)  # stable row order
    return df.head(limit) if limit else df


def extract_egemaps(df: pd.DataFrame, path: Path) -> None:
    import opensmile

    smile = opensmile.Smile(
        feature_set=opensmile.FeatureSet.eGeMAPSv02,
        feature_level=opensmile.FeatureLevel.Functionals,
    )
    feats = []
    for i, wav in enumerate(df["_wav"]):
        feats.append(smile.process_file(str(wav)).iloc[0])
        if (i + 1) % 200 == 0:
            print(f"[egemaps] {i + 1}/{len(df)}")
    out = pd.concat([df[META], pd.DataFrame(feats).reset_index(drop=True)], axis=1)
    out.to_csv(path, index=False, encoding="utf-8")
    print(f"[egemaps] wrote {path} ({len(out)} x {out.shape[1] - len(META)} features)")


def extract_wavlm_layers(df: pd.DataFrame, path: Path) -> None:
    import torch
    from transformers import AutoFeatureExtractor, WavLMModel

    device = "cuda" if torch.cuda.is_available() else "cpu"
    fe = AutoFeatureExtractor.from_pretrained(BACKBONE)
    model = WavLMModel.from_pretrained(BACKBONE).to(device).eval()

    embs = []
    for i, wav_path in enumerate(df["_wav"]):
        wav, sr = sf.read(wav_path, dtype="float32")
        assert sr == SR, f"{wav_path}: {sr} Hz"
        if wav.ndim > 1:
            wav = wav.mean(axis=1)
        inp = fe(wav, sampling_rate=SR, return_tensors="pt").input_values.to(device)
        with torch.no_grad():
            hs = model(inp, output_hidden_states=True).hidden_states  # 25 x [1, T, 1024]
        embs.append(torch.stack([h.mean(dim=1).squeeze(0) for h in hs]).cpu().numpy())
        if (i + 1) % 100 == 0:
            print(f"[wavlm] {i + 1}/{len(df)}")
    emb = np.stack(embs).astype("float32")  # [N, 25, 1024]
    np.savez(path, keys=df["key"].to_numpy(), emb=emb)
    print(f"[wavlm] wrote {path} {emb.shape}")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--limit", type=int, help="first N clips only (smoke test)")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    df = clean_clips(args.limit)
    print(f"[data] {len(df)} human-clean clips · {df['series'].value_counts().to_dict()}")

    eg, wl = args.out / "egemaps.csv", args.out / "wavlm_layers.npz"
    if eg.exists():
        print(f"[egemaps] exists, skip: {eg}")
    else:
        extract_egemaps(df, eg)
    if wl.exists():
        print(f"[wavlm] exists, skip: {wl}")
    else:
        extract_wavlm_layers(df, wl)

    import opensmile
    import transformers

    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT
    ).stdout.strip()
    (args.out / "config.json").write_text(
        json.dumps(
            {
                "change": "015",
                "n_clips": len(df),
                "series": df["series"].value_counts().to_dict(),
                "filter": "human emotion, not rejected, not multi (I3) — same as build_kaggle_gold.py; "
                f"series in {list(SERIES)}",
                "egemaps": {
                    "feature_set": "eGeMAPSv02",
                    "level": "functionals",
                    "opensmile": opensmile.__version__,
                },
                "wavlm": {
                    "backbone": BACKBONE,
                    "frozen": True,
                    "pool": "mean over time",
                    "layers": "hidden_states[0..24]; 24 == last_hidden_state (baseline)",
                    "transformers": transformers.__version__,
                },
                "label_source": "human single-annotator (ADR-003)",
                "git_commit": commit,
                "created": dt.datetime.now(dt.UTC).isoformat(timespec="seconds"),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
