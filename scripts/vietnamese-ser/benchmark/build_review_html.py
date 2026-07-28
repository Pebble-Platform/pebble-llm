"""Generate a reviewable HTML set for the papers the benchmark-survey is based on.

One self-contained HTML per paper (its deep-read analysis, rendered) + an index page
that links them, grouped by their role in the survey. Local files, relative-linked —
open `docs/survey-review/index.html` in a browser and click through.

Provenance: derived from the committed deep-read analyses in docs/papers/**. Rerun to
regenerate. Usage:  python scripts/vietnamese-ser/benchmark/build_review_html.py
"""

from __future__ import annotations

from pathlib import Path

import markdown

REPO = Path(__file__).resolve().parents[3]
PAPERS_DIR = REPO / "docs/papers"
OUT = REPO / "docs/survey-review"

GROUPS = {
    "methods": ("Phương pháp được benchmark", "#2563eb",
                "Sáu phương pháp được tái hiện và chạy trực tiếp trên corpus ViEmoSpeech."),
    "fusion": ("Fusion khảo sát (v2 tương lai)", "#7c3aed",
               "Các kiến trúc fusion được khảo sát trong survey nhưng chưa nằm trong Core-6."),
    "novelty": ("Novelty tone×emotion & tiền đề", "#dc2626",
                "Cơ sở cho luận điểm mới: thanh điệu tiếng Việt tranh kênh F0/phonation với cảm xúc."),
    "honest": ("Honest-eval, corpus & VN prior art", "#059669",
               "Cơ sở giao thức đánh giá trung thực, thiết kế corpus, và tiền lệ VN SER."),
}

# n=display label, file=output slug, src=md under docs/papers, group, role (why the survey uses it)
PAPERS = [
    # --- methods (benchmarked) ---
    ("M1", "vn10-vnemos-dynamic-cbam", "vietnamese-ser/10-vn-depression-dynamic-cbam",
     "Emotional Vietnamese Speech Depression Diagnosis (Dynamic-CBAM / VNEMOS)",
     "arXiv 2024", "methods",
     "Baseline audio-only MFCC (dòng VNEMOS) — mốc 'không-SSL' của bảng benchmark."),
    ("M2", "bi01-c2ser", "bimodal-ser/01-c2ser",
     "C²SER — Contextual Perception + Chain-of-Thought", "IEEE TASLP 2025", "methods",
     "Nguồn checkpoint emotion2vec-S (frozen) — một arm audio-only của benchmark."),
    ("M3", "bi12-msp-podcast", "bimodal-ser/12-msp-podcast-corpus",
     "The MSP-Podcast Corpus", "arXiv 2025 → IEEE TAC", "methods",
     "Công thức WavLM frozen probe + CCC cho V/A; tiền lệ corpus found-speech."),
    ("M4", "bi11-bridging-text-speech", "bimodal-ser/11-bridging-text-speech-fusion",
     "Bridging Text and Speech — RoBERTa + WavLM fusion", "J. Intelligence 2025", "methods",
     "Khớp gần nhất với PhoBERT+WavLM: nhánh text + concat fusion (method 4 & 5)."),
    ("M5", "bi17-rjcma", "bimodal-ser/17-rjcma",
     "RJCMA — Recursive Joint Cross-Modal Attention", "CVPRW 2024 (ABAW6)", "methods",
     "Nguồn objective CCC loss (L=1−ρc) cho head valence/arousal."),
    ("M6", "vn09-phowhisper-phobert", "vietnamese-ser/09-phowhisper-phobert-fusion",
     "PhoWhisper + PhoBERT pipeline (VNU) — withdrawn", "arXiv 2024 (rút)", "methods",
     "Rule-fusion baseline (§2.6) phải tự re-implement — bài gốc đã bị rút, không có số."),
    # --- fusion surveyed (future) ---
    ("F1", "bi02-abhinaya", "bimodal-ser/02-abhinaya-ser-challenge",
     "ABHINAYA — SSL + LLM fusion, imbalance-aware", "Interspeech 2025", "fusion",
     "Fusion late-vote + xử lý mất cân bằng bằng loss; ứng viên v2."),
    ("F2", "bi06-wavfusion", "bimodal-ser/06-wavfusion",
     "WavFusion — gated cross-modal attention", "MMM 2025", "fusion",
     "Gated fusion; nhắc rằng gain phụ thuộc transcript sạch (v2)."),
    ("F3", "bi07-bcaf", "bimodal-ser/07-bimodal-connection-attention",
     "Bimodal Connection Attention Fusion", "arXiv 2025", "fusion",
     "Fusion audio↔text thật + deep-supervision (audio-anchoring); ứng viên v2."),
    ("F4", "bi09-blsp-emo", "bimodal-ser/09-blsp-emo",
     "BLSP-Emo — empathetic speech-language model", "arXiv 2024", "fusion",
     "Bằng chứng 'fusion nhỏ > ALM lớn' — chứng minh hướng frozen-probe hợp lý."),
    # --- novelty / premise ---
    ("N1", "vn06-shen-lexical-tone", "vietnamese-ser/06-shen-lexical-tone-ssl",
     "Encoding of Lexical Tone in SSL Models", "NAACL 2024", "novelty",
     "Tiền đề then chốt: thanh điệu VN thiên phonation — chưa ai đo trực tiếp."),
    ("N2", "vn13-chang-tone-emotion", "vietnamese-ser/13-chang-mandarin-tone-emotion",
     "Emotional Tones of Voice Affect Mandarin Tones", "PLOS ONE 2023", "novelty",
     "Bằng chứng thực nghiệm: emotion và tone tranh riêng kênh F0 (định lượng)."),
    ("N3", "vn07-case-fas", "vietnamese-ser/07-case-tone-words-disagree",
     "When Tone and Words Disagree (CASE / FAS)", "arXiv 2026", "novelty",
     "Đối thủ kiến trúc gần nhất — cite-and-distinguish: 'tone' của họ là paralinguistic."),
    ("N4", "vn12-incongruent-slm", "vietnamese-ser/12-emotionally-incongruent-slm",
     "Emotion Recognition on Incongruent Speech (SLM)", "arXiv 2025", "novelty",
     "Khung register-dependence + công cụ đo (target/proxy, Cramér's V)."),
    # --- honest-eval / corpus / VN prior ---
    ("H1", "bi15-replication", "bimodal-ser/15-ser-15years-replication",
     "Charting 15 Years of SER Progress — Replication", "IEEE TAFFC 2026", "honest",
     "Đồng minh methodolog mạnh nhất: trần honest ~0.65 UAR, mới/to hơn ≠ tốt hơn."),
    ("H2", "bi16-databases-review", "bimodal-ser/16-ser-databases-review",
     "Databases for SER — 50+ corpora review", "Data (MDPI) 2025", "honest",
     "Bằng chứng novelty corpus: 0/52 VN, 0/52 gán lexical tone, 0/52 cat+dim+distress."),
    ("H3", "vn11-thai-ser", "vietnamese-ser/11-thai-ser-corpus",
     "THAI-SER corpus", "arXiv 2025", "honest",
     "Tiền lệ corpus ngôn ngữ thanh điệu (CC-BY-SA) + crowd-QC (Krippendorff α)."),
    ("H4", "vn08-hgr-vnser", "vietnamese-ser/08-human-guided-reasoning-vnser",
     "Human-Guided LLM Reasoning for Vietnamese SER", "arXiv 2026", "honest",
     "VN SER mới nhất — baseline/κ comparator; nêu tone-confound mà không giải."),
]

MD_EXT = ["tables", "fenced_code", "sane_lists", "toc", "attr_list"]

CSS = """
:root{--fg:#1a1a1a;--muted:#666;--bg:#fff;--card:#f7f7f8;--border:#e3e3e6;--link:#2563eb}
@media(prefers-color-scheme:dark){:root{--fg:#e8e8ea;--muted:#9a9aa2;--bg:#16171a;--card:#1e1f24;--border:#2c2e35;--link:#6ea8fe}}
*{box-sizing:border-box}
body{margin:0;font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;color:var(--fg);background:var(--bg)}
.wrap{max-width:880px;margin:0 auto;padding:0 24px 80px}
.topnav{position:sticky;top:0;background:var(--bg);border-bottom:1px solid var(--border);padding:12px 0;margin-bottom:8px}
.topnav a{color:var(--link);text-decoration:none;font-size:14px}
.pill{display:inline-block;padding:2px 10px;border-radius:999px;color:#fff;font-size:12px;font-weight:600;letter-spacing:.02em}
h1{font-size:26px;line-height:1.25;margin:18px 0 6px}
.venue{color:var(--muted);font-size:14px;margin:0 0 14px}
.role{background:var(--card);border-left:4px solid var(--accent,#2563eb);padding:12px 16px;border-radius:6px;margin:14px 0 24px;font-size:15px}
.links a{display:inline-block;margin-right:14px;color:var(--link);text-decoration:none;font-size:14px}
article :is(h2,h3){margin-top:30px;line-height:1.3;border-top:1px solid var(--border);padding-top:18px}
article h2{font-size:21px} article h3{font-size:17px;border-top:none;padding-top:6px}
article table{border-collapse:collapse;width:100%;font-size:14px;margin:14px 0;display:block;overflow-x:auto}
article th,article td{border:1px solid var(--border);padding:6px 10px;text-align:left}
article th{background:var(--card)}
article code{background:var(--card);padding:1px 5px;border-radius:4px;font-size:.9em}
article pre{background:var(--card);padding:14px;border-radius:8px;overflow-x:auto}
article blockquote{border-left:3px solid var(--border);margin:14px 0;padding:2px 16px;color:var(--muted)}
article a{color:var(--link)}
/* index */
.hero{padding:34px 0 10px} .hero p{color:var(--muted);font-size:16px;max-width:60ch}
.grp{margin-top:38px} .grp h2{font-size:18px;margin-bottom:2px;display:flex;align-items:center;gap:10px}
.grp>p{color:var(--muted);font-size:14px;margin:4px 0 16px}
.card{background:var(--card);border:1px solid var(--border);border-left:4px solid var(--accent);border-radius:8px;padding:14px 16px;margin:10px 0}
.card .t{font-weight:600;font-size:15px}.card .v{color:var(--muted);font-size:13px;margin:2px 0 6px}
.card .r{font-size:14px;margin:6px 0 8px}.card .lk a{margin-right:14px;font-size:13px;color:var(--link);text-decoration:none}
.tag{font-family:ui-monospace,monospace;font-size:12px;color:var(--muted)}
"""


def md_to_html(src_md: Path) -> str:
    text = src_md.read_text(encoding="utf-8")
    return markdown.markdown(text, extensions=MD_EXT)


def page(p) -> str:
    n, _slug, src, title, venue, group, role = p
    gname, gcolor, _ = GROUPS[group]
    src_md = PAPERS_DIR / f"{src}.md"
    body = md_to_html(src_md)
    stream = src.split("/")[0]
    base = src.split("/")[1]
    pdf = f"../papers/{stream}/pdfs/{base}.pdf"
    vi = f"../papers/{stream}/{base}.vi.md"
    return f"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{n} · {title}</title><style>{CSS}</style></head>
<body><div class="wrap">
<div class="topnav"><a href="index.html">← Tất cả bài báo (index)</a></div>
<span class="pill" style="background:{gcolor}">{n} · {gname}</span>
<h1>{title}</h1><p class="venue">{venue}</p>
<div class="role" style="--accent:{gcolor}"><b>Vai trò trong survey:</b> {role}</div>
<div class="links"><a href="{pdf}">📄 PDF gốc</a><a href="{vi}">🇻🇳 Bản dịch (.vi.md)</a>
<a href="../papers/{src}.md">📝 Nguồn phân tích (.md)</a></div>
<article>{body}</article>
</div></body></html>"""


def index() -> str:
    secs = []
    for gkey, (gname, gcolor, blurb) in GROUPS.items():
        cards = []
        for p in [x for x in PAPERS if x[5] == gkey]:
            n, slug, src, title, venue, _, role = p
            cards.append(
                f'<div class="card" style="--accent:{gcolor}">'
                f'<div class="t"><span class="tag">{n}</span> &nbsp;{title}</div>'
                f'<div class="v">{venue}</div><div class="r">{role}</div>'
                f'<div class="lk"><a href="{slug}.html">▶ Review phân tích</a>'
                f'<a href="../papers/{src}.md">.md</a></div></div>')
        secs.append(
            f'<section class="grp"><h2><span class="pill" style="background:{gcolor}">'
            f'{len([x for x in PAPERS if x[5]==gkey])}</span>{gname}</h2>'
            f'<p>{blurb}</p>{"".join(cards)}</section>')
    return f"""<!doctype html><html lang="vi"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ViEmoSpeech benchmark-survey — bài báo tham chiếu</title><style>{CSS}</style></head>
<body><div class="wrap">
<div class="hero"><span class="pill" style="background:#111">SURVEY · REVIEW</span>
<h1>ViEmoSpeech benchmark-survey — {len(PAPERS)} bài báo nền tảng</h1>
<p>Các bài báo mà bài survey/benchmark dựa vào, nhóm theo vai trò: phương pháp được
tái hiện & đo trên corpus ViEmoSpeech, các fusion được khảo sát, cơ sở novelty
tone×emotion, và nền tảng đánh giá trung thực + thiết kế corpus. Mỗi thẻ mở phân tích
deep-read (toàn văn PDF) của bài đó. Kế hoạch & số liệu:
<a href="../tasks/viemospeech-benchmark-survey.md">viemospeech-benchmark-survey.md</a>.</p></div>
{"".join(secs)}
<p class="tag" style="margin-top:40px">Sinh tự động từ docs/papers/** bằng
scripts/vietnamese-ser/benchmark/build_review_html.py</p>
</div></body></html>"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for p in PAPERS:
        (OUT / f"{p[1]}.html").write_text(page(p), encoding="utf-8")
    (OUT / "index.html").write_text(index(), encoding="utf-8")
    print(f"wrote {len(PAPERS)} paper pages + index.html to {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
