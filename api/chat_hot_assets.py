from __future__ import annotations

from pathlib import Path

from fastapi import Request
from fastapi.responses import FileResponse, JSONResponse

from api.hot_loader import HOT_CHAT

_ALLOWED = {
    "chat_account.js": "application/javascript; charset=utf-8",
    "chat_stream_focus.js": "application/javascript; charset=utf-8",
    "chat_enhancements.js": "application/javascript; charset=utf-8",
    "chat_enhancements.css": "text/css; charset=utf-8",
}


def install(server) -> None:
    @server.app.get("/api/chat/assets/{asset_name}")
    async def chat_hot_asset(asset_name: str, request: Request):
        media_type = _ALLOWED.get(asset_name)
        if not media_type:
            return JSONResponse({"ok": False, "error": "chat asset not allowed"}, status_code=404)
        target = (HOT_CHAT / asset_name).resolve()
        root = HOT_CHAT.resolve()
        if target.parent != root or not target.is_file():
            return JSONResponse({"ok": False, "error": "hot chat asset not loaded"}, status_code=503)
        return FileResponse(
            target,
            media_type=media_type,
            headers={
                "Cache-Control": "no-store, max-age=0",
                "Vercel-CDN-Cache-Control": "no-store",
                "Cross-Origin-Resource-Policy": "same-origin",
                "X-SWRLZ-Hot-Asset": asset_name,
            },
        )

    server.CAPABILITIES["hot-chat-assets"] = {
        "kind": "runtime-mutation",
        "ready": True,
        "source": "runtime",
        "path": "/api/chat/assets/{asset_name}",
        "assets": sorted(_ALLOWED),
    }
