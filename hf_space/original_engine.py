"""Original HF LFM2 inference path, kept independent of R39."""
from __future__ import annotations
import os, threading, time, json
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

MODEL_REPO="LiquidAI/LFM2-350M-GGUF"
MODEL_FILE="LFM2-350M-Q4_K_M.gguf"
MODEL_REVISION="31cd51db1365"
_lock=threading.RLock()
_model=None

def prepare():
    return hf_hub_download(repo_id=MODEL_REPO,filename=MODEL_FILE,revision=MODEL_REVISION)

def load(threads=4,context=1024):
    global _model
    with _lock:
        if _model is None:
            path=prepare()
            _model=Llama(model_path=path,n_ctx=context,n_threads=threads,n_threads_batch=threads,n_batch=128,n_gpu_layers=0,use_mmap=True,verbose=False)
        return _model

def generate_events(payload):
    """Station event contract; stream deltas without replacing the original model."""
    prompt=str(payload.get("prompt") or "").strip()
    if not prompt: raise ValueError("Empty prompt")
    history=[{"role":m["role"],"content":m["text"]} for m in payload.get("history",[]) if isinstance(m,dict) and m.get("role") in ("user","assistant") and isinstance(m.get("text"),str)]
    messages=(history[-16:]+[{"role":"user","content":prompt}])
    started=time.perf_counter()
    yield {"type":"STATUS","phase":"LOADING"}
    model=load()
    loaded=time.perf_counter()
    yield {"type":"STATUS","phase":"GENERATING","loadLatencyMs":round((loaded-started)*1000,3)}
    # llama.cpp model context is shared; serialize independent conversations.
    first_delta=None
    with _lock:
        for chunk in model.create_chat_completion(messages=messages,max_tokens=128,temperature=0.3,stream=True):
            choices=chunk.get("choices") or []
            delta=(choices[0].get("delta") or {}).get("content") if choices else None
            if delta:
                if first_delta is None:first_delta=round((time.perf_counter()-started)*1000,3)
                yield {"type":"DELTA","text":delta}
    yield {"type":"COMPLETED","phase":"COMPLETE","totalLatencyMs":round((time.perf_counter()-started)*1000),"loadLatencyMs":round((loaded-started)*1000,3),"firstDeltaLatencyMs":first_delta}
