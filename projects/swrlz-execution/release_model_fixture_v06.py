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

def _swrlz_v06_candidate_delta(broken, reviewed, candidate):
    """Safe mismatch metadata only; do not return model-generated source."""
    import hashlib
    def span(a,b):
        start=0
        while start<min(len(a),len(b)) and a[start]==b[start]:start+=1
        tail=0
        while tail<min(len(a)-start,len(b)-start) and a[-1-tail]==b[-1-tail]:tail+=1
        return {"start":start,"removedChars":len(a)-start-tail,"addedChars":len(b)-start-tail}
    if not isinstance(candidate,str):return {"kind":"CANDIDATE_MISSING"}
    allowed=span(broken,reviewed)
    actual=span(broken,candidate)
    mismatch=span(reviewed,candidate)
    return {"kind":"EXACT_BYTES_MISMATCH","allowedChange":allowed,"actualChange":actual,
            "remainingDifference":mismatch,"candidateSha256":hashlib.sha256(candidate.encode()).hexdigest(),
            "originalSelectorStillPresent":"querySelector('#missing')" in candidate,
            "expectedSelectorPresent":"querySelector('#state')" in candidate,
            "changedOutsideAllowedSpan":actual["start"]<allowed["start"] or actual["start"]+actual["removedChars"]>allowed["start"]+allowed["removedChars"]}

@app.post("/api/swrlz-x/v1/model-fixture",include_in_schema=False)
def _swrlz_v06_model_fixture(
    raw:str=_swrlz_v06_header(default="",alias="X-Swrlz-X-Request"),
    signature:str=_swrlz_v06_header(default="",alias="X-Swrlz-X-Signature")):
    import hashlib,hmac,json,os,re,time
    import x_diagnostic_client as x
    key=os.environ.get(x.KEY_NAME,"")
    if len(key)!=64 or len(raw)>512 or len(signature)!=64 or not hmac.compare_digest(x.mac(key,"model-fixture-request",raw.encode()),signature):
        raise _swrlz_v06_http_error(403,"MODEL_FIXTURE_V06_DENIED")
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
            if not callable(globals().get("_coder_generate")):raise RuntimeError("LIVE_CODER_NOT_CALLABLE")
            active=_swrlz_verified_repair_runtime_v7()
            baseline=signed_suite()
            result["beforeSha256"]=before
            result["baselineNonce"]=baseline["nonce"]
            result["baselineFailure"]=baseline["diagnostics"]["trusted_development"]["broken"]
            evidence=[{"runtimeEvidence":result["baselineFailure"],"expectedBehavior":"Click the Test interaction button; state changes from Ready to Click passed without page errors."}]
            evidence.append({"scope":"The reviewed fixture permits changing only the invalid CSS selector inside the existing onclick handler. The target is the existing status element containing Ready. All other characters, including quote style, whitespace and line endings, must remain identical. Browser behavior alone is insufficient for this trusted-only test."})
            task="Identify the existing status element ID from the HTML source. Repair the click handler by replacing only its incorrect selector token with that existing ID. Return exactly ONE replace_once patch in index.html using the shortest unique literal anchor. Do not rewrite the handler, change quotes, add a null guard, rename IDs, alter markup or modify any other bytes. No full page or prose."
            # This deliberately invokes the same production coding model and
            # exact patch engine, with no executor fallback or model authority.
            failures=[]
            for attempt in range(3):
                messages=active.prompt_messages(project,files,evidence,task,prior_failures=failures)
                def coder(payload):
                    if payload.get("modelId")!="coder":raise RuntimeError("WRONG_MODEL_ROUTE")
                    result["realModelCalls"]+=1
                    yield from _coder_generate(payload)
                mismatch=None
                try:
                    raw_proposal=active._model_patch(coder,{},messages)
                    edits=raw_proposal.get("patches")
                    if not isinstance(edits,list) or len(edits)!=1 or any(not isinstance(p,dict) or p.get("path")!="index.html" or p.get("op")!="replace_once" for p in edits):
                        raise ValueError("FIXTURE_PATCH_SCOPE")
                    proposal=active.bind_model_edits(project,files,raw_proposal)
                    applied=active.apply_proposal(project,files,proposal,expected_hashes={"index.html":before})
                    candidate=applied["proposedFiles"].get("index.html")
                    if not isinstance(candidate,str) or candidate!=fixture or applied["afterHashes"].get("index.html")!=expected:
                        mismatch=_swrlz_v06_candidate_delta(broken,fixture,candidate)
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
                    rejected={"attempt":attempt+1,"state":"rejected","reason":label}
                    if mismatch is not None:
                        rejected["mismatch"]=mismatch
                        failures.append(label+": "+json.dumps(mismatch,sort_keys=True)+
                            ". Re-read the original source; correct only the erroneous selector to the existing status element ID. Preserve all other characters. Submit a new single exact patch.")
                    else:
                        failures.append(label+". Return one exact replace_once edit on the existing selector token, not an entire handler.")
                    result["attempts"].append(rejected)
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
    tree=ast.parse(source)
    # The production coder can be imported under an alias, not defined in
    # station.py. Verify the existing binding or the established v12 call site.
    definitions={n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
    bindings=set(definitions)
    for n in ast.walk(tree):
        if isinstance(n,(ast.Import,ast.ImportFrom)):
            bindings.update(a.asname or a.name.split(".")[0] for a in n.names)
        elif isinstance(n,(ast.Assign,ast.AnnAssign)):
            targets=n.targets if isinstance(n,ast.Assign) else [n.target]
            bindings.update(t.id for t in targets if isinstance(t,ast.Name))
    calls=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=="_coder_generate"]
    # Register alongside the existing, verified live diagnostic route rather
    # than assuming the repair helper is before every ASGI mount/startup.
    diagnostic_routes=[n for n in definitions.values() if any(
        isinstance(d,ast.Call) and isinstance(d.func,ast.Attribute)
        and isinstance(d.func.value,ast.Name) and d.func.value.id=="app"
        and d.func.attr=="post" and d.args and isinstance(d.args[0],ast.Constant)
        and d.args[0].value=="/api/swrlz-x/v1/diagnostics" for d in n.decorator_list)]
    missing=[]
    anchor=definitions.get("_swrlz_execute_model_repair_v7")
    if anchor is None:missing.append("REPAIR_ENTRY")
    if "_swrlz_verified_repair_runtime_v7" not in definitions:missing.append("RUNTIME_GUARD")
    if "_coder_generate" not in bindings and not calls:missing.append("CODER_BINDING")
    if len(diagnostic_routes)!=1:missing.append("SIGNED_DIAGNOSTIC_ROUTE")
    if missing:raise RuntimeError("LIVE_STATION_ANCHOR_DRIFT:"+",".join(missing))
    # Insert before the actual AST node (including any decorators); preserve all
    # other source bytes. No invented alternate inference function or route.
    anchor=diagnostic_routes[0]
    line=min([anchor.lineno]+[d.lineno for d in anchor.decorator_list])
    lines=source.splitlines(keepends=True)
    lines.insert(line-1,block+"\n")
    updated="".join(lines)
    ast.parse(updated)
    print("LIVE_STATION_ANCHORS_PASS",flush=True)
    return updated

def selftest():
    for coder in ("def _coder_generate(payload):pass\n","from qwen_coder_engine import generate as _coder_generate\n","def existing_probe(payload):\n    yield from _coder_generate(payload)\n"):
        stub="def _swrlz_verified_repair_runtime_v7():pass\n"+coder+'@app.post("/api/swrlz-x/v1/diagnostics")\ndef existing_diagnostic():pass\n'+"def _swrlz_execute_model_repair_v7():pass\n"
        patched=patch_station(stub)
        assert patch_station(patched)==patched
        compile(patched,"<station fixture>","exec")
    try:patch_station("def _swrlz_execute_model_repair_v7():pass\n")
    except RuntimeError as exc:
        assert "CODER_BINDING" in str(exc) and "SIGNED_DIAGNOSTIC_ROUTE" in str(exc)
    else:raise AssertionError("missing production anchors accepted")
    # Exercise mismatch classification without executing any proposed HTML.
    route_tree=ast.parse(ROUTE.replace("__TRUSTED_FIXTURE__",repr("fixture")).replace("__X_SOURCE_SHA__",repr("digest")))
    helper=next(n for n in route_tree.body if isinstance(n,ast.FunctionDef) and n.name=="_swrlz_v06_candidate_delta")
    scope={}
    exec(compile(ast.Module(body=[helper],type_ignores=[]),"<trusted delta helper>","exec"),scope)
    delta=scope[helper.name]
    reviewed,_=source_fixture()
    broken=reviewed.replace("querySelector('#state')","querySelector('#missing')",1)
    assert broken!=reviewed
    assert delta(broken,reviewed,broken)["originalSelectorStillPresent"]
    changed=delta(broken,reviewed,reviewed+"\n")
    assert changed["expectedSelectorPresent"] and changed["changedOutsideAllowedSpan"]
    assert delta(broken,reviewed,None)["kind"]=="CANDIDATE_MISSING"
    print("MODEL_FIXTURE_SOURCE_SELFTEST_PASS",flush=True)

def wait_ready(api, revision):
    """Only test route registration. Invalid signature must reject before inference."""
    deadline=time.monotonic()+540
    attempt=0
    evidence={}
    with requests.Session() as session:
        session.trust_env=False
        while time.monotonic()<deadline:
            attempt+=1
            if str(api.repo_info(SPACE,repo_type="space").sha)!=revision:
                raise RuntimeError("STATION_CONCURRENT_CHANGE")
            try:
                stage=str(api.get_space_runtime(SPACE).stage)
            except Exception as exc:
                stage="UNKNOWN_"+type(exc).__name__
            evidence={"stage":stage,"attempt":attempt}
            try:
                with session.post(BASE+CHECK,headers={"X-Swrlz-X-Request":"{}","X-Swrlz-X-Signature":"0"*64},timeout=(10,10),allow_redirects=False,stream=True) as response:
                    evidence["httpStatus"]=response.status_code
                    if response.status_code==403:
                        body=response.raw.read(4097)
                        if len(body)<=4096:
                            try:detail=json.loads(body).get("detail")
                            except (ValueError,AttributeError):detail=None
                            if detail=="MODEL_FIXTURE_V06_DENIED":
                                print("MODEL_FIXTURE_ROUTE_READY",json.dumps(evidence),flush=True)
                                return
                if evidence.get("httpStatus")==404 and attempt%5==1:
                    with session.post(BASE+"/api/swrlz-x/v1/diagnostics",headers={"X-Swrlz-X-Request":"{}","X-Swrlz-X-Signature":"0"*64},timeout=(10,10),allow_redirects=False,stream=True) as previous:
                        evidence["existingDiagnosticHttpStatus"]=previous.status_code
            except requests.RequestException as exc:
                evidence["transport"]=type(exc).__name__
            print("MODEL_FIXTURE_STARTUP",json.dumps(evidence,sort_keys=True),flush=True)
            Path("swrlz-model-fixture-startup.json").write_text(json.dumps(evidence,indent=2)+"\n")
            time.sleep(10)
    raise RuntimeError("MODEL_FIXTURE_ROUTE_UNVERIFIED:"+json.dumps(evidence,sort_keys=True))

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
        if new!=old:api.restart_space(SPACE)
        wait_ready(api,new)
        # Do not repeatedly trigger the real model if a long request loses its connection.
        rec=live(key)
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
            api.restart_space(SPACE)
        raise

if __name__=="__main__":
    selftest()
    if sys.argv[1:]==["publish"]:publish()
    elif sys.argv[1:]:raise SystemExit("unknown mode")
