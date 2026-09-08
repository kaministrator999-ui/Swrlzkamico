"""R39 v28 draft-prefill experiment layered on v27."""
from __future__ import annotations
import hashlib, threading, time, urllib.request

_V27_URL="https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/dev/runtime_hot/r39_engine_v27.py"
_req=urllib.request.Request(_V27_URL,headers={"User-Agent":"swrlz-hot-r39-v28"})
with urllib.request.urlopen(_req,timeout=20) as _response: _source=_response.read(4_000_001)
if len(_source)>4_000_000: raise RuntimeError("R39_V27_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"),_V27_URL,"exec"),globals(),globals())

_DRAFT_LOCK=threading.RLock(); _DRAFT_TTL_SECONDS=120; _DRAFTS={}
_V27_PREFIX_GET=_impl._prefix_get; _V27_GENERATE_EVENTS=generate_events; _V27_INSPECT_ENGINE=inspect_engine

def _draft_key(thread_id): return hashlib.sha256(str(thread_id).encode()).hexdigest()[:40]
def _clone_state(state): return _impl._clone_state(state)
def _prune():
    cutoff=time.time()-_DRAFT_TTL_SECONDS
    for key,item in list(_DRAFTS.items()):
        if float(item.get("at") or 0)<cutoff: _DRAFTS.pop(key,None)

def _draft_tokens(payload):
    p={"prompt":str(payload.get("draft") or ""),"history":list(payload.get("history") or []),"threadId":str(payload.get("threadId") or ""),"profileId":str(payload.get("profileId") or ""),"requestId":"draft-prefill"}
    controlled,_=_controlled_payload(p)
    rendered=_impl.base.render_chat_prompt(controlled)
    suffix="<|im_start|>assistant\n"
    if not rendered.endswith(suffix): raise RuntimeError("draft renderer contract changed")
    rendered=rendered[:-len(suffix)]
    model=_impl._load_model()
    return model,list(model.tokenizer.encode(rendered))

def prefill_draft(payload):
    thread_id=str(payload.get("threadId") or "")
    if not thread_id: return {"ok":False,"code":"DRAFT_THREAD_REQUIRED"}
    _CURSOR_THREAD.thread_id=thread_id; _CURSOR_THREAD.request_id="draft:"+_draft_key(thread_id)[:16]; _CURSOR_THREAD.put_count=0
    started=time.perf_counter()
    try:
        model,tokens=_draft_tokens(payload)
        prefix_len,state,logits=_V27_PREFIX_GET(tokens)
        if state is None: state=_impl.base.RecurrentState(); logits=None; prefix_len=0
        else: state=_clone_state(state); logits=None if logits is None else logits.copy()
        for token in tokens[prefix_len:]: logits=model.forward_token(int(token),state)
        if logits is None: return {"ok":False,"code":"DRAFT_PREFILL_EMPTY"}
        with _DRAFT_LOCK:
            _prune(); _DRAFTS[_draft_key(thread_id)]={"at":time.time(),"tokens":list(tokens),"state":_clone_state(state),"logits":logits.copy()}
        return {"ok":True,"code":"DRAFT_PREFILL_READY","draftTokens":len(tokens),"reusedTokens":prefix_len,"prefilledTokens":len(tokens)-prefix_len,"draftChars":len(str(payload.get("draft") or "")),"elapsedMs":int((time.perf_counter()-started)*1000),"authoritative":False,"ttlSeconds":_DRAFT_TTL_SECONDS}
    finally:
        _CURSOR_THREAD.thread_id=""; _CURSOR_THREAD.request_id=""; _CURSOR_THREAD.put_count=0

def _draft_prefix_get(tokens):
    thread_id=str(getattr(_CURSOR_THREAD,"thread_id","") or "")
    if thread_id:
        key=_draft_key(thread_id)
        with _DRAFT_LOCK:
            _prune(); item=_DRAFTS.get(key)
            if item is not None:
                cached=list(item.get("tokens") or [])
                if cached and len(cached)<=len(tokens) and tokens[:len(cached)]==cached:
                    _DRAFTS.pop(key,None); _set_cursor_status(f"draft cursor promoted · reused={len(cached)}/{len(tokens)} · speculative=true · exactPrefix=true")
                    return len(cached),_clone_state(item["state"]),item["logits"].copy()
                _DRAFTS.pop(key,None); _set_cursor_status(f"draft prefix diverged · speculative cursor discarded safely · draft={len(cached)} current={len(tokens)}")
    return _V27_PREFIX_GET(tokens)

_impl._prefix_get=_draft_prefix_get
_impl.HOT_SERVER_VERSION="2.1.37"; _impl.HOT_REVISION="2.1.37-hot-boundary-v28-speculative-draft-prefill-v3.3"
HOT_SERVER_VERSION=_impl.HOT_SERVER_VERSION; HOT_REVISION=_impl.HOT_REVISION

def generate_events(payload,is_cancelled=None):
    yield from _V27_GENERATE_EVENTS(payload,is_cancelled)

def inspect_engine():
    result=_V27_INSPECT_ENGINE()
    if isinstance(result,dict): result.update({"hotServerVersion":HOT_SERVER_VERSION,"hotRevision":HOT_REVISION,"speculativeDraftPrefill":True,"draftCursorAuthoritative":False,"draftCursorPromotion":"exact-token-prefix-only","draftCursorTtlSeconds":_DRAFT_TTL_SECONDS,"draftDivergenceSafeFallback":True})
    return result
