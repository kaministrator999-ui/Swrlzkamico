from __future__ import annotations

import hmac
import os
from typing import Callable

from fastapi import Request


def _normalize_secret(value: str | None) -> str:
    """Normalize harmless representation only; never alter token identity."""
    text = (value or "").strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {"'", '"'}:
        text = text[1:-1].strip()
    return text


def install(server) -> None:
    def auth(request: Request) -> bool:
        # Resolve on every request so auth follows the current deployment environment
        # instead of an import-time snapshot. Matching remains constant-time and exact
        # after harmless whitespace/wrapping-quote normalization.
        configured = _normalize_secret(os.environ.get("SWRLZ_ADMIN_TOKEN"))
        supplied = _normalize_secret(request.headers.get("x-swrlz-admin-token"))
        return bool(configured) and bool(supplied) and hmac.compare_digest(supplied, configured)

    server.auth = auth
    server.CAPABILITIES["admin-auth-resolution"] = {
        "kind": "security-auth",
        "ready": True,
        "source": "SWRLZ_ADMIN_TOKEN",
        "resolution": "per-request",
        "normalization": "outer whitespace and one matching wrapping quote pair only",
        "identityMatch": "constant-time exact",
    }
