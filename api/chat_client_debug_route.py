from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler
import json
from threading import Lock
from urllib.parse import parse_qs, urlsplit

_RECENT = deque(maxlen=500)
_LOCK = Lock()


def _clean(value, depth=0):
    if depth > 4:
        return "[depth-limit]"
    if value is None or isinstance(value, (bool, int, float)):
        return value
    if isinstance(value, str):
        return value[:2000]
    if isinstance(value, list):
        return [_clean(v, depth + 1) for v in value[:40]]
    if isinstance(value, dict):
        return {str(k)[:80]: _clean(v, depth + 1) for k, v in list(value.items())[:40]}
    return str(value)[:2000]


class handler(BaseHTTPRequestHandler):
    """Path-agnostic Vercel Python diagnostic function.

    Routing is owned by vercel.json.  The function deliberately does not use an
    ASGI router, so a rewritten pathname cannot cause an application-level 404.
    """

    def _json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        try:
            query = parse_qs(urlsplit(self.path).query)
            limit = int((query.get("limit") or ["120"])[0])
        except (TypeError, ValueError):
            limit = 120
        safe_limit = max(1, min(limit, 500))
        with _LOCK:
            rows = list(_RECENT)[-safe_limit:]
        self._json(200, {"ok": True, "count": len(rows), "events": rows})

    def do_POST(self) -> None:
        try:
            length = max(0, min(int(self.headers.get("content-length", "0") or 0), 65536))
        except ValueError:
            length = 0
        try:
            raw = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            raw = {}
        record = {
            "receivedAt": datetime.now(timezone.utc).isoformat(),
            "event": _clean(raw if isinstance(raw, dict) else {}),
        }
        with _LOCK:
            _RECENT.append(record)
        print("SWRLZ_CHAT_CLIENT_DEBUG " + json.dumps(record, separators=(",", ":"), ensure_ascii=True), flush=True)
        self._json(200, {"ok": True})

    def log_message(self, format: str, *args) -> None:
        return
