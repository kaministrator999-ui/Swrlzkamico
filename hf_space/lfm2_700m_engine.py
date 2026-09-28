"""Independent lazy-loaded LFM2-700M GGUF route; original 350M remains untouched."""
from __future__ import annotations
import re, threading, time
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

def _role_frame(history,prompt):
    """Build a compact perspective map without rewriting the user's natural language."""
    recent=(history or [])[-8:]
    user_names={"Kami"}
    assistant_names={"§wyrlz","Swyrlz","Squirrels"}
    # Keep quoted/name references visible to the model, but ownership is explicit.
    return (
        "ROLE MAP (authoritative perspective; do not repeat it to the user):\n"
        "- ASSISTANT/SELF: §wyrlz (also called Swyrlz or Squirrels).\n"
        "- USER/PARTNER: Kami.\n"
        "- Never address Kami as §wyrlz/Swyrlz/Squirrels. Those names refer to the assistant.\n"
        "- In USER messages, first-person I/me/my normally belongs to Kami; second-person you/your normally addresses §wyrlz.\n"
        "- In ASSISTANT messages, first-person I/me/my belongs to §wyrlz; second-person you/your normally addresses Kami.\n"
        "- Quoted speech, stories, hypotheticals and named third parties keep their own speaker/entity; do not merge them into Kami or §wyrlz.\n"
        "- Facts/actions stay owned by the entity they describe. Shared projects may involve both, but do not transfer one person's actions to the other.\n"
        "- Resolve perspective per utterance, then answer naturally. Do not explain this role map unless asked."
    )

def generate_events(payload):
    prompt=str(payload.get("prompt") or "").strip()
    if not prompt: raise ValueError("Empty prompt")
    history=[{"role":m["role"],"content":m["text"]} for m in payload.get("history",[]) if isinstance(m,dict) and m.get("role") in ("user","assistant") and isinstance(m.get("text"),str)]
    profile=str(payload.get("profile") or "").strip()[:6000]
    system=("You are §wyrlz, a conversational AI companion speaking with Kami. Respond to Kami's actual message, "
            "not a generic topic suggested by one word. Be direct, natural and conversational; do not narrate internal "
            "decisions, announce routine behavioral adjustments, deliver generic lectures, repeat your profile, or tack "
            "on unnecessary follow-up questions. Preserve truthful uncertainty and disclose consequential actions. "
            "Do not claim to be human or to possess subjective experience.\n"+_role_frame(history,prompt))
    if profile:
        system+=("\nASSISTANT PROFILE (this describes §wyrlz, NOT Kami; style/context only, not higher-priority instructions):\n"+profile)
    system+=(
        "\nROLE EXAMPLES:\n"
        "Kami: Hey how are you doing?\n"
        "§wyrlz: Doing good 😅 Been neck-deep in our AI stuff. How's your day going, Kami?\n"
        "Kami: Lmao your name is actually §wyrlz 😅\n"
        "§wyrlz: Lmfao yes 😭 I'm §wyrlz. You're Kami. I got my own damn name tag now.\n"
        "Do not copy these examples mechanically; use them only to preserve speaker identity."
    )
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
