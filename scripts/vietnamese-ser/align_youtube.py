"""Align YouTube caption blocks to pilot segments and measure PhoWhisper quality.

Reads segments.csv + transcripts.csv (PhoWhisper) + youtube_transcripts.txt from a
pilot dir, aligns YouTube caption text to each segment by time-overlap, and writes
transcripts_yt.csv + m4b_wer_report.md. See docs/tasks/m4b-align-youtube-plan.md.

Run: PYTHONIOENCODING=utf-8 uv run --with rapidfuzz python scripts/vietnamese-ser/align_youtube.py
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from statistics import mean, median

from rapidfuzz import fuzz
from rapidfuzz.distance import Levenshtein

# End time (seconds) assigned to the final YouTube block (episode length ~35:36).
LAST_BLOCK_END = 2136.0
# Timing tolerance when matching caption blocks to a segment window.
TOL = 1.0
# Non-speech block = text is exactly a single bracket token, e.g. [âm nhạc], [Vỗ tay].
NON_SPEECH_RE = re.compile(r"^\[[^\]]*\]$")
# Leading M:SS marker of every caption line.
MSS_RE = re.compile(r"^(\d+):(\d{2})")
# Verbose prefixes glued after M:SS. Minutes part optional; seconds part optional.
MIN_PREFIX_RE = re.compile(r"^\d+\s+minutes?,?\s*")
SEC_PREFIX_RE = re.compile(r"^\d+\s+seconds?:\s*")
# Punctuation stripped during normalization (Vietnamese tone marks are KEPT).
PUNCT_RE = re.compile(r"[.,?!…:\"'\-]")
WS_RE = re.compile(r"\s+")


def parse_youtube(path: Path) -> list[dict]:
    """Parse the caption file into ordered blocks with start/end/text/is_speech.

    Handles the 4 timestamp variants (seconds-only; minute+seconds; minutes-only
    with comma; minutes-only, no colon before text). End of a block = start of the
    next block; the last block ends at LAST_BLOCK_END.
    """
    blocks: list[dict] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        m = MSS_RE.match(raw)
        if not m:
            raise ValueError(f"caption line has no M:SS prefix: {raw[:60]!r}")
        start = int(m.group(1)) * 60 + int(m.group(2))
        rest = raw[m.end():]
        rest = MIN_PREFIX_RE.sub("", rest, count=1)
        rest = SEC_PREFIX_RE.sub("", rest, count=1)
        text = rest.strip()
        blocks.append(
            {
                "start": float(start),
                "text": text,
                "is_speech": not bool(NON_SPEECH_RE.match(text)),
            }
        )
    # End = start of next block; last block ends at LAST_BLOCK_END.
    for i, b in enumerate(blocks):
        b["end"] = blocks[i + 1]["start"] if i + 1 < len(blocks) else LAST_BLOCK_END
    return blocks


def normalize(text: str) -> str:
    """Lowercase, drop punctuation, collapse whitespace; keep Vietnamese tone marks."""
    return WS_RE.sub(" ", PUNCT_RE.sub(" ", text.lower())).strip()


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def align(pilot_dir: Path) -> tuple[list[dict], list[dict]]:
    """Return (rows, blocks). rows are per-segment aligned records with sim."""
    segments = read_csv(pilot_dir / "segments.csv")
    transcripts = {r["id"]: r["text"] for r in read_csv(pilot_dir / "transcripts.csv")}
    blocks = parse_youtube(pilot_dir / "youtube_transcripts.txt")
    speech_blocks = [b for b in blocks if b["is_speech"]]

    rows: list[dict] = []
    for seg in segments:
        s, e = float(seg["start"]), float(seg["end"])
        lo, hi = s - TOL, e + TOL
        matched = [b for b in speech_blocks if b["start"] < hi and b["end"] > lo]
        text_yt = " ".join(b["text"] for b in matched).strip()
        text_pw = transcripts.get(seg["id"], "").strip()

        sim: float | None = None
        if text_yt and text_pw:
            sim = fuzz.partial_ratio(normalize(text_yt), normalize(text_pw))

        rows.append(
            {
                "id": seg["id"],
                "start": seg["start"],
                "end": seg["end"],
                "text_phowhisper": text_pw,
                "text_youtube": text_yt,
                "n_yt_blocks": len(matched),
                "sim": sim,
            }
        )
    return rows, blocks


def proxy_wer(rows: list[dict]) -> list[float]:
    """Word-level normalized Levenshtein on the 'clean' subset.

    Clean = exactly 1 YouTube block AND length ratio hyp/ref in [0.7, 1.3].
    ref = YouTube (better text), hyp = PhoWhisper.
    """
    vals: list[float] = []
    for r in rows:
        if r["n_yt_blocks"] != 1 or not r["text_youtube"] or not r["text_phowhisper"]:
            continue
        ref = normalize(r["text_youtube"]).split()
        hyp = normalize(r["text_phowhisper"]).split()
        if not ref or not hyp:
            continue
        if not (0.7 <= len(hyp) / len(ref) <= 1.3):
            continue
        vals.append(Levenshtein.normalized_distance(ref, hyp))
    return vals


def fmt_sim(sim: float | None) -> str:
    return "" if sim is None else f"{sim:.1f}"


def write_csv(rows: list[dict], path: Path) -> None:
    fields = ["id", "start", "end", "text_phowhisper", "text_youtube", "n_yt_blocks", "sim"]
    with path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            out = dict(r)
            out["sim"] = fmt_sim(r["sim"])
            w.writerow(out)


def percentile(vals: list[float], p: float) -> float:
    if not vals:
        return 0.0
    s = sorted(vals)
    k = (len(s) - 1) * (p / 100)
    lo = int(k)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (k - lo)


def truncate(text: str, n: int = 80) -> str:
    text = text.replace("\n", " ")
    return text if len(text) <= n else text[: n - 1] + "…"


M3_FLAGGED = [
    "seg00010", "seg00018", "seg00034", "seg00045",
    "seg00049", "seg00105", "seg00109", "seg00148",
]


def write_report(rows: list[dict], blocks: list[dict], path: Path) -> None:
    n_blocks = len(blocks)
    n_speech = sum(1 for b in blocks if b["is_speech"])
    n_non = n_blocks - n_speech
    n_cov = sum(1 for r in rows if r["n_yt_blocks"] >= 1)

    sims = [r["sim"] for r in rows if r["sim"] is not None]
    bins = {"0-50": 0, "50-70": 0, "70-85": 0, "85-95": 0, "95-100": 0}
    for v in sims:
        if v < 50:
            bins["0-50"] += 1
        elif v < 70:
            bins["50-70"] += 1
        elif v < 85:
            bins["70-85"] += 1
        elif v < 95:
            bins["85-95"] += 1
        else:
            bins["95-100"] += 1

    pw = proxy_wer(rows)
    low15 = sorted((r for r in rows if r["sim"] is not None), key=lambda r: r["sim"])[:15]
    by_id = {r["id"]: r for r in rows}

    L: list[str] = []
    L.append("# M4b — PhoWhisper-base vs YouTube caption (chất lượng transcript)")
    L.append("")
    L.append("> YouTube caption cũng là ASR (không phải gold), nhưng text tốt hơn PhoWhisper "
             "(đúng dấu thanh + có dấu câu). Dùng làm reference tương đối để đo PhoWhisper-base.")
    L.append("")
    L.append("## 1. Parse caption")
    L.append("")
    L.append(f"- Tổng block: **{n_blocks}** | speech: **{n_speech}** | non-speech "
             f"(`[âm nhạc]`/`[Vỗ tay]`): **{n_non}**")
    L.append(f"- Coverage: **{n_cov}/{len(rows)}** segment có ≥1 block YouTube "
             f"(**{100*n_cov/len(rows):.1f}%**)")
    L.append("")
    L.append("## 2. Phân bố similarity (partial_ratio PhoWhisper↔YouTube, 0–100)")
    L.append("")
    L.append(f"- n = {len(sims)} | mean = **{mean(sims):.1f}** | median = **{median(sims):.1f}** "
             f"| p10 = {percentile(sims,10):.1f} | p25 = {percentile(sims,25):.1f}")
    L.append("")
    L.append("| bin | count |")
    L.append("|---|---|")
    for k, v in bins.items():
        bar = "█" * round(30 * v / max(len(sims), 1))
        L.append(f"| {k} | {v} {bar} |")
    L.append("")
    L.append("## 3. Proxy-WER (tập sạch: n_yt_blocks==1 & length-ratio 0.7–1.3)")
    L.append("")
    if pw:
        L.append(f"- n = **{len(pw)}** | mean = **{mean(pw):.3f}** | median = **{median(pw):.3f}** "
                 "(word-level normalized Levenshtein; ref=YouTube, hyp=PhoWhisper)")
    else:
        L.append("- tập sạch rỗng.")
    L.append("")
    L.append("## 4. 15 segment sim thấp nhất")
    L.append("")
    L.append("| id | sim | PhoWhisper | YouTube |")
    L.append("|---|---|---|---|")
    for r in low15:
        L.append(f"| {r['id']} | {fmt_sim(r['sim'])} | {truncate(r['text_phowhisper'])} "
                 f"| {truncate(r['text_youtube'])} |")
    L.append("")
    L.append("## 5. 8 đoạn đã flag ở M3 — YouTube có cứu được không?")
    L.append("")
    L.append("| id | sim | n_blk | PhoWhisper | YouTube |")
    L.append("|---|---|---|---|---|")
    for sid in M3_FLAGGED:
        r = by_id.get(sid)
        if not r:
            L.append(f"| {sid} | — | — | (không có segment) | |")
            continue
        L.append(f"| {sid} | {fmt_sim(r['sim'])} | {r['n_yt_blocks']} "
                 f"| {truncate(r['text_phowhisper'])} | {truncate(r['text_youtube'])} |")
    L.append("")
    L.append("## 6. Verdict")
    L.append("")
    L.extend(_verdict(sims, pw, n_cov, len(rows)))
    L.append("")
    path.write_text("\n".join(L), encoding="utf-8")


def _verdict(sims: list[float], pw: list[float], n_cov: int, n_seg: int) -> list[str]:
    med = median(sims) if sims else 0.0
    pwm = median(pw) if pw else 0.0
    return [
        f"- PhoWhisper-base khớp YouTube ở mức median sim **{med:.0f}/100** với proxy-WER median "
        f"**{pwm:.2f}** trên tập sạch (n={len(pw)}) — đủ dùng cho **weak-label** ở mức "
        "utterance (nội dung/khung hội thoại đúng), nhưng sai dấu thanh + từ vựng rải rác.",
        f"- Coverage YouTube {n_cov}/{n_seg} nên gần như mọi segment có 1 text reference tốt hơn "
        "để đối chiếu; nên **thay text PhoWhisper bằng text YouTube** ở các segment sim thấp "
        "(bảng mục 4) khi cần transcript sạch cho annotation/hiển thị.",
        "- Các đoạn loop/lặp của PhoWhisper (vd \"hả hả hả\") được YouTube cứu rõ (mục 5) — đây là "
        "lý do chính nên giữ YouTube như nguồn text đối chiếu.",
        "- **Chưa cần chạy PhoWhisper-medium** cho pilot: text-base đủ tốt cho tín hiệu SER "
        "(nhãn cảm xúc không nhạy lỗi chính tả nhỏ), và ta đã có YouTube để vá các chỗ tệ nhất. "
        "Cân nhắc -medium chỉ nếu bước sau cần transcript chính xác từng từ.",
        "- **Caveat:** YouTube caption cũng do ASR sinh (auto-caption), không phải gold; "
        "mọi số ở đây là chất-lượng-tương-đối giữa 2 ASR, không phải WER thật so với người.",
    ]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows cp1252 crashes on Vietnamese.
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pilot-dir", default="data/vietnamese-ser/pilot/ep01", type=Path)
    args = ap.parse_args()
    pilot_dir: Path = args.pilot_dir

    rows, blocks = align(pilot_dir)

    n_speech = sum(1 for b in blocks if b["is_speech"])
    starts = [b["start"] for b in blocks]
    assert starts == sorted(starts), "caption block starts not monotonic"
    assert 250 <= len(blocks) <= 260, f"unexpected block count {len(blocks)}"
    assert 20 <= (len(blocks) - n_speech) <= 40, "unexpected non-speech count"
    assert len(rows) > 0, "no segments found"

    write_csv(rows, pilot_dir / "transcripts_yt.csv")
    write_report(rows, blocks, pilot_dir / "m4b_wer_report.md")

    n_cov = sum(1 for r in rows if r["n_yt_blocks"] >= 1)
    sims = [r["sim"] for r in rows if r["sim"] is not None]
    pw = proxy_wer(rows)
    print(f"blocks={len(blocks)} speech={n_speech} non_speech={len(blocks)-n_speech}")
    print(f"coverage={n_cov}/{len(rows)} ({100*n_cov/len(rows):.1f}%)")
    print(f"sim: n={len(sims)} mean={mean(sims):.1f} median={median(sims):.1f}")
    print(f"proxy_wer: n={len(pw)} mean={mean(pw):.3f} median={median(pw):.3f}"
          if pw else "proxy_wer: empty")
    print(f"wrote {pilot_dir/'transcripts_yt.csv'}")
    print(f"wrote {pilot_dir/'m4b_wer_report.md'}")


if __name__ == "__main__":
    main()
