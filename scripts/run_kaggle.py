"""Universal Kaggle job driver — build -> push -> poll -> fetch, for any kernel dir.

Both Pebble GPU jobs run on Kaggle with the same lifecycle, so one script drives both:
  - text  : fabiocarava/pebble-mlm-ablation-3seed  (NeoBERT MLM ablation, 3 seeds, paired delta)
  - voice : fabiocarava/pebble-voice-backbone       (WavLM-Large vs emotion2vec backbone pilot)

Examples
--------
  # run the text 3-seed model end to end (build the .ipynb, push, wait, download results)
  python scripts/run_kaggle.py --job text

  # run the voice backbone pilot
  python scripts/run_kaggle.py --job voice

  # just re-download a finished run's output (no push)
  python scripts/run_kaggle.py --job text --no-build --no-push

  # generic: any kernel dir that has kernel-metadata.json (+ optional build_ipynb.py)
  python scripts/run_kaggle.py --kernel kaggle/pebble-voice-backbone --out kaggle/pebble-voice-backbone/out

Auth: needs a Kaggle key. If ~/.kaggle/kaggle.json is missing, this builds it from the
raw token at ~/.kaggle/access_token (username defaults to 'fabiocarava'). Run with a
Python that has the `kaggle` package installed (`python -m pip install kaggle`).
"""

from __future__ import annotations

import argparse
import json
import os
import runpy
import subprocess
import sys
import time
from pathlib import Path

# Turn-key presets for the two known jobs (dir holds kernel-metadata.json + cells).
JOBS = {
    "text": "kaggle/pebble-mlm-ablation-3seed",
    "voice": "kaggle/pebble-voice-backbone",
}

KAGGLE_DIR = Path.home() / ".kaggle"
# Kaggle CLI prints Unicode logs; without this it crashes on Windows (cp1252).
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}


def ensure_auth(username: str) -> None:
    """Build kaggle.json from the raw access_token if the CLI has no credentials."""
    kj = KAGGLE_DIR / "kaggle.json"
    if kj.exists() or os.environ.get("KAGGLE_KEY"):
        return
    token = KAGGLE_DIR / "access_token"
    if not token.exists():
        sys.exit(f"No Kaggle credentials: create {kj} or put a raw key at {token}.")
    key = token.read_text().strip()
    kj.write_text(json.dumps({"username": username, "key": key}))
    try:
        kj.chmod(0o600)
    except OSError:
        pass
    print(f"[auth] wrote {kj} from access_token (user={username})")


def kaggle(*args: str, capture: bool = False) -> str:
    """Invoke the kaggle CLI via the current interpreter, UTF-8 forced."""
    cmd = [sys.executable, "-m", "kaggle", *args]
    if capture:
        r = subprocess.run(cmd, env=ENV, text=True, capture_output=True)
        return (r.stdout or "") + (r.stderr or "")
    subprocess.run(cmd, env=ENV, check=True)
    return ""


def kernel_id(kernel_dir: Path) -> str:
    meta = json.loads((kernel_dir / "kernel-metadata.json").read_text())
    return meta["id"]


def build(kernel_dir: Path) -> None:
    builder = kernel_dir / "build_ipynb.py"
    if not builder.exists():
        print(f"[build] no build_ipynb.py in {kernel_dir} — using the .ipynb as-is")
        return
    print(f"[build] running {builder}")
    runpy.run_path(str(builder), run_name="__main__")


def poll(kid: str, interval: int, timeout_min: int) -> str:
    """Poll kernels status until it leaves the running/queued state (or times out)."""
    deadline = time.time() + timeout_min * 60
    last = ""
    while time.time() < deadline:
        out = kaggle("kernels", "status", kid, capture=True).strip()
        low = out.lower()
        if out != last:
            print(f"[poll] {out}")
            last = out
        if "complete" in low:
            return "complete"
        if "error" in low or "cancel" in low:
            return "error"
        time.sleep(interval)
    return "timeout"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--job", choices=JOBS, help="preset: text (MLM 3-seed) or voice (backbone pilot)")
    g.add_argument("--kernel", help="path to a kernel dir (has kernel-metadata.json)")
    ap.add_argument("--out", help="dir to download outputs into (default: <kernel>/out)")
    ap.add_argument("--username", default="fabiocarava", help="Kaggle username for kaggle.json")
    ap.add_argument("--poll-interval", type=int, default=90, help="seconds between status polls")
    ap.add_argument("--timeout-min", type=int, default=180, help="give up polling after N minutes")
    ap.add_argument("--no-build", dest="build", action="store_false", help="skip (re)assembling the .ipynb")
    ap.add_argument("--no-push", dest="push", action="store_false", help="skip pushing a new run")
    ap.add_argument("--no-fetch", dest="fetch", action="store_false", help="skip downloading outputs")
    args = ap.parse_args()

    kernel_dir = Path(JOBS[args.job] if args.job else args.kernel)
    if not (kernel_dir / "kernel-metadata.json").exists():
        sys.exit(f"{kernel_dir} has no kernel-metadata.json")
    out_dir = Path(args.out) if args.out else kernel_dir / "out"
    kid = kernel_id(kernel_dir)
    print(f"=== Kaggle job: {kid} ===\n    dir={kernel_dir}  out={out_dir}")

    ensure_auth(args.username)
    if args.build:
        build(kernel_dir)
    if args.push:
        print(f"[push] kaggle kernels push -p {kernel_dir}  (triggers a GPU batch run)")
        kaggle("kernels", "push", "-p", str(kernel_dir))
        state = poll(kid, args.poll_interval, args.timeout_min)
        print(f"[poll] final state: {state}")
        if state == "error":
            print(f"[poll] run failed — fetching the log anyway for diagnosis")
        elif state == "timeout":
            print(f"[poll] still running after {args.timeout_min} min; re-run with --no-build --no-push to fetch later")
    if args.fetch:
        out_dir.mkdir(parents=True, exist_ok=True)
        print(f"[fetch] kaggle kernels output {kid} -p {out_dir}")
        kaggle("kernels", "output", kid, "-p", str(out_dir))
        print(f"[done] outputs in {out_dir}:")
        for p in sorted(out_dir.rglob("*")):
            if p.is_file():
                print(f"        {p.relative_to(out_dir)}  ({p.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
