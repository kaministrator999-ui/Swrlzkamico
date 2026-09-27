"""§wyrlz isolated R39 inference probe; not the canonical account-backed Chat."""
from __future__ import annotations
import json, os, runpy, threading, time, uuid
from pathlib import Path
import spaces
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

def respond(message,history,model_id):
    started=time.perf_counter()
    try:
        generate=(engine()[1] if model_id=="r39" else original_generate)
        payload={"requestId":str(uuid.uuid4()),"prompt":message,"history":[{"role":item.get("role"),"text":item.get("content")} for item in (history or []) if isinstance(item,dict) and item.get("role") in ("user","assistant") and isinstance(item.get("content"),str)],"profileId":"LALM"}
        output=""
        for event in dispatch(model_id,payload,generate,original_generate):
            if not isinstance(event,dict): continue
            kind=str(event.get("type") or "")
            if kind=="DELTA":
                output+=str(event.get("text") or "")
                yield output
            elif kind=="FAILED":
                raise RuntimeError(str(event.get("reason") or "R39 generation failed"))
        if not output: raise RuntimeError("R39 returned no assistant DELTA")
        print(json.dumps({"event":"HF_MODEL_TERMINAL","modelId":model_id,"elapsedSeconds":round(time.perf_counter()-started,3),"chars":len(output)}),flush=True)
    except Exception as exc:
        print(json.dumps({"event":"HF_MODEL_FAILED","modelId":model_id,"errorType":type(exc).__name__,"detail":str(exc)[:300]}),flush=True)
        raise gr.Error(model_id+" unavailable: "+str(exc)[:220])

def available_models():
    return [dict(modelId=r.model_id,label=r.label,available=r.available,checkpoint=r.checkpoint,reason=r.reason) for r in routes()]

@spaces.GPU(duration=1)
def _zerogpu_registration_probe():
    """Registered Gradio handler used only so ZeroGPU can validate this mounted app."""
    return "ZeroGPU handler registered"

with gr.Blocks(title="§wyrlz Inference Laboratory") as demo:
    gr.ChatInterface(
        fn=respond,
        additional_inputs=[gr.Dropdown(choices=[("Original HF · LFM2-350M","stock"),("§wyrlz R39","r39")],value="stock",label="Inference model")],
        title="§wyrlz Inference Laboratory",
        description="Independent model probe. The dragon Chat is at /; HF-only session state is not durable account storage.",
    )
    _zg_button=gr.Button("ZeroGPU registration probe",visible=False)
    _zg_output=gr.Textbox(visible=False)
    _zg_button.click(fn=_zerogpu_registration_probe,inputs=[],outputs=_zg_output,api_visibility="private")
set_generator(lambda payload: engine()[1](payload),original_generate)
app=gr.mount_gradio_app(station_app,demo,path="/probe")
# Keep the pinned original Test Bench available independently of R39.
legacy_source=ROOT/"original_workstation.py"
if not legacy_source.is_file():
    raise RuntimeError("Pinned original Test Bench missing; refuse to replace live Space")
legacy=runpy.run_path(str(legacy_source))
if "demo" not in legacy:
    raise RuntimeError("Original Test Bench does not export its Gradio demo")
app=gr.mount_gradio_app(app,legacy["demo"],path="/legacy")

def _report_zerogpu_startup():
    """mount_gradio_app + uvicorn bypass Gradio's normal launch hook on ZeroGPU."""
    try:
        from spaces.zero import startup as zero_startup
    except ImportError:
        return
    zero_startup()
    print(json.dumps({"event":"ZEROGPU_STARTUP_REPORTED"}),flush=True)

if __name__=="__main__":
    print(json.dumps({"event":"HF_MODEL_ROUTES","routes":available_models()}),flush=True)
    _report_zerogpu_startup()
    uvicorn.run(app,host="0.0.0.0",port=int(os.environ.get("PORT","7860")))
