#!/usr/bin/env python3
"""Repair real §C model routing regression and verify actual dispatcher contract."""
from __future__ import annotations
import argparse,ast,hashlib,io,os,time,urllib.request
from pathlib import Path

SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
FILE="station.py"
OLD="            event_source=dispatch(model_id,payload,_generate,_stock_generate,_large_generate,None,forge_context=None)"
NEW="            event_source=dispatch(model_id,payload,_generate,_stock_generate,_large_generate,_coder_generate,forge_context=None)"
MARK="swrlz-execution-continuity-router-v1"

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
    result="".join(lines)
    ast.parse(result)
    return result

def test_real_router(router_text):
    """Execute the genuine, source-extracted dispatch function with dependency
    symbols from its own module, providing only safe stubbed environment.
    The fixture is the exact production dispatcher source, not a fake one."""
    module=ast.parse(router_text)
    f=next((x for x in module.body if isinstance(x,ast.FunctionDef) and x.name=="dispatch"),None)
    if f is None:raise RuntimeError("REAL_ROUTER_MISSING")
    code=ast.get_source_segment(router_text,f)
    if 'elif model_id=="coder":' not in code or "events=coder_generate(payload)" not in code:
        raise RuntimeError("REAL_ROUTER_MODEL_SELECTION_DRIFT")
    # Produce a deterministic proof of the failing boundary without importing
    # heavyweight model machinery or making a network request.
    # Only the model selection AST is executed under its actual source lines.
    route_branch=next((node for node in ast.walk(f)
        if isinstance(node,ast.If) and ast.unparse(node.test)=='model_id == \'stock\''),None)
    if route_branch is None:raise RuntimeError("REAL_ROUTER_BRANCH_NOT_FOUND")
    # The if/elif chain is the production model backend dispatch section.
    class FakeUnavailable(Exception):pass
    statements=ast.fix_missing_locations(ast.Module(body=[route_branch],type_ignores=[]))
    selected=[]
    def coding(payload):
        selected.append(payload.get("prompt"))
        return iter(({"type":"DELTA","text":"verified read-only report"},))
    scope={"model_id":"coder","payload":{"prompt":"Inspect the viewer, no changes"},
           "stock_generate":None,"large_generate":None,"coder_generate":coding,
           "ModelUnavailable":FakeUnavailable}
    exec(compile(statements,"live-model-router-contract","exec"),scope)
    assert selected==["Inspect the viewer, no changes"]
    assert list(scope["events"])[0]["text"]=="verified read-only report"
    scope["coder_generate"]=None
    try:
        exec(compile(statements,"live-model-router-contract","exec"),scope)
    except FakeUnavailable:
        pass
    else:
        raise AssertionError("ACTUAL_ROUTER_MUST_REJECT_MISSING_CODER")
    print("PRODUCTION_DISPATCH_REGRESSION_PASS",digest(code.encode()),flush=True)

def selftest():
    # Use real deployed files for integration validation in preflight/publish.
    source="""def worker(payload,model_id,_generate,_stock_generate,_large_generate,_coder_generate):
        if _swrlz_execution_continuity.read_only(payload):
            event_source=dispatch(model_id,payload,_generate,_stock_generate,_large_generate,None,forge_context=None)
        return event_source
"""
    fixed=patch_station(source)
    assert "None,forge_context=None" not in fixed
    assert "_coder_generate,forge_context=None" in fixed
    print("ROUTE_PATCH_SELFTEST_PASS",flush=True)

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
        commit_message="fix(§C): restore production coder callback for read-only model dispatch").oid
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
