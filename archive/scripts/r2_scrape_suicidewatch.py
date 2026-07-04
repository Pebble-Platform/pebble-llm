"""Scrape r/SuicideWatch submissions (no Reddit creds) and group into per-author sequences.

Source: pullpush.io (Pushshift successor) — plain HTTP, no OAuth. Mirrors the data-collection
half of Yang et al. (arXiv:2510.20085): scrape SuicideWatch posts to be LLM-labeled on the
C-SSRS scale. Labeling is a separate step (scripts/r2_llm_label.py).

Output (gitignored): data/finetuning-message/external/scraped-suicidewatch/
  - raw_posts.jsonl   one line per kept post {id, author, created_utc, text}
  - sequences.jsonl   one line per author  {author, posts:[{text, created_utc}...]}  (<=5 most-recent)

Usage:
    .venv-voice/bin/python scripts/r2_scrape_suicidewatch.py --target-authors 9000
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

API_SUB = "https://api.pullpush.io/reddit/search/submission/"
API_COM = "https://api.pullpush.io/reddit/search/comment/"
OUT = Path("data/finetuning-message/external/scraped-suicidewatch")
SKIP_BODY = {"", "[removed]", "[deleted]"}
SKIP_AUTHOR = {"", "[deleted]", "AutoModerator", None}
SEQ_LEN = 5
MIN_CHARS = 50
MAX_CHARS = 6000


def fetch_page(before: int | None, kind: str = "submission") -> list[dict] | None:
    """Returns the data list on HTTP 200 (may be []), or None on persistent network failure
    (so the caller can distinguish a real end-of-data from a timeout streak)."""
    if kind == "comment":
        url = f"{API_COM}?subreddit=SuicideWatch&size=100&fields=id,author,created_utc,body"
    else:
        url = f"{API_SUB}?subreddit=SuicideWatch&size=100&fields=id,author,created_utc,title,selftext"
    if before:
        url += f"&before={before}"
    for attempt in range(8):
        try:
            req = Request(url, headers={"User-Agent": "pebble-research/1.0"})
            with urlopen(req, timeout=40) as r:
                return json.loads(r.read())["data"]
        except Exception as e:                          # network/SSL/RemoteDisconnected/json — all transient
            wait = min(3 * (attempt + 1), 20)
            print(f"  ! {type(e).__name__}: {e} — retry in {wait}s", flush=True)
            time.sleep(wait)
    return None


def save(by_author: dict[str, list[dict]]) -> int:
    """Write raw posts + per-author sequences (<=SEQ_LEN most-recent, chronological). Idempotent —
    called periodically as a checkpoint so a crash never loses progress."""
    with (OUT / "raw_posts.jsonl").open("w") as f:
        for posts in by_author.values():
            for r in posts:
                f.write(json.dumps(r) + "\n")
    n_seq = 0
    with (OUT / "sequences.jsonl").open("w") as f:
        for author, posts in by_author.items():
            posts = sorted(posts, key=lambda r: r["created_utc"])[-SEQ_LEN:]
            f.write(json.dumps({"author": author,
                                "posts": [{"text": r["text"], "created_utc": r["created_utc"]}
                                          for r in posts]}) + "\n")
            n_seq += 1
    return n_seq


def _load_existing() -> tuple[dict[str, list[dict]], set[str]]:
    by_author: dict[str, list[dict]] = {}
    seen: set[str] = set()
    raw = OUT / "raw_posts.jsonl"
    if raw.exists():
        for line in raw.read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            by_author.setdefault(r["author"], []).append(r)
            seen.add(r["id"])
    return by_author, seen


def usable(p: dict) -> dict | None:
    author = p.get("author")
    if author in SKIP_AUTHOR:
        return None
    if "body" in p:                                    # comment
        text = (p.get("body") or "").strip()
    else:                                              # submission
        body = (p.get("selftext") or "").strip()
        if body in SKIP_BODY:
            return None
        text = ((p.get("title") or "").strip() + "\n\n" + body).strip()
    if text in SKIP_BODY or not (MIN_CHARS <= len(text) <= MAX_CHARS):
        return None
    return {"id": p["id"], "author": author, "created_utc": int(p["created_utc"]), "text": text}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--target-authors", type=int, default=9000)
    ap.add_argument("--max-pages", type=int, default=600)
    ap.add_argument("--resume", action="store_true", help="continue from existing raw_posts.jsonl")
    ap.add_argument("--kind", choices=["submission", "comment"], default="submission")
    args = ap.parse_args()

    OUT.mkdir(parents=True, exist_ok=True)
    if args.resume:
        by_author, seen_ids = _load_existing()
        kept = sum(len(p) for p in by_author.values())
        # comment timeline is independent of the submission timeline → start newest for comments
        before = (None if args.kind == "comment"
                  else min((r["created_utc"] for posts in by_author.values() for r in posts), default=None))
        print(f">>> resume({args.kind}): {len(by_author)} authors, {kept} posts, before={before}", flush=True)
    else:
        by_author, seen_ids, before, kept = {}, set(), None, 0

    stop = "max-pages reached"
    try:
        for page in range(args.max_pages):
            data = fetch_page(before, args.kind)
            if data is None:
                stop = "persistent fetch failure"
                break
            if not data:
                stop = "genuine empty page (end of data)"
                break
            before = min(p["created_utc"] for p in data)
            for p in data:
                if p["id"] in seen_ids:
                    continue
                seen_ids.add(p["id"])
                row = usable(p)
                if row:
                    by_author.setdefault(row["author"], []).append(row)
                    kept += 1
            if page % 10 == 0:
                print(f"  page {page}: authors={len(by_author)} kept_posts={kept} "
                      f"before={before}", flush=True)
            if page % 25 == 0:                          # periodic checkpoint — survive crashes
                save(by_author)
            if len(by_author) >= args.target_authors:
                stop = f"reached {len(by_author)} authors"
                break
            time.sleep(0.7)
    except KeyboardInterrupt:
        stop = "interrupted"

    n_seq = save(by_author)
    print(f">>> stop={stop} | {len(seen_ids)} fetched | {kept} usable posts | "
          f"{n_seq} author-sequences → {OUT}", flush=True)


if __name__ == "__main__":
    main()
