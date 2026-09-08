"""R39 v29 shared speculative draft cursor experiment."""
from __future__ import annotations
import urllib.request

URL='https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/dev/runtime_hot/r39_engine_v28.py'
req=urllib.request.Request(URL,headers={'User-Agent':'swrlz-hot-r39-v29'})
with urllib.request.urlopen(req,timeout=20) as response: source=response.read(4_000_001)
if len(source)>4_000_000: raise RuntimeError('R39_V28_SOURCE_TOO_LARGE')
exec(compile(source.decode('utf-8'),URL,'exec'),globals(),globals())

V28_PREFILL=prefill_draft
V28_INSPECT=inspect_engine

def _draft_thread(thread_id): return 'draft:'+str(thread_id)

def prefill_draft(payload):
    result=V28_PREFILL(payload)
    if not result.get('ok'): return result
    thread_id=str(payload.get('threadId') or '')
    with _DRAFT_LOCK:
        item=_DRAFTS.get(_draft_key(thread_id))
        if item is not None and _RUNTIME_CACHE is not None:
            _persist_cursor(_draft_thread(thread_id),list(item['tokens']),item['state'],item['logits'])
            result['sharedDraftCommitted']=True
            result['sharedDraftBackend']='vercel-runtime-cache'
        else:
            result['sharedDraftCommitted']=False
    return result

def _draft_prefix_get_v29(tokens):
    thread_id=str(getattr(_CURSOR_THREAD,'thread_id','') or '')
    if thread_id:
        with _DRAFT_LOCK:
            _prune(); item=_DRAFTS.get(_draft_key(thread_id))
            if item is not None:
                cached=list(item.get('tokens') or [])
                if cached and len(cached)<=len(tokens) and tokens[:len(cached)]==cached:
                    _DRAFTS.pop(_draft_key(thread_id),None)
                    _set_cursor_status(f'draft cursor promoted · reused={len(cached)}/{len(tokens)} · exactPrefix=true · crossWorker=false')
                    return len(cached),_clone_state(item['state']),item['logits'].copy()
                _DRAFTS.pop(_draft_key(thread_id),None)
        if _RUNTIME_CACHE is not None:
            reused,state,logits=_restore_cursor(_draft_thread(thread_id),tokens)
            if reused>0 and state is not None and logits is not None:
                _set_cursor_status(f'draft cursor promoted · reused={reused}/{len(tokens)} · exactPrefix=true · crossWorker=true')
                return reused,state,logits
    return _V27_PREFIX_GET(tokens)

_impl._prefix_get=_draft_prefix_get_v29
_impl.HOT_SERVER_VERSION='2.1.38'
_impl.HOT_REVISION='2.1.38-hot-boundary-v29-shared-draft-prefill-v3.4'
HOT_SERVER_VERSION=_impl.HOT_SERVER_VERSION
HOT_REVISION=_impl.HOT_REVISION

def inspect_engine():
    result=V28_INSPECT()
    if isinstance(result,dict): result.update({'hotServerVersion':HOT_SERVER_VERSION,'hotRevision':HOT_REVISION,'sharedSpeculativeDraftCursor':_RUNTIME_CACHE is not None,'draftCursorCrossWorkerPromotion':True})
    return result
