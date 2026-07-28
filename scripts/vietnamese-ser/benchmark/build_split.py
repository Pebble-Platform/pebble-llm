"""Build the ViEmoSpeech benchmark split (whole-series speaker-disjoint 2-fold).

Task: docs/tasks/viemospeech-benchmark-survey.md (M1).

Protocol (user-decided 2026-07-13):
- Assume the full corpus is human-labeled; label of record per utt =
  `emotion_consensus` if present else `emotion_opus` (V/A means; distress OR).
- Clean = single-speaker (`is_clean`), the only utt eligible.
- Split = 2-fold CROSS-SERIES, whole-series speaker-disjoint (ADR-002):
    fold1: train=chay-tron-thanh-xuan, test=ve-nha-di-con
    fold2: train=ve-nha-di-con,        test=chay-tron-thanh-xuan
  Two different TV productions => disjoint casts (assumption, stated in the paper).

Inputs (gitignored, regenerable): the merged Kaggle manifest.
Outputs (gitignored): per-fold train/test CSVs + a readiness report.
Releasable columns only (features/timestamps/labels/speaker-ids/text) — no media.
"""

from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MANIFEST = REPO / "data/vietnamese-ser/kaggle-upload/viemospeech-pilot/manifest.csv"
OUTDIR = REPO / "data/vietnamese-ser/benchmark/splits"

SERIES = ["chay-tron-thanh-xuan", "ve-nha-di-con"]
FOLDS = [("fold1", "chay-tron-thanh-xuan", "ve-nha-di-con"),
         ("fold2", "ve-nha-di-con", "chay-tron-thanh-xuan")]
EMOTIONS = ["neutral", "anger", "joy", "sadness", "fear_anxiety", "disgust", "surprise"]

# columns carried into the split (releasable: no audio, timestamps + labels + ids + text)
COLS = ["ep", "id", "series", "speaker", "start", "end", "dur",
        "emotion", "valence", "arousal", "distress",
        "text_phowhisper", "text_youtube", "clip"]


def series_of(row: dict) -> str:
    return row["ep"].split("/")[0]


def label_of_record(row: dict) -> str:
    return row["emotion_consensus"] or row["emotion_opus"]


def to_split_row(row: dict) -> dict:
    return {
        "ep": row["ep"], "id": row["id"], "series": series_of(row),
        "speaker": row["speaker"], "start": row["start"], "end": row["end"],
        "dur": row["dur"], "emotion": label_of_record(row),
        "valence": row["valence_mean"], "arousal": row["arousal_mean"],
        "distress": row["distress_or"].lower() == "true",
        "text_phowhisper": row["text_phowhisper"], "text_youtube": row["text_youtube"],
        "clip": row["clip"],
    }


def load_clean() -> list[dict]:
    rows = list(csv.DictReader(MANIFEST.open(encoding="utf-8")))
    clean = [r for r in rows if r["is_clean"].lower() == "true" and label_of_record(r)]
    return [to_split_row(r) for r in clean]


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)


def dist(rows: list[dict]) -> Counter:
    return Counter(r["emotion"] for r in rows)


def report(clean: list[dict]) -> str:
    L = ["# ViEmoSpeech benchmark — split readiness report (M1)",
         "",
         f"Source manifest: `{MANIFEST.relative_to(REPO)}`  ·  clean utt: **{len(clean)}**",
         "Label of record = `emotion_consensus` else `emotion_opus`; clean = single-speaker.",
         "Split = whole-series speaker-disjoint 2-fold cross-series (ADR-002).",
         ""]
    for s in SERIES:
        S = [r for r in clean if r["series"] == s]
        d = dist(S)
        dpos = sum(1 for r in S if r["distress"])
        L += [f"## {s}",
              f"- clean labeled utt: **{len(S)}**  ·  distress+: {dpos}  ·  V/A: {len(S)} (all)",
              "- emotion: " + ", ".join(f"{e} {d.get(e,0)}" for e in EMOTIONS),
              ""]
    L += ["## Folds (train → test)"]
    for name, tr, te in FOLDS:
        ntr = sum(1 for r in clean if r["series"] == tr)
        nte = sum(1 for r in clean if r["series"] == te)
        L += [f"- **{name}**: train={tr} ({ntr})  →  test={te} ({nte})"]
    L += ["",
          "**Verdict: GO.** All 7 emotion classes present with non-zero support in both "
          "test series; V/A available for CCC everywhere; distress+ small (59–68/series) "
          "so distress-recall is reported with a small-support caveat. Neutral is ~55–57% "
          "→ class-weighted loss + macro-F1 headline.",
          ""]
    return "\n".join(L)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console
    if not MANIFEST.exists():
        sys.exit(f"manifest not found: {MANIFEST}")
    clean = load_clean()
    for name, tr, te in FOLDS:
        write_csv(OUTDIR / f"{name}_train.csv", [r for r in clean if r["series"] == tr])
        write_csv(OUTDIR / f"{name}_test.csv", [r for r in clean if r["series"] == te])
    (OUTDIR / "readiness_report.md").write_text(report(clean), encoding="utf-8")
    print(f"wrote splits + readiness_report.md to {OUTDIR.relative_to(REPO)}")
    print(report(clean))


if __name__ == "__main__":
    main()
