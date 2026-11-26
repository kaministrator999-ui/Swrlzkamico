"""Release v0.7: production project adapter, trusted-only execution on §X."""
import ast,hashlib,hmac,io,json,os,secrets,sys,time
from pathlib import Path
import requests
from x_diagnostic_client import derive_key,mac,wire,diagnose
ROOT=Path(__file__).resolve().parents[2]
SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
CHECK="/api/swrlz-x/v1/project-adapter"
MARK="# swrlz-project-adapter-v07"
SCHEMA="swrlz-project-adapter-v07"
BACKEND="html_project_browser_backend_v1.py"
APPROVAL="html_project_repair_v1.py"
MODULE="html_project_x_reviewed_v1.py"
STATION="station.py"
def digest(raw):return hashlib.sha256(raw).hexdigest()
def assets():
    raw=(ROOT/"projects/swrlz-execution/app.py").read_bytes()
    tree=ast.parse(raw)
    fixture=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="FIXTURE" for t in n.targets))
    alternate=fixture.replace("document.querySelector('#state')","document.getElementById('state')",1)
    module=(ROOT/"api"/MODULE).read_text().replace("__X_SOURCE_SHA__",digest(raw)).replace("__REPAIRED_SHA__",digest(fixture.encode())).replace("__ALTERNATE_SHA__",digest(alternate.encode()))
    return fixture,digest(raw),module
def replace_one(source,old,new):
    if source.count(old)!=1:raise RuntimeError("V07_SOURCE_ANCHOR_DRIFT:"+old[:80])
    return source.replace(old,new,1)
def patch_backend(source):
    old='''            auth=p._authorized(owner)
            return GitHubBrowserBackend(lambda method,path,**kw:p._github(auth,method,path,**kw),
                     auth["token"],source_sha,cancel=payload.get("_cancelCheck"))'''
    new='''            from html_project_x_reviewed_v1 import ReviewedXBackend
            def existing_worker():
                auth=p._authorized(owner)
                return GitHubBrowserBackend(lambda method,path,**kw:p._github(auth,method,path,**kw),
                         auth["token"],source_sha,cancel=payload.get("_cancelCheck"))
            return ReviewedXBackend(existing_worker,cancel=payload.get("_cancelCheck"))'''
    return replace_one(source,old,new)
def patch_approval(source):
    # The reviewed §X result is preapproval evidence, not a supported publication
    # receipt. Existing workflow must independently execute candidate after YES.
    return replace_one(source,'        if proposal.get("browserReceipt"):\n','        if proposal.get("browserReceipt") and proposal["browserReceipt"].get("backend")!="swrlz-x-reviewed":\n')
ROUTE=r'''
# swrlz-project-adapter-v07
from fastapi import Header as _x07_header, HTTPException as _x07_error
import threading as _x07_threading
_x07_lock=_x07_threading.Lock()
_x07_seen={}
_x07_release=__RELEASE__
_x07_fixture=__FIXTURE__
@app.post("/api/swrlz-x/v1/project-adapter",include_in_schema=False)
def _x07_project_adapter(raw:str=_x07_header(default="",alias="X-Swrlz-X-Request"),
                         signature:str=_x07_header(default="",alias="X-Swrlz-X-Signature")):
    import json,os,time,hmac,re
    import x_diagnostic_client as x
    from html_project_browser_backend_v1 import backend
    from html_project_x_reviewed_v1 import BACKEND
    key=os.environ.get(x.KEY_NAME,"")
    if len(key)!=64 or len(raw)>512 or len(signature)!=64 or not hmac.compare_digest(x.mac(key,"project-adapter-request",raw.encode()),signature):
        raise _x07_error(403,"V07_DENIED:"+_x07_release)
    try:
        obj=json.loads(raw);now=int(time.time())
        if set(obj)!={"schema","nonce","timestamp","releaseId"} or obj["schema"]!="swrlz-project-adapter-v07" or obj["releaseId"]!=_x07_release or not re.fullmatch(r"[a-f0-9]{32}",obj["nonce"]) or type(obj["timestamp"]) is not int or abs(now-obj["timestamp"])>120:
            raise ValueError()
    except (ValueError,TypeError,KeyError):raise _x07_error(400,"V07_INVALID")
    if not _x07_lock.acquire(blocking=False):raise _x07_error(429,"V07_BUSY")
    try:
        for n in list(_x07_seen):
            if now-_x07_seen[n]>300:del _x07_seen[n]
        if obj["nonce"] in _x07_seen or len(_x07_seen)>=256:raise _x07_error(409,"V07_REPLAY")
        _x07_seen[obj["nonce"]]=now
        rec={"schema":obj["schema"],"nonce":obj["nonce"],"releaseId":_x07_release,"state":"failed","realModelCalls":0,"projectCommitted":False,"projectDeployed":False}
        try:
            active=_swrlz_verified_repair_runtime_v7()
            broken=_x07_fixture.replace("document.querySelector('#state')","document.querySelector('#missing')",1)
            # Exact same selector and shared candidate loop used by owner-authenticated production route.
            # Probe does not create owner credentials; the fallback must never run here.
            adapter=backend.for_source("google:trusted-probe","0"*40,{})
            if adapter.name!=BACKEND:raise RuntimeError("V07_BACKEND_NOT_ACTIVE")
            def no_fallback():raise ValueError("V07_UNREVIEWED_CANDIDATE")
            adapter.fallback=no_fallback
            baseline=x.diagnose(key)
            evidence=baseline["diagnostics"]["trusted_development"]["broken"]
            if evidence.get("detected") is not True:raise RuntimeError("V07_BASELINE")
            def coder(payload):
                if payload.get("modelId")!="coder":raise RuntimeError("V07_WRONG_MODEL")
                rec["realModelCalls"]+=1
                yield from _coder_generate(payload)
            gen=active.repair_candidate({},coder,"trusted-browser-fixture",{"index.html":broken},
                "Fix the click handler DOM lookup to the existing status element. Use one minimal exact patch; preserve all other bytes.",[{"runtimeEvidence":evidence}],browser_validator=adapter)
            while True:
                try:next(gen)
                except StopIteration as done:
                    proposal,result,origin,failures=done.value
                    break
            envelope=result["validation"]["browserReceipt"]
            receipt=envelope["receipt"]
            if origin!="model" or envelope["backend"]!=BACKEND or receipt["workerNonce"]==baseline["nonce"] or receipt["browserVerified"] is not True or receipt["hashes"]!=result["afterHashes"]:raise RuntimeError("V07_RESULT_INVALID")
            rec.update(state="passed",repairOrigin=origin,backend=envelope["backend"],browserReceipt=receipt,baselineNonce=baseline["nonce"],ownerApprovalRequired=True)
        except Exception as exc:
            rec["blocker"]=type(exc).__name__
        rec["timestamp"]=int(time.time())
        return {"receipt":rec,"signature":x.mac(key,"project-adapter-receipt",x.wire(rec))}
    finally:_x07_lock.release()
'''
def release_id():
    fixture,xsha,module=assets()
    return digest((ROUTE+fixture+xsha+module+patch_backend((ROOT/"api"/BACKEND).read_text())+patch_approval((ROOT/"api"/APPROVAL).read_text())).encode())
def patch_station(source):
    fixture,_,_=assets()
    block=ROUTE.replace("__RELEASE__",repr(release_id())).replace("__FIXTURE__",repr(fixture))
    if MARK in source:
        if block.strip() not in source:raise RuntimeError("V07_STATION_DRIFT")
        return source
    if "# swrlz-trusted-model-fixture-v06" not in source:raise RuntimeError("V06_NOT_PRESENT")
    return replace_one(source,'@app.post("/api/swrlz-x/v1/diagnostics"',block+'\n@app.post("/api/swrlz-x/v1/diagnostics"')
def selftest():
    fixture,xsha,module=assets()
    scope={}
    exec(compile(module,"<reviewed adapter>","exec"),scope)
    cls=scope["ReviewedXBackend"]
    # Test routing and receipt rejection with a local stub; no arbitrary code executed.
    scope["candidate_hashes"]=lambda project,files:{p:digest(v.encode()) for p,v in files.items()}
    class Fallback:
        def validate_candidate(self,*a):return {"backend":"github-actions"}
    case={"passed":True,"fixtureSha256":digest(fixture.encode()),"before":"Ready","after":"Click passed","pageErrors":[],"screenshotSha256":"a"*64}
    signed={"nonce":"a"*32,"diagnostics":{"source_sha256":xsha,"trusted_development":{"schema":"swrlz-trusted-development-v1","passed":True,"arbitraryExecution":False,"isolationVerified":False,"repaired":case}}}
    obj=cls(Fallback,diagnose=lambda:signed)
    assert obj.validate_candidate("fixture",{"index.html":fixture},True,{})["backend"]=="swrlz-x-reviewed"
    assert obj.validate_candidate("fixture",{"index.html":fixture,"extra.js":"x"},True,{})["backend"]=="github-actions"
    assert obj.validate_candidate("fixture",{"index.html":fixture+" "},True,{})["backend"]=="github-actions"
    case["fixtureSha256"]="b"*64
    assert obj.validate_candidate("fixture",{"index.html":fixture},True,{})["backend"]=="github-actions"
    for name,patch in ((BACKEND,patch_backend),(APPROVAL,patch_approval)):
        compile(patch((ROOT/"api"/name).read_text()),name,"exec")
    stub='# swrlz-trusted-model-fixture-v06\n@app.post("/api/swrlz-x/v1/diagnostics")\ndef existing():pass\n'
    updated=patch_station(stub)
    assert patch_station(updated)==updated
    compile(updated,STATION,"exec")
    print("V07_ADAPTER_SELFTEST_PASS",release_id(),flush=True)
def publish():
    from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd,CommitOperationDelete
    token=os.environ["HF_TOKEN"];key=derive_key(token);api=HfApi(token=token)
    fixture,xsha,module=assets()
    if diagnose(key)["diagnostics"]["source_sha256"]!=xsha:raise RuntimeError("V07_X_SOURCE_MISMATCH")
    def rev():return str(api.repo_info(SPACE,repo_type="space").sha)
    old=rev();names=set(api.list_repo_files(SPACE,repo_type="space",revision=old))
    def read(name,r):return Path(hf_hub_download(SPACE,name,repo_type="space",revision=r,token=token)).read_bytes()
    orig={n:read(n,old) for n in (BACKEND,APPROVAL,STATION,MODULE) if n in names}
    candidates={MODULE:module.encode(),STATION:patch_station(orig[STATION].decode()).encode()}
    for name,patch in ((BACKEND,patch_backend),(APPROVAL,patch_approval)):
        base=(ROOT/"api"/name).read_bytes()
        candidate=patch(base.decode()).encode()
        if orig.get(name) not in (base,candidate):raise RuntimeError("V07_LIVE_SOURCE_DRIFT:"+name)
        candidates[name]=candidate
    if MODULE in orig and orig[MODULE]!=candidates[MODULE]:raise RuntimeError("V07_MODULE_COLLISION")
    for name,raw in candidates.items():compile(raw,name,"exec")
    changed={n:v for n,v in candidates.items() if orig.get(n)!=v}
    def add(n,v):return CommitOperationAdd(path_in_repo=n,path_or_fileobj=io.BytesIO(v))
    new=old
    if changed:new=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=old,operations=[add(n,v) for n,v in changed.items()],commit_message="§C v0.7 reviewed §X project adapter").oid
    try:
        for n,v in candidates.items():assert read(n,new)==v
        if changed:api.restart_space(SPACE)
        deadline=time.monotonic()+720
        expected=release_id()
        while time.monotonic()<deadline:
            if rev()!=new:raise RuntimeError("V07_CONCURRENT_CHANGE")
            stage=str(api.get_space_runtime(SPACE).stage)
            try:
                r=requests.post(BASE+CHECK,headers={"X-Swrlz-X-Request":"{}","X-Swrlz-X-Signature":"0"*64},timeout=12,allow_redirects=False)
                if stage.split(".")[-1]=="RUNNING" and r.status_code==403 and r.json().get("detail")=="V07_DENIED:"+expected:break
                print("V07_STARTUP",stage,r.status_code,flush=True)
            except (requests.RequestException,ValueError):print("V07_STARTUP",stage,flush=True)
            time.sleep(10)
        else:raise RuntimeError("V07_LIVE_ROUTE_UNVERIFIED")
        obj={"schema":SCHEMA,"nonce":secrets.token_hex(16),"timestamp":int(time.time()),"releaseId":expected}
        raw=wire(obj)
        with requests.post(BASE+CHECK,headers={"X-Swrlz-X-Request":raw.decode(),"X-Swrlz-X-Signature":mac(key,"project-adapter-request",raw)},timeout=(10,420),allow_redirects=False,stream=True) as r:
            r.raise_for_status();body=r.raw.read(65537)
        if len(body)>65536:raise RuntimeError("V07_RECEIPT_LIMIT")
        env=json.loads(body);rec=env["receipt"]
        if not hmac.compare_digest(mac(key,"project-adapter-receipt",wire(rec)),env["signature"]) or rec.get("nonce")!=obj["nonce"] or rec.get("releaseId")!=expected or rec.get("schema")!=SCHEMA or abs(time.time()-rec["timestamp"])>180:raise RuntimeError("V07_RECEIPT_IDENTITY")
        Path("swrlz-project-adapter-receipt.json").write_text(json.dumps(rec,indent=2)+"\n")
        print("V07_RECEIPT",json.dumps(rec),flush=True)
        b=rec.get("browserReceipt",{})
        if not (rec.get("state")=="passed" and rec.get("repairOrigin")=="model" and rec.get("realModelCalls",0)>0 and rec.get("backend")=="swrlz-x-reviewed" and rec.get("ownerApprovalRequired") is True and rec.get("projectCommitted") is False and rec.get("projectDeployed") is False and b.get("browserVerified") is True and b.get("arbitraryExecution") is False and b.get("isolationVerified") is False and b.get("requiresIndependentApprovalValidation") is True and b.get("workerSourceSha256")==xsha):raise RuntimeError("V07_LIVE_PROJECT_ADAPTER_UNVERIFIED")
        print("V07_LIVE_PROJECT_ADAPTER_PASS",new,flush=True)
    except Exception:
        if changed and rev()==new:
            restored=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=new,operations=[add(n,orig[n]) if n in orig else CommitOperationDelete(path_in_repo=n) for n in changed],commit_message="Rollback unverified §C v0.7").oid
            api.restart_space(SPACE);print("V07_ROLLBACK",restored,flush=True)
        raise
if __name__=="__main__":
    selftest()
    if sys.argv[1:]==["publish"]:publish()
