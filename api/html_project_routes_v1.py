"""Isolated browser delivery for user-authored HTML projects in the existing Chat Space.

Never mount user assets beneath the authenticated chat app or serve them without
the HTTP CSP sandbox response header: iframe sandbox alone is insufficient.
"""
from __future__ import annotations

from pathlib import Path
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

MARKER = "swrlz-html-project-isolation-v1"
PROJECT_PATH = "/projects"
# This forces an opaque origin, even when the HTML URL is opened directly.
# Deliberately omit allow-same-origin, allow-forms and allow-top-navigation.
SANDBOX_POLICY = (
    "sandbox allow-scripts; "
    "default-src 'none'; "
    "script-src 'unsafe-inline' https: blob:; "
    "style-src 'unsafe-inline' https:; "
    "img-src https: data: blob:; "
    "font-src https: data:; "
    "connect-src https:; "
    "object-src 'none'; "
    "base-uri 'none'; "
    "form-action 'none'; "
    "frame-ancestors 'self'; "
    "upgrade-insecure-requests"
)


class SandboxedProjectFiles(StaticFiles):
    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        response.headers["Content-Security-Policy"] = SANDBOX_POLICY
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-store"
        # For ES modules loaded by the opaque-origin sandbox. No credentials.
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Cross-Origin-Resource-Policy"] = "cross-origin"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response


def install(app, root):
    root = Path(root)
    app.mount(
        PROJECT_PATH,
        SandboxedProjectFiles(
            directory=root / "chat" / "§wyrlz" / "projects",
            html=True,
            check_dir=False,
        ),
        name="sandboxed-html-projects",
    )

    @app.get("/api/html-projects/security")
    def html_project_security():
        return JSONResponse(
            {"contract": MARKER, "isolated": True, "projectPath": PROJECT_PATH,
             "cspSandbox": "allow-scripts", "sameOriginPermission": False},
            headers={"Cache-Control": "no-store", "X-Content-Type-Options": "nosniff"},
        )
