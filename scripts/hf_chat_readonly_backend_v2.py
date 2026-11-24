#!/usr/bin/env python3
"""Repair real §C model routing regression and verify actual dispatcher contract."""
from __future__ import annotations
import argparse,ast,hashlib,io,os,time,urllib.request
from pathlib import Path

SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
FILE="station.py"
OLD="            event_source=dispatch(model_id,payload,_generate,_stock_generate,_large_generate,_coder_generate,forge_context=None)"
NEW="            event_source=_swrlz_readonly_report(payload,_large_generate,_stock_generate)"
MARK="swrlz-execution-continuity-router-v1"

REPORT_HELPER = '''
def _swrlz_readonly_report(payload, large, stock):
    report=dict(payload)
    report["programmingIntent"]={"codingTask":False,"contentMode":"explanation","source":"verified-read-only-inspection"}
    report["programming"]=report["programmingIntent"]
    report["presentationIntent"]="PROSE"
    for key in ("codeContinuation","priorProgrammingState","sourceChangeMode","githubSourceChangeTask"):
        report.pop(key,None)
    backend=large if callable(large) else stock
    if not callable(backend):
        raise RuntimeError("No conversational backend available for read-only inspection")
    report["selectedModelId"]="700m" if backend is large else "stock"
    yield {"type":"STATUS","phase":"READ_ONLY_REPORT","reason":"Generating an evidence-based report using the conversational backend."}
    yield from backend(report)
'''
def digest(data):return hashlib.sha256(data).hexdigest()

def patch_station(source):
    tree=ast.parse(source)
    matches=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.If) and ast.unparse(node.test)=="_swrlz_execution_continuity.read_only(payload)":
            matches.append(node)
    if len(matches)!=1:raise RuntimeError("READONLY_ROUTE_DRIFT")
    positions=[n.lineno-1 for n in matches[0].body if isinstance(n,ast.Assign)
               and isinstance(n.value,ast.Call) and ast.unparse(n.value.func)=="dispatch"]
    lines=source.splitlines(keepends=True)
    if len(positions)!=1 or lines[positions[0]].rstrip("\n")!=OLD:
        raise RuntimeError("LIVE_DISPATCH_BINDING_DRIFT")
    lines[positions[0]]=NEW+"\n"
    result="".join(lines)+"\n"+REPORT_HELPER+"\n"
    ast.parse(result)
    return result

def test_real_router(router_text):
    tree=ast.parse(router_text)
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="dispatch")
    assert any(isinstance(n,ast.Call) and ast.unparse(n.func)=="large_generate" for n in ast.walk(fn))
    print("PRODUCTION_CONVERSATIONAL_CALLBACK_VERIFIED",flush=True)

def selftest():
    source="""def worker(payload,model_id,_generate,_stock_generate,_large_generate,_coder_generate):
        if _swrlz_execution_continuity.read_only(payload):
            event_source=dispatch(model_id,payload,_generate,_stock_generate,_large_generate,_coder_generate,forge_context=None)
        return event_source
"""
    from types import SimpleNamespace
    ns={"_swrlz_execution_continuity":SimpleNamespace(read_only=lambda p:True)}
    exec(compile(patch_station(source),"station-test","exec"),ns)
    def backend(p):
        assert p["programmingIntent"]["codingTask"] is False
        assert p["projectFileEvidence"]=="verified"
        assert "codeContinuation" not in p
        yield {"type":"DELTA","text":"report"}
    p={"projectFileEvidence":"verified","codeContinuation":{}}
    for large,stock in ((backend,None),(None,backend)):
        events=list(ns["worker"](p,"coder",None,stock,large,None))
        assert events[-1]["text"]=="report"
    print("READONLY_BACKEND_REGRESSION_PASS",flush=True)

def health():
    req=urllib.request.Request(BASE+"/chat/%C2%A7wyrlz?__routing_fix=1",
         headers={"Cache-Control":"no-cache"})
    with urllib.request.urlopen(req,timeout=25) as resp:
        if resp.status!=200 or "text/html" not in resp.headers.get("Content-Type",""):
            raise RuntimeError("CHAT_HEALTH_UNVERIFIED")
        resp.read(200)

def main(mode):
    selftest()
    if mode=="selftest":return
    from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
    token=os.getenv("HF_TOKEN") or None
    api=HfApi(token=token)
    rev=str(api.repo_info(SPACE,repo_type="space").sha)
    before=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=rev,token=token)).read_bytes()
    router=Path(hf_hub_download(SPACE,"model_router.py",repo_type="space",revision=rev,token=token)).read_text()
    candidate=patch_station(before.decode()).encode()
    test_real_router(router)
    print("PRODUCTION_ROUTER_PREFLIGHT",rev,digest(candidate),flush=True)
    if mode=="preflight":return
    if mode!="publish" or not token or os.environ.get("SWRLZ_REAL_ROUTER_APPROVED")!="1":
        raise PermissionError("RELEASE_NOT_AUTHORIZED")
    if str(api.repo_info(SPACE,repo_type="space").sha)!=rev:
        raise RuntimeError("CONCURRENT_SPACE_UPDATE")
    new=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
        operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=io.BytesIO(candidate))],
        commit_message="fix(§C): use conversational backend for read-only inspection").oid
    print("ROUTER_FIX_HF_COMMITTED",new,flush=True)
    try:
        got=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=new,token=token)).read_bytes()
        if got!=candidate:raise RuntimeError("SOURCE_READBACK_MISMATCH")
        for i in range(25):
            try:
                health()
                print("ROUTER_FIX_LIVE_HEALTH_VERIFIED",new,flush=True)
                return
            except (RuntimeError,OSError,TimeoutError) as exc:
                if i==24:raise RuntimeError("LIVE_CHAT_HEALTH_NOT_VERIFIED") from exc
                time.sleep(10)
    except Exception:
        if str(api.repo_info(SPACE,repo_type="space").sha)==new:
            reverted=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=new,
                operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=io.BytesIO(before))],
                commit_message="rollback(§C): production routing health unverified").oid
            print("ROUTER_FIX_ROLLBACK",reverted,flush=True)
        raise
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=["selftest","preflight","publish"])
    main(parser.parse_args().mode)
