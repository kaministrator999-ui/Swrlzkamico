from __future__ import annotations

from pathlib import Path

from fastapi import Request
from fastapi.responses import FileResponse, HTMLResponse

from api.hot_loader import hot_chat_path

ROOT = Path(__file__).resolve().parents[1]
BUNDLED_CHAT_PAGE = ROOT / "web" / "chat.html"
ADMIN_SESSION_JS = ROOT / "web" / "chat_admin_session.js"
STREAM_FOCUS_JS = ROOT / "web" / "chat_stream_focus.js"
ACCOUNT_BRIDGE_JS = ROOT / "web" / "chat_account_bridge.js"
ACCOUNT_JS = ROOT / "web" / "chat_account.js"
ENH_CSS = '<link rel="stylesheet" href="/api/chat/assets/enhancements.css">'
ENH_JS = '<script src="/api/chat/assets/enhancements.js"></script>'
SESSION_JS = '<script src="/api/chat/admin-session-ui.js"></script>'
STREAM_FOCUS_TAG = '<script src="/api/chat/stream-focus.js"></script>'
ACCOUNT_BRIDGE_TAG = '<script src="/api/chat/account-bridge.js"></script>'
ACCOUNT_TAG = '<script src="/api/chat/account.js"></script>'
MOBILE_POLISH = '''<style id="swrlz-mobile-polish">
@media (max-width:820px){
  :root{--sidebar:min(82vw,360px)}
  .sidebar{width:var(--sidebar);max-width:360px;box-shadow:18px 0 55px rgba(0,0,0,.38)}
  .sidebar-foot{flex:0 0 auto;max-height:34dvh;overflow:auto;padding-bottom:10px}
  .swrlz-account{padding-bottom:4px}
  .swrlz-account-card{min-width:0}
  .swrlz-google-host{max-width:100%;overflow:hidden}
  .swrlz-enhance-bar[data-expanded="true"]{position:relative;z-index:10;background:rgba(5,9,18,.985);border-bottom:1px solid var(--line-strong);box-shadow:0 16px 38px rgba(0,0,0,.34);backdrop-filter:blur(18px)}
  .swrlz-enhance-bar[data-expanded="true"] button{background:rgba(13,23,42,.98);box-shadow:0 6px 18px rgba(0,0,0,.2)}
}
</style>'''
UI_VERSION = "1.4.1"


def _inject(html: str) -> str:
    if "/api/chat/assets/enhancements.css" not in html:
        html = html.replace("</head>", ENH_CSS + MOBILE_POLISH + "</head>")
    elif "swrlz-mobile-polish" not in html:
        html = html.replace("</head>", MOBILE_POLISH + "</head>")
    scripts = ""
    for marker, tag in (
        ("/api/chat/assets/enhancements.js", ENH_JS),
        ("/api/chat/admin-session-ui.js", SESSION_JS),
        ("/api/chat/stream-focus.js", STREAM_FOCUS_TAG),
        ("/api/chat/account-bridge.js", ACCOUNT_BRIDGE_TAG),
        ("/api/chat/account.js", ACCOUNT_TAG),
    ):
        if marker not in html:
            scripts += tag
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
                    "Content-Security-Policy": (
                        "default-src 'self'; "
                        "img-src 'self' data: https://*.googleusercontent.com; "
                        "style-src 'self' 'unsafe-inline' https://accounts.google.com; "
                        "script-src 'self' 'unsafe-inline' https://accounts.google.com; "
                        "connect-src 'self' https://accounts.google.com; "
                        "frame-src https://accounts.google.com; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
                    ),
                },
            )
        assets = {
            "/api/chat/admin-session-ui.js": ADMIN_SESSION_JS,
            "/api/chat/stream-focus.js": STREAM_FOCUS_JS,
            "/api/chat/account-bridge.js": ACCOUNT_BRIDGE_JS,
            "/api/chat/account.js": ACCOUNT_JS,
        }
        if request.method == "GET" and path in assets:
            return FileResponse(assets[path], media_type="application/javascript", headers={"Cache-Control": "no-store, max-age=0", "X-SWRLZ-Chat-UI-Version": UI_VERSION})
        return await call_next(request)

    server.CAPABILITIES["chat-ui-parent-guard"] = {
        "kind": "runtime-serving",
        "ready": True,
        "path": "/api/chat",
        "hotSource": True,
        "enhancementsRequired": True,
        "uiVersion": UI_VERSION,
        "serverManagedBrowserSession": True,
        "durableAccountLayer": True,
        "activeThreadDurableHandoff": True,
        "lineAwareStreamFollow": True,
        "copyableArtifactBlocks": True,
        "queryTolerance": "ignores unrelated query decoration; action=page stays UI, functional actions pass through",
    }
