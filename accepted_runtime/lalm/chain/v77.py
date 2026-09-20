"""R39 v77: first-time prefill kernel breakdown camera over v76.

Observability only. Times the existing batch-prefill primitives without changing
prompt construction, batching policy, cache policy, sampling, or model math.
"""
from __future__ import annotations
import json,threading,time

_V77_CONTRACT="r39-v77-prefill-kernel-profile-v1"
_V76_GENERATE=generate_events
_V76_INSPECT=inspect_engine
_V77_TLS=threading.local()
_V77_PATCHED=False

def _v77_bucket(name):
    n=str(name)
    if ".ffn_" in n:return "ffnMatmat"
    if ".attn_" in n:return "attnMatmat"
    if ".shortconv." in n:return "shortconvMatmat"
    return "otherMatmat"

def _v77_add(key,seconds):
    m=getattr(_V77_TLS,"metrics",None)
    if isinstance(m,dict):
        m[key]=float(m.get(key,0.0))+float(seconds)
        m[key+"Calls"]=int(m.get(key+"Calls",0))+1

def _v77_patch():
    global _V77_PATCHED
    if _V77_PATCHED:return
    batch=globals().get("_batch")
    if batch is None:return
    originals={}
    for name in ("_matmat","_causal_gqa","_rms_cols","_head_rms_cols","_rope_cols"):
        fn=getattr(batch,name,None)
        if callable(fn):originals[name]=fn
    if "_matmat" in originals:
        fn=originals["_matmat"]
        def timed_matmat(bridge,model,name,x):
            s=time.monotonic()
            try:return fn(bridge,model,name,x)
            finally:_v77_add(_v77_bucket(name),time.monotonic()-s)
        batch._matmat=timed_matmat
    for name,key in (("_causal_gqa","causalGqa"),("_rms_cols","rms"),("_head_rms_cols","headRms"),("_rope_cols","rope")):
        fn=originals.get(name)
        if fn is None:continue
        def make_timed(original,bucket):
            def timed(*args,**kwargs):
                s=time.monotonic()
                try:return original(*args,**kwargs)
                finally:_v77_add(bucket,time.monotonic()-s)
            return timed
        setattr(batch,name,make_timed(fn,key))
    _V77_PATCHED=True

_v77_patch()

def _v77_log(request_id,metrics,prefill_ms):
    accounted=sum(float(metrics.get(k,0.0)) for k in ("ffnMatmat","attnMatmat","shortconvMatmat","otherMatmat","causalGqa","rms","headRms","rope"))
    record={"contract":_V77_CONTRACT,"requestId":str(request_id or "")[:160],"stage":"prefill-kernel-summary","prefillMs":int(prefill_ms),"accountedKernelMs":int(accounted*1000)}
    for k,v in metrics.items():
        if k=="requestId":continue
        record[k]=round(v*1000,3) if isinstance(v,float) and not k.endswith("Calls") else v
    print("SWRLZ_R39_PREFILL_KERNEL "+json.dumps(record,ensure_ascii=False,separators=(",",":")),flush=True)

def generate_events(payload,is_cancelled=None):
    request_id=_request_id(payload) if isinstance(payload,dict) else ""
    metrics={"requestId":request_id}
    _V77_TLS.metrics=metrics
    prefill_start=None
    logged=False
    try:
        for event in _V76_GENERATE(payload,is_cancelled):
            phase=str(event.get("phase") or "")
            if phase=="PREFILL" and prefill_start is None:prefill_start=time.monotonic()
            if phase=="GENERATING" and prefill_start is not None and not logged:
                _v77_log(request_id,metrics,(time.monotonic()-prefill_start)*1000)
                logged=True
            yield event
    finally:
        if prefill_start is not None and not logged:
            _v77_log(request_id,metrics,(time.monotonic()-prefill_start)*1000)
        try:delattr(_V77_TLS,"metrics")
        except Exception:pass

def inspect_engine():
    result=_V76_INSPECT()
    if isinstance(result,dict):
        result.update({"hotServerVersion":"2.1.89","hotRevision":"2.1.89-hot-prefill-kernel-profile-v77","v76Preserved":True,"prefillKernelProfileCamera":True,"prefillKernelProfileContract":_V77_CONTRACT,"prefillKernelProfileChangesMath":False})
    return result

HOT_SERVER_VERSION="2.1.89"
HOT_REVISION="2.1.89-hot-prefill-kernel-profile-v77"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION
