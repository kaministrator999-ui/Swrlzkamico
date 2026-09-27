"""§wyrlz isolated R39 inference probe; not the canonical account-backed Chat."""
from __future__ import annotations
import json, os, runpy, threading, time, uuid
from pathlib import Path
import gradio as gr
import uvicorn
from station import app as station_app, set_generator
from model_router import dispatch, routes, ModelUnavailable
from original_engine import generate_events as original_generate

ROOT=Path(__file__).resolve().parent
PROVENANCE=json.loads((ROOT/"MODEL_PROVENANCE.json").read_text(encoding="utf-8"))
os.environ["SWRLZ_REPO_ROOT"]=str(ROOT)
os.environ["SWRLZ_GITHUB_OWNER"]="kaministrator999-ui"
os.environ["SWRLZ_GITHUB_REPO"]="Swrlzkamico"
os.environ["SWRLZ_GITHUB_REF"]=PROVENANCE["sourceCommit"]
os.environ["SWRLZ_R39_TRANSPORT_MANIFEST"]=str(ROOT/"lalm§wyrlz.transport.json")
_engine=None
_lock=threading.Lock()

def engine():
    global _engine
    with _lock:
        if _engine is None:
            # Load the accepted v90 chain, rather than a generic HF model.
            candidate=runpy.run_path(str(ROOT/"accepted_runtime/lalm/r39_engine.py"))
            inspect=candidate.get("inspect_engine")
            generate=candidate.get("generate_events")
            if not callable(inspect) or not callable(generate):
                raise RuntimeError("Accepted R39 engine lacks inspect/generate contract")
            state=inspect()
            if not (state.get("interactiveReady") or state.get("oneTokenReady")):
                raise RuntimeError("R39 model not ready: "+str(state.get("code") or state))
            _engine=(inspect,generate)
        return _engine

def respond(message,history):
    started=time.perf_counter()
    try:
        inspect,generate=engine()
        payload={"requestId":str(uuid.uuid4()),"prompt":message,"history":[{"role":item.get("role"),"text":item.get("content")} for item in (history or []) if isinstance(item,dict) and item.get("role") in ("user","assistant") and isinstance(item.get("content"),str)],"profileId":"LALM"}
        output=""
        for event in dispatch("r39",payload,generate):
            if not isinstance(event,dict): continue
            kind=str(event.get("type") or "")
            if kind=="DELTA":
                output+=str(event.get("text") or "")
                yield output
            elif kind=="FAILED":
                raise RuntimeError(str(event.get("reason") or "R39 generation failed"))
        if not output: raise RuntimeError("R39 returned no assistant DELTA")
        print(json.dumps({"event":"HF_R39_TERMINAL","elapsedSeconds":round(time.perf_counter()-started,3),"chars":len(output)}),flush=True)
    except Exception as exc:
        print(json.dumps({"event":"HF_R39_FAILED","errorType":type(exc).__name__,"detail":str(exc)[:300]}),flush=True)
        raise gr.Error("R39 unavailable: "+str(exc)[:220])

def available_models():
    return [dict(modelId=r.model_id,label=r.label,available=r.available,checkpoint=r.checkpoint,reason=r.reason) for r in routes()]

demo=gr.ChatInterface(fn=respond,type="messages",title="§wyrlz R39 — isolated inference candidate",description="Real accepted R39 inference probe. Canonical clean-room Chat and account persistence are not migrated yet.")
set_generator(lambda payload: engine()[1](payload),original_generate)
app=gr.mount_gradio_app(station_app,demo,path="/probe")
if __name__=="__main__":
    print(json.dumps({"event":"HF_MODEL_ROUTES","routes":available_models()}),flush=True)
    uvicorn.run(app,host="0.0.0.0",port=int(os.environ.get("PORT","7860")))
