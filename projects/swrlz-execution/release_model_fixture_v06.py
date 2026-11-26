"""Deploy a signed, fixture-only model repair probe into §C.
No candidate HTML crosses the network or executes unless it is byte-identical
to the already reviewed built-in §X fixture. No project writes or publication.
"""
import ast, hashlib, hmac, io, json, os, re, secrets, sys, time
from pathlib import Path
import requests
from x_diagnostic_client import derive_key, mac, wire

ROOT=Path(__file__).resolve().parent
SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
CHECK="/api/swrlz-x/v1/model-fixture"
MARK="# swrlz-trusted-model-fixture-v06"
SCHEMA="swrlz-trusted-model-fixture-v06"
STATION="station.py"

ROUTE=r'''
# swrlz-trusted-model-fixture-v06
import threading as _swrlz_v06_threading
from fastapi import Header as _swrlz_v06_header, HTTPException as _swrlz_v06_http_error
_swrlz_v06_lock=_swrlz_v06_threading.Lock()
_swrlz_v06_seen={}
_swrlz_v06_fixture=__TRUSTED_FIXTURE__
_swrlz_v06_source_sha=__X_SOURCE_SHA__

@app.post("/api/swrlz-x/v1/model-fixture",include_in_schema=False)
def _swrlz_v06_model_fixture(
    raw:str=_swrlz_v06_header(default="",alias="X-Swrlz-X-Request"),
    signature:str=_swrlz_v06_header(default="",alias="X-Swrlz-X-Signature")):
    import hashlib,hmac,json,os,re,time
    import x_diagnostic_client as x
    key=os.environ.get(x.KEY_NAME,"")
    if len(key)!=64 or len(raw)>512 or len(signature)!=64 or not hmac.compare_digest(x.mac(key,"model-fixture-request",raw.encode()),signature):
        raise _swrlz_v06_http_error(403,"DIAGNOSTIC_DENIED")
    try:
        obj=json.loads(raw);now=int(time.time())
        if set(obj)!={"schema","nonce","timestamp"} or obj["schema"]!="swrlz-trusted-model-fixture-v06" or not re.fullmatch(r"[0-9a-f]{32}",obj["nonce"]) or type(obj["timestamp"]) is not int or abs(now-obj["timestamp"])>120:
            raise ValueError()
    except (ValueError,TypeError,KeyError):
        raise _swrlz_v06_http_error(400,"DIAGNOSTIC_INVALID")
    if not _swrlz_v06_lock.acquire(blocking=False):
        raise _swrlz_v06_http_error(429,"DIAGNOSTIC_BUSY")
    try:
        for n in list(_swrlz_v06_seen):
            if now-_swrlz_v06_seen[n]>300:del _swrlz_v06_seen[n]
        if obj["nonce"] in _swrlz_v06_seen or len(_swrlz_v06_seen)>=256:
            raise _swrlz_v06_http_error(409,"DIAGNOSTIC_REPLAY")
        _swrlz_v06_seen[obj["nonce"]]=now
        result={"schema":obj["schema"],"nonce":obj["nonce"],"state":"failed",
                "realModelCalls":0,"attempts":[],"arbitraryExecution":False,
                "isolationVerified":False,"projectCommitted":False,"projectDeployed":False}
        def sha(text):return hashlib.sha256(text.encode()).hexdigest()
        fixture=_swrlz_v06_fixture
        broken=fixture.replace("document.querySelector('#state').textContent","document.querySelector('#missing').textContent",1)
        before=sha(broken);expected=sha(fixture)
        project="trusted-browser-fixture"
        files={"index.html":broken}
        def signed_suite():
            rec=x.diagnose(key)
            d=rec["diagnostics"];s=d["trusted_development"]
            if (d.get("source_sha256")!=_swrlz_v06_source_sha or s.get("schema")!="swrlz-trusted-development-v1"
                or s.get("arbitraryExecution") is not False or s.get("isolationVerified") is not False
                or s.get("passed") is not True or s["broken"].get("detected") is not True
                or s["repaired"].get("passed") is not True
                or s["broken"].get("fixtureSha256")!=before or s["repaired"].get("fixtureSha256")!=expected
                or any(not re.fullmatch(r"[0-9a-f]{64}",s[c].get("screenshotSha256") or "") for c in ("broken","repaired"))):
                raise RuntimeError("FIXTURE_RECEIPT_MISMATCH")
            return rec
        try:
            active=_swrlz_verified_repair_runtime_v7()
            baseline=signed_suite()
            result["beforeSha256"]=before
            result["baselineNonce"]=baseline["nonce"]
            result["baselineFailure"]=baseline["diagnostics"]["trusted_development"]["broken"]
            evidence=[{"runtimeEvidence":result["baselineFailure"],"expectedBehavior":"Click the Test interaction button; state changes from Ready to Click passed without page errors."}]
            task="Fix the existing trusted fixture's click interaction using the smallest exact source edit. Preserve layout, button and WebGL surface. Return an exact patch only."
            # This deliberately invokes the same production coding model and
            # exact patch engine, with no executor fallback or model authority.
            failures=[]
            for attempt in range(3):
                messages=active.prompt_messages(project,files,evidence,task,prior_failures=failures)
                def coder(payload):
                    if payload.get("modelId")!="coder":raise RuntimeError("WRONG_MODEL_ROUTE")
                    result["realModelCalls"]+=1
                    yield from _coder_generate(payload)
                try:
                    raw_proposal=active._model_patch(coder,{},messages)
                    edits=raw_proposal.get("patches")
                    if not isinstance(edits,list) or not 1<=len(edits)<=3 or any(not isinstance(p,dict) or p.get("path")!="index.html" or p.get("op")!="replace_once" for p in edits):
                        raise ValueError("FIXTURE_PATCH_SCOPE")
                    proposal=active.bind_model_edits(project,files,raw_proposal)
                    applied=active.apply_proposal(project,files,proposal,expected_hashes={"index.html":before})
                    candidate=applied["proposedFiles"].get("index.html")
                    if not isinstance(candidate,str) or candidate!=fixture or applied["afterHashes"].get("index.html")!=expected:
                        raise ValueError("CANDIDATE_NOT_REVIEWED_FIXTURE")
                    result["attempts"].append({"attempt":attempt+1,"state":"reviewed_fixture_match","patchCount":len(edits)})
                    result["candidateSha256"]=sha(candidate)
                    # No model-generated source is transmitted or evaluated.
                    # Execute the byte-identical reviewed fixture via existing §X.
                    fresh=signed_suite()
                    if fresh["nonce"]==baseline["nonce"]:raise RuntimeError("STALE_RETEST")
                    result.update(state="passed",repairOrigin="model",afterSha256=expected,
                                  retestNonce=fresh["nonce"],retest=fresh["diagnostics"]["trusted_development"]["repaired"],
                                  browserVerified=True,fixtureBytesMatched=True)
                    break
                except Exception as exc:
                    # Fixed categories only, not model output or private traces.
                    label=str(exc) if str(exc) in ("FIXTURE_PATCH_SCOPE","CANDIDATE_NOT_REVIEWED_FIXTURE","STALE_RETEST","FIXTURE_RECEIPT_MISMATCH") else type(exc).__name__
                    result["attempts"].append({"attempt":attempt+1,"state":"rejected","reason":label})
                    failures.append(label)
            if result["state"]!="passed":result["blocker"]="MODEL_FIXTURE_REPAIR_UNVERIFIED"
        except Exception as exc:
            result["blocker"]="FIXTURE_INFRASTRUCTURE_"+type(exc).__name__
        result["timestamp"]=int(time.time())
        return {"receipt":result,"signature":x.mac(key,"model-fixture-receipt",x.wire(result))}
    finally:_swrlz_v06_lock.release()

'''

def source_fixture():
    raw=(ROOT/"app.py").read_bytes()
    tree=ast.parse(raw)
    values=[ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="FIXTURE" for t in n.targets)]
    if len(values)!=1 or not isinstance(values[0],str):raise RuntimeError("FIXTURE_SOURCE_DRIFT")
    return values[0],hashlib.sha256(raw).hexdigest()

def patch_station(source):
    fixture,digest=source_fixture()
    block=ROUTE.replace("__TRUSTED_FIXTURE__",repr(fixture)).replace("__X_SOURCE_SHA__",repr(digest))
    if MARK in source:
        if source.count(MARK)!=1 or block.strip() not in source:raise RuntimeError("EXISTING_MODEL_FIXTURE_DRIFT")
        return source
    anchor="def _swrlz_execute_model_repair_v7("
    if source.count(anchor)!=1 or "def _swrlz_verified_repair_runtime_v7(" not in source or "def _coder_generate(" not in source or "/api/swrlz-x/v1/diagnostics" not in source:
        raise RuntimeError("LIVE_STATION_ANCHOR_DRIFT")
    updated=source.replace(anchor,block+"\n"+anchor,1)
    ast.parse(updated)
    return updated

def selftest():
    stub="def _swrlz_verified_repair_runtime_v7():pass\ndef _coder_generate(payload):pass\n# /api/swrlz-x/v1/diagnostics\ndef _swrlz_execute_model_repair_v7():pass\n"
    patched=patch_station(stub)
    assert patch_station(patched)==patched
    compile(patched,"<station fixture>","exec")
    print("MODEL_FIXTURE_SOURCE_SELFTEST_PASS",flush=True)

def live(key):
    obj={"schema":SCHEMA,"nonce":secrets.token_hex(16),"timestamp":int(time.time())}
    raw=wire(obj)
    with requests.Session() as s:
        s.trust_env=False
        with s.post(BASE+CHECK,headers={"X-Swrlz-X-Request":raw.decode(),"X-Swrlz-X-Signature":mac(key,"model-fixture-request",raw)},timeout=(10,420),allow_redirects=False,stream=True) as r:
            r.raise_for_status()
            body=r.raw.read(65537)
    if len(body)>65536:raise RuntimeError("RECEIPT_TOO_LARGE")
    env=json.loads(body);rec=env["receipt"]
    if not hmac.compare_digest(mac(key,"model-fixture-receipt",wire(rec)),env["signature"]) or rec["nonce"]!=obj["nonce"] or rec["schema"]!=SCHEMA or abs(time.time()-rec["timestamp"])>180:
        raise RuntimeError("RECEIPT_IDENTITY")
    return rec

def publish():
    from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
    token=os.environ["HF_TOKEN"];key=derive_key(token);api=HfApi(token=token)
    def rev():return str(api.repo_info(SPACE,repo_type="space").sha)
    def read(r):return Path(hf_hub_download(SPACE,STATION,repo_type="space",revision=r,token=token)).read_bytes()
    old=rev();original=read(old);updated=patch_station(original.decode()).encode()
    def write(parent,raw,msg):
        return api.create_commit(repo_id=SPACE,repo_type="space",revision="main",parent_commit=parent,operations=[CommitOperationAdd(path_in_repo=STATION,path_or_fileobj=io.BytesIO(raw))],commit_message=msg).oid
    new=old
    if updated!=original:new=write(old,updated,"§C: signed trusted model fixture repair probe v0.6")
    try:
        assert read(new)==updated
        for attempt in range(15):
            try:rec=live(key);break
            except Exception as exc:
                if attempt==14:raise
                print("MODEL_FIXTURE_PENDING",type(exc).__name__,flush=True);time.sleep(8)
        Path("swrlz-model-fixture-receipt.json").write_text(json.dumps(rec,indent=2,sort_keys=True)+"\n")
        print("MODEL_FIXTURE_RECEIPT",json.dumps(rec,sort_keys=True),flush=True)
        fixture,_=source_fixture();expected=hashlib.sha256(fixture.encode()).hexdigest()
        if not (rec.get("state")=="passed" and rec.get("realModelCalls",0)>=1 and rec.get("repairOrigin")=="model" and rec.get("fixtureBytesMatched") is True and rec.get("browserVerified") is True and rec.get("afterSha256")==expected and rec.get("candidateSha256")==expected and rec.get("baselineNonce")!=rec.get("retestNonce") and rec.get("arbitraryExecution") is False and rec.get("isolationVerified") is False and rec.get("projectCommitted") is False and rec.get("projectDeployed") is False):
            raise RuntimeError("MODEL_REPAIR_NOT_VERIFIED")
        print("C_MODEL_TO_X_FIXTURE_REPAIR_PASS",flush=True)
    except Exception:
        if new!=old and rev()==new:
            restored=write(new,original,"Rollback unverified §C model fixture probe")
            print("STATION_ROLLBACK",restored,flush=True)
        raise

if __name__=="__main__":
    selftest()
    if sys.argv[1:]==["publish"]:publish()
    elif sys.argv[1:]:raise SystemExit("unknown mode")
