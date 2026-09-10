from __future__ import annotations

import json
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
BRANCH = "runtime"
RAW_BASE = f"https://raw.githubusercontent.com/{OWNER}/{REPO}"
ROOT = Path(__file__).resolve().parents[1]
CACHE_TTL = 1.0
FETCH_TIMEOUT = 8
MAX_SOURCE_BYTES = 4_000_000
MANIFEST = "runtime_pages/manifest.json"

_CACHE: dict[str, tuple[float, bytes]] = {}


def _fetch(source: str, limit: int = MAX_SOURCE_BYTES) -> bytes:
    now = time.time()
    cached = _CACHE.get(source)
    if cached and now - cached[0] <= CACHE_TTL:
        return cached[1]
    url = f"{RAW_BASE}/{urllib.parse.quote(BRANCH, safe='-._/')}/{urllib.parse.quote(source, safe='-._/')}"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "swrlz-live-runtime/4", "Cache-Control": "no-cache"},
    )
    with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"LIVE_SOURCE_TOO_LARGE:{source}")
    data.decode("utf-8")
    if b"\x00" in data:
        raise ValueError(f"LIVE_SOURCE_BINARY_REJECTED:{source}")
    _CACHE[source] = (now, data)
    return data


def _headers(source: str, resolved: str = "github-runtime") -> dict[str, str]:
    return {
        "Cache-Control": "no-store, max-age=0",
        "X-Content-Type-Options": "nosniff",
        "X-SWRLZ-Live-Source": resolved,
        "X-SWRLZ-Live-Branch": BRANCH,
        "X-SWRLZ-Live-Path": source,
    }


def _manifest() -> dict[str, object]:
    try:
        return json.loads(_fetch(MANIFEST, 128_000).decode("utf-8"))
    except Exception:
        return {}


def _runtime_path_for_route(path: str) -> str | None:
    manifest = _manifest()
    routes = manifest.get("routes") if isinstance(manifest, dict) else None
    if isinstance(routes, dict):
        target = routes.get(path)
        if isinstance(target, str) and target and ".." not in Path(target).parts:
            return target
    return None


def _serve_source(source: str, fallback: Path | None = None) -> Response:
    try:
        data = _fetch(source)
        resolved = "github-runtime"
    except Exception:
        if fallback is None or not fallback.is_file():
            return Response(
                "Live runtime source unavailable",
                status_code=503,
                media_type="text/plain",
                headers=_headers(source, "unavailable"),
            )
        data = fallback.read_bytes()
        resolved = "bundled-fallback"

    media = mimetypes.guess_type(source)[0] or "application/octet-stream"
    if source.endswith(".html"):
        media = "text/html; charset=utf-8"
    elif source.endswith(".js"):
        media = "application/javascript; charset=utf-8"
    elif source.endswith(".css"):
        media = "text/css; charset=utf-8"
    elif source.endswith(".json"):
        media = "application/json; charset=utf-8"
    return Response(content=data, media_type=media, headers=_headers(source, resolved))


def _fallback(source: str) -> Path | None:
    path = ROOT / source
    return path if path.is_file() else None


def install(server) -> None:
    @server.app.middleware("http")
    async def live_runtime_guard(request: Request, call_next):
        path = request.url.path.rstrip("/") or "/"
        action = request.query_params.get("action", "page").strip().lower()
        if request.method != "GET":
            return await call_next(request)

        # Every page route is resolved from the durable runtime manifest.
        # The stable server does not inject UI/version/Chat code into pages.
        if path == "/chat" or (path == "/api/chat" and action == "page"):
            source = _runtime_path_for_route("/chat") or "web/chat.html"
            response = _serve_source(source, _fallback(source))
            return attach_browser_session_cookie(response, request)

        source = _runtime_path_for_route(path)
        if source:
            response = _serve_source(source, _fallback(source))
            if path == "/chat":
                return attach_browser_session_cookie(response, request)
            return response

        # Generic runtime asset path. This keeps page-owned JS/CSS/assets hot.
        if path.startswith("/live/assets/"):
            rel = path[len("/live/assets/"):]
            if rel and ".." not in Path(rel).parts:
                source = "web/" + rel
                return _serve_source(source, None)

        # Generic runtime page namespace. Add/remove files on runtime without
        # changing the stable server.
        if path.startswith("/live/pages/"):
            rel = path[len("/live/pages/"):]
            if rel and ".." not in Path(rel).parts:
                source = "runtime_pages/pages/" + rel
                return _serve_source(source, None)

        if path == "/live/manifest.json":
            return _serve_source(MANIFEST, None)

        return await call_next(request)

    server.CAPABILITIES["instance-independent-live-source"] = {
        "kind": "github-runtime-complete-application",
        "ready": True,
        "sourceBranch": BRANCH,
        "manifest": MANIFEST,
        "cacheTtlSeconds": CACHE_TTL,
        "serverRestartRequiredForRuntimeChanges": False,
        "vercelDeploymentRequiredForRuntimeChanges": False,
        "stableBootstrapOwnsPageCode": False,
        "durability": "GitHub runtime branch is source of truth; instance memory is only a bounded read cache.",
        "detail": "The runtime manifest controls page routes. Runtime HTML, CSS, JavaScript, and page assets are fetched from GitHub runtime per request. The stable bootstrap does not inject versions, watchdogs, CSS, JavaScript, or other page behavior.",
    }
