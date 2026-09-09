from __future__ import annotations

import json
from pathlib import Path

from fastapi import Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse

from api import chat
from api import user_data

ROOT = Path(__file__).resolve().parents[1]
ACCOUNT_JS = ROOT / "web" / "chat_account.js"
_INSTALLED = False


def install(server):
    global _INSTALLED
    if _INSTALLED:
        return
    _INSTALLED = True

    @chat.app.get("/auth/config", include_in_schema=False)
    async def auth_config():
        return JSONResponse({
            "googleClientId": __import__("os").getenv("GOOGLE_OAUTH_CLIENT_ID", ""),
            "persistentStore": bool(__import__("os").getenv("KV_REST_API_URL") or __import__("os").getenv("UPSTASH_REDIS_REST_URL")),
            "accountContract": "swrlz-user-account-v1",
            "chatClientOverlay": "1.3.31",
        }, headers={"Cache-Control": "no-store"})

    @chat.app.get("/auth/me", include_in_schema=False)
    async def auth_me(request: Request):
        return user_data.auth_response(request)

    @chat.app.post("/auth/google", include_in_schema=False)
    async def auth_google(request: Request):
        try:
            body = json.loads((await request.body()) or b"{}")
        except Exception:
            return JSONResponse({"ok": False, "code": "INVALID_JSON"}, status_code=400)
        credential = str(body.get("credential") or "").strip()
        if not credential:
            return JSONResponse({"ok": False, "code": "GOOGLE_CREDENTIAL_REQUIRED"}, status_code=400)
        return user_data.login_response(request, credential)

    @chat.app.post("/auth/logout", include_in_schema=False)
    async def auth_logout(request: Request):
        return user_data.logout_response(request)

    @chat.app.get("/data", include_in_schema=False)
    async def user_data_get(request: Request):
        user = user_data.current_user(request)
        if not user:
            return JSONResponse({"ok": False, "code": "AUTH_REQUIRED"}, status_code=401)
        return JSONResponse({"ok": True, "user": user, "data": user_data.load_user_data(str(user["userId"]))}, headers={"Cache-Control": "no-store"})

    @chat.app.put("/data", include_in_schema=False)
    async def user_data_put(request: Request):
        user = user_data.current_user(request)
        if not user:
            return JSONResponse({"ok": False, "code": "AUTH_REQUIRED"}, status_code=401)
        try:
            body = json.loads((await request.body()) or b"{}")
        except Exception:
            return JSONResponse({"ok": False, "code": "INVALID_JSON"}, status_code=400)
        result = user_data.save_user_data(str(user["userId"]), body if isinstance(body, dict) else {})
        return JSONResponse({"ok": True, "data": result, "user": user}, headers={"Cache-Control": "no-store"})

    @chat.app.get("/assets/account.js", include_in_schema=False)
    async def account_js():
        return FileResponse(ACCOUNT_JS, media_type="application/javascript", headers={"Cache-Control": "no-store"})

    @server.app.middleware("http")
    async def identity_middleware(request: Request, call_next):
        response = await call_next(request)
        if request.method == "GET" and request.url.path.rstrip("/") == "/api/chat" and response.headers.get("content-type", "").startswith("text/html"):
            body = b"".join([chunk async for chunk in response.body_iterator])
            html = body.decode("utf-8", "replace")
            html = html.replace("</body>", '<script src="/api/chat/assets/account.js"></script></body>')
            headers = dict(response.headers)
            response = HTMLResponse(html, status_code=response.status_code, headers=headers)
            csp = response.headers.get("Content-Security-Policy", "")
            if csp:
                csp = csp.replace("script-src 'self' 'unsafe-inline'", "script-src 'self' 'unsafe-inline' https://accounts.google.com")
                csp = csp.replace("connect-src 'self'", "connect-src 'self' https://accounts.google.com")
                csp += "; frame-src https://accounts.google.com"
                response.headers["Content-Security-Policy"] = csp
        return response
