"""Per-syllable lexical-tone checker (change 017).

Given audio + its Vietnamese script, decide for every syllable which of its allowed tones
the audio supports, by CTC "tone-GOP" scoring on a Vietnamese wav2vec2 CTC model: the
whole-sentence CTC log-likelihood is computed with syllable i spelled in each allowed tone
(every other syllable fixed). The best-scoring tone is the checker's reading of the audio;
``margin`` = score(scripted tone) - best other tone. CTC has no language model, so the
reading comes from the audio, unlike an ASR transcript (which "corrects" a wrong tone into
a meaningful word).

Subcommand ``validate`` runs the checker on ViEmoSpeech (real speech, so the scripted tone
is the truth) and writes the noise-floor report the TTS evaluation is compared against
(docs/spec/changes/017-tone-checker/README.md). Per-syllable scores (contain words) go to
data/** (gitignored, I1); the report holds aggregates only.

Usage (from repo root):
  PYTHONIOENCODING=utf-8 PYTHONPATH=scripts/vietnamese-ser \
    .venv-vnser/Scripts/python.exe scripts/vietnamese-ser/tone_check.py validate
  # smoke: validate --limit 20 --out <tmp> --report <tmp>
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
EPISODES = ROOT / "data" / "vietnamese-ser" / "episodes"
OUT = ROOT / "data" / "vietnamese-ser" / "features" / "017"
REPORT = ROOT / "docs" / "reports" / "017"
MODEL = "nguyenvulebinh/wav2vec2-base-vietnamese-250h"
SR = 16000

TONES = ("ngang", "huyen", "sac", "hoi", "nga", "nang")
MARK_TONE = {
    "̀": "huyen",
    "́": "sac",
    "̉": "hoi",
    "̃": "nga",
    "̣": "nang",
}
TONE_MARK = {t: m for m, t in MARK_TONE.items()}
VOWELS = set("aăâeêioôơuưy")
DIACRITIC_VOWELS = set("ăâêôơư")
CHECKED = ("sac", "nang")  # the only tones a p/t/c/ch-final syllable can carry


# --- orthography --------------------------------------------------------------------


def normalize_text(text: str) -> str:
    """NFC, lower-case, punctuation → space. Digits are kept so the caller can exclude."""
    text = unicodedata.normalize("NFC", text).lower()
    text = "".join(ch if ch.isalnum() or ch.isspace() else " " for ch in text)
    return " ".join(text.split())


def split_tone(syl: str) -> tuple[str, str]:
    """'Người' → ('ngươi', 'huyen'): tone mark removed, vowel-quality marks kept."""
    decomposed = unicodedata.normalize("NFD", syl.lower())
    tone = "ngang"
    kept = []
    for ch in decomposed:
        if ch in MARK_TONE:
            tone = MARK_TONE[ch]
        else:
            kept.append(ch)
    return unicodedata.normalize("NFC", "".join(kept)), tone


def place_tone(base: str, tone: str) -> str | None:
    """Spell ``base`` with ``tone``, mark placed by the traditional rule ('hòa', 'thủy').

    None when the syllable has no vowel to carry a tone.
    """
    s = base
    i = 0
    if (s.startswith("qu") and len(s) > 2) or (
        s.startswith("gi") and len(s) > 2 and s[2] in VOWELS
    ):
        i = 2
    while i < len(s) and s[i] not in VOWELS:
        i += 1
    if i == len(s):
        return None
    j = i
    while j < len(s) and s[j] in VOWELS:
        j += 1
    if tone == "ngang":
        return s
    marked = [k for k in range(i, j) if s[k] in DIACRITIC_VOWELS]
    if marked:
        pos = marked[-1]  # ươ → ơ, iê → ê
    elif j < len(s):
        pos = j - 1  # coda present → last vowel (hoán)
    elif j - i <= 2:
        pos = i  # open 1–2 vowel cluster → first vowel (hòa, mía)
    else:
        pos = i + 1  # open 3-vowel cluster → middle (ngoài)
    ch = unicodedata.normalize("NFC", s[pos] + TONE_MARK[tone])
    return s[:pos] + ch + s[pos + 1 :]


def allowed_tones(base: str) -> tuple[str, ...]:
    return CHECKED if base.endswith(("p", "t", "c", "ch")) else TONES


# --- scoring -------------------------------------------------------------------------


class Scorer:
    def __init__(self, model: str = MODEL):
        import torch
        from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

        self.torch = torch
        self.proc = Wav2Vec2Processor.from_pretrained(model)
        self.model = Wav2Vec2ForCTC.from_pretrained(model).eval()
        self.vocab = self.proc.tokenizer.get_vocab()
        self.blank = self.proc.tokenizer.pad_token_id
        self.delim = self.vocab["|"]

    def emissions(self, wav: np.ndarray):
        """[T, V] CTC log-probabilities for a 16 kHz mono waveform."""
        inp = self.proc(wav, sampling_rate=SR, return_tensors="pt").input_values
        with self.torch.no_grad():
            return self.model(inp).logits[0].log_softmax(-1)

    def encode(self, words: list[str]) -> list[int] | None:
        ids = []
        for k, w in enumerate(words):
            if k:
                ids.append(self.delim)
            for ch in w:
                if ch not in self.vocab:
                    return None
                ids.append(self.vocab[ch])
        return ids

    def score(self, logp, text: str) -> list[dict] | str:
        """One row per scored syllable, or the reason the clip can't be scored."""
        text = normalize_text(text)
        if not text:
            return "empty"
        if any(ch.isdigit() for ch in text):
            return "digit"
        parsed = [split_tone(w) for w in text.split()]
        spelled = [place_tone(b, t) for b, t in parsed]
        if any(s is None for s in spelled):
            return "no_vowel"
        variants = []  # (syllable index, tone, target ids)
        for i, (base, tone) in enumerate(parsed):
            allowed = allowed_tones(base)
            if tone not in allowed:
                continue  # e.g. a loanword spelled ngang with a stop coda: kept, not scored
            for t in allowed:
                words = list(spelled)
                words[i] = place_tone(base, t)
                ids = self.encode(words)
                if ids is None:
                    return "oov_char"
                variants.append((i, t, ids))
        if not variants:
            return "no_scorable_syllable"

        F = self.torch.nn.functional
        targets = self.torch.tensor([x for _, _, ids in variants for x in ids])
        tlen = self.torch.tensor([len(ids) for _, _, ids in variants])
        n = len(variants)
        lp = logp.unsqueeze(1).expand(-1, n, -1).contiguous()
        ilen = self.torch.full((n,), logp.shape[0], dtype=self.torch.long)
        ll = -F.ctc_loss(lp, targets, ilen, tlen, blank=self.blank, reduction="none")
        if not self.torch.isfinite(ll).all():
            return "too_short"

        scores: dict[int, dict[str, float]] = {}
        for (i, t, _), v in zip(variants, ll.tolist(), strict=True):
            scores.setdefault(i, {})[t] = v
        rows = []
        for i, sc in scores.items():
            base, tone = parsed[i]
            best = max(sc, key=sc.get)
            rows.append(
                {
                    "i": i,
                    "word": spelled[i],
                    "base": base,
                    "tone": tone,
                    "n_allowed": len(sc),
                    "best": best,
                    "margin": sc[tone] - max(v for t, v in sc.items() if t != tone),
                    **{f"ll_{t}": sc.get(t, np.nan) for t in TONES},
                }
            )
        return rows


# --- validation on ViEmoSpeech ----------------------------------------------------


def clean_clips(limit: int | None) -> pd.DataFrame:
    """Same human-clean filter as extract_emotion_features.py (emotion, not rejected/multi)."""
    from labeler_store import read_records

    rows = []
    for r in read_records(EPISODES):
        if not r.get("emotion") or r.get("rejected") or r.get("multi"):
            continue
        wav = EPISODES / r["epKey"] / "clips" / f"{r['id']}.wav"
        if not wav.is_file():
            continue
        rows.append(
            {
                "key": f"{r['epKey']}/{r['id']}",
                "series": r["epKey"].split("/")[0],
                "emotion": r["emotion"],
                "arousal": r.get("arousal"),
                "valence": r.get("valence"),
                "text": r.get("gold_text") or "",
                "wav": wav,
            }
        )
    df = pd.DataFrame(rows).sort_values("key").reset_index(drop=True)
    return df.head(limit) if limit else df


def arousal_band(a) -> str:
    if a is None or pd.isna(a):
        return "unknown"
    return "low (1-2)" if a <= 2 else ("mid (3)" if a == 3 else "high (4-5)")


def boot_ci(per_clip: pd.DataFrame, reps: int = 1000, seed: int = 0) -> tuple[float, float]:
    """95% CI of pooled syllable accuracy, resampling clips (syllables share a clip)."""
    if per_clip.empty:
        return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    c = per_clip["correct"].to_numpy()
    n = per_clip["n"].to_numpy()
    idx = rng.integers(0, len(c), size=(reps, len(c)))
    acc = c[idx].sum(1) / n[idx].sum(1)
    return (float(np.quantile(acc, 0.025)), float(np.quantile(acc, 0.975)))


def detection_and_auc(syl: pd.DataFrame) -> tuple[float, float]:
    """Simulated wrong-script test: for each syllable and each wrong tone t'.

    detection = P(checker's best tone != t'); AUC separates margin(true) from margin(t').
    """
    from sklearn.metrics import roc_auc_score

    flagged, neg, pos = [], [], []
    for r in syl.itertuples():
        sc = {t: getattr(r, f"ll_{t}") for t in TONES if not np.isnan(getattr(r, f"ll_{t}"))}
        neg.append(r.margin)
        for t in sc:
            if t == r.tone:
                continue
            flagged.append(r.best != t)
            pos.append(sc[t] - max(v for u, v in sc.items() if u != t))
    y = [0] * len(neg) + [1] * len(pos)
    auc = roc_auc_score(y, [-m for m in neg + pos])  # low margin ⇒ "wrong tone"
    return float(np.mean(flagged)), float(auc)


def group_table(syl: pd.DataFrame, col: str) -> list[dict]:
    out = []
    for g, d in syl.groupby(col, sort=True):
        per_clip = d.groupby("key")["ok"].agg(correct="sum", n="count").reset_index()
        lo, hi = boot_ci(per_clip)
        det, auc = detection_and_auc(d)
        out.append(
            {
                col: g,
                "clips": int(d["key"].nunique()),
                "syllables": len(d),
                "accuracy": float(d["ok"].mean()),
                "ci95": [lo, hi],
                "false_alarm": float(1 - d["ok"].mean()),
                "detection": det,
                "auc": auc,
                "chance": float((1 / d["n_allowed"]).mean()),
            }
        )
    return out


def summarize(syl: pd.DataFrame, clips: pd.DataFrame) -> dict:
    syl = syl.copy()
    syl["ok"] = syl["best"] == syl["tone"]
    syl["all"] = "all"
    syl["checked"] = np.where(syl["n_allowed"] == 2, "checked (p/t/c/ch)", "open")
    syl["arousal_band"] = syl["arousal"].map(arousal_band)
    conf = pd.crosstab(syl["tone"], syl["best"]).reindex(index=TONES, columns=TONES, fill_value=0)
    return {
        "clips_total": len(clips),
        "clips_scored": int((clips["status"] == "ok").sum()),
        "excluded": clips.loc[clips["status"] != "ok", "status"].value_counts().to_dict(),
        "syllables_unscored": int(clips["unscored"].sum()),
        "groups": {
            col: group_table(syl, col)
            for col in ("all", "emotion", "arousal_band", "tone", "checked", "series")
        },
        "confusion": {"rows_scripted_cols_best": TONES, "counts": conf.to_numpy().tolist()},
    }


def render(m: dict, prov: dict) -> str:
    def table(rows: list[dict], col: str) -> list[str]:
        lines = [
            f"| {col} | clip | âm tiết | chính xác [CI95] | báo nhầm | phát hiện | AUC | ngẫu nhiên |",
            "|---|---:|---:|---|---:|---:|---:|---:|",
        ]
        for r in rows:
            lo, hi = r["ci95"]
            lines.append(
                f"| {r[col]} | {r['clips']} | {r['syllables']} | {r['accuracy']:.3f} "
                f"[{lo:.3f}, {hi:.3f}] | {r['false_alarm']:.3f} | {r['detection']:.3f} | "
                f"{r['auc']:.3f} | {r['chance']:.3f} |"
            )
        return lines

    titles = {
        "all": "Tổng",
        "emotion": "Theo cảm xúc",
        "arousal_band": "Theo arousal",
        "tone": "Theo thanh trong kịch bản",
        "checked": "Âm tiết tắc / không tắc",
        "series": "Theo series",
    }
    out = [
        "# Change 017 — kiểm chứng tone checker trên ViEmoSpeech (giọng thật)",
        "",
        f"Sinh bởi `scripts/vietnamese-ser/tone_check.py validate` · commit `{prov['git_commit']}`"
        f" · model `{prov['model']}` · {prov['generated']}. Không chứa text (I1).",
        "",
        "Giọng thật đọc đúng thanh, nên thanh trong kịch bản là đáp án. **Báo nhầm** = 1 − "
        "chính xác (mức nền nhiễu). **Phát hiện** = giả lập kịch bản ghi sai một thanh, tỉ lệ "
        "công cụ gắn cờ. Định nghĩa: `docs/spec/changes/017-tone-checker/README.md`.",
        "",
        f"- Clip: {m['clips_scored']} chấm được / {m['clips_total']}; loại: {m['excluded']}",
        f"- Âm tiết giữ trong câu nhưng không chấm (thanh không hợp lệ với vần): "
        f"{m['syllables_unscored']}",
        "- ⚠ `gold_text` chưa được soát: lỗi text hiện ra thành báo nhầm, nên báo nhầm là cận trên.",
        "",
    ]
    for col, title in titles.items():
        out += [f"## {title}", "", *table(m["groups"][col], col), ""]
    out += [
        "## Ma trận nhầm (hàng = thanh kịch bản, cột = thanh công cụ đọc)",
        "",
        "| | " + " | ".join(TONES) + " |",
        "|---" * (len(TONES) + 1) + "|",
    ]
    for t, row in zip(TONES, m["confusion"]["counts"], strict=True):
        out.append(f"| {t} | " + " | ".join(str(x) for x in row) + " |")
    return "\n".join(out) + "\n"


def validate(args: argparse.Namespace) -> None:
    import soundfile as sf

    clips = clean_clips(args.limit)
    print(f"[017] {len(clips)} clean clips")
    scorer = Scorer(args.model)
    syl_rows, status, unscored = [], [], []
    for k, c in enumerate(clips.itertuples()):
        wav, sr = sf.read(c.wav, dtype="float32")
        assert sr == SR, f"{c.wav}: {sr} Hz"
        if wav.ndim > 1:
            wav = wav.mean(axis=1)
        res = scorer.score(scorer.emissions(wav), c.text)
        if isinstance(res, str):
            status.append(res)
            unscored.append(0)
        else:
            status.append("ok")
            unscored.append(len(normalize_text(c.text).split()) - len(res))
            for r in res:
                syl_rows.append(
                    {"key": c.key, "series": c.series, "emotion": c.emotion,
                     "arousal": c.arousal, **r}
                )  # fmt: skip
        if (k + 1) % 100 == 0:
            print(f"[017] {k + 1}/{len(clips)}")
    clips = clips.drop(columns=["wav", "text"]).assign(status=status, unscored=unscored)
    syl = pd.DataFrame(syl_rows)

    args.out.mkdir(parents=True, exist_ok=True)
    syl.to_csv(args.out / "syllables.csv", index=False, encoding="utf-8")
    clips.to_csv(args.out / "clips.csv", index=False, encoding="utf-8")

    prov = {
        "generated": dt.datetime.now().isoformat(timespec="seconds"),
        "git_commit": subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=ROOT
        ).stdout.strip(),
        "model": args.model,
        "limit": args.limit,
    }
    m = summarize(syl, clips)
    args.report.mkdir(parents=True, exist_ok=True)
    (args.report / "metrics.json").write_text(
        json.dumps({"provenance": prov, **m}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (args.report / "report.md").write_text(render(m, prov), encoding="utf-8")
    print(f"[017] wrote {args.report / 'report.md'}")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("validate", help="run on ViEmoSpeech → noise-floor report")
    v.add_argument("--limit", type=int, default=None)
    v.add_argument("--model", default=MODEL)
    v.add_argument("--out", type=Path, default=OUT)
    v.add_argument("--report", type=Path, default=REPORT)
    args = ap.parse_args()
    validate(args)


if __name__ == "__main__":
    main()
