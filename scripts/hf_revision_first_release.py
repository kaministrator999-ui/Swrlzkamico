"""Source-pinned revision-first Redis traffic optimization for the actual HF §C.

Never downloads private Redis values or user chat histories. No user keys
are deleted. Legacy manifests without the revision sidecar use full reads.
"""
from __future__ import annotations
import ast, hashlib, io, json, os, re, sys, time, types, urllib.request
from pathlib import Path
from huggingface_hub import CommitOperationAdd, HfApi, hf_hub_download
SPACE="kamiloki/Swyrlz"
FILES=("account_chat_store.py","station.py")
BACKUP=Path("swrlz-revision-first-original")
MARK="SWRLZ_REDIS_REVISION_FIRST_V1"

def one(source, old, new, what):
    count=source.count(old)
    if count!=1: raise RuntimeError("SOURCE_DRIFT_"+what+"_"+str(count))
    return source.replace(old,new,1)

def patch_store(source):
    if MARK in source:raise RuntimeError("ALREADY_PATCHED_STORE")
    source=one(source,
        '''    "redis.call('SET',KEYS[1],ARGV[2]); return 1"''',
        '''    "redis.call('SET',KEYS[1],ARGV[2]);"
    "redis.call('SET',KEYS[2],ARGV[3]); return 1"''',
        "CAS_SCRIPT")
    source=one(source,
        '''    return "swrlz:google:chat:v1:"+hashlib.sha256(owner.encode("utf-8")).hexdigest()''',
        '''    return "swrlz:google:chat:v1:"+hashlib.sha256(owner.encode("utf-8")).hexdigest()

# SWRLZ_REDIS_REVISION_FIRST_V1: this sidecar is committed atomically with
# the canonical encrypted manifest. If missing, always read that manifest.
def _chat_revision_key(owner):
    return _chat_key(owner)+":revision:v1"

def peek_chat_revision(owner):
    raw=gh._redis(_config(),"GET",_chat_revision_key(owner))
    if raw is None:
        return None
    if not isinstance(raw,str) or not re.fullmatch(r"(?:0|[1-9][0-9]{0,17})",raw):
        raise HTTPException(503,"Stored chat revision marker is invalid")
    return int(raw)''',
        "SIDECAR_HELPER")
    source=one(source,
        '''response=gh._redis(c,"EVAL",_CAS_LUA,"1",key,str(expected_revision),
                       json.dumps(envelope,separators=(",",":")))''',
        '''response=gh._redis(c,"EVAL",_CAS_LUA,"2",key,_chat_revision_key(owner),
                       str(expected_revision),json.dumps(envelope,separators=(",",":")),
                       str(state["revision"]))''',
        "ATOMIC_CAS")
    ast.parse(source,filename=FILES[0])
    return source

def patch_station(source):
    if MARK in source:raise RuntimeError("ALREADY_PATCHED_STATION")
    source=one(source,
        '''    fresh=account_chat_store.load_chat(owner)
    s["_lastAccountStoreCheck"]=now''',
        '''    # SWRLZ_REDIS_REVISION_FIRST_V1: the small sidecar is updated in
    # the exact same Lua transaction as the encrypted canonical manifest.
    # A missing sidecar denotes a legacy snapshot and demands a full read.
    revision=account_chat_store.peek_chat_revision(owner)
    local_rev=int(s.get("revision") or 0)
    if revision is not None:
        if revision<local_rev:
            raise HTTPException(503,"Saved account chat revision regressed; refusing stale replacement")
        if revision==local_rev:
            s["_lastAccountStoreCheck"]=now
            return False
    fresh=account_chat_store.load_chat(owner)
    s["_lastAccountStoreCheck"]=now''',
        "REVISION_FIRST_REFRESH")
    ast.parse(source,filename=FILES[1])
    return source

def selftest(store,station):
    # Tests actual patched functions with safe stub, not private account data.
    def getfunction(source,name):
        tree=ast.parse(source)
        found=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name]
        if len(found)!=1:raise AssertionError(name)
        return compile(ast.Module(body=found,type_ignores=[]),"<source>", "exec")
    class HTTPException(Exception):
        def __init__(self,status_code,detail):self.status_code=status_code;self.detail=detail
    class StoreGH:
        def __init__(self):self.ops=[];self.marker=None
        def _redis(self,config,*args):
            self.ops.append(args)
            if args[:1]==("GET",):return self.marker
            raise AssertionError(args)
    gh=StoreGH()
    env={"gh":gh,"_config":lambda:{"test":True},"_chat_key":lambda owner:"owner:"+owner,
         "HTTPException":HTTPException,"re":re}
    for name in ("_chat_revision_key","peek_chat_revision"):exec(getfunction(store,name),env)
    assert env["peek_chat_revision"]("user1") is None
    gh.marker="5";assert env["peek_chat_revision"]("user1")==5
    assert gh.ops[-1]==("GET","owner:user1:revision:v1")
    gh.marker="NaN"
    try:env["peek_chat_revision"]("user1");raise AssertionError("bad marker accepted")
    except HTTPException as e:assert e.status_code==503
    class M:
        monotonic=lambda self:100.
    class Store:
        def __init__(self,marker,remote=None):self.marker=marker;self.remote=remote;self.calls=[]
        def peek_chat_revision(self,owner):self.calls.append("peek");return self.marker
        def load_chat(self,owner):self.calls.append("load");return self.remote
    storeobj=Store(5)
    ev={"time":M(),"account_chat_store":storeobj,"HTTPException":HTTPException}
    exec(getfunction(station,"_refresh_account_chat"),ev)
    base={"ownerGoogleId":"google:abcde","revision":5,"threads":[],"currentId":"", "activeGeneration":None}
    assert ev["_refresh_account_chat"](dict(base),force=True) is False
    assert storeobj.calls==["peek"],storeobj.calls
    storeobj.marker=6;storeobj.remote={**base,"revision":6,"threads":[{"id":"new"}]}
    s=dict(base);assert ev["_refresh_account_chat"](s) is True and s["revision"]==6
    assert storeobj.calls[-2:]==["peek","load"]
    storeobj.marker=None;storeobj.remote={**base,"revision":5}
    assert ev["_refresh_account_chat"](dict(base),force=True) is False
    assert storeobj.calls[-2:]==["peek","load"]
    storeobj.marker=4
    try:ev["_refresh_account_chat"](dict(base),force=True);raise AssertionError("regression accepted")
    except HTTPException as e:assert e.status_code==503
    assert "redis.call('SET',KEYS[2],ARGV[3]); return 1" in store
    assert 'gh._redis(c,"EVAL",_CAS_LUA,"2",key,_chat_revision_key(owner)' in store
    print("SWRLZ_REVISION_FIRST_FAKE_TEST_PASS",json.dumps({
        "scenarios":6,"atomicSidecar":True,"unchangedSkipsPayload":True,
        "legacyFallback":True,"staleFailsClosed":True
    }),flush=True)

def main():
    token=os.environ.get("HF_TOKEN","")
    if not token:raise RuntimeError("HF_TOKEN_MISSING")
    api=HfApi(token=token)
    info=api.repo_info(SPACE,repo_type="space")
    expected=os.environ.get("EXPECTED_SPACE_REV","")
    if expected and expected!=info.sha:
        raise RuntimeError("EXPECTED_SPACE_REV_DRIFT")
    allpaths=set(api.list_repo_files(SPACE,repo_type="space",revision=info.sha))
    if not set(FILES).issubset(allpaths):
        raise RuntimeError("LIVE_STORE_NOT_FOUND")
    original={p:Path(hf_hub_download(SPACE,p,repo_type="space",revision=info.sha,token=token)).read_bytes() for p in FILES}
    candidates={
        "account_chat_store.py":patch_store(original["account_chat_store.py"].decode("utf-8")),
        "station.py":patch_station(original["station.py"].decode("utf-8"))
    }
    selftest(**{"store":candidates["account_chat_store.py"],"station":candidates["station.py"]})
    BACKUP.mkdir(exist_ok=True)
    for path,body in original.items():(BACKUP/path).write_bytes(body)
    (BACKUP/"manifest.json").write_text(json.dumps({"revision":info.sha,"space":SPACE,
        "sha256":{p:hashlib.sha256(body).hexdigest() for p,body in original.items()},
        "files":FILES,"userRecordsRead":False},indent=2))
    print("SWRLZ_REVISION_FIRST_PREFLIGHT "+json.dumps({
        "spaceRevision":info.sha,"files":FILES,"legacyFallback":True,
        "atomicRevisionSidecar":True,"keysDeleted":False}),flush=True)
    if sys.argv[1:]==["publish"]:
        result=api.create_commit(repo_id=SPACE,repo_type="space",
           operations=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=io.BytesIO(data.encode("utf-8")))
                      for p,data in candidates.items()],
           commit_message="Optimize §C Redis refresh by atomic revision marker instead of full chat reads",
           parent_commit=info.sha)
        print("SWRLZ_REVISION_FIRST_PUBLISHED "+json.dumps({"revision":result.oid,
             "originalRevision":info.sha,"noAccountHistoryRead":True}),flush=True)

if __name__=="__main__":main()
