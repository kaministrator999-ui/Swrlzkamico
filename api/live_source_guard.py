from __future__ import annotations

import mimetypes
import time
import urllib.parse
import urllib.request
from pathlib import Path

from fastapi import Request
from fastapi.responses import RedirectResponse, Response

from api.chat_admin_session import attach_browser_session_cookie

OWNER = "kaministrator999-ui"
REPO = "Swrlzkamico"
BRANCH = "dev"
RAW_BASE = f"https://raw.githubusercontent.com/{OWNER}/{REPO}"
ROOT = Path(__file__).resolve().parents[1]
CACHE_TTL = 2.0
_CACHE: dict[str, tuple[float, bytes]] = {}

CHAT_HTML = "web/chat.html"
CHAT_CSS = "web/chat_enhancements.css"
CHAT_JS = "web/chat_enhancements.js"
CHAT_FOCUS_JS = "web/chat_stream_focus.js"
ADMIN_HTML = "web/admin.html"
SERVER_HTML = "web/server.html"
LALM_HTML = "web/lalm.html"
INDEX_HTML = "runtime_pages/index.html"

ENH_CSS = '<link rel="stylesheet" href="/api/chat/assets/enhancements.css">'
ENH_JS = '<script src="/api/chat/assets/enhancements.js"></script>'
FOCUS_JS = '<script src="/api/chat/assets/stream-focus.js"></script>'
SESSION_JS = '<script src="/api/chat/admin-session-ui.js"></script>'


def _fetch(source: str, limit: int = 4_000_000) -> bytes:
    now = time.time()
    cached = _CACHE.get(source)
    if cached and now - cached[0] <= CACHE_TTL:
        return cached[1]
    url = f"{RAW_BASE}/{urllib.parse.quote(BRANCH, safe='-._/')}/{urllib.parse.quote(source, safe='-._/')}"
    req = urllib.request.Request(url, headers={"User-Agent": "swrlz-live-source/2", "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=8) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"LIVE_SOURCE_TOO_LARGE:{source}")
    data.decode("utf-8")
    if b"\x00" in data:
        raise ValueError(f"LIVE_SOURCE_BINARY_REJECTED:{source}")
    _CACHE[source] = (now, data)
    return data


def _headers(source: str, resolved: str = "github-dev") -> dict[str, str]:
    return {
        "Cache-Control": "no-store, max-age=0",
        "X-Content-Type-Options": "nosniff",
        "X-SWRLZ-Live-Source": resolved,
        "X-SWRLZ-Live-Branch": BRANCH,
        "X-SWRLZ-Live-Path": source,
    }


def _inject_chat(data: bytes) -> bytes:
    html = data.decode("utf-8")
    if "/api/chat/assets/enhancements.css" not in html:
        html = html.replace("</head>", ENH_CSS + "</head>")
    scripts = ""
    if "/api/chat/assets/enhancements.js" not in html:
        scripts += ENH_JS
    if "/api/chat/assets/stream-focus.js" not in html:
        scripts += FOCUS_JS
    if "/api/chat/admin-session-ui.js" not in html:
        scripts += SESSION_JS
    if scripts:
        html = html.replace("</body>", scripts + "</body>")
    return html.encode("utf-8")


def _serve_source(source: str, fallback: Path | None = None, *, chat_html: bool = False) -> Response:
    try:
        data = _fetch(source)
        resolved = "github-dev"
    except Exception:
        if fallback is None or not fallback.is_file():
            return Response("Live source unavailable", status_code=503, media_type="text/plain", headers=_headers(source, "unavailable"))
        data = fallback.read_bytes()
        resolved = "bundled-fallback"
    if chat_html:
        data = _inject_chat(data)
    media = mimetypes.guess_type(source)[0] or "application/octet-stream"
    if source.endswith(".html"):
        media = "text/html; charset=utf-8"
    elif source.endswith(".js"):
        media = "application/javascript; charset=utf-8"
    elif source.endswith(".css"):
        media = "text/css; charset=utf-8"
    return Response(content=data, media_type=media, headers=_headers(source, resolved))


def install(server) -> None:
    bundled_chat = ROOT / CHAT_HTML
    bundled_css = ROOT / CHAT_CSS
    bundled_js = ROOT / CHAT_JS
    bundled_focus_js = ROOT / CHAT_FOCUS_JS
    bundled_admin = ROOT / ADMIN_HTML
    bundled_server = ROOT / SERVER_HTML
    bundled_lalm = ROOT / LALM_HTML
    bundled_index = ROOT / INDEX_HTML

    @server.app.middleware("http")
    async def live_source_guard(request: Request, call_next):
        path = request.url.path.rstrip("/") or "/"
        action = request.query_params.get("action", "page").strip().lower()
        if request.method == "GET" and path == "/chat":
            return RedirectResponse("/api/chat", status_code=307)
        if request.method == "GET" and path == "/api/chat" and action == "page":
            response = _serve_source(CHAT_HTML, bundled_chat, chat_html=True)
            return attach_browser_session_cookie(response, request)
        if request.method == "GET" and path == "/api/chat/assets/enhancements.js":
            return _serve_source(CHAT_JS, bundled_js)
        if request.method == "GET" and path == "/api/chat/assets/stream-focus.js":
            return _serve_source(CHAT_FOCUS_JS, bundled_focus_js)
        if request.method == "GET" and path == "/api/chat/assets/enhancements.css":
            return _serve_source(CHAT_CSS, bundled_css)
        if request.method == "GET" and path == "/api/admin":
            return _serve_source(ADMIN_HTML, bundled_admin)
        if request.method == "GET" and path == "/server":
            return _serve_source(SERVER_HTML, bundled_server)
        if request.method == "GET" and path == "/lalm":
            return _serve_source(LALM_HTML, bundled_lalm)
        if request.method == "GET" and path == "/live":
            return _serve_source(INDEX_HTML, bundled_index)
        if request.method == "GET" and path.startswith("/live/pages/"):
            rel = path[len("/live/pages/"):]
            if rel and ".." not in Path(rel).parts:
                return _serve_source("runtime_pages/pages/" + rel, None)
        return await call_next(request)

    server.CAPABILITIES["instance-independent-live-source"] = {
        "kind": "github-backed-runtime-serving",
        "ready": True,
        "sourceBranch": BRANCH,
        "cacheTtlSeconds": CACHE_TTL,
        "instanceLocalTmpRequiredForReads": False,
        "chatSessionCookieOnPageLoad": True,
        "corePages": {
            "chat": CHAT_HTML,
            "server": SERVER_HTML,
            "lalm": LALM_HTML,
            "admin": ADMIN_HTML,
            "live": INDEX_HTML,
        },
        "chatAssets": [CHAT_CSS, CHAT_JS, CHAT_FOCUS_JS],
        "detail": "Chat, Server, LALM, Admin, live index, and Chat assets resolve from GitHub dev per request with a 2-second in-instance cache and bundled fallback. R39 engine code remains request-driven hot runtime with its own 30-second delta refresh.",
    }
