"""Mint annotator tokens, build their queues, and print a ready-to-send invite (change 011).

Replaces the fiddly multi-step dance in RUNBOOK.md §1-2 with one command. Safe to
re-run: an existing annotator keeps their token (so a link already sent keeps working),
and a queue that already has answers is never rebuilt.

    # 1. dry run — see what would happen
    .venv-vnser/Scripts/python.exe scripts/vietnamese-ser/invite_annotators.py \
        --annotators ann01,ann02 --dry-run

    # 2. for real, once ngrok is up and you know the URL
    .venv-vnser/Scripts/python.exe scripts/vietnamese-ser/invite_annotators.py \
        --annotators ann01,ann02 --n 250 \
        --gold docs/spec/changes/011-online-multi-annotator/gold-set.txt \
        --base-url https://<subdomain>.ngrok.app

`tokens.json` lands in the data root: gitignored, never committed (ADR-005 #1).
Keep the mapping from ann01 -> a real person OUTSIDE this repo; the released corpus
carries only the pseudonym.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "tools" / "labeler"))
import auth  # noqa: E402
import store  # noqa: E402

INVITE = """\
--- gửi cho {ann} ---------------------------------------------------

Chào anh/chị,

Nhờ anh/chị giúp gán nhãn cảm xúc cho ViEmoSpeech — bộ dữ liệu giọng nói cảm xúc
tiếng Việt đầu tiên. Việc cụ thể: nghe các đoạn thoại ngắn (2–10 giây) cắt từ phim
truyền hình, rồi chọn cảm xúc nghe thấy + 2 thang điểm. Không cắt, không sửa gì cả.

  Link riêng của anh/chị (đừng chia sẻ cho ai):
  {link}

  Số clip: {n}    ·    Ước tính: {hours}
  Không có deadline gấp — làm tới đâu hay tới đó, đóng tab rồi mở lại là tiếp đúng chỗ.

Trước khi bắt đầu, đọc 2 tài liệu đính kèm:
  1. Hướng dẫn gán nhãn  (annotator-guideline.vi.md)
  2. Bản đồng ý tham gia + thoả thuận sử dụng dữ liệu  (consent.vi.md)

Mở link lần đầu sẽ có màn xác nhận đồng ý — đọc kỹ rồi tick.

Ba điều quan trọng:
  · Chọn cảm xúc anh/chị THẬT SỰ nghe thấy. Không có đáp án đúng giấu sẵn.
  · ĐỪNG bàn với người khác đang cùng gán nhãn — làm thế là hỏng phép đo.
  · Clip nào không nghe được thì bấm "bỏ qua", đừng đoán bừa.

Nội dung phim có cảnh cãi vã, quát mắng, khóc, hoảng sợ. Đều là diễn xuất, nhưng nghe
nhiều vẫn mệt — nghỉ giải lao, và dừng bất cứ lúc nào nếu thấy không thoải mái.

Vướng gì nhắn em/mình nhé.
---------------------------------------------------------------------
"""


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="mint tokens + queues + invite text")
    ap.add_argument("--root", default="data/vietnamese-ser/episodes")
    ap.add_argument("--annotators", required=True, help="comma-separated ids, e.g. ann01,ann02")
    ap.add_argument("--n", type=int, default=250, help="reliability subset size")
    ap.add_argument("--gold", default=None, help="gold-set.txt")
    ap.add_argument("--base-url", default="https://<ngrok-url>", help="public tunnel URL")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    root = Path(a.root).resolve()
    if not root.is_dir():
        raise SystemExit(f"--root is not a directory: {root}")
    anns = [x.strip() for x in a.annotators.split(",") if x.strip()]

    # 1. tokens — existing ones are preserved so links already sent keep working
    tpath = root / "tokens.json"
    tokens: dict[str, dict] = (
        json.loads(tpath.read_text(encoding="utf-8")) if tpath.is_file() else {}
    )
    by_id = {v["id"]: k for k, v in tokens.items()}
    minted = []
    for ann in anns:
        if ann not in by_id:
            tok = auth.mint()
            tokens[tok] = {"id": ann, "role": "annotator"}
            by_id[ann] = tok
            minted.append(ann)
    if not a.dry_run:
        tpath.write_text(json.dumps(tokens, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        f"tokens: {len(tokens)} total, {len(minted)} new ({', '.join(minted) or 'none'}) -> {tpath}"
    )

    # 2. queues (delegated — one implementation of the sampling protocol, not two)
    cmd = [
        sys.executable,
        str(REPO / "scripts" / "vietnamese-ser" / "build_assignments.py"),
        "--root",
        str(root),
        "--annotators",
        ",".join(anns),
        "--n",
        str(a.n),
    ]
    if a.gold:
        cmd += ["--gold", a.gold]
    if a.dry_run:
        cmd.append("--dry-run")
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    print(r.stdout.strip() or r.stderr.strip())
    if r.returncode:
        print("\n(queue build failed — tokens above are still valid)", file=sys.stderr)

    # 3. invite text
    store.set_root(root)
    store.load()
    print()
    for ann in anns:
        n = store.progress(ann)["total"] if not a.dry_run else a.n
        hours = f"{n / 60:.0f}–{n / 30:.0f} giờ" if n else "—"
        print(
            INVITE.format(
                ann=ann, link=f"{a.base_url}/rate.html?t={by_id[ann]}", n=n or a.n, hours=hours
            )
        )

    if a.dry_run:
        print("(dry run — tokens.json and queues NOT written)")
    if a.base_url.startswith("https://<"):
        print("WARNING: --base-url not set, links above are placeholders", file=sys.stderr)


if __name__ == "__main__":
    main()
