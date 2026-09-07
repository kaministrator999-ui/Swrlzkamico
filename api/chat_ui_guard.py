from __future__ import annotations

from pathlib import Path

from fastapi import Request
from fastapi.responses import FileResponse, HTMLResponse

from api.hot_loader import hot_chat_path

ROOT = Path(__file__).resolve().parents[1]
BUNDLED_CHAT_PAGE = ROOT / "web" / "chat.html"
ADMIN_SESSION_JS = ROOT / "web" / "chat_admin_session.js"
ENH_CSS = '<link rel="stylesheet" href="/api/chat/assets/enhancements.css">'
ENH_JS = '<script src="/api/chat/assets/enhancements.js"></script>'
SESSION_JS = '<script src="/api/chat/admin-session-ui.js"></script>'
UI_VERSION = "1.3.12"


def _inject(html: str) -> str:
    if "/api/chat/assets/enhancements.css" not in html:
        html = html.replace("</head>", ENH_CSS + "</head>")
    scripts = ""
    if "/api/chat/assets/enhancements.js" not in html:
        scripts += ENH_JS
    if "/api/chat/admin-session-ui.js" not in html:
        scripts += SESSION_JS
    if scripts:
        html = html.replace("</body>", scripts + "</body>")
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
                    "X-SWRLZ-Chat-UI-Version": UI_VERSION,
                    "Content-Security-Policy": "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'",
                },
            )
        if request.method == "GET" and path == "/api/chat/admin-session-ui.js":
            return FileResponse(ADMIN_SESSION_JS, media_type="application/javascript", headers={"Cache-Control": "no-store, max-age=0", "X-SWRLZ-Chat-UI-Version": UI_VERSION})
        return await call_next(request)

    server.CAPABILITIES["chat-ui-parent-guard"] = {
        "kind": "runtime-serving",
        "ready": True,
        "path": "/api/chat",
        "hotSource": True,
        "enhancementsRequired": True,
        "uiVersion": UI_VERSION,
        "serverManagedBrowserSession": True,
        "queryTolerance": "ignores unrelated query decoration; action=page stays UI, functional actions pass through",
    }
