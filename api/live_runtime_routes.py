from __future__ import annotations

import mimetypes
import urllib.parse
from pathlib import Path

from fastapi import Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse

WEB_ROOT = Path("/tmp/swrlz-admin/web")


def _headers() -> dict[str, str]:
    return {
        "Cache-Control": "no-store, max-age=0",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "no-referrer",
        "Cross-Origin-Resource-Policy": "same-origin",
    }


def _safe(asset_path: str) -> Path:
    root = WEB_ROOT.resolve()
    candidate = (WEB_ROOT / asset_path.lstrip("/")).resolve()
    if candidate != root and root not in candidate.parents:
        raise PermissionError("LIVE_PATH_REJECTED")
    return candidate


def _serve(request: Request, asset_path: str):
    try:
        target = _safe(asset_path)
    except PermissionError:
        return JSONResponse({"ok": False, "error": "LIVE_PATH_REJECTED"}, status_code=403, headers=_headers())

    if target.is_dir():
        index = target / "index.html"
        if not index.is_file():
            return JSONResponse({"ok": False, "error": "LIVE_INDEX_MISSING", "path": asset_path or "/"}, status_code=404, headers=_headers())
        if asset_path and not request.url.path.endswith("/"):
            public_path = "/live/" + urllib.parse.quote(asset_path.strip("/"), safe="/-._~") + "/"
            return RedirectResponse(public_path, status_code=307, headers=_headers())
        target = index

    if not target.is_file():
        return JSONResponse({"ok": False, "error": "LIVE_FILE_NOT_FOUND", "path": asset_path}, status_code=404, headers=_headers())

    media_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
    return FileResponse(target, media_type=media_type, headers=_headers())


def install(server) -> None:
    @server.app.get("/live", include_in_schema=False)
    @server.app.get("/live/", include_in_schema=False)
    async def live_root(request: Request):
        return _serve(request, "")

    @server.app.get("/live/{asset_path:path}", include_in_schema=False)
    async def live_asset(request: Request, asset_path: str):
        return _serve(request, asset_path)

    server.CAPABILITIES["live-page-direct-route"] = {
        "kind": "runtime-serving",
        "ready": True,
        "basePath": "/live/",
        "root": str(WEB_ROOT),
    }
