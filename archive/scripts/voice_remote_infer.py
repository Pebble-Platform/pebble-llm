#!/usr/bin/env python
"""Call a deployed voice-tester (HF Space / any host) from local — runs the model on the cloud.

Usage:
    python scripts/voice_remote_infer.py <base_url> <model_id> <wav>
    python scripts/voice_remote_infer.py https://user-pebble-voice-tester.hf.space \
        emotion2vec--superb-frame my.wav

List models/samples on the remote:
    python scripts/voice_remote_infer.py <base_url> --list

Only depends on `requests` (or falls back to urllib) — no torch/funasr needed locally, so this
is how you test emotion2vec from the Intel-mac: the cloud does the work.
"""
import json
import os
import sys
import urllib.request

# Private HF Spaces need a bearer token; set HF_TOKEN to call them.
_TOKEN = os.environ.get("HF_TOKEN")
_AUTH = {"Authorization": f"Bearer {_TOKEN}"} if _TOKEN else {}


def _get(url):
    req = urllib.request.Request(url, headers=_AUTH)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def _post_file(url, model_id, wav_path):
    import mimetypes
    import uuid
    boundary = uuid.uuid4().hex
    with open(wav_path, "rb") as f:
        data = f.read()
    ctype = mimetypes.guess_type(wav_path)[0] or "audio/wav"
    parts = []
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"model_id\"\r\n\r\n{model_id}\r\n")
    parts.append(f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; "
                 f"filename=\"{wav_path.split('/')[-1]}\"\r\nContent-Type: {ctype}\r\n\r\n")
    body = b"".join(p.encode() for p in parts) + data + f"\r\n--{boundary}--\r\n".encode()
    headers = {"Content-Type": f"multipart/form-data; boundary={boundary}", **_AUTH}
    req = urllib.request.Request(url, data=body, method="POST", headers=headers)
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    base = sys.argv[1].rstrip("/")
    if sys.argv[2] == "--list":
        print("models:", json.dumps(_get(f"{base}/api/models"), indent=2))
        print("samples:", json.dumps(_get(f"{base}/api/samples"), indent=2))
        return
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    model_id, wav = sys.argv[2], sys.argv[3]
    r = _post_file(f"{base}/api/infer", model_id, wav)
    top = sorted(r["probs"].items(), key=lambda kv: -kv[1])[:3]
    print(f"model={r['model']} backbone={r['backbone']} head={r['head']} ({r['latency_ms']} ms)")
    print(f"PREDICTED: {r['emotion']}" + (f"   truth={r['truth']}" if r.get("truth") else ""))
    print("top-3:", ", ".join(f"{k}={v:.3f}" for k, v in top))


if __name__ == "__main__":
    main()
