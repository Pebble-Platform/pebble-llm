"""Report labeling progress per series: videos, human labels, labeled duration.

Reads the labeler's source of truth directly (state.db, ADR-003/ADR-004) plus a
scan of the episode dirs — no running server needed.

  videos   = epNN[_K] dirs that have cut clips (same rule as the labeler listing)
  labels   = records with an emotion and not rejected
  duration = sum(end - start) over those same records

Also breaks the labeled records down by emotion, gender, and age_group (audios +
duration each); "(chưa gán)" = labeled but that demographic not set yet.

Usage:
  PYTHONIOENCODING=utf-8 python scripts/vietnamese-ser/labeler_stats.py \
      [--root data/vietnamese-ser/episodes] [--html labeler_stats.html]

Without --html it prints text tables; with --html it writes a self-contained
dashboard file (open offline, regenerate any time to refresh the snapshot).
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from datetime import datetime
from pathlib import Path

from labeler_store import read_records

ROOT = Path(__file__).resolve().parents[2]
EP_RE = re.compile(r"^ep\d+(_\d+)?$", re.IGNORECASE)


def hms(sec: float) -> str:
    s = round(sec)
    return f"{s // 3600}:{s // 60 % 60:02d}:{s % 60:02d}"


def collect(root: Path) -> tuple[dict, dict, dict, dict]:
    """Scan episode dirs + records; return (stats, per_label, per_gender, per_age).

    stats: series -> [videos, labels, duration]; the rest: key -> [audios, duration].
    """
    stats: dict[str, list] = {}
    per_label: dict[str, list] = {}
    per_gender: dict[str, list] = {}
    per_age: dict[str, list] = {}

    for ep in sorted(p for p in root.rglob("*") if p.is_dir() and EP_RE.match(p.name)):
        if not any((ep / "clips").glob("seg*.wav")):
            continue
        series = ep.parent.relative_to(root).as_posix() or "(root)"
        stats.setdefault(series, [0, 0, 0.0])[0] += 1

    for r in read_records(root):
        if not r.get("emotion") or r.get("rejected"):
            continue
        series = Path(r["epKey"]).parent.as_posix()
        series = "(root)" if series == "." else series
        dur = r["end"] - r["start"]
        row = stats.setdefault(series, [0, 0, 0.0])
        row[1] += 1
        row[2] += dur
        for d, key in (
            (per_label, r["emotion"]),
            (per_gender, r.get("gender") or "(chưa gán)"),
            (per_age, r.get("age_group") or "(chưa gán)"),
        ):
            cell = d.setdefault(key, [0, 0.0])
            cell[0] += 1
            cell[1] += dur

    return stats, per_label, per_gender, per_age


def breakdown(title: str, d: dict[str, list]) -> None:
    """Print an '<title> | audios | duration' table, most-frequent first."""
    w = max([len(k) for k in d] + [len(title)])
    print(f"\n{title:<{w}}  {'audios':>6}  {'duration':>9}")
    for k, (n, dur) in sorted(d.items(), key=lambda kv: -kv[1][0]):
        print(f"{k:<{w}}  {n:>6}  {hms(dur):>9}")


def print_text(stats: dict, per_label: dict, per_gender: dict, per_age: dict) -> None:
    w = max([len(s) for s in stats] + [len("TOTAL")])
    print(f"{'series':<{w}}  {'videos':>6}  {'labels':>6}  {'duration':>9}")
    for series, (v, n, d) in sorted(stats.items()):
        print(f"{series:<{w}}  {v:>6}  {n:>6}  {hms(d):>9}")
    tv, tn, td = (sum(c) for c in zip(*stats.values())) if stats else (0, 0, 0.0)
    print("-" * (w + 27))
    print(f"{'TOTAL':<{w}}  {tv:>6}  {tn:>6}  {hms(td):>9}")

    breakdown("emotion", per_label)
    breakdown("gender", per_gender)
    breakdown("age", per_age)


# ---------- HTML dashboard ----------
CSS = """
:root{--bg:#f7f7f8;--card:#fff;--fg:#1a1a1e;--mut:#6b6b76;--line:#e3e3e8;--bar:#4f7fff;--barbg:#ececf2}
:root[data-theme=dark]{--bg:#16161a;--card:#202027;--fg:#ececf1;--mut:#9a9aa6;--line:#31313b;--bar:#6f97ff;--barbg:#2a2a33}
@media(prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#16161a;--card:#202027;--fg:#ececf1;--mut:#9a9aa6;--line:#31313b;--bar:#6f97ff;--barbg:#2a2a33}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,'Segoe UI',sans-serif}
.wrap{max-width:960px;margin:0 auto;padding:32px 20px 64px}
h1{font-size:22px;margin:0 0 4px}
.sub{color:var(--mut);font-size:13px;margin-bottom:24px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:14px;margin-bottom:32px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.card .n{font-size:28px;font-weight:650;letter-spacing:-.5px}
.card .l{color:var(--mut);font-size:13px;margin-top:2px}
section{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin-bottom:20px}
h2{font-size:15px;margin:0 0 14px;font-weight:600}
.scroll{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:14px;min-width:360px}
th,td{text-align:left;padding:7px 10px;border-bottom:1px solid var(--line);white-space:nowrap}
th{color:var(--mut);font-weight:500;font-size:12px;text-transform:uppercase;letter-spacing:.04em}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}
tr:last-child td{border-bottom:none}
tr.total td{font-weight:650;border-top:2px solid var(--line)}
.bar{position:relative;background:var(--barbg);border-radius:5px;height:22px;min-width:120px}
.bar>span{position:absolute;inset:0;background:var(--bar);border-radius:5px}
.bar>b{position:absolute;left:8px;top:0;line-height:22px;font-weight:500;font-size:12px;color:var(--fg)}
""".strip()


def _rows(d: dict[str, list]) -> str:
    """Sorted <tr> rows for a breakdown, most-frequent first, with an audios bar."""
    items = sorted(d.items(), key=lambda kv: -kv[1][0])
    mx = max((n for _, (n, _) in items), default=1) or 1
    out = []
    for k, (n, dur) in items:
        pct = round(n / mx * 100)
        out.append(
            f"<tr><td>{html.escape(k)}</td>"
            f'<td class="num">{n}</td>'
            f'<td><div class="bar"><span style="width:{pct}%"></span>'
            f"<b>{hms(dur)}</b></div></td></tr>"
        )
    return "\n".join(out)


def _section(title: str, d: dict[str, list]) -> str:
    """A breakdown <section> (title + audios/duration table with bars)."""
    return (
        f'<section><h2>{title}</h2><div class="scroll"><table>'
        f'<tr><th>{title}</th><th class="num">audios</th><th>duration</th></tr>'
        f"{_rows(d)}</table></div></section>"
    )


def render_html(root: Path, stats: dict, per_label: dict, per_gender: dict, per_age: dict) -> str:
    tv, tn, td = (sum(c) for c in zip(*stats.values())) if stats else (0, 0, 0.0)
    series_rows = "\n".join(
        f"<tr><td>{html.escape(s)}</td>"
        f'<td class="num">{v}</td><td class="num">{n}</td>'
        f'<td class="num">{hms(d)}</td></tr>'
        for s, (v, n, d) in sorted(stats.items())
    )
    when = datetime.now().strftime("%Y-%m-%d %H:%M")
    return f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ViEmoSpeech — tiến độ gán nhãn</title>
<style>{CSS}</style></head><body><div class="wrap">
<h1>ViEmoSpeech — tiến độ gán nhãn</h1>
<div class="sub">{html.escape(str(root))} · tạo lúc {when}</div>
<div class="cards">
  <div class="card"><div class="n">{tv}</div><div class="l">videos</div></div>
  <div class="card"><div class="n">{tn}</div><div class="l">labels</div></div>
  <div class="card"><div class="n">{hms(td)}</div><div class="l">duration đã gán</div></div>
</div>
<section><h2>Theo series</h2><div class="scroll"><table>
<tr><th>series</th><th class="num">videos</th><th class="num">labels</th><th class="num">duration</th></tr>
{series_rows}
<tr class="total"><td>TOTAL</td><td class="num">{tv}</td><td class="num">{tn}</td><td class="num">{hms(td)}</td></tr>
</table></div></section>
{_section("emotion", per_label)}
{_section("gender", per_gender)}
{_section("age", per_age)}
</div></body></html>"""


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default="data/vietnamese-ser/episodes")
    ap.add_argument(
        "--html", metavar="PATH", help="write a dashboard HTML file instead of printing"
    )
    args = ap.parse_args()

    root = (ROOT / args.root).resolve() if not Path(args.root).is_absolute() else Path(args.root)
    if not root.is_dir():
        raise SystemExit(f"--root is not a directory: {root}")

    stats, per_label, per_gender, per_age = collect(root)

    if args.html:
        out = Path(args.html)
        out.write_text(render_html(root, stats, per_label, per_gender, per_age), encoding="utf-8")
        print(f"wrote {out.resolve()}")
    else:
        print_text(stats, per_label, per_gender, per_age)


if __name__ == "__main__":
    main()
