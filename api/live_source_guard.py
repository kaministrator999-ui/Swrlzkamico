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
CACHE_TTL = 2.0
FETCH_TIMEOUT = 8
MAX_SOURCE_BYTES = 4_000_000
MANIFEST = "runtime_pages/manifest.json"
IMMUTABLE_ASSET_CACHE = "public, max-age=31536000, immutable"
NO_STORE_CACHE = "no-store, max-age=0"

_CACHE: dict[str, tuple[float, bytes]] = {}


def _fetch(source: str, limit: int = MAX_SOURCE_BYTES) -> bytes:
    now = time.time()
    cached = _CACHE.get(source)
    if cached and now - cached[0] <= CACHE_TTL:
        return cached[1]
    encoded_branch = urllib.parse.quote(BRANCH, safe='-._/')
    encoded_source = urllib.parse.quote(source, safe='-._/')
    url = f"{RAW_BASE}/{encoded_branch}/{encoded_source}?swrlz_runtime={int(now * 1000)}"
    req = urllib.request.Request(url, headers={"User-Agent": "swrlz-live-runtime/7", "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"LIVE_SOURCE_TOO_LARGE:{source}")
    data.decode("utf-8")
    if b"\x00" in data:
        raise ValueError(f"LIVE_SOURCE_BINARY_REJECTED:{source}")
    _CACHE[source] = (now, data)
    return data


def _headers(source: str, resolved: str = "github-runtime", *, cache_control: str = NO_STORE_CACHE) -> dict[str, str]:
    return {"Cache-Control": cache_control, "X-Content-Type-Options": "nosniff", "X-SWRLZ-Live-Source": resolved, "X-SWRLZ-Live-Branch": BRANCH, "X-SWRLZ-Live-Path": source}


def _manifest() -> dict[str, object]:
    try:
        value = json.loads(_fetch(MANIFEST, 128_000).decode("utf-8"))
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _manifest_revision() -> str:
    value = _manifest().get("version")
    if isinstance(value, (str, int, float)) and str(value).strip():
        return str(value).strip()
    return "unversioned"


def _route_meta(path: str) -> dict[str, object] | None:
    routes = _manifest().get("routes")
    if not isinstance(routes, dict):
        return None
    value = routes.get(path)
    if isinstance(value, str):
        return {"source": value}
    return value if isinstance(value, dict) else None


def _safe_runtime_source(source: object) -> str | None:
    if not isinstance(source, str) or not source or ".." in Path(source).parts:
        return None
    return source


def _serve_source(source: str, fallback: Path | None = None, *, cache_control: str = NO_STORE_CACHE) -> Response:
    try:
        data = _fetch(source)
        resolved = "github-runtime"
    except Exception:
        if fallback is None or not fallback.is_file():
            return Response("Live runtime source unavailable", status_code=503, media_type="text/plain", headers=_headers(source, "unavailable", cache_control=NO_STORE_CACHE))
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
    return Response(content=data, media_type=media, headers=_headers(source, resolved, cache_control=cache_control))


def _fallback(source: str) -> Path | None:
    path = ROOT / source
    return path if path.is_file() else None


def _asset_url(source: str, revision: str) -> str:
    path = source.removeprefix("web/") if source.startswith("web/") else source
    encoded_revision = urllib.parse.quote(str(revision), safe="-._~")
    return f"/live/assets/{path}?v={encoded_revision}"


def _inject_runtime_assets(data: bytes, meta: dict[str, object]) -> bytes:
    html = data.decode("utf-8")
    styles = meta.get("styles") if isinstance(meta.get("styles"), list) else []
    scripts = meta.get("scripts") if isinstance(meta.get("scripts"), list) else []
    revision = _manifest_revision()
    style_tags: list[str] = []
    script_tags: list[str] = []
    for item in styles:
        source = _safe_runtime_source(item)
        if source and source.endswith(".css"):
            style_tags.append(f'<link rel="stylesheet" href="{_asset_url(source, revision)}">')
    for item in scripts:
        source = _safe_runtime_source(item)
        if source and source.endswith(".js"):
            script_tags.append(f'<script src="{_asset_url(source, revision)}"></script>')
    if style_tags and "data-swrzl-runtime-styles" not in html:
        html = html.replace("</head>", f'<meta name="data-swrzl-runtime-styles" content="runtime-v{revision}">' + "".join(style_tags) + "</head>")
    if script_tags and "data-swrzl-runtime-scripts" not in html:
        html = html.replace("</body>", '<div id="data-swrzl-runtime-scripts" hidden></div>' + "".join(script_tags) + "</body>")
    return html.encode("utf-8")


def install(server) -> None:
    @server.app.middleware("http")
    async def live_runtime_guard(request: Request, call_next):
        path = request.url.path.rstrip("/") or "/"
        action = request.query_params.get("action", "page").strip().lower()
        if request.method != "GET":
            return await call_next(request)

        if path == "/chat":
            meta = _route_meta("/chat") or {"source": "web/chat.html"}
            source = _safe_runtime_source(meta.get("source")) or "web/chat.html"
            response = _serve_source(source, _fallback(source))
            if response.status_code == 200 and response.media_type and response.media_type.startswith("text/html"):
                response.body = _inject_runtime_assets(response.body, meta)
                response.headers["content-length"] = str(len(response.body))
            return attach_browser_session_cookie(response, request)

        if path == "/api/chat" and action == "page":
            meta = _route_meta("/chat") or {"source": "web/chat.html"}
            source = _safe_runtime_source(meta.get("source")) or "web/chat.html"
            response = _serve_source(source, _fallback(source))
            if response.status_code == 200 and response.media_type and response.media_type.startswith("text/html"):
                response.body = _inject_runtime_assets(response.body, meta)
                response.headers["content-length"] = str(len(response.body))
            return attach_browser_session_cookie(response, request)

        meta = _route_meta(path)
        if meta:
            source = _safe_runtime_source(meta.get("source"))
            if source:
                response = _serve_source(source, _fallback(source))
                if response.status_code == 200 and response.media_type and response.media_type.startswith("text/html"):
                    response.body = _inject_runtime_assets(response.body, meta)
                    response.headers["content-length"] = str(len(response.body))
                return response

        if path.startswith("/live/assets/"):
            rel = path[len("/live/assets/"):]
            if rel and ".." not in Path(rel).parts:
                # Injected assets carry the manifest revision in ?v=. That URL is
                # immutable for that revision, so the browser can cache it heavily.
                versioned = bool(request.query_params.get("v", "").strip())
                return _serve_source("web/" + rel, None, cache_control=IMMUTABLE_ASSET_CACHE if versioned else NO_STORE_CACHE)

        if path.startswith("/live/pages/"):
            rel = path[len("/live/pages/"):]
            if rel and ".." not in Path(rel).parts:
                return _serve_source("runtime_pages/pages/" + rel, None)

        if path == "/live/manifest.json":
            return _serve_source(MANIFEST, None)

        return await call_next(request)

    server.CAPABILITIES["instance-independent-live-source"] = {
        "kind": "github-runtime-complete-application",
        "ready": True,
        "sourceBranch": BRANCH,
        "manifest": MANIFEST,
        "cacheTtlSeconds": CACHE_TTL,
        "assetCacheContract": "manifest-versioned-immutable-v1",
        "versionedAssetCacheControl": IMMUTABLE_ASSET_CACHE,
        "serverRestartRequiredForRuntimeChanges": False,
        "vercelDeploymentRequiredForRuntimeChanges": False,
        "stableBootstrapOwnsPageCode": False,
        "durability": "GitHub runtime branch is source of truth; instance memory is only a bounded read cache.",
        "detail": "HTML and the manifest remain live/no-store. Manifest-injected JS/CSS use revisioned URLs and immutable browser caching, preserving hot updates while removing repeated asset transfer on unchanged revisions.",
    }
