"""M4: weak-label pilot transcripts with TWO Claude models, then measure agreement.

Teachers: Opus 4.8 (claude-opus-4-8) + Sonnet 5 (claude-sonnet-5).
Labels per utterance (design doc 04-pioneer-corpus-design.md SS2):
  emotion (7-class) + valence/arousal (1-5) + distress flag + confidence.
Segments are sent in chunks of 20 so the model sees conversational flow.
Outputs (next to the input csv):
  labels_opus.csv / labels_sonnet.csv  - one row per segment per model
  m4_report.md                         - label distributions + inter-teacher kappa

Usage (needs ANTHROPIC_API_KEY):
  uv run --with anthropic --with pydantic python scripts/vietnamese-ser/m4_weak_label.py \
      --transcripts data/vietnamese-ser/pilot/ep01/transcripts.csv
Optional: --models opus,sonnet   --chunk 20

Provenance: model IDs + prompt are versioned in this file; label csvs carry the model id.
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path
from typing import Literal

import anthropic
from pydantic import BaseModel

MODELS = {"opus": "claude-opus-4-8", "sonnet": "claude-sonnet-5"}
EMOTIONS = ["joy", "sadness", "anger", "fear_anxiety", "surprise", "disgust", "neutral"]

SYSTEM = """Bạn là annotator cảm xúc cho corpus giọng nói tiếng Việt xây từ phim truyền hình.
Input là các utterance THOẠI PHIM, transcript sinh bởi ASR nên CÓ NHIỄU (sai dấu thanh,
lặp từ, thiếu dấu câu, đôi khi 2 nhân vật trong 1 đoạn). Gán nhãn cho TỪNG utterance theo id:

- emotion: joy | sadness | anger | fear_anxiety | surprise | disgust | neutral
  (cảm xúc CHỦ ĐẠO của người nói; nếu 2 người 2 cảm xúc, lấy cảm xúc nổi trội của đoạn)
- valence: 1 (rất tiêu cực) .. 5 (rất tích cực)
- arousal: 1 (rất bình lặng) .. 5 (rất kích động)
- distress: true nếu người nói đang đau khổ/khủng hoảng tâm lý rõ rệt (khóc lóc, tuyệt vọng,
  hoảng loạn, bị đe dọa) - KHÔNG chỉ là buồn nhẹ hay cáu thường
- confidence: 0.0-1.0, độ tin của bạn (hạ thấp khi text nhiễu nặng hoặc mơ hồ)

Dựa vào ngữ cảnh các utterance liền kề trong cùng batch. Trả đúng một nhãn cho MỖI id."""


class SegLabel(BaseModel):
    id: str
    emotion: Literal["joy", "sadness", "anger", "fear_anxiety", "surprise", "disgust", "neutral"]
    valence: Literal[1, 2, 3, 4, 5]
    arousal: Literal[1, 2, 3, 4, 5]
    distress: bool
    confidence: float
    multi_speaker_suspect: bool


class ChunkLabels(BaseModel):
    labels: list[SegLabel]


def label_all(
    client: anthropic.Anthropic, model_id: str, rows: list[dict], chunk: int
) -> dict[str, SegLabel]:
    out: dict[str, SegLabel] = {}
    for i in range(0, len(rows), chunk):
        part = rows[i : i + chunk]
        listing = "\n".join(f"[{r['id']}] {r['text']}" for r in part)
        resp = client.messages.parse(
            model=model_id,
            max_tokens=4096,
            system=SYSTEM,
            messages=[{"role": "user", "content": f"Gán nhãn các utterance sau:\n{listing}"}],
            output_format=ChunkLabels,
        )
        got = {lab.id: lab for lab in resp.parsed_output.labels}
        missing = [r["id"] for r in part if r["id"] not in got]
        if missing:
            print(f"  ! {model_id}: thiếu nhãn cho {missing} (bỏ qua)")
        out.update(got)
        print(f"  {model_id}: {min(i + chunk, len(rows))}/{len(rows)}")
    return out


def cohen_kappa(a: list[str], b: list[str]) -> float:
    n = len(a)
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    ca, cb = Counter(a), Counter(b)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--transcripts", type=Path, required=True)
    ap.add_argument("--models", default="opus,sonnet")
    ap.add_argument("--chunk", type=int, default=20)
    args = ap.parse_args()

    rows = [r for r in csv.DictReader(args.transcripts.open(encoding="utf-8")) if r["text"].strip()]
    outdir = args.transcripts.parent
    client = anthropic.Anthropic()

    results: dict[str, dict[str, SegLabel]] = {}
    for name in args.models.split(","):
        model_id = MODELS[name.strip()]
        print(f">> labeling với {model_id} ({len(rows)} utterance)")
        labels = label_all(client, model_id, rows, args.chunk)
        results[name] = labels
        with (outdir / f"labels_{name}.csv").open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(
                [
                    "id",
                    "model",
                    "emotion",
                    "valence",
                    "arousal",
                    "distress",
                    "confidence",
                    "multi_speaker_suspect",
                ]
            )
            for r in rows:
                lab = labels.get(r["id"])
                if lab:
                    w.writerow(
                        [
                            lab.id,
                            model_id,
                            lab.emotion,
                            lab.valence,
                            lab.arousal,
                            lab.distress,
                            f"{lab.confidence:.2f}",
                            lab.multi_speaker_suspect,
                        ]
                    )

    # report
    lines = [f"# M4 weak-label report — {args.transcripts}", ""]
    for name, labels in results.items():
        dist = Counter(l.emotion for l in labels.values())
        n = len(labels)
        lines.append(f"## {MODELS[name]} — {n} nhãn")
        lines += [f"- {e}: {dist.get(e, 0)} ({dist.get(e, 0) / n:.0%})" for e in EMOTIONS]
        n_dis = sum(1 for l in labels.values() if l.distress)
        conf = sum(l.confidence for l in labels.values()) / n
        lines.append(f"- distress: {n_dis} ({n_dis / n:.0%}) · mean confidence: {conf:.2f}")
        lines.append("")
    if len(results) == 2:
        (na, la), (nb, lb) = results.items()
        common = [i for i in la if i in lb]
        ka = cohen_kappa([la[i].emotion for i in common], [lb[i].emotion for i in common])
        dv = sum(abs(la[i].valence - lb[i].valence) for i in common) / len(common)
        da = sum(abs(la[i].arousal - lb[i].arousal) for i in common) / len(common)
        dis_agree = sum(1 for i in common if la[i].distress == lb[i].distress) / len(common)
        disagreements = [i for i in common if la[i].emotion != lb[i].emotion]
        lines.append(f"## Agreement {na} vs {nb} (n={len(common)})")
        lines.append(f"- **Cohen's κ (emotion): {ka:.3f}**")
        lines.append(
            f"- mean |Δvalence|: {dv:.2f} · mean |Δarousal|: {da:.2f} · distress agree: {dis_agree:.0%}"
        )
        lines.append(
            f"- {len(disagreements)} đoạn bất đồng emotion: {' '.join(disagreements[:20])}"
            + (" ..." if len(disagreements) > 20 else "")
        )
    report = outdir / "m4_report.md"
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n>> report: {report}")
    print("\n".join(lines[-8:]))


if __name__ == "__main__":
    main()
