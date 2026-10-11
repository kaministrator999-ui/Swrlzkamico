"""Private, verified-account conversation totals; never answer by guessing/web search.

The imported transcript total is not the number of *new* messages in the last
ZIP run. Computing a cumulative total is read-only, detached, and bounded:
only integer per-thread counts are cached; no plaintext message text is copied.
"""
from __future__ import annotations

import re
import threading
import time
from fastapi import HTTPException
import account_chat_store
import chatgpt_archive as archive
import chatgpt_account_memory as memory
import github_connection as gh

_COUNT = re.compile(r"(?i)\b(?:how many|number of|count of|total (?:number|count)|how much)\b")
_TOPIC = re.compile(r"(?i)\b(?:chats?|threads?|conversations?|messages?)\b")
_IMPORTED = re.compile(r"(?i)\b(?:imported|imports?|chatgpt|exported|archive)\b")
_NATIVE = re.compile(r"(?i)(?:§wyrlz|swyrlz|native|original)\b")
_MESSAGES = re.compile(r"(?i)\bmessages?\b")
_LOCK = threading.RLock()
_CACHE = {}
_EPOCH = {}
_MAX_WORKERS = 2


def classify(prompt):
    q=str(prompt or "")[:400]
    if not _COUNT.search(q) or not _TOPIC.search(q):
        return ""
    if re.search(r"(?i)\b(?:last|yesterday|ago|earlier|between|in \d{4})\b",q):
        # Historical counts need a date-window lookup, not current catalog totals.
        return ""
    if _MESSAGES.search(q):
        return "imported-messages" if _IMPORTED.search(q) else (
            "native-messages" if _NATIVE.search(q) else "all-messages")
    return "imported-threads" if _IMPORTED.search(q) else (
        "native-threads" if _NATIVE.search(q) else "all-threads")


def invalidate(owner):
    with _LOCK:
        _EPOCH[owner]=_EPOCH.get(owner,0)+1
        _CACHE.pop(owner,None)


def _worker(owner,epoch):
    counted=0
    messages=0
    total=0
    try:
        c=account_chat_store._config()
        total=int(gh._redis(c,"ZCARD",archive._index(owner)))
        for offset in range(0,total,40):
            with _LOCK:
                if _EPOCH.get(owner,0)!=epoch:return
            ids=gh._redis(c,"ZREVRANGE",archive._index(owner),str(offset),
                          str(min(total-1,offset+39)))
            if not isinstance(ids,list):
                raise RuntimeError("Unable to retrieve an archive page")
            for cid in ids:
                with _LOCK:
                    if _EPOCH.get(owner,0)!=epoch:return
                rec,_=archive._read_record(owner,cid,c)
                if rec:
                    messages+=len(rec.get("messages",[]))
                    counted+=1
            with _LOCK:
                if _EPOCH.get(owner,0)!=epoch:return
                _CACHE[owner]={"state":"counting","total":total,"done":counted}
        with _LOCK:
            if _EPOCH.get(owner,0)==epoch:
                _CACHE[owner]={"state":"ready","total":total,"done":counted,"messages":messages}
    except Exception:
        with _LOCK:
            if _EPOCH.get(owner,0)==epoch:
                _CACHE[owner]={"state":"error","total":total,"done":counted}


def _count_status(owner):
    with _LOCK:
        value=_CACHE.get(owner)
        if value and value["state"] in ("counting","ready"):
            return dict(value)
        if sum(v["state"]=="counting" for v in _CACHE.values())>=_MAX_WORKERS:
            return {"state":"queued"}
        epoch=_EPOCH.get(owner,0)
        _CACHE[owner]={"state":"counting","total":0,"done":0}
        threading.Thread(target=_worker,args=(owner,epoch),daemon=True,
                         name="private-thread-count").start()
        return {"state":"counting","total":0,"done":0}


def answer(owner,native_threads,prompt):
    """Server-authoritative response only for exact CURRENT count questions."""
    kind=classify(prompt)
    if not kind:return ""
    archive._owner(owner)
    threads=[t for t in native_threads if isinstance(t,dict)]
    native_count=len(threads)
    native_msgs=sum(1 for t in threads for m in (t.get("messages") or [])
                    if isinstance(m,dict) and m.get("role") in ("user","assistant"))
    try:
        total=int(gh._redis(account_chat_store._config(),"ZCARD",archive._index(owner)))
    except Exception:
        return ("I can see the native account snapshot, but the encrypted imported "
                "archive count is temporarily unavailable. I won't invent a number.")
    base=f"Authenticated account totals: {total:,} stored imported ChatGPT conversation threads; "
    base+=f"{native_count:,} native §wyrlz conversation threads."
    if kind in ("imported-threads","native-threads","all-threads"):
        return base+" These are separate archives; their thread counts are not interchangeable."
    if kind=="native-messages":
        return base+f" The native snapshot contains {native_msgs:,} visible user/assistant messages."
    with memory._LOCK:
        indexed=memory._STATE.get(owner)
        indexed=(indexed if indexed and indexed.get("state")=="ready"
                 and len(indexed.get("docs",[]))==total else None)
    if indexed and all("messageCount" in d for d in indexed["docs"]):
        imported_count=sum(int(d["messageCount"]) for d in indexed["docs"])
        return base+f" The imported archive contains {imported_count:,} stored visible text messages. "+(
            f"The native snapshot contains {native_msgs:,} more visible messages."
            if kind=="all-messages" else "")
    counted=_count_status(owner)
    if counted["state"]=="ready" and counted.get("total")==total:
        return base+f" The imported archive contains {counted['messages']:,} stored text messages. "+(
            f"The native snapshot contains {native_msgs:,} more visible messages."
            if kind=="all-messages" else "")
    if counted["state"]=="error":
        return base+" I couldn't verify the imported message total; please retry the count."
    progress=(f" ({counted.get('done',0):,} of {counted.get('total',total):,} threads checked)"
              if counted["state"]=="counting" else "")
    return (base+" The exact cumulative imported message count is being checked"
            +progress+". Please ask again after it finishes. The number of messages "
             "ADDED by the most recent import is not the total stored message count.")
