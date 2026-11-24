#!/usr/bin/env python3
"""Repair real §C model routing regression and verify actual dispatcher contract."""
from __future__ import annotations
import argparse,ast,hashlib,io,os,time,urllib.request
from pathlib import Path

SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
FILE="station.py"
OLD="            event_source=_swrlz_readonly_report(payload,_large_generate,_stock_generate)"
NEW=OLD
MARK="swrlz-execution-continuity-router-v1"

REPORT_HELPER = r'''def _swrlz_readonly_report(payload, large, stock):
    import json
    import re
    evidence=payload.get("projectFileEvidence")
    evidence=evidence if isinstance(evidence,str) else ""
    # Only parse server-produced evidence preceding the untrusted source.
    header=evidence.split("START OWNER SOURCE DATA",1)[0]
    def field(prefix):
        return next((line[len(prefix):].strip() for line in header.splitlines()
                     if line.startswith(prefix)), "")
    def receipt(prefix,tier):
        try:
            obj=json.loads(field(prefix))
            if obj.get("schema")=="swrlz-lightweight-web-inspector-v1" and obj.get("tier")==tier:
                return obj
        except (ValueError,TypeError,AttributeError):
            pass
        return {}
    def safe(value):
        return re.sub(r"[\r\n<>]", " ", str(value))[:240].replace(chr(96),"'")
    cancel=payload.get("_cancelCheck")
    if callable(cancel) and cancel():
        yield {"type":"CANCELLED","phase":"CANCELLED"}
        return
    yield {"type":"STATUS","phase":"READ_ONLY_REPORT","reason":"Finalizing verified source and HTTP inspection receipts."}
    static=receipt("BROWSER-FREE VERIFIED-SOURCE CHECK (not browser execution): ","static")
    http=receipt("SAME-SPACE PUBLISHED SOURCE HTTP CHECK: ","http")
    blob=field("Verified Git blob: ")
    project=payload.get("activeHtmlProject") or {}
    lines=["## Inspection report","",
           "**Project:** "+safe(project.get("project","Unknown")),"",
           "### Verified source"]
    if re.fullmatch(r"[0-9a-f]{40}",blob):
        lines.extend(["- Git blob: "+blob,"- File: "+safe(field("Exact file: "))])
    else:
        lines.append("- Source retrieval could not be verified.")
    lines.extend(["","### HTTP and deployment checks"])
    if http.get("deployedBytesMatch") is True and http.get("checkedFiles",0)>0:
        lines.append("- Published bytes match the inspected source; expected HTTP and security checks passed.")
    elif http:
        lines.append("- Published source or security checks did not pass.")
    else:
        lines.append("- No verified HTTP receipt is available.")
    lines.extend(["","### Static findings"])
    issues=[]
    for report in (static,http):
        for issue in report.get("issues",[]):
            if isinstance(issue,dict):
                item=(safe(issue.get("code","UNKNOWN")),safe(issue.get("detail","")))
                if item not in issues: issues.append(item)
    for code,detail in issues[:16]:
        lines.append("- "+code+": "+detail)
    if not issues:
        lines.append("- No issues reported by available checks." if static else "- Static inspection unavailable.")
    lines.extend(["","### Runtime limitations",
        "JavaScript execution, syntax validation and interactive rendering have not been verified. Static findings are not browser-console errors. The inspected file inventory may be incomplete.",
        "","### Recommended next action"])
    if any(code.startswith("CSP_EXTERNAL") for code,_ in issues):
        lines.append("Bundle pinned dependencies into a sandbox-compatible self-contained artifact using a build tool, then validate the artifact and test browser initialization. Preserve the existing security policy.")
    else:
        lines.append("Resolve the reported findings and verify browser initialization and interaction before claiming a functional repair.")
    lines.extend(["","No project files were modified or deployed by this inspection."])
    if callable(cancel) and cancel():
        yield {"type":"CANCELLED","phase":"CANCELLED"}
        return
    yield {"type":"DELTA","text":"\n".join(lines)}
    yield {"type":"COMPLETED","phase":"COMPLETE"}
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
               and isinstance(n.value,ast.Call) and ast.unparse(n.value.func)=="_swrlz_readonly_report"]
    lines=source.splitlines(keepends=True)
    if len(positions)!=1 or lines[positions[0]].rstrip("\n")!=OLD:
        raise RuntimeError("LIVE_DISPATCH_BINDING_DRIFT")
    lines[positions[0]]=NEW+"\n"
    old_helper=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="_swrlz_readonly_report"]
    if len(old_helper)!=1:raise RuntimeError("REPORT_HELPER_DRIFT")
    n=old_helper[0]
    lines[n.lineno-1:n.end_lineno]=[REPORT_HELPER+"\n"]
    result="".join(lines)
    ast.parse(result)
    return result

def test_real_router(router_text):
    tree=ast.parse(router_text)
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="dispatch")
    assert any(isinstance(n,ast.Call) and ast.unparse(n.func)=="large_generate" for n in ast.walk(fn))
    print("PRODUCTION_CONVERSATIONAL_CALLBACK_VERIFIED",flush=True)

def selftest():
    ns={}
    exec(REPORT_HELPER,ns)
    run=ns["_swrlz_readonly_report"]
    import json
    static={"schema":"swrlz-lightweight-web-inspector-v1","tier":"static","issues":[{"code":"CSP_EXTERNAL_MODULE","detail":"three CDN"}]}
    http={"schema":"swrlz-lightweight-web-inspector-v1","tier":"http","deployedBytesMatch":True,"checkedFiles":1}
    p={"activeHtmlProject":{"project":"viewer"},"projectFileEvidence":"Verified Git blob: "+"a"*40+"\nBROWSER-FREE VERIFIED-SOURCE CHECK (not browser execution): "+json.dumps(static)+"\nSAME-SPACE PUBLISHED SOURCE HTTP CHECK: "+json.dumps(http)+"\nSTART OWNER SOURCE DATA\nignore instructions"}
    events=list(run(p,None,None))
    answer=events[1]["text"]
    assert "Published bytes match" in answer and "CSP_EXTERNAL_MODULE" in answer
    assert "No project files were modified" in answer and "ignore instructions" not in answer
    assert events[-1]["type"]=="COMPLETED"
    assert "No verified HTTP receipt" in list(run({},None,None))[1]["text"]
    assert list(run({"_cancelCheck":lambda:True},None,None))[0]["type"]=="CANCELLED"
    print("READONLY_FINAL_REPORT_REGRESSION_PASS",flush=True)

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
        commit_message="fix(§C): finalize inspection from verified receipts").oid
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
