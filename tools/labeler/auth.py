"""Token auth + role separation for the labeler (change 011, ADR-005 safeguards #1/#2/#6).

Two roles:

* **admin** — the owner. Full surface: label, recut, split, excise, segment, export.
* **annotator** — an invited second-pass rater. `/rate/*` only. Deny-by-default:
  every other data route is 403, so `/gold`, `/episode`, `/export`, and every mutating
  route are unreachable with an annotator token (ADR-005 safeguard #2).

Principal resolution, in order:

1. token (``?t=`` once, then the ``X-Token`` header) matched against ``tokens.json``;
2. otherwise **loopback admin** — preserves the owner's existing tokenless local
   workflow, but ONLY for a request that is genuinely local.

The loopback rule needs care: a tunnel (ngrok/Cloudflare) connects to the server over
localhost, so ``request.client.host`` is 127.0.0.1 for tunnelled traffic too. Trusting
the socket alone would hand admin to the whole internet the moment a tunnel opens. A
proxied request always carries ``x-forwarded-*``, so a request is treated as local only
when it is loopback AND carries no forwarding headers. `--no-local-admin` drops the
rule entirely for a labeling round.

``tokens.json`` lives in the data root (gitignored, never committed) as::

    {"<random-token>": {"id": "ann01", "role": "annotator"}, ...}
"""

from __future__ import annotations

import json
import secrets
from dataclasses import dataclass
from pathlib import Path

from fastapi import HTTPException, Request

LOOPBACK = {"127.0.0.1", "::1", "localhost"}
FORWARD_HINTS = ("x-forwarded-for", "x-forwarded-proto", "x-forwarded-host", "forwarded")

TOKENS: dict[str, dict] = {}
ALLOW_LOCAL_ADMIN = True
_LOG_PATH: Path | None = None


@dataclass(frozen=True)
class Principal:
    id: str
    role: str

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


def configure(tokens_path: Path | None, allow_local_admin: bool, log_path: Path) -> int:
    """Load tokens.json (if any) and set the access-log destination. Returns token count."""
    global ALLOW_LOCAL_ADMIN, _LOG_PATH
    ALLOW_LOCAL_ADMIN = allow_local_admin
    _LOG_PATH = log_path
    TOKENS.clear()
    if tokens_path and tokens_path.is_file():
        raw = json.loads(tokens_path.read_text(encoding="utf-8"))
        for tok, who in raw.items():
            if who.get("role") not in ("admin", "annotator"):
                raise SystemExit(f"tokens.json: bad role for {who.get('id')!r}")
            TOKENS[tok] = who
    return len(TOKENS)


def _is_local(request: Request) -> bool:
    host = request.client.host if request.client else ""
    if host not in LOOPBACK:
        return False
    # A tunnel also arrives on loopback — but always proxied, so it announces itself.
    return not any(h in request.headers for h in FORWARD_HINTS)


def principal(request: Request) -> Principal:
    """Resolve the caller, or raise 401. Use as a FastAPI dependency."""
    tok = request.headers.get("x-token") or request.query_params.get("t")
    if tok:
        # constant-time compare against every known token (the table is tiny)
        for known, who in TOKENS.items():
            if secrets.compare_digest(tok, known):
                return Principal(who["id"], who["role"])
        raise HTTPException(401, "bad token")
    if ALLOW_LOCAL_ADMIN and _is_local(request):
        return Principal("owner", "admin")
    raise HTTPException(401, "token required")


def admin(request: Request) -> Principal:
    """Dependency for every owner-only route — annotators get 403, not 404."""
    p = principal(request)
    if not p.is_admin:
        raise HTTPException(403, "admin only")
    return p


def log_access(who: str, action: str, detail: str = "") -> None:
    """Append one access line (ADR-005 safeguard #6: who heard which clip, when).

    Never published; local provenance only. Best-effort — a logging failure must not
    take down a labeling session.
    """
    if _LOG_PATH is None:
        return
    from datetime import UTC, datetime

    line = f"{datetime.now(UTC).isoformat(timespec='seconds')}\t{who}\t{action}\t{detail}\n"
    try:
        with _LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(line)
    except OSError:
        pass


def mint(n: int = 24) -> str:
    return secrets.token_urlsafe(n)
