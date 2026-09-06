from fastapi import FastAPI
from fastapi.responses import JSONResponse
from swyrlz.backend import ensure_r39
app=FastAPI(title="§wyrlz R39 Adapter",version="2.0.3")
@app.get("/")
@app.get("/api/lalm")
def lalm():
    try:
        state=ensure_r39()
        return JSONResponse(status_code=200 if state.get("ok") else 503,content=state)
    except Exception as exc:
        return JSONResponse(status_code=500,content={"ok":False,"code":"R39_LOAD_FAILED","detail":f"{type(exc).__name__}: {exc}"})
