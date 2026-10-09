from pathlib import Path

# python-pptx is resolved from the user environment
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE, MSO_CONNECTOR
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parents[1]


OUT = ROOT / "docs" / "ViEmoSpeech-progress-presentation-2026-07-29.pptx"

NAVY = RGBColor(14, 26, 43)
BLUE = RGBColor(42, 111, 219)
CYAN = RGBColor(55, 195, 205)
GREEN = RGBColor(42, 170, 112)
ORANGE = RGBColor(240, 153, 57)
RED = RGBColor(218, 75, 75)
INK = RGBColor(29, 39, 53)
MUTED = RGBColor(95, 110, 127)
PALE = RGBColor(242, 246, 250)
WHITE = RGBColor(255, 255, 255)
LIGHT = RGBColor(218, 228, 238)


def box(slide, x, y, w, h, fill=WHITE, radius=True, line=None):
    shape = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.ROUNDED_RECTANGLE if radius else MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        Inches(x),
        Inches(y),
        Inches(w),
        Inches(h),
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill
    shape.line.color.rgb = line or fill
    return shape


def text(
    slide,
    x,
    y,
    w,
    h,
    value,
    size=20,
    color=INK,
    bold=False,
    align=PP_ALIGN.LEFT,
    valign=MSO_ANCHOR.TOP,
    font="Aptos",
    margin=0.05,
):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(margin)
    tf.margin_top = tf.margin_bottom = Inches(margin)
    tf.vertical_anchor = valign
    p = tf.paragraphs[0]
    p.alignment = align
    r = p.add_run()
    r.text = value
    r.font.name = font
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.color.rgb = color
    return tb


def rich(slide, x, y, w, h, lines, size=18, color=INK, bullet=False):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.clear()
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.08)
    for i, item in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = item
        p.font.name = "Aptos"
        p.font.size = Pt(size)
        p.font.color.rgb = color
        p.space_after = Pt(9)
        p.level = 0
        if bullet:
            p.text = "•  " + p.text
    return tb


def base(prs, title, kicker=None, dark=False):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    bg = slide.background.fill
    bg.solid()
    bg.fore_color.rgb = NAVY if dark else WHITE
    if kicker:
        text(slide, 0.65, 0.32, 7.8, 0.3, kicker.upper(), 10, CYAN if dark else BLUE, True)
    text(slide, 0.65, 0.68, 12.0, 0.6, title, 27, WHITE if dark else NAVY, True)
    if not dark:
        box(slide, 0.65, 1.34, 12.0, 0.025, BLUE, False)
    return slide


def footer(slide, n, source="Progress report · 29 Jul 2026"):
    text(slide, 0.68, 7.15, 10.8, 0.18, source, 8, MUTED)
    text(slide, 12.0, 7.12, 0.65, 0.2, f"{n:02d}", 9, MUTED, True, PP_ALIGN.RIGHT)


def metric(slide, x, y, w, value, label, color=BLUE):
    box(slide, x, y, w, 1.25, PALE)
    text(slide, x + 0.18, y + 0.15, w - 0.36, 0.5, value, 28, color, True)
    text(slide, x + 0.18, y + 0.72, w - 0.36, 0.35, label, 11, MUTED)


def bar(slide, x, y, w, value, maxv, label, value_label, color=BLUE):
    text(slide, x, y, 2.2, 0.28, label, 11, INK, True)
    box(slide, x + 2.2, y + 0.02, w - 3.2, 0.22, LIGHT, False)
    box(slide, x + 2.2, y + 0.02, (w - 3.2) * value / maxv, 0.22, color, False)
    text(slide, x + w - 0.9, y - 0.02, 0.9, 0.28, value_label, 11, color, True, PP_ALIGN.RIGHT)


prs = Presentation()
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# 1 — Title
s = base(prs, "ViEmoSpeech", dark=True)
text(
    s,
    0.68,
    1.55,
    8.7,
    0.9,
    "Building a Vietnamese Speech Emotion Corpus\nand Testing the Tone × Emotion Hypothesis",
    28,
    WHITE,
    True,
)
box(s, 9.65, 1.45, 2.8, 3.8, RGBColor(25, 45, 70))
text(s, 10.05, 1.95, 2.0, 0.4, "VOICE", 11, CYAN, True, PP_ALIGN.CENTER)
for i, h in enumerate([0.35, 0.8, 1.4, 0.65, 1.75, 0.95, 0.45, 0.85, 0.3]):
    box(s, 10.12 + i * 0.21, 3.8 - h / 2, 0.10, h, CYAN if i % 2 else BLUE, False)
text(s, 0.72, 5.65, 7.5, 0.35, "Progress update · 3 July – 1 August 2026", 15, LIGHT)
text(s, 0.72, 6.12, 7.5, 0.3, "Nguyễn Duy Tấn Phát (dev.phatdt)", 12, WHITE, True)
text(
    s,
    0.72,
    6.78,
    11.8,
    0.25,
    "All reported measurements are traceable to repository artifacts.",
    9,
    MUTED,
)

# 2 — Why
s = base(prs, "Why Vietnamese SER needs a new starting point", "Problem")
for x, num, head, body, col in [
    (
        0.7,
        "01",
        "Data gap",
        "No Vietnamese SER corpus is simultaneously accessible, natural-speech, and clearly licensed.",
        BLUE,
    ),
    (
        4.5,
        "02",
        "Scientific gap",
        "Vietnamese lexical tone and emotion compete for the same acoustic channel.",
        CYAN,
    ),
    (
        8.3,
        "03",
        "Practical impact",
        "A reliable corpus enables customer care, virtual assistants, and mental-health screening research.",
        ORANGE,
    ),
]:
    box(s, x, 1.75, 3.55, 3.85, PALE)
    text(s, x + 0.22, 2.0, 0.7, 0.5, num, 24, col, True)
    text(s, x + 0.22, 2.72, 3.0, 0.45, head, 18, NAVY, True)
    text(s, x + 0.22, 3.42, 3.0, 1.3, body, 15, INK)
text(
    s,
    0.75,
    6.15,
    11.8,
    0.55,
    "ViEmoSpeech creates the resource first—then uses it to test a language-specific hypothesis.",
    20,
    NAVY,
    True,
    PP_ALIGN.CENTER,
)
footer(s, 2)

# 3 — Hypothesis
s = base(prs, "The central hypothesis is measurable", "Research idea")
box(s, 0.8, 1.72, 3.3, 3.6, PALE)
box(s, 5.0, 1.72, 3.3, 3.6, PALE)
box(s, 9.2, 1.72, 3.3, 3.6, PALE)
text(s, 1.05, 2.05, 2.8, 0.45, "LEXICAL TONE", 14, BLUE, True, PP_ALIGN.CENTER)
text(
    s, 1.1, 2.9, 2.7, 0.6, "Pitch + phonation\nencode word meaning", 20, NAVY, True, PP_ALIGN.CENTER
)
text(s, 5.25, 2.05, 2.8, 0.45, "EMOTION", 14, ORANGE, True, PP_ALIGN.CENTER)
text(
    s, 5.3, 2.9, 2.7, 0.6, "The same cues encode\naffective state", 20, NAVY, True, PP_ALIGN.CENTER
)
text(s, 9.45, 2.05, 2.8, 0.45, "PREDICTION", 14, GREEN, True, PP_ALIGN.CENTER)
text(
    s,
    9.5,
    2.75,
    2.7,
    0.95,
    "Text/semantics must carry more weight in Vietnamese SER",
    19,
    NAVY,
    True,
    PP_ALIGN.CENTER,
)
for x1, x2 in [(4.1, 5.0), (8.3, 9.2)]:
    ln = s.shapes.add_connector(
        MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(3.5), Inches(x2), Inches(3.5)
    )
    ln.line.color.rgb = MUTED
    ln.line.width = Pt(2)
text(
    s,
    0.9,
    5.85,
    11.6,
    0.55,
    "Early signal: audio-only CCC ≈ 0.09, while strong-emotion ASR errors often alter lexical tones.",
    19,
    RED,
    True,
    PP_ALIGN.CENTER,
)
footer(s, 3)

# 4 — products and constraints
s = base(prs, "Two research products, one hard constraint", "Scope")
box(s, 0.75, 1.75, 5.7, 3.95, PALE)
box(s, 6.88, 1.75, 5.7, 3.95, PALE)
text(s, 1.05, 2.05, 4.9, 0.4, "A · CORPUS PAPER", 13, BLUE, True)
text(s, 1.05, 2.65, 4.9, 0.7, "ViEmoSpeech", 25, NAVY, True)
rich(
    s,
    1.05,
    3.45,
    4.9,
    1.6,
    [
        "Natural dialogue from Vietnamese TV drama",
        "7 emotions + valence/arousal + distress flag",
        "Tone annotation and clear CC-BY artifact license",
    ],
    14,
    INK,
    True,
)
text(s, 7.18, 2.05, 4.9, 0.4, "B · METHOD PAPER", 13, CYAN, True)
text(s, 7.18, 2.65, 4.9, 0.7, "Bimodal tone × emotion", 25, NAVY, True)
rich(
    s,
    7.18,
    3.45,
    4.9,
    1.6,
    [
        "Audio + text modeling",
        "Speaker-disjoint evaluation",
        "Recall floor for distress (non-clinical proxy)",
    ],
    14,
    INK,
    True,
)
box(s, 1.75, 6.05, 9.8, 0.55, NAVY)
text(
    s,
    1.95,
    6.16,
    9.4,
    0.28,
    "Copyright constraint: release features + timestamps + labels—never full audio or transcripts.",
    13,
    WHITE,
    True,
    PP_ALIGN.CENTER,
)
footer(s, 4)

# 5 pipeline
s = base(prs, "The extraction pipeline now runs end to end", "Completed")
steps = [
    ("TV episode", "35.6 min"),
    ("Music separation", "Demucs"),
    ("Voice activity", "11.9 min · 33%"),
    ("Turn splitting", "175 clips · 10.3 min"),
    ("ASR + alignment", "87.2 similarity"),
]
for i, (a, b) in enumerate(steps):
    x = 0.55 + i * 2.55
    box(s, x, 2.15, 2.15, 1.55, PALE)
    text(s, x + 0.15, 2.42, 1.85, 0.4, a, 14, NAVY, True, PP_ALIGN.CENTER)
    text(s, x + 0.15, 3.05, 1.85, 0.3, b, 11, BLUE if i else MUTED, True, PP_ALIGN.CENTER)
    if i < 4:
        text(s, x + 2.18, 2.73, 0.35, 0.3, "→", 20, MUTED, True, PP_ALIGN.CENTER)
metric(s, 0.85, 4.45, 3.65, "33%", "usable clean speech yield", GREEN)
metric(s, 4.85, 4.45, 3.65, "100%", "single-speaker after diarization", BLUE)
metric(s, 8.85, 4.45, 3.65, "11.4%", "diarization blind spot caught by text filter", ORANGE)
footer(s, 5, "Measured on episode 01 · 35.6 minutes")

# 6 corpus
s = base(prs, "The corpus is extracted; annotation is the limiting factor", "Corpus status")
metric(s, 0.75, 1.7, 2.75, "3,775", "clips extracted", BLUE)
metric(s, 3.75, 1.7, 2.75, "≈10 h", "single-speaker speech", CYAN)
metric(s, 6.75, 1.7, 2.75, "926", "emotion-labeled clips", GREEN)
metric(s, 9.75, 1.7, 2.75, "445", "rejected clips", ORANGE)
text(s, 0.8, 3.45, 4.0, 0.35, "Current corpus coverage", 15, NAVY, True)
box(s, 0.8, 4.05, 11.65, 0.45, LIGHT, False)
box(s, 0.8, 4.05, 11.65 * 0.245, 0.45, GREEN, False)
box(s, 0.8 + 11.65 * 0.245, 4.05, 11.65 * 0.118, 0.45, ORANGE, False)
text(s, 0.8, 4.66, 3.0, 0.3, "24.5% labeled", 12, GREEN, True)
text(s, 3.7, 4.66, 3.0, 0.3, "11.8% rejected", 12, ORANGE, True)
text(s, 7.0, 4.66, 4.9, 0.3, "63.7% not yet reviewed", 12, MUTED, True, PP_ALIGN.RIGHT)
box(s, 0.85, 5.52, 11.55, 0.75, PALE)
text(
    s,
    1.05,
    5.72,
    11.1,
    0.35,
    "Rare-class warning: surprise had only 40 examples in the 29 July snapshot.",
    16,
    RED,
    True,
    PP_ALIGN.CENTER,
)
footer(s, 6, "Current status measured 1 Aug 2026; class distribution snapshot 29 Jul 2026")

# 7 baseline
s = base(prs, "Honest evaluation reveals a meaningful generalization gap", "Pilot baseline")
text(s, 0.78, 1.65, 5.4, 0.3, "7-class emotion macro-F1", 15, NAVY, True)
bar(s, 0.78, 2.25, 6.0, 0.314, 0.4, "GroupKFold (optimistic)", "0.314", BLUE)
bar(s, 0.78, 3.05, 6.0, 0.249, 0.4, "Cross-series (reported)", "0.249", GREEN)
bar(s, 0.78, 3.85, 6.0, 0.04, 0.4, "Random level", "≈0.04", MUTED)
box(s, 7.25, 1.72, 5.25, 3.05, PALE)
text(s, 7.58, 2.0, 4.6, 0.35, "What the gap means", 15, ORANGE, True)
text(s, 7.58, 2.7, 4.5, 0.65, "Δ ≈ 0.065", 30, NAVY, True)
text(
    s,
    7.58,
    3.45,
    4.35,
    0.85,
    "Repeated actors inflate performance when train and test share a series.",
    15,
    INK,
)
box(s, 0.78, 5.25, 11.72, 0.85, NAVY)
text(
    s,
    1.05,
    5.45,
    11.15,
    0.42,
    "0.249 is well above chance—but remains a pilot until human–human reliability is measured.",
    17,
    WHITE,
    True,
    PP_ALIGN.CENTER,
)
footer(s, 7, "WavLM-Large frozen + linear probe · 750 human-labeled clean clips")

# 8 CCC
s = base(prs, "Weak dimensional prediction supports the bimodal direction", "Key evidence")
metric(s, 0.85, 1.75, 3.25, "0.091", "CCC valence · cross-series", RED)
metric(s, 4.15, 1.75, 3.25, "0.087", "CCC arousal · cross-series", RED)
metric(s, 7.45, 1.75, 3.25, "1.000", "perfect agreement", MUTED)
text(
    s,
    0.85,
    3.5,
    11.4,
    0.7,
    "Audio alone is close to the floor for valence and arousal.",
    28,
    NAVY,
    True,
    PP_ALIGN.CENTER,
)
text(
    s,
    1.35,
    4.52,
    10.4,
    0.7,
    "This “bad” result is useful: it quantitatively motivates the text branch and the tone × emotion study.",
    18,
    INK,
    align=PP_ALIGN.CENTER,
)
box(s, 2.05, 5.72, 9.2, 0.58, RGBColor(234, 244, 255))
text(
    s,
    2.25,
    5.86,
    8.8,
    0.3,
    "Next test: does bimodal fusion outperform audio-only under speaker-disjoint splits?",
    14,
    BLUE,
    True,
    PP_ALIGN.CENTER,
)
footer(s, 8)

# 9 blocker
s = base(prs, "The critical path is human–human reliability", "Current blocker")
items = [
    ("Tools", "Complete", "Consent, blind UI, access control, audit logs", GREEN),
    ("Protocol", "Complete", "Pre-registered QC, qualification rounds, gold-set workflow", GREEN),
    ("Statistics", "Complete", "Fleiss’ κ + Krippendorff’s α, unit-checked", GREEN),
    ("People", "Blocked", "3 real annotators + ~250 fully overlapping clips", RED),
]
for i, (a, b, c, col) in enumerate(items):
    y = 1.65 + i * 1.12
    box(s, 0.8, y, 11.7, 0.87, PALE)
    text(s, 1.05, y + 0.18, 1.5, 0.32, a, 14, NAVY, True)
    text(s, 2.75, y + 0.18, 1.5, 0.32, b, 13, col, True)
    text(s, 4.25, y + 0.18, 7.8, 0.36, c, 13, INK)
box(s, 1.65, 6.32, 10.0, 0.55, NAVY)
text(
    s,
    1.9,
    6.44,
    9.5,
    0.3,
    "Without human–human κ, the dataset paper is not publication-ready.",
    15,
    WHITE,
    True,
    PP_ALIGN.CENTER,
)
footer(s, 9)

# 10 decisions and next steps
s = base(prs, "Three decisions unlock the next phase", "Next steps")
for i, (num, title, body, col) in enumerate(
    [
        (
            "1",
            "Resolve annotation hosting",
            "Company policy blocks the original local-tunnel plan; cloud hosting requires a new legal decision.",
            RED,
        ),
        (
            "2",
            "Recruit and run reliability study",
            "Finalize the gold set, qualify 3 annotators, then label ~250 overlapping clips.",
            ORANGE,
        ),
        (
            "3",
            "Freeze labels and benchmark",
            "Run six methods, preserve cross-series splits, and begin the two papers.",
            GREEN,
        ),
    ]
):
    x = 0.72 + i * 4.18
    box(s, x, 1.75, 3.78, 4.25, PALE)
    text(s, x + 0.25, 2.02, 0.55, 0.55, num, 25, col, True, PP_ALIGN.CENTER)
    text(s, x + 0.25, 2.8, 3.25, 0.8, title, 19, NAVY, True)
    text(s, x + 0.25, 3.85, 3.2, 1.3, body, 14, INK)
text(
    s,
    0.75,
    6.42,
    11.8,
    0.4,
    "Target outcome: a traceable Vietnamese SER corpus and the first direct test of lexical-tone interference in SER.",
    17,
    NAVY,
    True,
    PP_ALIGN.CENTER,
)
footer(s, 10)

prs.core_properties.title = "ViEmoSpeech Progress Presentation"
prs.core_properties.subject = (
    "Vietnamese Speech Emotion Recognition corpus and tone × emotion research"
)
prs.core_properties.author = "Nguyễn Duy Tấn Phát"
prs.core_properties.comments = "Generated from docs/progress-report-2026-07-29.md"
OUT.parent.mkdir(parents=True, exist_ok=True)
prs.save(OUT)
print(OUT)
