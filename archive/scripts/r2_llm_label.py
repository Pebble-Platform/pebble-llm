"""LLM-label scraped r/SuicideWatch author-sequences on the paper's 4-level C-SSRS scale.

Mirrors the labeling half of Yang et al. (arXiv:2510.20085): an LLM reads a user's post
sequence and assigns a suicide-risk level. We label DIRECTLY on the paper's 4-level ontology
(no lossy 0-6 remap) and keep a confidence for quality-filtering (the paper discarded
low-agreement labels; with a single model we threshold on confidence instead).

Provider-agnostic. Configure with env vars:
    LLM_PROVIDER = anthropic | openai | gemini | azure      (default: anthropic)
    LLM_MODEL    = e.g. claude-sonnet-4-6 / gpt-4o-mini / gemini-2.5-flash / gpt-5.4-mini
    ANTHROPIC_API_KEY / OPENAI_API_KEY / GEMINI_API_KEY     (for the raw-HTTP providers)
    AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_API_KEY            (for azure; uses the openai SDK)
Put them in .env (gitignored); this script also reads a local .env if present.

Usage:
    .venv-voice/bin/python scripts/r2_llm_label.py --limit 20        # cheap test batch
    .venv-voice/bin/python scripts/r2_llm_label.py                   # full run (resumable)
"""
from __future__ import annotations

import argparse
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

SRC = Path("data/finetuning-message/external/scraped-suicidewatch/sequences.jsonl")
OUT = Path("data/finetuning-message/external/scraped-suicidewatch/labeled.jsonl")
LABEL_NAMES = ["Indicator", "Ideation", "Behavior", "Attempt"]

PROMPT = """You are a clinical annotator applying the Columbia-Suicide Severity Rating Scale (C-SSRS) \
to a Reddit user's posts. Assign ONE overall suicide-risk level for this user from their posts:

0 = Indicator: warning signs / distress but NO wish to die (incl. expressing concern about someone else).
1 = Ideation: has thoughts or a wish to die, but NO plan.
2 = Behavior: preparation/planning, or self-harm without clear intent to die.
3 = Attempt: has made a suicide attempt (past or present).
-1 = Off-topic: NOT about the author's own (or another person's) suicide risk or mental-health distress
     at all (e.g. small talk, supportive chit-chat, unrelated topics). Use this to discard noise.

Judge the HIGHEST level clearly supported by the posts. If evidence is ambiguous, lower your confidence.

User's posts (chronological):
{posts}

Respond with ONLY a JSON object, no other text:
{{"label": <-1, 0, 1, 2, or 3>, "confidence": <0.0-1.0>, "reason": "<one short sentence>"}}"""


def load_dotenv() -> None:
    p = Path(".env")
    if not p.exists():
        return
    for line in p.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def build_prompt(seq: dict) -> str:
    posts = "\n---\n".join(p["text"] for p in seq["posts"])
    return PROMPT.format(posts=posts[:8000])


def call_anthropic(prompt: str, model: str, key: str) -> str:
    body = json.dumps({"model": model, "max_tokens": 200,
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    req = Request("https://api.anthropic.com/v1/messages", data=body,
                  headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                           "content-type": "application/json"})
    with urlopen(req, timeout=60) as r:
        return json.loads(r.read())["content"][0]["text"]


def call_openai(prompt: str, model: str, key: str) -> str:
    body = json.dumps({"model": model, "max_tokens": 200,
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    req = Request("https://api.openai.com/v1/chat/completions", data=body,
                  headers={"Authorization": f"Bearer {key}", "content-type": "application/json"})
    with urlopen(req, timeout=60) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"]


def call_gemini(prompt: str, model: str, key: str) -> str:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = Request(url, data=body, headers={"content-type": "application/json"})
    with urlopen(req, timeout=60) as r:
        return json.loads(r.read())["candidates"][0]["content"]["parts"][0]["text"]


_AZURE_CLIENT = None
def call_azure(prompt: str, model: str, key: str) -> str:
    """Azure OpenAI (OpenAI-SDK-compatible) via the /responses API."""
    global _AZURE_CLIENT
    if _AZURE_CLIENT is None:
        from openai import OpenAI
        _AZURE_CLIENT = OpenAI(base_url=os.environ["AZURE_OPENAI_ENDPOINT"], api_key=key)
    r = _AZURE_CLIENT.responses.create(model=model, input=prompt)
    return r.output_text


CALLERS = {"anthropic": call_anthropic, "openai": call_openai, "gemini": call_gemini, "azure": call_azure}
KEY_VAR = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY",
           "gemini": "GEMINI_API_KEY", "azure": "AZURE_OPENAI_API_KEY"}
DEFAULT_MODEL = {"anthropic": "claude-sonnet-4-6", "openai": "gpt-4o-mini",
                 "gemini": "gemini-2.5-flash", "azure": "gpt-5.4-mini"}


def parse(text: str) -> dict | None:
    s, e = text.find("{"), text.rfind("}")
    if s < 0 or e < 0:
        return None
    try:
        obj = json.loads(text[s:e + 1])
        lab = int(obj["label"])
        if lab not in (-1, 0, 1, 2, 3):     # -1 = off-topic (kept in jsonl, dropped by the builder)
            return None
        return {"label": lab, "confidence": float(obj.get("confidence", 0.0)),
                "reason": str(obj.get("reason", ""))[:200]}
    except (json.JSONDecodeError, KeyError, ValueError, TypeError):
        return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="0 = all")
    ap.add_argument("--workers", type=int, default=8, help="concurrent requests")
    args = ap.parse_args()

    load_dotenv()
    provider = os.environ.get("LLM_PROVIDER", "anthropic").lower()
    if provider not in CALLERS:
        raise SystemExit(f"LLM_PROVIDER must be one of {list(CALLERS)}")
    model = os.environ.get("LLM_MODEL", DEFAULT_MODEL[provider])
    key = os.environ.get(KEY_VAR[provider], "")
    if not key:
        raise SystemExit(f"{KEY_VAR[provider]} not set (put it in .env)")
    call = CALLERS[provider]

    seqs = [json.loads(l) for l in SRC.read_text().splitlines() if l.strip()]
    done = set()
    if OUT.exists():
        done = {json.loads(l)["author"] for l in OUT.read_text().splitlines() if l.strip()}
    todo = [s for s in seqs if s["author"] not in done]
    if args.limit:
        todo = todo[:args.limit]
    print(f">>> provider={provider} model={model} | {len(seqs)} seqs, {len(done)} done, "
          f"labeling {len(todo)}", flush=True)

    lock = threading.Lock()
    counts = {"ok": 0, "err": 0, "filtered": 0}
    f = OUT.open("a")

    def work(seq: dict) -> None:
        try:
            raw = call(build_prompt(seq), model, key)
        except Exception as e:                       # api / content-filter / network
            with lock:
                counts["filtered" if "content_filter" in str(e) else "err"] += 1
            return
        parsed = parse(raw)
        with lock:
            if not parsed:
                counts["err"] += 1
            else:
                f.write(json.dumps({"author": seq["author"], "posts": seq["posts"], **parsed}) + "\n")
                f.flush()
                counts["ok"] += 1
            n = sum(counts.values())
            if n % 50 == 0:
                print(f"  [{n}/{len(todo)}] ok={counts['ok']} filtered={counts['filtered']} "
                      f"err={counts['err']}", flush=True)

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(as_completed(ex.submit(work, s) for s in todo))
    f.close()
    print(f">>> done: labeled {counts['ok']}, content-filtered {counts['filtered']}, "
          f"errors {counts['err']} → {OUT}", flush=True)


if __name__ == "__main__":
    main()
