"""R39 v76: bounded cold-prefill observability overlay.

Preserves v75 behavior and adds privacy-safe structured timing cameras around the
existing PREFILL status stream. No prompt text, token ids, logits, or hidden
reasoning are logged.
"""
from __future__ import annotations
import json,re,time

_V76_CONTRACT="r39-v76-cold-prefill-profile-v1"
_V75_GENERATE=generate_events
_V75_INSPECT=inspect_engine

def _v76_log(request_id,stage,**fields):
    record={"contract":_V76_CONTRACT,"requestId":str(request_id or "")[:160],"stage":stage,"atUnixMs":int(time.time()*1000)}
    for key,value in fields.items():
        if value is None or isinstance(value,(str,int,float,bool)):
            record[str(key)[:64]]=value
    print("SWRLZ_R39_PREFILL_PROFILE "+json.dumps(record,ensure_ascii=False,separators=(",",":")),flush=True)

def generate_events(payload,is_cancelled=None):
    request_id=_request_id(payload) if isinstance(payload,dict) else ""
    started=time.monotonic()
    prefill_started=None
    prefill_finished=None
    prefill_events=0
    rendered_tokens=0
    cached_tokens=0
    uncached_tokens=0
    last_reason=""
    for event in _V75_GENERATE(payload,is_cancelled):
        phase=str(event.get("phase") or "")
        reason=str(event.get("reason") or "")
        now=time.monotonic()
        if phase=="PREFILL":
            if prefill_started is None:
                prefill_started=now
                _v76_log(request_id,"prefill-enter",elapsedMs=int((now-started)*1000))
            prefill_events+=1
            last_reason=reason[:480]
            full=re.search(r"Prefilling (\d+) token",reason)
            reuse=re.search(r"reused (\d+) token\(s\); only (\d+) new",reason)
            progress=re.search(r"Prefill new \d+/(\d+) · cached (\d+)",reason)
            if full: uncached_tokens=max(uncached_tokens,int(full.group(1)))
            if reuse:
                cached_tokens=max(cached_tokens,int(reuse.group(1)))
                uncached_tokens=max(uncached_tokens,int(reuse.group(2)))
            if progress:
                uncached_tokens=max(uncached_tokens,int(progress.group(1)))
                cached_tokens=max(cached_tokens,int(progress.group(2)))
            if prefill_events<=4 or prefill_events%8==0:
                _v76_log(request_id,"prefill-progress",eventIndex=prefill_events,elapsedMs=int((now-prefill_started)*1000),cachedTokens=cached_tokens,uncachedTokens=uncached_tokens,reason=last_reason)
        elif phase=="GENERATING" and prefill_started is not None and prefill_finished is None:
            prefill_finished=now
            seconds=max(1e-9,prefill_finished-prefill_started)
            _v76_log(request_id,"prefill-exit",prefillMs=int(seconds*1000),cachedTokens=cached_tokens,uncachedTokens=uncached_tokens,effectiveTokPerSec=round(uncached_tokens/seconds,3) if uncached_tokens else 0.0,prefillEvents=prefill_events,lastReason=last_reason)
        elif phase=="PERF_METRICS":
            _v76_log(request_id,"perf-metrics",elapsedMs=int((now-started)*1000),reason=reason[:700])
        yield event
    if prefill_started is not None and prefill_finished is None:
        now=time.monotonic(); seconds=max(1e-9,now-prefill_started)
        _v76_log(request_id,"prefill-terminal-without-generating",prefillMs=int(seconds*1000),cachedTokens=cached_tokens,uncachedTokens=uncached_tokens,prefillEvents=prefill_events,lastReason=last_reason)

def inspect_engine():
    result=_V75_INSPECT()
    if isinstance(result,dict):
        result.update({"hotServerVersion":"2.1.88","hotRevision":"2.1.88-hot-cold-prefill-profile-v76","v75Preserved":True,"coldPrefillProfileCamera":True,"coldPrefillProfileContract":_V76_CONTRACT,"coldPrefillLogsPromptText":False,"coldPrefillLogsTokenIds":False})
    return result

HOT_SERVER_VERSION="2.1.88"
HOT_REVISION="2.1.88-hot-cold-prefill-profile-v76"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION
