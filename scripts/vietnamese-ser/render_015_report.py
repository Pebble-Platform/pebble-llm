"""Render docs/reports/015/report.html — the change-015 report, written as a story.

The page answers three questions in order (what does sound say about emotion? which WavLM
layer to use? does dropping/merging hard classes help?), each as: why ask -> what we did ->
one chart -> what it means. Technical detail and limits go to the appendix.

Every number comes from docs/reports/015/metrics.json (analyze_emotion_features.py, the
pre-registered run), docs/reports/015/classset.json (classset_015.py, exploratory), or is
computed here from the extracted features (valence partial correlation, exploratory) —
none is typed by hand (I5). Run classset_015.py before this script.

Usage (from repo root):
  PYTHONIOENCODING=utf-8 PYTHONPATH=scripts/vietnamese-ser \
    .venv-vnser/Scripts/python.exe scripts/vietnamese-ser/render_015_report.py
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from analyze_emotion_features import FEAT_DIR, H1A, REPORT_DIR, VOICE_QUALITY, norm_groups
from scipy.stats import rankdata, spearmanr

VI = {
    "neutral": "trung tính",
    "anger": "giận",
    "joy": "vui",
    "fear_anxiety": "sợ / lo",
    "sadness": "buồn",
    "disgust": "ghê / khinh",
    "surprise": "ngạc nhiên",
}
THRESHOLD = 0.02  # same "meaningful difference" bar as 012 / 015 §5


def exploratory(features: Path) -> dict:
    """Spearman(V, A) of the labels + valence partial ρ | arousal for the voice-quality set."""
    eg = pd.read_csv(features / "egemaps.csv").dropna(subset=["gender", "age_group"])
    eg = eg.reset_index(drop=True)
    x = eg[VOICE_QUALITY]
    g = x.groupby(norm_groups(eg, 20))
    z = (x - g.transform("mean")) / g.transform("std", ddof=0)
    rv, ra = rankdata(eg["valence"]), rankdata(eg["arousal"])
    r = lambda u, v: float(np.corrcoef(u, v)[0, 1])  # noqa: E731
    va = r(rv, ra)
    partial = {}
    for c in VOICE_QUALITY:
        rf = rankdata(z[c])
        fv, fa = r(rf, rv), r(rf, ra)
        partial[c] = (fv - fa * va) / np.sqrt((1 - fa**2) * (1 - va**2))
    return {"va_spearman": float(spearmanr(eg["valence"], eg["arousal"])[0]), "partial": partial}


def chance_macro_f1(support: dict) -> float:
    """Expected macro-F1 of guessing uniformly at random, given the class counts."""
    n, k = sum(support.values()), len(support)
    return float(np.mean([2 * (s / n) * (1 / k) / (s / n + 1 / k) for s in support.values()]))


def f2(x: float) -> str:
    """2 decimals without a "-0.00"."""
    return f"{0.0 if abs(x) < 0.005 else x:.2f}"


def ci(m: dict, k: str) -> str:
    lo, hi = m[f"{k}_ci95"]
    return f'{m[k]:.3f} <span class="ci">[{lo:.3f}, {hi:.3f}]</span>'


def delta_cell(d: dict) -> str:
    lo, hi = d["ci95"]
    real = d["delta"] >= THRESHOLD and lo > 0
    verdict = '<span class="up">có</span>' if real else '<span class="flat">không</span>'
    return (
        f'<td class="num">{d["delta"]:+.3f} <span class="ci">[{lo:+.3f}, {hi:+.3f}]</span></td>'
        f"<td>{verdict}</td>"
    )


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    m = json.loads((REPORT_DIR / "metrics.json").read_text(encoding="utf-8"))
    cs_path = REPORT_DIR / "classset.json"
    if not cs_path.exists():
        raise SystemExit("run classset_015.py first (writes docs/reports/015/classset.json)")
    cs = json.loads(cs_path.read_text(encoding="utf-8"))
    st, lp = m["egemaps_stats"], m["layer_probe"]
    ex = exploratory(FEAT_DIR)
    by = {r["feature"]: r for r in st["features"]}
    d = lp["delta_selected_minus_24"]
    sel = lp["selected"]["metrics"]
    loso = {int(k): v["leave_one_series_out"] for k, v in lp["curve"].items()}
    base = loso[24]
    egp = lp["egemaps_probe"]["leave_one_series_out"]
    support = base["emotion_support"]
    max_v = max(st["features"], key=lambda r: abs(r["rho_valence"]))
    max_a = max(st["features"], key=lambda r: abs(r["rho_arousal"]))
    jit = "jitterLocal_sma3nz_amean"
    chosen = lp["selected"]["chosen"]
    series = lp["series"]
    picked_on = {s: [c["layer"] for c in chosen if c["test_series"] != s] for s in series}
    mode0 = max(set(picked_on[series[0]]), key=picked_on[series[0]].count)
    c16, c24, hum = cs["layers"]["16"], cs["layers"]["24"], cs["human"]
    medians = st["class_medians_z"]
    emo_order = sorted(VI, key=lambda e: -medians[H1A[0]][e])
    dis_model = c24["merge"]["disgust_predicted_as"]
    n_dis_model, n_dis_hum = sum(dis_model.values()), sum(hum["disgust_row"].values())
    dis_order = sorted(VI, key=lambda e: -dis_model[e])

    data = {
        "fig1": [
            {"e": e, "vi": VI[e], "f0": medians[H1A[0]][e], "ld": medians[H1A[1]][e]}
            for e in emo_order
        ],
        "fig2": [
            {"l": k, "f1": loso[k]["emotion_macro_f1"], "ci": loso[k]["emotion_macro_f1_ci95"]}
            for k in sorted(loso)
        ],
        "sel": sel["emotion_macro_f1"],
        "egp": egp["emotion_macro_f1"],
        "fig3": [
            {
                "e": e,
                "vi": VI[e],
                "m": dis_model[e] / n_dis_model,
                "h": hum["disgust_row"][e] / n_dis_hum,
            }
            for e in dis_order
        ],
        "nm": n_dis_model,
        "nh": n_dis_hum,
    }

    lo, hi = d["ci95"]
    values = {
        "data_js": json.dumps(data, ensure_ascii=False).replace("</", "<\\/"),
        "style": STYLE,
        "n": str(m["n_clips"]),
        "series0": series[0],
        "series1": series[1],
        "commit": m["analysis_git_commit"][:7],
        "chance": f"{chance_macro_f1(support):.2f}",
        "support": " · ".join(f"{VI[e]} {support[e]}" for e in VI),
        # Q1
        "f0_ra": f"{by[H1A[0]]['rho_arousal']:+.2f}",
        "ld_ra": f"{by[H1A[1]]['rho_arousal']:+.2f}",
        "max_a": f"{abs(max_a['rho_arousal']):.2f}",
        "max_v": f"{abs(max_v['rho_valence']):.2f}",
        "va": f"{ex['va_spearman']:+.2f}",
        "jit_raw": f"{by[jit]['rho_valence']:+.2f}",
        "jit_p": f"{ex['partial'][jit]:+.2f}",
        "egp_cv": f2(egp["ccc_valence"]),
        # Q2
        "base_f1": f"{base['emotion_macro_f1']:.3f}",
        "sel_f1": f"{sel['emotion_macro_f1']:.3f}",
        "egp_f1": f"{egp['emotion_macro_f1']:.3f}",
        "delta": f"{d['delta']:+.3f}",
        "lo": f"{lo:+.3f}",
        "hi": f"{hi:+.3f}",
        "s0": f"{d['seed_range'][0]:+.3f}",
        "s1": f"{d['seed_range'][1]:+.3f}",
        "seeds": str(len(m["seeds"])),
        "nm_txt": str(n_dis_model),
        "nh_txt": str(n_dis_hum),
        "mode0": str(mode0),
        "picked0": ", ".join(map(str, picked_on[series[0]])),
        "picked1": ", ".join(map(str, picked_on[series[1]])),
        "base_cv": f2(base["ccc_valence"]),
        "sel_cv": f2(sel["ccc_valence"]),
        # Q3
        "dis_f1": f"{c24['seven_per_class']['disgust']:.2f}",
        "sur_f1": f"{c24['seven_per_class']['surprise']:.2f}",
        "naive7": f"{c16['seven_macro_f1']:.3f}",
        "naive5": f"{c16['drop']['naive_5class']:.3f}",
        "n5": str(cs["n_5"]),
        "drop7": f"{c16['drop']['seven_model']:.3f}",
        "drop5": f"{c16['drop']['five_model']:.3f}",
        "drop_d": delta_cell(c16["drop"]["delta"]),
        "merge7": f"{c16['merge']['seven_model']:.3f}",
        "merge6": f"{c16['merge']['merged_model']:.3f}",
        "merge_d": delta_cell(c16["merge"]["delta"]),
        "k7": f"{hum['seven']:.2f}",
        "k6": f"{hum['merge_disgust_anger']:.2f}",
        "k5": f"{hum['drop_disgust_surprise']:.2f}",
        "kn": str(hum["n"]),
        "dis_anger_m": f"{dis_model['anger'] / n_dis_model:.0%}",
        "dis_anger_h": f"{hum['disgust_row']['anger'] / n_dis_hum:.0%}",
        # appendix
        "groups": " · ".join(f"{k} {v:g}" for k, v in st["groups"].items()),
        "h1": "".join(
            f"<li>{k}: {'đúng' if v else 'sai'}</li>" for k, v in st["hypotheses"].items()
        ),
        "layer_rows": "".join(
            f"<tr><td>tầng {k}{' (đang dùng)' if k == 24 else ''}</td>"
            f'<td class="num">{ci(loso[k], "emotion_macro_f1")}</td>'
            f'<td class="num">{lp["curve"][str(k)]["groupkfold"]["emotion_macro_f1"]:.3f}</td>'
            f'<td class="num">{loso[k]["ccc_valence"]:.3f}</td>'
            f'<td class="num">{loso[k]["ccc_arousal"]:.3f}</td></tr>'
            for k in sorted(loso)
        ),
        "feat_rows": "".join(
            f"<tr><td>{r['group']}</td><td><code>{html.escape(r['feature'])}</code></td>"
            f'<td class="num">{r["rho_arousal"] + 0.0:+.3f}</td><td class="num">{round(r["rho_valence"], 3) + 0.0:+.3f}</td>'
            f'<td class="num">{r["eps2"]:.3f}</td></tr>'
            for r in sorted(st["features"], key=lambda r: -abs(r["rho_arousal"]))
        ),
        "cs24_drop": delta_cell(c24["drop"]["delta"]),
        "cs24_merge": delta_cell(c24["merge"]["delta"]),
        "cs24_drop_v": f"{c24['drop']['seven_model']:.3f} → {c24['drop']['five_model']:.3f}",
        "cs24_merge_v": f"{c24['merge']['seven_model']:.3f} → {c24['merge']['merged_model']:.3f}",
    }
    page = TEMPLATE
    for k, v in values.items():
        page = page.replace("@@" + k + "@@", v)
    assert "@@" not in page, "unfilled placeholder"
    out = REPORT_DIR / "report.html"
    out.write_text(page, encoding="utf-8")
    print(f"wrote {out}")


STYLE = r"""
  :root{
    --bg:#f7f8fa; --panel:#fff; --ink:#1c2128; --muted:#57606a; --faint:#8c959f; --line:#d8dee4;
    --accent:#2563eb; --s1:#2563eb; --s2:#c2410c; --ok:#1a7f37; --warn:#bc4c00;
    --code:#eef1f4; --grid:#e6e9ed; --okbg:rgba(26,127,55,.07); --qbg:rgba(37,99,235,.06);
    color-scheme:light;
  }
  @media (prefers-color-scheme: dark){
    :root:not([data-theme="light"]){
      --bg:#0d1117; --panel:#161b22; --ink:#e6edf3; --muted:#9aa4af; --faint:#6e7681; --line:#2d333b;
      --accent:#589bff; --s1:#3b82f6; --s2:#e0702a; --ok:#3fb950; --warn:#f0883e;
      --code:#1c2128; --grid:#21262d; --okbg:rgba(63,185,80,.10); --qbg:rgba(88,155,255,.08);
      color-scheme:dark;
    }
  }
  :root[data-theme="dark"]{
    --bg:#0d1117; --panel:#161b22; --ink:#e6edf3; --muted:#9aa4af; --faint:#6e7681; --line:#2d333b;
    --accent:#589bff; --s1:#3b82f6; --s2:#e0702a; --ok:#3fb950; --warn:#f0883e;
    --code:#1c2128; --grid:#21262d; --okbg:rgba(63,185,80,.10); --qbg:rgba(88,155,255,.08);
    color-scheme:dark;
  }
  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
    font:16px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Arial,sans-serif}
  .wrap{max-width:860px;margin:0 auto;padding-inline:16px;padding-block:32px 80px}
  header{border-bottom:2px solid var(--line);padding-bottom:16px}
  h1{font-size:28px;line-height:1.3;margin:0 0 8px;text-wrap:balance}
  h2{font-size:22px;margin:48px 0 6px;padding-top:16px;border-top:1px solid var(--line)}
  h2 small{display:block;font-size:13px;font-weight:700;color:var(--accent);
    text-transform:uppercase;letter-spacing:.06em;margin-bottom:2px}
  h3{font-size:16px;margin:22px 0 4px}
  p,li{margin:8px 0}
  .sub{color:var(--muted);font-size:14px}
  a{color:var(--accent)}
  code{background:var(--code);padding:1px 5px;border-radius:4px;font-size:13px;
    font-family:"SF Mono",Consolas,monospace}
  .scroll{overflow-x:auto}
  table{width:100%;border-collapse:collapse;margin:12px 0;font-size:15px;background:var(--panel);
    border:1px solid var(--line);border-radius:8px;overflow:hidden}
  th,td{padding:9px 12px;border-bottom:1px solid var(--line);text-align:left;vertical-align:middle}
  th{background:rgba(127,127,127,.08);font-weight:600;font-size:13px;color:var(--muted)}
  tr:last-child td{border-bottom:none}
  .num{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
  .ci{color:var(--muted);font-size:13px;white-space:nowrap}
  .up{color:var(--ok);font-weight:700}
  .flat{color:var(--warn);font-weight:700}
  .q{background:var(--qbg);border-radius:8px;padding:12px 16px;margin:10px 0 4px}
  .q p{margin:4px 0}
  .ans{background:var(--okbg);border:1px solid var(--ok);border-radius:10px;padding:12px 18px;margin:18px 0}
  .ans b.t{color:var(--ok)}
  .ans p{margin:4px 0}
  .warnbox{background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--warn);
    border-radius:8px;padding:12px 16px;margin:16px 0}
  .warnbox p{margin:4px 0}
  .summary{display:grid;gap:10px;margin:18px 0;padding:0;list-style:none;counter-reset:s}
  .summary li{background:var(--panel);border:1px solid var(--line);border-radius:8px;
    padding:12px 16px 12px 52px;position:relative;margin:0}
  .summary li::before{counter-increment:s;content:counter(s);position:absolute;left:16px;top:12px;
    width:24px;height:24px;border-radius:50%;background:var(--accent);color:var(--panel);
    font-weight:700;font-size:14px;text-align:center;line-height:24px}
  .tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin:14px 0}
  .tile{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px 14px}
  .tile .k{font-size:13px;color:var(--muted)}
  .tile .v{font-size:26px;font-weight:700;line-height:1.3}
  .tile p{margin:0;font-size:14px;color:var(--muted)}
  figure{margin:16px 0;background:var(--panel);border:1px solid var(--line);border-radius:8px;
    padding:14px 16px 10px}
  .fig-title{font-weight:600;font-size:15px;margin:0}
  figcaption{font-size:14px;color:var(--muted);margin-top:6px}
  .legend{display:flex;flex-wrap:wrap;gap:6px 18px;font-size:13px;color:var(--muted);margin:6px 0}
  .legend span{display:inline-flex;align-items:center;gap:6px}
  .sw{width:14px;height:10px;border-radius:2px;display:inline-block}
  .sw.dash{height:0;border-top:2px dashed var(--faint);background:none}
  svg{display:block;width:100%;height:auto;overflow:visible}
  svg text{fill:var(--muted);font-size:12px;font-family:inherit}
  svg .lbl{fill:var(--ink);font-size:13px}
  svg .strong{fill:var(--ink);font-weight:700;font-size:13px}
  details{margin:12px 0}
  summary{cursor:pointer;color:var(--accent);font-weight:600}
  .tip{position:fixed;pointer-events:none;background:var(--ink);color:var(--bg);font-size:13px;
    padding:6px 9px;border-radius:6px;line-height:1.4;max-width:280px;z-index:10}
  @media (max-width:560px){ h1{font-size:23px} }
"""

TEMPLATE = r"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Đặc trưng cảm xúc trong audio</title>
<style>@@style@@</style>
</head>
<body>
<div class="wrap">
<header>
  <h1>Trong âm thanh có gì cho biết cảm xúc, và dùng nó thế nào cho tốt nhất?</h1>
  <div class="sub">ViEmoSpeech · change 015 · @@n@@ clip từ 2 phim · phân tích chạy từ commit
    <code>@@commit@@</code></div>
</header>

<h2><small>Tóm tắt</small>Ba câu hỏi, ba câu trả lời</h2>
<ol class="summary">
  <li><b>Âm thanh cho biết cảm xúc <i>mạnh hay yếu</i>, gần như không cho biết <i>tích cực hay tiêu cực</i>.</b>
    Cao độ và độ to giọng tăng rõ theo mức kích động. Với vui/buồn, tín hiệu rất yếu.</li>
  <li><b>Lấy thông tin ở tầng giữa của WavLM tốt hơn tầng cuối đang dùng.</b>
    Điểm tăng từ @@base_f1@@ lên @@sel_f1@@, và mức tăng này đáng tin.</li>
  <li><b>Bỏ hoặc gộp các lớp khó (ghê/khinh, ngạc nhiên) không làm model tốt hơn.</b>
    Con số trông tăng chỉ vì bài kiểm tra trở nên dễ hơn.</li>
</ol>

<h2><small>Trước khi đọc</small>Dữ liệu và cách chấm điểm</h2>
<p><b>Dữ liệu:</b> @@n@@ đoạn thoại ngắn cắt từ 2 phim truyền hình Việt (@@series0@@, @@series1@@). Mỗi
đoạn được người gán một trong 7 cảm xúc (@@support@@), cùng hai điểm 1–5:</p>
<ul>
  <li><b>Arousal</b> (mức kích động): bình thản → kích động mạnh.</li>
  <li><b>Valence</b> (cực tính): tiêu cực → tích cực.</li>
</ul>
<p><b>Cách chấm:</b> model học trên một phim rồi bị kiểm tra trên phim kia, với dàn diễn viên khác hẳn.
Như vậy model không thể "nhớ giọng" người quen, và điểm số phản ánh khả năng tổng quát thật.</p>
<p><b>Điểm số chính:</b> macro-F1, từ 0 đến 1, là trung bình độ chính xác của từng cảm xúc (lớp hiếm
được tính ngang lớp phổ biến). Đoán ngẫu nhiên được khoảng @@chance@@. Với valence và arousal (điểm
1–5) dùng <b>CCC</b>, cũng từ 0 đến 1: 0 là không đoán được gì, 1 là đoán trúng hoàn toàn.</p>

<h2><small>Câu hỏi 1</small>Những đặc trưng âm thanh quen thuộc nói gì về cảm xúc?</h2>
<div class="q">
  <p><b>Vì sao hỏi:</b> trước khi dùng model "hộp đen", cần biết những thứ đo được bằng tay, như cao độ,
  độ to, độ rung của giọng, có mang cảm xúc không, và mang loại thông tin nào.</p>
  <p><b>Đã làm:</b> đo 88 đặc trưng âm học chuẩn (bộ eGeMAPS) cho mọi đoạn. Mỗi đặc trưng được so với
  giọng cùng giới và cùng lứa tuổi, để không nhầm "giọng nữ cao" với "đang kích động". Sau đó xem mỗi đặc
  trưng đi cùng chiều với arousal và valence đến mức nào (hệ số tương quan ρ: 0 là không liên quan,
  ±1 là hoàn toàn cùng chiều hoặc ngược chiều).</p>
</div>

<h3>Kết quả 1a: cao độ và độ to đi theo mức kích động</h3>
<figure>
  <p class="fig-title">Cao độ và độ to giọng theo từng cảm xúc (so với trung bình giọng cùng giới, cùng tuổi)</p>
  <div class="legend"><span><i class="sw" style="background:var(--s1)"></i>cao độ (F0)</span>
    <span><i class="sw" style="background:var(--s2)"></i>độ to</span></div>
  <svg id="fig1" role="img" aria-label="Cao độ và độ to theo cảm xúc"></svg>
  <figcaption>Giận và sợ: giọng cao và to hơn bình thường. Ngạc nhiên: cao hơn nhưng không to hơn.
  Trung tính và buồn: thấp và nhỏ hơn.
  Tương quan với arousal: cao độ ρ = @@f0_ra@@, độ to ρ = @@ld_ra@@, đúng như các nghiên cứu trước.</figcaption>
</figure>

<h3>Kết quả 1b: với valence (tích cực / tiêu cực), tín hiệu rất yếu</h3>
<div class="tiles">
  <div class="tile"><div class="k">Đặc trưng mạnh nhất với arousal</div><div class="v">ρ @@max_a@@</div>
    <p>tín hiệu rõ</p></div>
  <div class="tile"><div class="k">Đặc trưng mạnh nhất với valence</div><div class="v">ρ @@max_v@@</div>
    <p>yếu hơn gần 3 lần</p></div>
  <div class="tile"><div class="k">Còn lại sau khi trừ phần arousal</div><div class="v">ρ @@jit_p@@</div>
    <p>chỉ có độ rung giọng (jitter)</p></div>
</div>
<p>Một phần tín hiệu valence thực ra là arousal "lọt sang": trong nhãn, đoạn kích động thường bị chấm
valence thấp (giận, sợ), hai điểm tương quan ρ = @@va@@. Khi trừ phần đó ra, chỉ <b>jitter</b> (độ rung
không đều của dây thanh) còn giữ tín hiệu, từ @@jit_raw@@ xuống @@jit_p@@. Dùng cả 88 đặc trưng để dự đoán
valence ở phim còn lại thì điểm gần bằng 0 (CCC = @@egp_cv@@).</p>

<div class="ans"><p><b class="t">Trả lời câu 1:</b> âm thanh cho biết cảm xúc <b>mạnh hay yếu</b>, nhưng gần
như không cho biết <b>tích cực hay tiêu cực</b>. Muốn đoán valence tốt, cần thêm nguồn khác ngoài âm
thanh, ví dụ lời thoại.</p></div>

<h2><small>Câu hỏi 2</small>Để model tự học, nên lấy thông tin ở tầng nào?</h2>
<div class="q">
  <p><b>Vì sao hỏi:</b> model hiện tại dùng WavLM, một mạng có 24 tầng đã được huấn luyện trước trên rất
  nhiều giọng nói, và đang lấy thông tin ở <b>tầng cuối cùng</b>. Nhưng tầng cuối thường chuyên về "nói chữ
  gì", trong khi cảm xúc có thể nằm ở tầng giữa.</p>
  <p><b>Đã làm:</b> thử từng tầng (0 đến 24), cùng một cách học đơn giản, cùng cách chấm. Để công bằng, tầng
  "tốt nhất" được chọn <b>chỉ bằng phim dùng để học</b>, không nhìn phim kiểm tra.</p>
</div>

<figure>
  <p class="fig-title">Điểm macro-F1 khi lấy thông tin ở từng tầng của WavLM</p>
  <div class="legend"><span><i class="sw" style="background:var(--s1)"></i>điểm theo tầng (dải mờ = khoảng tin cậy 95%)</span>
    <span><i class="sw dash"></i>mốc so sánh</span></div>
  <svg id="fig2" role="img" aria-label="macro-F1 theo tầng WavLM"></svg>
  <figcaption>Điểm tăng dần đến khoảng tầng 9–15 rồi giảm về tầng cuối. Rê chuột lên biểu đồ để xem điểm
  từng tầng.</figcaption>
</figure>

<div class="scroll"><table>
  <thead><tr><th>Cách lấy thông tin</th><th class="num">macro-F1</th><th class="num">CCC valence</th></tr></thead>
  <tbody>
    <tr><td>Tầng cuối (đang dùng)</td><td class="num">@@base_f1@@</td><td class="num">@@base_cv@@</td></tr>
    <tr><td><b>Tầng chọn bằng phim học</b></td><td class="num"><b>@@sel_f1@@</b></td><td class="num">@@sel_cv@@</td></tr>
    <tr><td>88 đặc trưng thủ công (câu 1)</td><td class="num">@@egp_f1@@</td><td class="num">@@egp_cv@@</td></tr>
  </tbody>
</table></div>
<p>Chênh lệch giữa tầng chọn và tầng cuối là <b>@@delta@@</b>, khoảng tin cậy 95% [@@lo@@, @@hi@@], và
chênh lệch ở từng lần trong @@seeds@@ lần chạy lại nằm trong [@@s0@@, @@s1@@]. Mức này vượt ngưỡng "đáng kể" 0.02 đã đặt trước khi chạy, nên là
cải thiện thật. Khi học trên @@series0@@, tầng được chọn gần như luôn là <b>@@mode0@@</b>.</p>

<div class="ans"><p><b class="t">Trả lời câu 2:</b> nên lấy thông tin ở <b>tầng giữa</b> của WavLM thay vì
tầng cuối. Đây là cải thiện rẻ nhất có thể: không cần thêm dữ liệu, chỉ đổi chỗ lấy. Valence vẫn thấp
(@@base_cv@@ → @@sel_cv@@), khớp với câu 1.</p></div>

<h2><small>Câu hỏi 3</small>Bỏ hoặc gộp các cảm xúc khó có làm model tốt hơn không?</h2>
<div class="q">
  <p><b>Vì sao hỏi:</b> model gần như không nhận ra <b>ghê/khinh</b> (F1 @@dis_f1@@) và <b>ngạc nhiên</b>
  (F1 @@sur_f1@@). Người gán nhãn cũng hay bất đồng ở hai lớp này. Nếu bỏ hoặc gộp chúng, các cảm xúc còn
  lại có được nhận tốt hơn không?</p>
  <p><b>Đã làm:</b> dùng tầng tốt từ câu 2, thử hai cách: (a) bỏ hẳn hai lớp, còn 5 cảm xúc, @@n5@@ đoạn;
  (b) gộp ghê/khinh vào giận, còn 6 cảm xúc.</p>
</div>

<div class="warnbox">
  <p><b>Cái bẫy cần tránh:</b> bỏ hai lớp thì điểm nhảy từ @@naive7@@ lên @@naive5@@. Nhưng đó là vì bài kiểm
  tra dễ hơn (ít lựa chọn hơn, bỏ đúng hai lớp khó nhất), không phải vì model giỏi hơn. So sánh đúng là:
  chấm <b>model cũ và model mới trên cùng những đoạn đó, cùng những cảm xúc đó</b>.</p>
</div>

<div class="scroll"><table>
  <thead><tr><th>Cách thử</th><th class="num">Model cũ (7 lớp)</th><th class="num">Model mới</th>
    <th class="num">Chênh lệch [khoảng tin cậy]</th><th>Đáng kể?</th></tr></thead>
  <tbody>
    <tr><td>(a) Bỏ ghê/khinh + ngạc nhiên</td><td class="num">@@drop7@@</td><td class="num">@@drop5@@</td>@@drop_d@@</tr>
    <tr><td>(b) Gộp ghê/khinh vào giận</td><td class="num">@@merge7@@</td><td class="num">@@merge6@@</td>@@merge_d@@</tr>
  </tbody>
</table></div>
<p>Cả hai chênh lệch đều dưới ngưỡng 0.02: các cảm xúc còn lại gần như không được nhận tốt hơn.</p>

<h3>Vì sao gộp vào "giận" không giúp</h3>
<figure>
  <p class="fig-title">Những đoạn được gán "ghê/khinh" bị model và người soát lại gọi là gì</p>
  <div class="legend"><span><i class="sw" style="background:var(--s1)"></i>model (@@nm_txt@@ đoạn)</span>
    <span><i class="sw" style="background:var(--s2)"></i>người soát lại mù (@@nh_txt@@ đoạn)</span></div>
  <svg id="fig3" role="img" aria-label="Đoạn ghê/khinh được gọi là gì"></svg>
  <figcaption>Chỉ khoảng @@dis_anger_m@@ (model) và @@dis_anger_h@@ (người) gọi chúng là "giận"; phần còn lại rải sang
  trung tính, buồn, vui. Ghê/khinh trong hai phim này chủ yếu là nói giọng bình thường mà nội dung khinh
  bỉ, nên nhận ra qua lời nói hơn là qua âm thanh, đúng như câu 1.</figcaption>
</figure>
<p>Điều thay đổi thật khi bỏ hai lớp là <b>độ đồng thuận của người gán nhãn</b>: hệ số κ tăng từ @@k7@@
(7 lớp) lên @@k5@@ (5 lớp), còn gộp chỉ lên @@k6@@ (đo trên @@kn@@ đoạn được hai người gán độc lập). Một
phần là vì những đoạn khó nhất cũng bị bỏ theo.</p>

<div class="ans"><p><b class="t">Trả lời câu 3:</b> <b>không</b>, đổi bộ cảm xúc không làm model tốt hơn.
Lý do chính đáng duy nhất để bỏ hai lớp này là nhãn của chúng kém tin cậy. Nếu muốn, có thể giữ 7 lớp
trong dữ liệu và báo cáo thêm kết quả 5 lớp, nhưng cần một kế hoạch đo riêng.</p></div>

<h2><small>Kết luận</small>Việc nên làm tiếp</h2>
<ol class="summary">
  <li><b>Đổi model hiện tại sang lấy thông tin ở tầng giữa của WavLM</b> (cải thiện đã chứng minh,
    @@base_f1@@ → @@sel_f1@@).</li>
  <li><b>Thêm nguồn ngoài âm thanh cho valence</b>, như lời thoại hoặc thanh điệu (hướng của change 013),
    vì âm thanh một mình không đủ.</li>
  <li><b>Xem lại hướng dẫn gán nhãn cho ghê/khinh và ngạc nhiên</b>, thay vì bỏ chúng khỏi model.</li>
</ol>

<h2><small>Phụ lục</small>Giới hạn và chi tiết kỹ thuật</h2>
<h3>Giới hạn cần nhớ</h3>
<ul>
  <li>Nhãn chủ yếu do một người gán, độ đồng thuận với người thứ hai κ = @@k7@@. Các con số là thử nghiệm,
    chưa phải kết quả chính thức.</li>
  <li>Tiếng Việt có thanh điệu: cao độ và chất giọng vừa mang thanh điệu vừa mang cảm xúc. Chưa có nhãn
    thanh điệu theo âm tiết để tách hai thứ này.</li>
  <li>Chỉ có giọng miền Bắc. Đặc trưng chỉ được chuẩn hoá theo giới và tuổi, nên khác biệt thu âm giữa hai
    phim vẫn còn.</li>
</ul>
<h3>Phần nào đã đặt kế hoạch trước, phần nào không</h3>
<ul>
  <li><b>Câu 1 và câu 2</b> theo kế hoạch đo đã chốt và commit trước khi chạy
    (<code>docs/spec/changes/015-emotion-acoustic-features/preregistration.md</code>). Ba giả thuyết của
    câu 1: <ul>@@h1@@</ul></li>
  <li><b>Phần "trừ arousal" ở câu 1 và toàn bộ câu 3</b> là phân tích thêm, làm sau khi đã thấy kết quả, chỉ
    dùng để định hướng.</li>
  <li>Câu 3 ở tầng cuối cho kết luận giống hệt: bỏ lớp @@cs24_drop_v@@, gộp lớp @@cs24_merge_v@@.</li>
</ul>
<h3>Cách đo</h3>
<ul>
  <li>Chuẩn hoá theo nhóm giới × tuổi: @@groups@@.</li>
  <li>Model: một lớp tuyến tính trên đặc trưng WavLM đã đóng băng, @@seeds@@ lần chạy với khởi tạo khác nhau
    rồi gộp. Khoảng tin cậy và chênh lệch tính bằng bootstrap ghép cặp 1000 lần.</li>
  <li>Tầng được chọn bằng phim học, theo từng lần chạy. Học trên @@series0@@: @@picked0@@. Học trên
    @@series1@@ (chỉ 3 tập, nên dao động): @@picked1@@.</li>
</ul>
<details><summary>Bảng điểm đủ 25 tầng</summary>
<div class="scroll"><table>
  <thead><tr><th>Tầng</th><th class="num">macro-F1 (học 1 phim, thử phim kia)</th>
    <th class="num">macro-F1 (trộn 2 phim, lạc quan)</th><th class="num">CCC valence</th>
    <th class="num">CCC arousal</th></tr></thead>
  <tbody>@@layer_rows@@</tbody>
</table></div>
</details>
<details><summary>Bảng đủ 88 đặc trưng âm học (xếp theo tương quan với arousal)</summary>
<div class="scroll"><table>
  <thead><tr><th>Nhóm</th><th>Đặc trưng</th><th class="num">ρ arousal</th><th class="num">ρ valence</th>
    <th class="num">ε² (phân biệt 7 lớp)</th></tr></thead>
  <tbody>@@feat_rows@@</tbody>
</table></div>
</details>
<p class="sub">Nguồn số liệu: <code>docs/reports/015/metrics.json</code> (<code>analyze_emotion_features.py</code>),
  <code>docs/reports/015/classset.json</code> (<code>classset_015.py</code>), κ từ
  <code>docs/reports/014/kappa.md</code>. Trang được sinh bởi <code>render_015_report.py</code>, không có
  số nào gõ tay.</p>
</div>
<div class="tip" id="tip" hidden></div>

<script>
const DATA = @@data_js@@;
(function () {
  const NS = "http://www.w3.org/2000/svg", tip = document.getElementById("tip");
  function moveTip(e) {
    let x = e.clientX + 14, y = e.clientY + 14;
    if (x + tip.offsetWidth > innerWidth - 8) x = e.clientX - tip.offsetWidth - 14;
    if (y + tip.offsetHeight > innerHeight - 8) y = e.clientY - tip.offsetHeight - 14;
    tip.style.left = x + "px"; tip.style.top = y + "px";
  }
  function bindTip(el, html) {
    el.addEventListener("pointerenter", e => { tip.innerHTML = html; tip.hidden = false; moveTip(e); });
    el.addEventListener("pointermove", moveTip);
    el.addEventListener("pointerleave", () => { tip.hidden = true; });
  }
  function el(tag, attrs, parent) {
    const n = document.createElementNS(NS, tag);
    for (const k in attrs) n.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(n);
    return n;
  }
  function text(p, x, y, s, a) { const t = el("text", Object.assign({x, y}, a || {}), p); t.textContent = s; return t; }
  const sg = v => (v >= 0 ? "+" : "") + v.toFixed(2), GRID = "var(--grid)", BASE = "var(--faint)";

  // grouped horizontal bars, zero-centred: rows of {vi, a, b}
  function pairedBars(id, rows, ka, kb, lim, ticks, fmt, tipf) {
    const svg = document.getElementById(id), W = 720, L = 120, R = 46, rowH = 34;
    const H = 26 + rows.length * rowH + 6, x0 = lim[0] < 0 ? L + (W - L - R) * (-lim[0]) / (lim[1] - lim[0]) : L;
    const sc = (W - L - R) / (lim[1] - lim[0]);
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    ticks.forEach(t => {
      const x = x0 + t * sc;
      el("line", {x1: x, x2: x, y1: 20, y2: H - 4, stroke: t === 0 ? BASE : GRID}, svg);
      text(svg, x, 13, fmt(t), {"text-anchor": "middle"});
    });
    rows.forEach((r, i) => {
      const y = 26 + i * rowH;
      text(svg, L - 10, y + 18, r.vi, {"text-anchor": "end", class: "lbl"});
      [[ka, "var(--s1)", 4], [kb, "var(--s2)", 16]].forEach(([k, c, dy]) => {
        const v = r[k], w = Math.max(Math.abs(v) * sc, 1.5);
        el("rect", {x: v >= 0 ? x0 : x0 - w, y: y + dy, width: w, height: 11, rx: 2, fill: c}, svg);
      });
      const hit = el("rect", {x: 0, y, width: W, height: rowH, fill: "transparent"}, svg);
      bindTip(hit, tipf(r));
    });
  }
  pairedBars("fig1", DATA.fig1, "f0", "ld", [-0.8, 0.8], [-0.8, -0.4, 0, 0.4, 0.8], sg,
    r => `<b>${r.vi}</b> (${r.e})<br>cao độ ${sg(r.f0)}<br>độ to ${sg(r.ld)}<br><span style="opacity:.8">đơn vị: độ lệch chuẩn so với giọng cùng nhóm</span>`);
  pairedBars("fig3", DATA.fig3, "m", "h", [0, 0.4], [0, 0.1, 0.2, 0.3, 0.4], t => Math.round(t * 100) + "%",
    r => `<b>${r.vi}</b><br>model ${Math.round(r.m * 100)}% · người ${Math.round(r.h * 100)}%`);

  // layer curve
  (function () {
    const svg = document.getElementById("fig2"), W = 720, L = 44, R = 170, T = 12, B = 34, H = 290;
    const lo = 0.15, hi = 0.35, xs = l => L + l * (W - L - R) / 24, ys = v => T + (hi - v) / (hi - lo) * (H - T - B);
    svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    for (let v = 0.15; v <= 0.3501; v += 0.05) {
      el("line", {x1: L, x2: W - R, y1: ys(v), y2: ys(v), stroke: GRID}, svg);
      text(svg, L - 6, ys(v) + 4, v.toFixed(2), {"text-anchor": "end"});
    }
    for (let l = 0; l <= 24; l += 4) text(svg, xs(l), H - 16, l, {"text-anchor": "middle"});
    text(svg, (L + W - R) / 2, H, "tầng của WavLM (0 = đầu vào, 24 = tầng cuối)", {"text-anchor": "middle"});
    const c = DATA.fig2;
    el("polygon", {points: c.map(p => `${xs(p.l)},${ys(p.ci[1])}`).concat(c.slice().reverse().map(p => `${xs(p.l)},${ys(p.ci[0])}`)).join(" "),
      fill: "var(--s1)", opacity: .14}, svg);
    el("polyline", {points: c.map(p => `${xs(p.l)},${ys(p.f1)}`).join(" "), fill: "none", stroke: "var(--s1)",
      "stroke-width": 2.5, "stroke-linejoin": "round"}, svg);
    [[DATA.sel, "tầng chọn bằng phim học", "strong"], [DATA.egp, "88 đặc trưng thủ công", ""]].forEach(([v, s, cl]) => {
      el("line", {x1: L, x2: W - R, y1: ys(v), y2: ys(v), stroke: BASE, "stroke-dasharray": "5 4"}, svg);
      text(svg, W - R + 8, ys(v) + 4, `${s} ${v.toFixed(3)}`, {class: cl});
    });
    const last = c[24];
    el("circle", {cx: xs(24), cy: ys(last.f1), r: 5.5, fill: "var(--s1)", stroke: "var(--panel)", "stroke-width": 2}, svg);
    text(svg, W - R + 8, ys(last.f1) + 4, `tầng cuối (đang dùng) ${last.f1.toFixed(3)}`, {class: "lbl"});
    const cross = el("line", {y1: T, y2: H - B, stroke: BASE, visibility: "hidden"}, svg), step = (W - L - R) / 24;
    c.forEach(p => {
      const hit = el("rect", {x: xs(p.l) - step / 2, y: T, width: step, height: H - T - B, fill: "transparent"}, svg);
      hit.addEventListener("pointerenter", () => { cross.setAttribute("x1", xs(p.l)); cross.setAttribute("x2", xs(p.l)); cross.setAttribute("visibility", "visible"); });
      hit.addEventListener("pointerleave", () => cross.setAttribute("visibility", "hidden"));
      bindTip(hit, `<b>tầng ${p.l}</b>${p.l === 24 ? " (đang dùng)" : ""}<br>macro-F1 ${p.f1.toFixed(3)}<br>khoảng tin cậy [${p.ci[0].toFixed(3)}, ${p.ci[1].toFixed(3)}]`);
    });
  })();
})();
</script>
</body>
</html>
"""

if __name__ == "__main__":
    main()
