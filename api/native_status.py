from __future__ import annotations

from fastapi.responses import JSONResponse


def install(server) -> None:
    @server.app.get("/api/lalm/native")
    async def lalm_native_status():
        try:
            from swyrlz import r39_native
            payload = r39_native.diagnostics() if hasattr(r39_native, "diagnostics") else {
                "available": bool(r39_native.available()),
                "diagnosticsAvailable": False,
            }
            return JSONResponse({"ok": True, "serverVersion": server.VERSION, **payload}, headers={"Cache-Control": "no-store"})
        except Exception as exc:
            return JSONResponse(
                status_code=500,
                content={"ok": False, "serverVersion": server.VERSION, "error": f"{type(exc).__name__}: {exc}"},
                headers={"Cache-Control": "no-store"},
            )

    server.CAPABILITIES["native-r39-diagnostics"] = {
        "kind": "runtime-observability",
        "ready": True,
        "endpoint": "/api/lalm/native",
    }
