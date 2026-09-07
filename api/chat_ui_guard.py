from __future__ import annotations

from pathlib import Path

from fastapi import Request
from fastapi.responses import HTMLResponse

from api.hot_loader import hot_chat_path

ROOT = Path(__file__).resolve().parents[1]
BUNDLED_CHAT_PAGE = ROOT / "web" / "chat.html"
ENH_CSS = '<link rel="stylesheet" href="/api/chat/assets/enhancements.css">'
ENH_JS = '<script src="/api/chat/assets/enhancements.js"></script>'


def _inject(html: str) -> str:
    if "/api/chat/assets/enhancements.css" not in html:
        html = html.replace("</head>", ENH_CSS + "</head>")
    if "/api/chat/assets/enhancements.js" not in html:
        html = html.replace("</body>", ENH_JS + "</body>")
    return html


def install(server) -> None:
    @server.app.middleware("http")
    async def swrlz_parent_chat_ui_guard(request: Request, call_next):
        path = request.url.path.rstrip("/") or "/"
        action = request.query_params.get("action", "page").strip().lower()
        if request.method == "GET" and path == "/api/chat" and action == "page":
            page = hot_chat_path("chat.html", BUNDLED_CHAT_PAGE)
            try:
                html = page.read_text("utf-8")
            except OSError:
                return HTMLResponse("Chat page missing", status_code=500, headers={"Cache-Control": "no-store"})
            source = "runtime-override" if page != BUNDLED_CHAT_PAGE else "bundled"
            return HTMLResponse(
                _inject(html),
                headers={
                    "Cache-Control": "no-store, max-age=0",
                    "X-SWRLZ-Chat-UI-Source": source,
                    "X-SWRLZ-Chat-Enhancements": "required",
                    "Content-Security-Policy": "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
                },
            )
        return await call_next(request)

    server.CAPABILITIES["chat-ui-parent-guard"] = {
        "kind": "runtime-serving",
        "ready": True,
        "path": "/api/chat",
        "hotSource": True,
        "enhancementsRequired": True,
        "queryTolerance": "ignores unrelated query decoration; action=page stays UI, functional actions pass through",
    }
