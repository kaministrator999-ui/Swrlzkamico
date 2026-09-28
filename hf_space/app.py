"""§wyrlz isolated R39 inference probe; not the canonical account-backed Chat."""
from __future__ import annotations
import json, os, queue, runpy, tempfile, threading, time, uuid
from pathlib import Path
import spaces
import gradio as gr
import uvicorn
# Compile against the Space's own Python/NumPy ABI before R39 is imported.
# Keep the existing Python fallback if the build environment lacks a compiler.
try:
    from scripts.build_r39_native import build as build_r39_native
    _native_build = build_r39_native(Path(__file__).resolve().parent)
    _native_build_error = None
    print(json.dumps({"event":"R39_NATIVE_BUILD","result":_native_build}),flush=True)
except Exception as _native_exc:
    _native_build = None
    _native_build_error = f"{type(_native_exc).__name__}: {_native_exc}"
    print(json.dumps({"event":"R39_NATIVE_BUILD_FAILED","errorType":type(_native_exc).__name__,"detail":str(_native_exc)[-700:]}),flush=True)
from station import app as station_app, set_generator
from model_router import dispatch, routes, ModelUnavailable
from original_engine import generate_events as original_generate, load as original_load
from lfm2_700m_engine import generate_events as large_generate

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
            # R39 must never silently spend minutes in the Python/NumPy path.
            # This gate affects only R39; the independent original remains available.
            from swyrlz import r39_native
            native = r39_native.diagnostics()
            if not (native["available"] and native["batchAvailable"]):
                detail = _native_build_error or native["importError"] or native["batchImportError"] or "native extensions unavailable"
                print(json.dumps({"event":"R39_NATIVE_REQUIRED","diagnostics":native,"buildError":_native_build_error}),flush=True)
                raise RuntimeError("R39_NATIVE_REQUIRED: "+detail[:300])
            # Load the accepted v90 chain, rather than a generic HF model.
            candidate=runpy.run_path(str(ROOT/"accepted_runtime/lalm/r39_engine.py"))
            inspect=candidate.get("inspect_engine")
            generate=candidate.get("generate_events")
            if not callable(inspect) or not callable(generate):
                raise RuntimeError("Accepted R39 engine lacks inspect/generate contract")
            state=inspect()
            print(json.dumps({"event":"R39_ENGINE_INSPECT","native":native,"engineId":state.get("engineId"),"nativeBackendAvailable":state.get("nativeBackendAvailable"),"batchInstalled":state.get("batchInstalled")}),flush=True)
            if not (state.get("interactiveReady") or state.get("oneTokenReady")):
                raise RuntimeError("R39 model not ready: "+str(state.get("code") or state))
            # The accepted entrypoint records installation in its module globals,
            # not in inspect_engine()'s returned schema.
            batch_install=candidate.get("_batch_install")
            batch_installed=isinstance(batch_install,dict) and batch_install.get("installed") is True
            print(json.dumps({"event":"R39_BATCH_INSTALL_CHECK","installed":batch_installed,"install":batch_install if isinstance(batch_install,dict) else None}),flush=True)
            if not batch_installed:
                raise RuntimeError("R39_BATCH_PREFILL_NOT_INSTALLED: accepted entrypoint did not confirm batch installation")
            _engine=(inspect,generate)
        return _engine

def respond(message,history,model_id,profile,user_profile):
    """Stream a downloadable diagnostic snapshot while inference is still running."""
    started=time.perf_counter()
    request_id=str(uuid.uuid4())
    history_items=[{"role":item.get("role"),"text":item.get("content")} for item in (history or []) if isinstance(item,dict) and item.get("role") in ("user","assistant") and isinstance(item.get("content"),str)]
    payload={"requestId":request_id,"prompt":message,"history":history_items,"profileId":"LALM","profile":str(profile or "")[:2000],"userProfile":str(user_profile or "")[:2000]}
    events=queue.Queue()
    report={"format":"swrlz-hf-probe-export-v2","modelId":model_id,"requestId":request_id,
            "prompt":message,"history":history_items,"profile":str(profile or "")[:2000],"userProfile":str(user_profile or "")[:2000],"response":"","phase":"STARTING",
            "timeToFirstDeltaSeconds":None,"elapsedSeconds":0.0,"deltaCount":0,
            "events":[],"diagnosticTrace":None,"memoryCandidates":[],"note":"Live probe timeline with structured observable diagnostics; no private chain-of-thought is stored. Download again for the latest snapshot."}
    with tempfile.NamedTemporaryFile(mode="w",encoding="utf-8",suffix=".json",prefix="swrlz-probe-",delete=False) as f:
        export_path=f.name

    def snapshot(phase=None,detail=None):
        if phase is not None:
            report["phase"]=phase
            report["events"].append({"elapsedSeconds":round(time.perf_counter()-started,3),
                                     "phase":phase,**({"detail":str(detail)[:300]} if detail else {})})
        report["elapsedSeconds"]=round(time.perf_counter()-started,3)
        # Atomic replacement avoids serving partially written JSON during a download.
        temporary=export_path+".tmp"
        Path(temporary).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
        os.replace(temporary,export_path)
        return {"phase":report["phase"],"elapsedSeconds":report["elapsedSeconds"],
                "timeToFirstDeltaSeconds":report["timeToFirstDeltaSeconds"],
                "deltaCount":report["deltaCount"],"responseChars":len(report["response"]),
                "requestId":request_id}

    def worker():
        try:
            events.put(("phase","LOADING_BACKEND"))
            generate=(engine()[1] if model_id=="r39" else large_generate if model_id=="700m" else original_generate)
            events.put(("phase","INFERENCE_RUNNING"))
            for event in dispatch(model_id,payload,generate,original_generate,large_generate):
                events.put(("event",event))
            events.put(("done",None))
        except Exception as exc:
            events.put(("error",exc))

    status=snapshot("STARTING")
    yield "",export_path,status
    threading.Thread(target=worker,daemon=True,name="swrlz-probe-"+request_id[:8]).start()
    while True:
        try:
            kind,value=events.get(timeout=2.0)
        except queue.Empty:
            # The inference worker may still be blocked in prefill. Keep the
            # report downloadable and update elapsed time without fake tokens.
            status=snapshot()
            yield report["response"],export_path,status
            continue
        if kind=="phase":
            status=snapshot(value)
        elif kind=="error":
            status=snapshot("FAILED",type(value).__name__+": "+str(value))
            yield report["response"],export_path,status
            print(json.dumps({"event":"HF_MODEL_FAILED","modelId":model_id,"requestId":request_id,
                              "elapsedSeconds":report["elapsedSeconds"],"detail":str(value)[:300]}),flush=True)
            raise gr.Error(model_id+" unavailable: "+str(value)[:220])
        elif kind=="done":
            if not report["response"]:
                status=snapshot("FAILED","No assistant DELTA")
                yield report["response"],export_path,status
                raise gr.Error(model_id+" returned no assistant text")
            status=snapshot("COMPLETE")
            yield report["response"],export_path,status
            print(json.dumps({"event":"HF_MODEL_TERMINAL","modelId":model_id,"requestId":request_id,
                              "elapsedSeconds":report["elapsedSeconds"],"chars":len(report["response"])}),flush=True)
            return
        elif kind=="event" and isinstance(value,dict):
            event_type=str(value.get("type") or "")
            if event_type=="DIAGNOSTIC":
                trace=value.get("trace")
                if isinstance(trace,dict):report["diagnosticTrace"]=trace
                status=snapshot("DIAGNOSTIC_READY")
                yield report["response"],export_path,status
                continue
            if event_type=="MEMORY_CANDIDATE":
                candidate=value.get("candidate")
                if isinstance(candidate,dict):report["memoryCandidates"].append(candidate)
                status=snapshot("MEMORY_CANDIDATE")
                yield report["response"],export_path,status
                continue
            if event_type=="DELTA":
                if report["timeToFirstDeltaSeconds"] is None:
                    report["timeToFirstDeltaSeconds"]=round(time.perf_counter()-started,3)
                    snapshot("FIRST_DELTA")
                report["response"]+=str(value.get("text") or "")
                report["deltaCount"]+=1
                status=snapshot("GENERATING")
            elif event_type=="FAILED":
                status=snapshot("FAILED",value.get("reason") or "Generation failed")
                yield report["response"],export_path,status
                raise gr.Error(str(value.get("reason") or "Generation failed")[:220])
            elif event_type in ("COMPLETE","COMPLETED"):
                status=snapshot("FINALIZING")
            else:
                # Preserve bounded, structured engine diagnostics during prefill.
                # Exclude arbitrary payload fields, prompt text and secrets.
                detail=value.get("reason") or value.get("phase")
                status=snapshot("ENGINE_"+event_type[:32],detail)
                if event_type in ("STATUS","ROUTE"):
                    report["events"][-1]["enginePhase"]=str(value.get("phase") or "")[:80]
                    for metric in ("totalLatencyMs","firstDeltaLatencyMs","loadLatencyMs"):
                        if isinstance(value.get(metric),(int,float)):
                            report["events"][-1][metric]=value[metric]
                    snapshot()
        else:
            status=snapshot()
        yield report["response"],export_path,status

def available_models():
    return [dict(modelId=r.model_id,label=r.label,available=r.available,checkpoint=r.checkpoint,reason=r.reason) for r in routes()]

@spaces.GPU(duration=1)
def _zerogpu_registration_probe():
    """Registered Gradio handler used only so ZeroGPU can validate this mounted app."""
    return "ZeroGPU handler registered"

with gr.Blocks(title="§wyrlz Inference Laboratory") as demo:
    gr.ChatInterface(
        fn=respond,
        additional_outputs=[gr.File(label="Download LIVE probe JSON (available during generation)",interactive=False),gr.JSON(label="Live inference status")],
        additional_inputs=[
            gr.Dropdown(choices=[("Original HF · LFM2-350M","stock"),("§wyrlz R39","r39"),("LFM2-700M Q4_K_M","700m")],value="700m",label="Inference model"),
            gr.Textbox(label="Optional §wyrlz customization · layered over built-in Mirror Muse core",lines=9,max_lines=18,max_length=2000,value="",info="Optional user-authored assistant customization. The built-in §wyrlzara Mirror Muse + Phoenix Armor/Core/Project/Creative profile is always active and is not replaced by this field."),
            gr.Textbox(label="Test user profile · editable",lines=5,max_lines=12,max_length=2000,value=(
                "Name: Kami. Collaborative technical/creative partner testing §wyrlz. "
                "Uses casual humor, callbacks, analogies and direct corrections. Prefers simple correct answers before "
                "needless abstraction, evidence over assumptions, and precise iterative debugging."
            ),info="Current-user identity/context for testing. Defaulted to Kami; replace this for another user."),
        ],
        title="§wyrlz Inference Laboratory",
        description="Independent model probe. The dragon Chat is at /; HF-only session state is not durable account storage.",
    )
    _zg_button=gr.Button("ZeroGPU registration probe",visible=False)
    _zg_output=gr.Textbox(visible=False)
    _zg_button.click(fn=_zerogpu_registration_probe,inputs=[],outputs=_zg_output,api_visibility="private")
set_generator(lambda payload: engine()[1](payload),original_generate,large_generate)
app=gr.mount_gradio_app(station_app,demo,path="/probe",ssr_mode=False)
# Keep the pinned original Test Bench available independently of R39.
legacy_source=ROOT/"original_workstation.py"
if not legacy_source.is_file():
    raise RuntimeError("Pinned original Test Bench missing; refuse to replace live Space")
legacy=runpy.run_path(str(legacy_source))
if "demo" not in legacy:
    raise RuntimeError("Original Test Bench does not export its Gradio demo")
app=gr.mount_gradio_app(app,legacy["demo"],path="/legacy",ssr_mode=False)

def _warm_backends():
    """Move one-time model setup off the first interactive request."""
    for name,loader in (("stock",original_load),("r39",engine)):
        start=time.perf_counter()
        try:
            loader()
            print(json.dumps({"event":"HF_WARMUP_READY","modelId":name,"elapsedSeconds":round(time.perf_counter()-start,3)}),flush=True)
        except Exception as exc:
            print(json.dumps({"event":"HF_WARMUP_FAILED","modelId":name,"errorType":type(exc).__name__,"detail":str(exc)[:300]}),flush=True)

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
    threading.Thread(target=_warm_backends,daemon=True,name="swrlz-model-warmup").start()
    # Bind the Python ASGI app to the Space application port.
    uvicorn.run(app,host="0.0.0.0",port=int(os.environ.get("APP_PORT","7860")))
