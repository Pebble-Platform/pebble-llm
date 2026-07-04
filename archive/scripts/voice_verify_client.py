"""Post a wav to the running voice verifier and pretty-print the response.

    PYTHONPATH=src .venv-voice/bin/python scripts/voice_verify_client.py \\
        artifacts/voice/artifact_wavlm-base/sample_val.wav
"""

from __future__ import annotations

import json
import sys
import urllib.request

URL = "http://localhost:8081/classify-voice"


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "artifacts/voice/artifact_wavlm-base/sample_val.wav"
    with open(path, "rb") as f:
        body = f.read()
    boundary = "----pebblevoice"
    payload = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="clip.wav"\r\n'
        f"Content-Type: audio/wav\r\n\r\n"
    ).encode() + body + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        URL, data=payload,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        print(json.dumps(json.loads(r.read()), indent=2))


if __name__ == "__main__":
    main()
