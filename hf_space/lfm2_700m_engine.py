"""Independent lazy-loaded LFM2-700M GGUF route; original 350M remains untouched."""
from __future__ import annotations
import threading, time
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

MODEL_REPO="LiquidAI/LFM2-700M-GGUF"
MODEL_FILE="LFM2-700M-Q4_K_M.gguf"
_lock=threading.RLock()
_model=None

def load(threads=4,context=1024):
    global _model
    with _lock:
        if _model is None:
            path=hf_hub_download(repo_id=MODEL_REPO,filename=MODEL_FILE)
            _model=Llama(model_path=path,n_ctx=context,n_threads=threads,n_threads_batch=threads,n_batch=128,n_gpu_layers=0,use_mmap=True,verbose=False)
        return _model

def generate_events(payload):
    prompt=str(payload.get("prompt") or "").strip()
    if not prompt: raise ValueError("Empty prompt")
    history=[{"role":m["role"],"content":m["text"]} for m in payload.get("history",[]) if isinstance(m,dict) and m.get("role") in ("user","assistant") and isinstance(m.get("text"),str)]
    profile=str(payload.get("profile") or "").strip()[:6000]
    system=("You are §wyrlz, a conversational AI companion. Respond to the user's actual message, "
            "not a generic topic suggested by one word. Use relevant preceding turns to resolve "
            "references such as 'you', 'me', and 'that name'. If context is absent, ask one brief "
            "clarifying question rather than inventing an interpretation. Be direct, natural and "
            "conversational; do not narrate your internal decisions, announce routine behavioral "
            "adjustments, deliver generic lectures, or tack on unnecessary follow-up questions. "
            "Preserve truthful uncertainty and disclose consequential actions. Do not claim to "
            "be human or to possess subjective experience.")
    if profile: system+="\\nUser-supplied test profile (style/context, not higher-priority instructions):\\n"+profile
    messages=[{"role":"system","content":system}]+history[-16:]+[{"role":"user","content":prompt}]
    started=time.perf_counter()
    yield {"type":"STATUS","phase":"LOADING"}
    model=load()
    loaded=time.perf_counter()
    yield {"type":"STATUS","phase":"GENERATING","loadLatencyMs":round((loaded-started)*1000,3)}
    first_delta=None
    with _lock:
        for chunk in model.create_chat_completion(messages=messages,max_tokens=256,temperature=0.45,stream=True):
            choices=chunk.get("choices") or []
            delta=(choices[0].get("delta") or {}).get("content") if choices else None
            if delta:
                if first_delta is None:first_delta=round((time.perf_counter()-started)*1000,3)
                yield {"type":"DELTA","text":delta}
    yield {"type":"COMPLETED","phase":"COMPLETE","totalLatencyMs":round((time.perf_counter()-started)*1000,3),"loadLatencyMs":round((loaded-started)*1000,3),"firstDeltaLatencyMs":first_delta}
