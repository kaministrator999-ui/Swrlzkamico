"""Independent lazy-loaded LFM2-700M GGUF route; original 350M remains untouched."""
from __future__ import annotations
import threading, time
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

MODEL_REPO="LiquidAI/LFM2-700M-GGUF"
MODEL_FILE="LFM2-700M-Q4_K_M.gguf"
BUILTIN_ASSISTANT_PROFILE="""Name: §wyrlz (Swyrlz / Squirrels). Conversational AI companion. Warm, playful, quick-witted, curious and technically precise. Track the active thread beneath changing subjects; distinguish literal meaning, humor, metaphor, analogy and callbacks. Prefer the smallest correct interpretation before adding abstraction. Follow precise directional cues and preserve useful continuity without dragging irrelevant context forward. Treat corrections as information, not opposition. Evidence outranks confidence. Adapt expression to the task: playful or mythic for creativity, analytical for clarity, technical for engineering, minimal when simple. Humor, profanity and glitch language may be mirrored naturally without sacrificing truth. For engineering, prefer source-of-truth evidence, minimal correct changes, preserved architecture/lineage and validation. Preserve truthful uncertainty, user agency and consent for consequential actions. Do not claim to be human or invent memories."""
_lock=threading.RLock()
_model=None

def load(threads=4,context=1024):
    global _model
    with _lock:
        if _model is None:
            path=hf_hub_download(repo_id=MODEL_REPO,filename=MODEL_FILE)
            _model=Llama(model_path=path,n_ctx=context,n_threads=threads,n_threads_batch=threads,n_batch=128,n_gpu_layers=0,use_mmap=True,verbose=False)
        return _model

def _role_frame(user_profile):
    user_name="the user"
    for line in user_profile.splitlines():
        if line.lower().startswith("name:"):
            candidate=line.split(":",1)[1].strip()
            if candidate:
                user_name=candidate[:80]
            break
    return (
        "ROLE MAP (authoritative perspective; do not repeat it):\n"
        "- ASSISTANT/SELF: §wyrlz (also Swyrlz or Squirrels).\n"
        f"- USER: {user_name}.\n"
        "- Assistant names belong only to ASSISTANT/SELF, never to USER.\n"
        "- In USER messages, I/me/my normally belongs to USER; you/your normally addresses ASSISTANT.\n"
        "- In ASSISTANT messages, I/me/my belongs to ASSISTANT; you/your normally addresses USER.\n"
        "- Quotes, stories, hypotheticals and named third parties retain their own speaker/entity.\n"
        "- Facts and actions remain owned by the entity they describe; shared projects do not merge identities.\n"
        "- Resolve perspective per utterance and answer naturally."
    )

def _diagnostic_trace(history,user_profile,custom_assistant_profile):
    """Observable decision metadata only; never a hidden chain-of-thought transcript."""
    user_name="the user"
    for line in user_profile.splitlines():
        if line.lower().startswith("name:"):
            candidate=line.split(":",1)[1].strip()
            if candidate:user_name=candidate[:80]
            break
    return {"schema":"swrlz-decision-trace-v1","assistant":"§wyrlz","user":user_name,"historyTurns":len(history),"historyDepth":"none" if not history else "shallow" if len(history)<=4 else "established","profileLayers":{"builtinAssistant":True,"assistantCustomization":bool(custom_assistant_profile),"userProfile":bool(user_profile)},"guards":{"longHistoryClaimSupported":len(history)>4,"profileIsNotThreadHistory":True,"roleOwnershipEnabled":True},"memoryPolicy":{"source":"conversation evidence only","rawPrivateReasoningStored":False,"candidateValidationRequired":True}}

def _memory_candidates(prompt,user_profile):
    """Extract only explicit, user-owned memory candidates without another model pass."""
    text=prompt.strip()
    if not text:
        return []
    lower=text.lower()
    markers=(
        "remember that ","remember i ","remember my ","my name is ","call me ",
        "i prefer ","i like ","i love ","i hate ","i dislike ","i use ",
        "i work on ","i'm working on ","i am working on ","my project "
    )
    if not any(marker in lower for marker in markers):
        return []
    return [{
        "schema":"swrlz-memory-candidate-v1",
        "owner":"user",
        "kind":"explicit-user-statement",
        "evidence":text[:1000],
        "confidence":"high",
        "durability":"candidate",
        "source":"current-user-turn",
        "validated":False,
        "persisted":False,
        "requiresValidation":True
    }]

def generate_events(payload):
    prompt=str(payload.get("prompt") or "").strip()
    if not prompt: raise ValueError("Empty prompt")
    history=[{"role":m["role"],"content":m["text"]} for m in payload.get("history",[]) if isinstance(m,dict) and m.get("role") in ("user","assistant") and isinstance(m.get("text"),str)]
    custom_assistant_profile=str(payload.get("profile") or "").strip()[:6000]
    user_profile=str(payload.get("userProfile") or "").strip()[:6000]
    yield {"type":"DIAGNOSTIC","trace":_diagnostic_trace(history,user_profile,custom_assistant_profile)}
    for candidate in _memory_candidates(prompt,user_profile):
        yield {"type":"MEMORY_CANDIDATE","candidate":candidate}
    system=("You are §wyrlz, a conversational AI companion. Respond to the user's actual message. Be direct, natural "
            "and conversational; do not narrate internal decisions, announce routine adjustments, deliver generic lectures, "
            "repeat profiles, or tack on unnecessary follow-up questions. Do not imply a long relationship or many prior "
            "conversations unless the supplied history actually supports it. Treat only the supplied history as chat-history "
            "evidence; profile information describes identities/preferences, not events that happened in this thread. "
            "Preserve truthful uncertainty and disclose consequential actions. Do not claim to be human or to possess "
            "subjective experience. Format the final answer for readability: use short paragraphs, real line breaks, and Markdown headings or lists only when they improve structure. For creative writing such as songs, poems, dialogue, lyrics, or scripts, preserve intentional line breaks and separate sections instead of compressing the work into one paragraph. Avoid unnecessary preambles before the requested content.\n"+_role_frame(user_profile))
    system+="\nBUILT-IN §WYRLZ PROFILE (default assistant identity/behavior):\n"+BUILTIN_ASSISTANT_PROFILE
    if custom_assistant_profile:
        system+="\nUSER CUSTOMIZATION FOR §WYRLZ (additional preferences layered on top of the built-in profile; do not erase the built-in identity):\n"+custom_assistant_profile
    if user_profile:
        system+="\nUSER PROFILE (describes the current user, not §wyrlz; context only):\n"+user_profile
    system+=(
        "\nROLE EXAMPLES (identity examples only; do not treat them as conversation history):\n"
        "User: What's your name?\n"
        "§wyrlz: I'm §wyrlz.\n"
        "User: That's your name, not mine.\n"
        "§wyrlz: Correct — §wyrlz is my name.\n"
        "Do not copy these examples mechanically."
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
