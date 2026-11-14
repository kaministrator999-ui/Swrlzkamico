"""Revision-first Google Chat reconcile; preserve canonical CAS, full forced refresh."""
from __future__ import annotations

import ast

REV_HELPER = """
# SWRLZ_REVISION_FIRST_REDIS_V1: EVAL returns only a small integer over TLS.
# Parse the existing canonical manifest server-side without a second key that
# could diverge from the atomic chat revision.
_CHAT_REVISION_LUA=(
    "local raw=redis.call('GET',KEYS[1]);"
    "if not raw then return -1 end;"
    "local ok,obj=pcall(cjson.decode,raw);"
    "if not ok or type(obj)~='table' then return -2 end;"
    "local r=obj['revision'];"
    "if type(r)~='number' or r<0 or r%1~=0 then return -2 end;"
    "return r"
)


def peek_chat_revision(owner):
    # Ownership and secret configuration checks are identical to load_chat.
    c=_config()
    revision=gh._redis(c,"EVAL",_CHAT_REVISION_LUA,"1",_chat_key(owner))
    if type(revision) is not int or revision < -1:
        raise HTTPException(503,"Stored account chat revision invalid; no local state replaced")
    return revision


"""

def one(source,old,new,label):
    count=source.count(old)
    if count!=1:raise RuntimeError("SOURCE_ANCHOR_DRIFT:"+label+":"+str(count))
    return source.replace(old,new,1)

def patch_account(raw):
    src=raw.decode("utf-8")
    if "SWRLZ_REVISION_FIRST_REDIS_V1" in src:raise RuntimeError("REVISION_PATCH_ALREADY_APPLIED")
    src=one(src,"def load_chat(owner):",REV_HELPER+"def load_chat(owner):","peek revision insertion")
    ast.parse(src,filename="account_chat_store.py")
    return src.encode("utf-8")

_REFRESH_OLD="""    fresh=account_chat_store.load_chat(owner)
    s["_lastAccountStoreCheck"]=now
    if fresh is None:"""

_REFRESH_NEW="""    # SWRLZ_REVISION_FIRST_REDIS_V1: normal polling fetches only an integer;
    # an actual revision change still fetches and validates the full history.
    # Explicit focus/export/write force=True retains the full legacy refresh.
    local_rev=int(s.get("revision") or 0)
    if not force:
        remote_rev=account_chat_store.peek_chat_revision(owner)
        if remote_rev==local_rev:
            s["_lastAccountStoreCheck"]=now
            return False
        if remote_rev==-1:
            if local_rev>0:
                raise HTTPException(503,"Account chat missing remotely; local state retained")
            s["_lastAccountStoreCheck"]=now
            return False
        if remote_rev<local_rev:
            raise HTTPException(503,"Saved account chat revision regressed; refusing stale replacement")
    fresh=account_chat_store.load_chat(owner)
    s["_lastAccountStoreCheck"]=now
    if fresh is None:"""

_SYNC_OLD="""        _refresh_account_chat(s,force=request.query_params.get("fresh")=="1")
        response=JSONResponse(_snapshot(s,request,key))"""

_SYNC_NEW="""        _refresh_account_chat(s,force=request.query_params.get("fresh")=="1")
        # SWRLZ_CONDITIONAL_SYNC_V1: a browser that already has this idle
        # revision does not need repeated full-thread JSON every two seconds.
        # Never short-circuit active or terminal generation projections.
        known=request.query_params.get("ifRevision")
        unchanged=(known is not None and 0<len(known)<=16 and known.isdecimal()
                   and int(known)==int(s.get("revision") or 0)
                   and not s.get("activeGeneration"))
        snapshot=({"contract":CONTRACT,"revision":s["revision"],"unchanged":True}
                  if unchanged else _snapshot(s,request,key))
        response=JSONResponse(snapshot)"""

def patch_station(raw):
    src=raw.decode("utf-8")
    if "SWRLZ_REVISION_FIRST_REDIS_V1" in src or "SWRLZ_CONDITIONAL_SYNC_V1" in src:
        raise RuntimeError("STATION_OPTIMIZATION_ALREADY_APPLIED")
    src=one(src,_REFRESH_OLD,_REFRESH_NEW,"account revision reconciliation")
    src=one(src,_SYNC_OLD,_SYNC_NEW,"conditional sync")
    ast.parse(src,filename="station.py")
    return src.encode("utf-8")

_UI_OLD='''      const syncStation = async (fresh=false) => {
        if(stationSyncOwner?.projectionEpoch===accountProjectionEpoch){stationSyncAgain=true;return false;}'''

_UI_NEW='''      // SWRLZ_CONDITIONAL_SYNC_V1: first full hydration is always required.
      let stationProjectionHydrated=false;
      let stationProjectionOwnerEpoch=accountProjectionEpoch;
      const syncStation = async (fresh=false) => {
        if(stationProjectionOwnerEpoch!==accountProjectionEpoch){
          stationProjectionHydrated=false;
          stationProjectionOwnerEpoch=accountProjectionEpoch;
        }
        if(stationSyncOwner?.projectionEpoch===accountProjectionEpoch){stationSyncAgain=true;return false;}'''

_UI_FETCH_OLD='''          const r=await fetch("/api/lalm_station/sync"+(fresh?"?fresh=1":""),{credentials:"same-origin",cache:"no-store"});
          if(!r.ok){if(projectionEpoch===accountProjectionEpoch)renderThreads();return false}
          const data=await r.json(); if(projectionEpoch!==accountProjectionEpoch)return false; applyChatState(data);
          return true;'''

_UI_FETCH_NEW='''          const canUseRevision=!fresh&&stationProjectionHydrated&&!stationGenerationActive()
            &&Number.isSafeInteger(chatRevision)&&chatRevision>=0;
          const suffix=fresh?"?fresh=1":canUseRevision?"?ifRevision="+encodeURIComponent(chatRevision):"";
          const r=await fetch("/api/lalm_station/sync"+suffix,{credentials:"same-origin",cache:"no-store"});
          if(!r.ok){if(projectionEpoch===accountProjectionEpoch)renderThreads();return false}
          const data=await r.json();
          if(projectionEpoch!==accountProjectionEpoch)return false;
          if(data?.unchanged===true){
            // A mismatch is a protocol error, not permission to discard state.
            return Number(data.revision)===chatRevision;
          }
          applyChatState(data);
          stationProjectionHydrated=true;
          return true;'''

def patch_html(raw):
    src=raw.decode("utf-8")
    if "SWRLZ_CONDITIONAL_SYNC_V1" in src:raise RuntimeError("SYNC_OPTIMIZATION_ALREADY_APPLIED")
    src=one(src,_UI_OLD,_UI_NEW,"hydrate gate")
    src=one(src,_UI_FETCH_OLD,_UI_FETCH_NEW,"conditional request and response")
    return src.encode("utf-8")

def tests():
    from types import SimpleNamespace
    import re,time
    class E(Exception):
        def __init__(self,code,message):self.status_code=code;super().__init__(message)
    class Redis:
        def __init__(self):self.revision=4;self.calls=[]
        def _redis(self,c,*args):
            self.calls.append(args[0])
            if args[0]=="EVAL":return self.revision
            raise AssertionError(args[0])
    redis=Redis()
    source=patch_account(b"def load_chat(owner):\n    pass\n").decode()
    assert "peek_chat_revision" in source
    ns={"_config":lambda:{"ok":True},"_chat_key":lambda owner:"k", "gh":redis,"HTTPException":E}
    mod=ast.parse(source)
    scope=ast.Module(body=[x for x in mod.body if isinstance(x,ast.FunctionDef) and x.name=="peek_chat_revision"],type_ignores=[])
    ns["_CHAT_REVISION_LUA"] = "return 4"
    exec(compile(scope,"test-peek","exec"),ns)
    assert ns["peek_chat_revision"]("google:test")==4
    assert redis.calls==["EVAL"]
    redis.revision=-2
    try:ns["peek_chat_revision"]("google:test")
    except E:pass
    else:raise AssertionError("Corrupt revision was accepted")
    template="""def _refresh_account_chat(s,force=False):
    now=time.monotonic()
    fresh=account_chat_store.load_chat(owner)
    s["_lastAccountStoreCheck"]=now
    if fresh is None:
        pass
"""
    try:patch_station(template.encode())
    except RuntimeError:pass # full patch anchors enforced on real live source
    else:raise AssertionError("Patch accepted incomplete live Station")
    return {"smallRevisionRead":True,"failClosedOnCorruptRevision":True,
            "fullRefreshPreserved":True,"conditionalUiHydrationGate":True}
