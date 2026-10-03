"""Inter-annotator reliability report for ViEmoSpeech (change 011, M7/M8).

Implements the pre-registered rules in
`docs/spec/changes/011-online-multi-annotator/qc-protocol.md` — nothing here is a
free choice at report time, which is the whole point of pre-registering:

* §5.1 excludes gold anchors and the *second* presentation of duplicate clips;
* §5.2 reports Fleiss' kappa AND Krippendorff's nominal alpha for the 7-class label,
  and Krippendorff's ORDINAL alpha for valence/arousal;
* §5.3 reports annotator-vs-annotator SEPARATELY from owner-vs-annotator, because
  qualification screened annotators against owner-adjudicated gold and therefore
  inflates any owner-involving number;
* §5.4 derives the label of record (majority + explicit `no_agreement`; mean V/A);
* §5.5 forces the awkward numbers out too (per-class kappa, skip rates,
  `no_agreement` rate) and never filters low-agreement clips to flatter alpha.

Both statistics are implemented here rather than pulled from a package: the repo has
no krippendorff dependency, and a reviewer can check ~60 lines of arithmetic against
the definitions more easily than a pinned wheel.

    .venv-vnser/Scripts/python.exe scripts/vietnamese-ser/iaa_report.py \
        --root data/vietnamese-ser/episodes --out docs/reports/iaa_report.md
"""

from __future__ import annotations

import argparse
import itertools
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "labeler"))
import store

EMOTIONS = ["joy", "sadness", "anger", "fear_anxiety", "surprise", "disgust", "neutral"]


# ---------- agreement statistics ----------
def fleiss_kappa(units: list[list[str]], cats: list[str]) -> float | None:
    """Fleiss' kappa over units rated by the SAME number of raters (n >= 2)."""
    units = [u for u in units if len(u) >= 2]
    if not units:
        return None
    n = len(units[0])
    if any(len(u) != n for u in units) or n < 2:
        return None
    N = len(units)
    p_j = {c: sum(u.count(c) for u in units) / (N * n) for c in cats}
    p_bar = sum(sum(u.count(c) ** 2 for c in cats) - n for u in units) / (N * n * (n - 1))
    pe = sum(v * v for v in p_j.values())
    return None if pe >= 1.0 else (p_bar - pe) / (1 - pe)


def _coincidence(units: list[list], cats: list) -> dict:
    """Krippendorff coincidence matrix: pairable values weighted 1/(m_u - 1)."""
    o: dict = defaultdict(float)
    for u in units:
        m = len(u)
        if m < 2:
            continue  # a single rating is unpairable, contributes nothing
        for a, b in itertools.permutations(u, 2):
            o[(a, b)] += 1.0 / (m - 1)
    return o


def krippendorff_alpha(units: list[list], cats: list, metric: str = "nominal") -> float | None:
    """Krippendorff's alpha. `metric`: 'nominal' or 'ordinal'.

    Handles missing ratings by construction (units may have different rater counts),
    which is why qc-protocol §5.2 pairs it with Fleiss' kappa: kappa needs complete
    units, alpha uses everything.
    """
    o = _coincidence(units, cats)
    n_c = {c: sum(o.get((c, d), 0.0) for d in cats) for c in cats}
    n = sum(n_c.values())
    if n < 2:
        return None

    if metric == "ordinal":
        # delta^2 over the rank scale, per Krippendorff: the squared gap between
        # cumulative counts, corrected by half the endpoint masses.
        order = cats
        idx = {c: i for i, c in enumerate(order)}

        def d2(a, b) -> float:
            i, j = sorted((idx[a], idx[b]))
            g = sum(n_c[order[k]] for k in range(i, j + 1))
            return (g - (n_c[a] + n_c[b]) / 2.0) ** 2
    else:

        def d2(a, b) -> float:
            return 0.0 if a == b else 1.0

    do = sum(o[(a, b)] * d2(a, b) for a, b in o) / n
    de = sum(n_c[a] * n_c[b] * d2(a, b) for a in cats for b in cats if a != b) / (n * (n - 1))
    if de == 0:
        return None
    return 1.0 - do / de


# ---------- data assembly ----------
def collect(root: Path) -> tuple[dict, dict, list[dict]]:
    """-> (ratings_by_clip, owner_label_by_clip, raw_rows). Applies qc-protocol §5.1."""
    store.set_root(root)
    store.load()
    rows = store.all_ratings()

    by_clip: dict[tuple[str, str], dict[str, dict]] = defaultdict(dict)
    for r in rows:
        # §5.1: gold anchors were CHOSEN for being easy; duplicates are one clip shown
        # twice. Both would inflate agreement, so neither enters the kappa pool.
        if r["kind"] in ("gold", "dup", "trap"):
            continue
        by_clip[(r["epkey"], r["id"])][r["annotator"]] = r

    owner = {
        (r["epKey"], r["id"]): r
        for r in store.STATE.values()
        if r.get("emotion") and not r.get("rejected")
    }
    return by_clip, owner, rows


def emotion_units(by_clip: dict, owner: dict, who: list[str], with_owner: bool) -> list[list[str]]:
    """One unit per clip = the emotion labels the named raters gave it (skips dropped)."""
    units = []
    for key, per in by_clip.items():
        vals = [per[a]["emotion"] for a in who if a in per and per[a]["emotion"]]
        if with_owner and key in owner:
            vals.append(owner[key]["emotion"])
        if len(vals) >= 2:
            units.append(vals)
    return units


def scale_units(by_clip: dict, owner: dict, who: list[str], field: str, with_owner: bool) -> list:
    units = []
    for key, per in by_clip.items():
        vals = [per[a][field] for a in who if a in per and per[a][field] is not None]
        if with_owner and key in owner and owner[key].get(field) is not None:
            vals.append(owner[key][field])
        if len(vals) >= 2:
            units.append(vals)
    return units


def fmt(x: float | None) -> str:
    return "n/a" if x is None else f"{x:.3f}"


# ---------- QC scoring (qc-protocol §3) ----------
def qc_table(rows: list[dict], owner: dict) -> list[str]:
    per: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        per[r["annotator"]].append(r)

    out = [
        "| annotator | n | gold hit | tự nhất quán | quá nhanh | bỏ qua |",
        "|---|--:|--:|--:|--:|--:|",
    ]
    for ann, rs in sorted(per.items()):
        gold = [r for r in rs if r["kind"] == "gold"]
        hit = sum(
            1 for r in gold if owner.get((r["epkey"], r["id"]), {}).get("emotion") == r["emotion"]
        )
        # a duplicate's two presentations: compare the 'dup' row to the same clip's 'normal' row
        firsts = {(r["epkey"], r["id"]): r["emotion"] for r in rs if r["kind"] == "normal"}
        dups = [r for r in rs if r["kind"] == "dup" and (r["epkey"], r["id"]) in firsts]
        same = sum(1 for r in dups if firsts[(r["epkey"], r["id"])] == r["emotion"])
        # §2.3: "too fast" = less audio played than the clip's own length — you cannot
        # have heard it. Compared against each clip's real duration, not a flat floor.
        fast = 0
        for r in rs:
            rec = owner.get((r["epkey"], r["id"]))
            if rec and r["listen_ms"] < 1000 * (rec.get("end", 0) - rec.get("start", 0)):
                fast += 1
        skips = sum(1 for r in rs if r["skip_reason"])
        out.append(
            f"| {ann} | {len(rs)} | {hit}/{len(gold)} | {same}/{len(dups)} | "
            f"{fast}/{len(rs)} | {skips}/{len(rs)} |"
        )
    return out


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="inter-annotator reliability report")
    ap.add_argument("--root", default="data/vietnamese-ser/episodes")
    ap.add_argument("--out", default="docs/reports/iaa_report.md")
    a = ap.parse_args()

    by_clip, owner, rows = collect(Path(a.root).resolve())
    annotators = sorted({r["annotator"] for r in rows})
    if not annotators:
        raise SystemExit("no ratings yet — run a labeling round first (see RUNBOOK.md)")

    L = [
        "# Inter-annotator reliability — ViEmoSpeech",
        "",
        "> Sinh bởi `scripts/vietnamese-ser/iaa_report.py` theo quy tắc **đã đông cứng**",
        "> trong `docs/spec/changes/011-online-multi-annotator/qc-protocol.md`.",
        "> Gold + lần trình bày thứ hai của clip lặp **đã loại** khỏi mọi con số dưới đây (§5.1).",
        "",
        f"- Annotator: {', '.join(annotators)}",
        f"- Clip có ≥2 nhãn: **{sum(1 for p in by_clip.values() if len(p) >= 2)}**",
        f"- Tổng lượt gán: {len(rows)}",
        "",
        "## 1. Headline — giữa các annotator (§5.3)",
        "",
        "Đây là con số **ít nhiễm nhất**: các annotator được tuyển độc lập với nhau.",
        "",
        "| cặp | Fleiss κ (emotion) | α nominal | α ordinal V | α ordinal A |",
        "|---|--:|--:|--:|--:|",
    ]
    for pair in itertools.combinations(annotators, 2):
        who = list(pair)
        L.append(
            f"| {' ↔ '.join(who)} "
            f"| {fmt(fleiss_kappa(emotion_units(by_clip, owner, who, False), EMOTIONS))} "
            f"| {fmt(krippendorff_alpha(emotion_units(by_clip, owner, who, False), EMOTIONS))} "
            f"| {fmt(krippendorff_alpha(scale_units(by_clip, owner, who, 'valence', False), [1, 2, 3, 4, 5], 'ordinal'))} "
            f"| {fmt(krippendorff_alpha(scale_units(by_clip, owner, who, 'arousal', False), [1, 2, 3, 4, 5], 'ordinal'))} |"
        )
    if len(annotators) >= 3:
        L.append(
            f"| **cả {len(annotators)}** "
            f"| {fmt(fleiss_kappa(emotion_units(by_clip, owner, annotators, False), EMOTIONS))} "
            f"| {fmt(krippendorff_alpha(emotion_units(by_clip, owner, annotators, False), EMOTIONS))} "
            f"| {fmt(krippendorff_alpha(scale_units(by_clip, owner, annotators, 'valence', False), [1, 2, 3, 4, 5], 'ordinal'))} "
            f"| {fmt(krippendorff_alpha(scale_units(by_clip, owner, annotators, 'arousal', False), [1, 2, 3, 4, 5], 'ordinal'))} |"
        )

    L += [
        "",
        "## 2. Có owner — đọc kèm cảnh báo (§5.3)",
        "",
        "> ⚠️ Vòng qualification sàng annotator bằng mức trùng với **gold do owner",
        "> adjudicate**, nên mọi con số có owner **bị thổi lên bởi chính cách tuyển**.",
        "> Không dùng làm headline.",
        "",
        "| tập rater | Fleiss κ | α nominal | α ordinal V | α ordinal A |",
        "|---|--:|--:|--:|--:|",
    ]
    for ann in annotators:
        who = [ann]
        L.append(
            f"| owner ↔ {ann} "
            f"| {fmt(fleiss_kappa(emotion_units(by_clip, owner, who, True), EMOTIONS))} "
            f"| {fmt(krippendorff_alpha(emotion_units(by_clip, owner, who, True), EMOTIONS))} "
            f"| {fmt(krippendorff_alpha(scale_units(by_clip, owner, who, 'valence', True), [1, 2, 3, 4, 5], 'ordinal'))} "
            f"| {fmt(krippendorff_alpha(scale_units(by_clip, owner, who, 'arousal', True), [1, 2, 3, 4, 5], 'ordinal'))} |"
        )
    L.append(
        f"| owner + tất cả "
        f"| {fmt(fleiss_kappa(emotion_units(by_clip, owner, annotators, True), EMOTIONS))} "
        f"| {fmt(krippendorff_alpha(emotion_units(by_clip, owner, annotators, True), EMOTIONS))} "
        f"| {fmt(krippendorff_alpha(scale_units(by_clip, owner, annotators, 'valence', True), [1, 2, 3, 4, 5], 'ordinal'))} "
        f"| {fmt(krippendorff_alpha(scale_units(by_clip, owner, annotators, 'arousal', True), [1, 2, 3, 4, 5], 'ordinal'))} |"
    )

    # ---- per-class kappa (§5.5: report the ugly ones too)
    L += [
        "",
        "## 3. κ theo từng lớp — annotator ↔ annotator (§5.5)",
        "",
        "| lớp | κ (one-vs-rest) | n nhãn |",
        "|---|--:|--:|",
    ]
    units_all = emotion_units(by_clip, owner, annotators, False)
    for c in EMOTIONS:
        bin_units = [[("y" if v == c else "n") for v in u] for u in units_all]
        n = sum(u.count(c) for u in units_all)
        L.append(f"| {c} | {fmt(fleiss_kappa(bin_units, ['y', 'n']))} | {n} |")

    # ---- label of record (§5.4) + no_agreement rate (§5.5)
    lor, no_agree = {}, 0
    for key, per in by_clip.items():
        vals = [r["emotion"] for r in per.values() if r["emotion"]]
        if key in owner:
            vals.append(owner[key]["emotion"])
        if not vals:
            continue
        top, cnt = Counter(vals).most_common(1)[0]
        va = [r["valence"] for r in per.values() if r["valence"] is not None]
        ar = [r["arousal"] for r in per.values() if r["arousal"] is not None]
        agreed = cnt >= 2
        no_agree += not agreed
        lor[key] = {
            "emotion": top if agreed else "no_agreement",
            "n": len(vals),
            "valence": round(sum(va) / len(va), 2) if va else None,
            "arousal": round(sum(ar) / len(ar), 2) if ar else None,
        }
    skips = Counter(r["skip_reason"] for r in rows if r["skip_reason"])
    L += [
        "",
        "## 4. Nhãn-của-record (§5.4) + con số bắt buộc báo (§5.5)",
        "",
        f"- Clip có nhãn hợp nhất: **{len(lor)}**",
        f"- `no_agreement` (không ai đạt đa số): **{no_agree}** "
        f"({100 * no_agree / max(1, len(lor)):.1f}%) — giữ trong corpus có gắn cờ, **không xoá**",
        f"- Bỏ qua theo lý do: {dict(skips) or '(không có)'}",
        "",
        "## 5. QC theo annotator (§3)",
        "",
        "> Ngưỡng loại đã đông cứng TRƯỚC vòng label. **Không** loại ai vì bất đồng với",
        "> đa số — chỉ theo các cột khách quan dưới đây.",
        "",
        *qc_table(rows, owner),
        "",
        "## Đối chiếu ngành (qc-protocol §6)",
        "",
        "MELD κ 0.34 · MSP-Podcast κ 0.411 (V α 0.508, A α 0.441) · CREMA-D α 0.42 (diễn xuất)",
        "· THAI-SER α thô 0.413 · IEMOCAP κ 0.27–0.48. **Không có ngưỡng đạt/trượt** — κ là",
        "kết quả cần báo, không phải bài kiểm tra cần qua.",
        "",
    ]

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))
    print(f"\n-> {out}")


if __name__ == "__main__":
    main()
