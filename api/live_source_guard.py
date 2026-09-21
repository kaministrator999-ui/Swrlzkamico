from __future__ import annotations

import base64
import json
import mimetypes
import time
import urllib.parse
import urllib.request
from pathlib import Path

from fastapi import Request
from fastapi.responses import Response

from api.chat_admin_session import attach_browser_session_cookie

OWNER = "kaministrator999-ui"
REPO = "Swrlzkamico"
BRANCH = "runtime"
CHAT_APP_BRANCH = "main"
RAW_BASE = f"https://raw.githubusercontent.com/{OWNER}/{REPO}"
CONTENTS_API_BASE = f"https://api.github.com/repos/{OWNER}/{REPO}/contents"
ROOT = Path(__file__).resolve().parents[1]
CACHE_TTL = 2.0
# The manifest is the cache-busting authority for every runtime Chat asset. A
# long worker-local cache here makes a freshly updated runtime branch look stale
# even when the browser reloads correctly. Keep only a tiny request-collapse
# window so one reload converges on the new revision without hammering GitHub.
MANIFEST_CACHE_TTL = 2.0
FETCH_TIMEOUT = 8
MAX_SOURCE_BYTES = 4_000_000
MANIFEST = "runtime_pages/manifest.json"
IMMUTABLE_ASSET_CACHE = "public, max-age=31536000, immutable"
NO_STORE_CACHE = "no-store, max-age=0"

_CACHE: dict[str, tuple[float, bytes]] = {}
_MANIFEST_CACHE: tuple[float, bytes, str] | None = None


def _validate_text_source(source: str, data: bytes, limit: int) -> bytes:
    if len(data) > limit:
        raise ValueError(f"LIVE_SOURCE_TOO_LARGE:{source}")
    data.decode("utf-8")
    if b"\x00" in data:
        raise ValueError(f"LIVE_SOURCE_BINARY_REJECTED:{source}")
    return data


def _fetch(source: str, limit: int = MAX_SOURCE_BYTES) -> bytes:
    now = time.time()
    cached = _CACHE.get(source)
    if cached and now - cached[0] <= CACHE_TTL:
        return cached[1]
    encoded_branch = urllib.parse.quote(BRANCH, safe='-._/')
    encoded_source = urllib.parse.quote(source, safe='-._/')
    url = f"{RAW_BASE}/{encoded_branch}/{encoded_source}?swrlz_runtime={int(now * 1000)}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "swrlz-live-runtime/8",
            "Cache-Control": "no-cache, no-store, max-age=0",
            "Pragma": "no-cache",
        },
    )
    with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as response:
        data = response.read(limit + 1)
    data = _validate_text_source(source, data, limit)
    _CACHE[source] = (now, data)
    return data


def _fetch_manifest_authoritative() -> tuple[bytes, str]:
    """Read the runtime manifest from GitHub repository-content authority.

    Raw GitHub remains the fast delivery path for revisioned assets, but a branch
    CDN response must never be allowed to pin Chat to an old manifest revision.
    The manifest therefore resolves through the repository contents API and is
    cached only for a tiny request-collapse window. If that authority is
    unavailable after the cache expires, callers fail closed rather than
    silently serving an older raw copy.
    """
    global _MANIFEST_CACHE
    now = time.time()
    if _MANIFEST_CACHE and now - _MANIFEST_CACHE[0] <= MANIFEST_CACHE_TTL:
        return _MANIFEST_CACHE[1], _MANIFEST_CACHE[2]

    encoded_source = urllib.parse.quote(MANIFEST, safe='-._/')
    encoded_branch = urllib.parse.quote(BRANCH, safe='-._/')
    url = f"{CONTENTS_API_BASE}/{encoded_source}?ref={encoded_branch}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "swrlz-live-manifest-authority/2",
            "Cache-Control": "no-cache, no-store, max-age=0",
            "Pragma": "no-cache",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as response:
        payload = json.loads(response.read(256_000).decode("utf-8"))
    if not isinstance(payload, dict) or payload.get("encoding") != "base64":
        raise ValueError("LIVE_MANIFEST_AUTHORITY_INVALID_RESPONSE")
    encoded = str(payload.get("content") or "").replace("\n", "")
    data = base64.b64decode(encoded, validate=True)
    data = _validate_text_source(MANIFEST, data, 128_000)
    value = json.loads(data.decode("utf-8"))
    if not isinstance(value, dict) or not isinstance(value.get("version"), (str, int, float)):
        raise ValueError("LIVE_MANIFEST_AUTHORITY_INVALID_MANIFEST")
    revision = str(value.get("version")).strip()
    if not revision:
        raise ValueError("LIVE_MANIFEST_AUTHORITY_MISSING_REVISION")
    _MANIFEST_CACHE = (now, data, revision)
    return data, revision


def _headers(source: str, resolved: str = "github-runtime", *, cache_control: str = NO_STORE_CACHE) -> dict[str, str]:
    return {
        "Cache-Control": cache_control,
        "X-Content-Type-Options": "nosniff",
        "X-SWRLZ-Live-Source": resolved,
        "X-SWRLZ-Live-Branch": BRANCH,
        "X-SWRLZ-Live-Path": source,
    }


def _manifest() -> dict[str, object]:
    data, _ = _fetch_manifest_authoritative()
    value = json.loads(data.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("LIVE_MANIFEST_AUTHORITY_INVALID_MANIFEST")
    return value


def _manifest_revision() -> str:
    _, revision = _fetch_manifest_authoritative()
    return revision


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


def _fetch_ref(source: str, limit: int = MAX_SOURCE_BYTES, *, ref: str) -> bytes:
    encoded_ref = urllib.parse.quote(ref, safe='-._/')
    encoded_source = urllib.parse.quote(source, safe='-._/')
    url = f"{RAW_BASE}/{encoded_ref}/{encoded_source}?swrlz_source={int(time.time() * 1000)}"
    req = urllib.request.Request(url, headers={"User-Agent": "swrlz-live-source/9", "Cache-Control": "no-cache, no-store, max-age=0", "Pragma": "no-cache"})
    with urllib.request.urlopen(req, timeout=FETCH_TIMEOUT) as response:
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"LIVE_SOURCE_TOO_LARGE:{source}")
    return data


def _serve_source(source: str, fallback: Path | None = None, *, cache_control: str = NO_STORE_CACHE, ref: str = BRANCH) -> Response:
    try:
        data = _fetch(source) if ref == BRANCH else _fetch_ref(source, ref=ref)
        resolved = "github-runtime"
    except Exception:
        if fallback is None or not fallback.is_file():
            return Response(
                "Live runtime source unavailable",
                status_code=503,
                media_type="text/plain",
                headers=_headers(source, "unavailable", cache_control=NO_STORE_CACHE),
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
    return Response(content=data, media_type=media, headers=_headers(source, resolved, cache_control=cache_control))


def _serve_manifest() -> Response:
    try:
        data, revision = _fetch_manifest_authoritative()
    except Exception as exc:
        return Response(
            f"Live manifest authority unavailable: {type(exc).__name__}",
            status_code=503,
            media_type="text/plain",
            headers=_headers(MANIFEST, "authority-unavailable", cache_control=NO_STORE_CACHE),
        )
    headers = _headers(MANIFEST, "github-contents-api", cache_control=NO_STORE_CACHE)
    headers["X-SWRLZ-Manifest-Authority"] = "github-contents-api-v1"
    headers["X-SWRLZ-Manifest-Revision"] = revision
    return Response(content=data, media_type="application/json; charset=utf-8", headers=headers)


def _serve_chat_app_source(source: str) -> Response:
    deployed = ROOT / source
    if not deployed.is_file():
        return Response("Deployed Chat application source unavailable", status_code=503, media_type="text/plain", headers=_headers(source, "deployment-missing", cache_control=NO_STORE_CACHE))
    media = mimetypes.guess_type(source)[0] or "application/octet-stream"
    if source.endswith(".html"):
        media = "text/html; charset=utf-8"
    cache_control = "public, max-age=31536000, immutable" if "/assets/" in source else NO_STORE_CACHE
    headers = _headers(source, "deployed-main-bundle", cache_control=cache_control)
    headers["X-SWRLZ-Live-Branch"] = CHAT_APP_BRANCH
    return Response(content=deployed.read_bytes(), media_type=media, headers=headers)


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
            # Runtime augmentation must never stop the base Chat document parser.
            # Ordered deferred scripts preserve manifest order while allowing the
            # base shell to finish parsing before augmentation executes.
            script_tags.append(f'<script defer src="{_asset_url(source, revision)}"></script>')
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

        if path.startswith("/live/assets/"):
            rel = path[len("/live/assets/"):]
            if rel and ".." not in Path(rel).parts:
                versioned = bool(request.query_params.get("v", "").strip())
                return _serve_source("web/" + rel, None, cache_control=IMMUTABLE_ASSET_CACHE if versioned else NO_STORE_CACHE)

        if path == "/live/manifest.json":
            return _serve_manifest()

        if path == "/chat/§wyrlz":
            return attach_browser_session_cookie(_serve_chat_app_source("chat/§wyrlz/index.html"), request)

        if path.startswith("/chat/§wyrlz/"):
            rel = path[len("/chat/§wyrlz/"):]
            if rel and ".." not in Path(rel).parts:
                return _serve_chat_app_source("chat/§wyrlz/" + rel)
            return Response("Chat application asset not found", status_code=404, media_type="text/plain")

        if path == "/chat":
            try:
                meta = _route_meta("/chat") or {"source": "web/chat.html"}
            except Exception as exc:
                return Response(f"Live manifest authority unavailable: {type(exc).__name__}",status_code=503,media_type="text/plain",headers=_headers(MANIFEST,"authority-unavailable"))
            source = _safe_runtime_source(meta.get("source")) or "web/chat.html"
            response = _serve_source(source, _fallback(source))
            if response.status_code == 200 and response.media_type and response.media_type.startswith("text/html"):
                response.body = _inject_runtime_assets(response.body, meta)
                response.headers["content-length"] = str(len(response.body))
                response.headers["X-SWRLZ-Manifest-Revision"] = _manifest_revision()
            return attach_browser_session_cookie(response, request)

        if path == "/api/chat" and action == "page":
            try:
                meta = _route_meta("/chat") or {"source": "web/chat.html"}
            except Exception as exc:
                return Response(f"Live manifest authority unavailable: {type(exc).__name__}",status_code=503,media_type="text/plain",headers=_headers(MANIFEST,"authority-unavailable"))
            source = _safe_runtime_source(meta.get("source")) or "web/chat.html"
            response = _serve_source(source, _fallback(source))
            if response.status_code == 200 and response.media_type and response.media_type.startswith("text/html"):
                response.body = _inject_runtime_assets(response.body, meta)
                response.headers["content-length"] = str(len(response.body))
                response.headers["X-SWRLZ-Manifest-Revision"] = _manifest_revision()
            return attach_browser_session_cookie(response, request)

        if path.startswith("/live/pages/"):
            rel = path[len("/live/pages/"):]
            if rel and ".." not in Path(rel).parts:
                return _serve_source("runtime_pages/pages/" + rel, None)

        try:
            meta = _route_meta(path)
        except Exception:
            meta = None
        if meta:
            source = _safe_runtime_source(meta.get("source"))
            if source:
                response = _serve_source(source, _fallback(source))
                if response.status_code == 200 and response.media_type and response.media_type.startswith("text/html"):
                    response.body = _inject_runtime_assets(response.body, meta)
                    response.headers["content-length"] = str(len(response.body))
                    response.headers["X-SWRLZ-Manifest-Revision"] = _manifest_revision()
                return response

        return await call_next(request)

    server.CAPABILITIES["instance-independent-live-source"] = {
        "kind": "github-runtime-complete-application",
        "ready": True,
        "sourceBranch": BRANCH,
        "manifest": MANIFEST,
        "cacheTtlSeconds": CACHE_TTL,
        "manifestAuthority": "github-contents-api-v1",
        "manifestAuthorityCacheTtlSeconds": MANIFEST_CACHE_TTL,
        "manifestFailurePolicy": "fail-closed-no-stale-raw-manifest",
        "assetCacheContract": "manifest-versioned-immutable-v1",
        "versionedAssetCacheControl": IMMUTABLE_ASSET_CACHE,
        "serverRestartRequiredForRuntimeChanges": False,
        "vercelDeploymentRequiredForRuntimeChanges": False,
        "stableBootstrapOwnsPageCode": False,
        "durability": "GitHub runtime branch is source of truth; instance memory is only a bounded read cache.",
        "detail": "Manifest revision is resolved through GitHub repository-content authority with only a 2-second request-collapse cache. Runtime augmentation scripts are injected as ordered deferred scripts so the base document parser cannot be blocked. Revisioned JS/CSS remain immutable browser-cache assets; asset requests bypass manifest lookup.",
    }
