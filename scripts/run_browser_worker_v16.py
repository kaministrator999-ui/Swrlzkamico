#!/usr/bin/env python3
"""Credential-free, read-only CI browser worker. Exact patch -> ephemeral files -> browser."""
from __future__ import annotations
import json,os,re,subprocess,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from api.html_project_agent_v1 import apply_proposal,verify_source,inspect_static,safe_path,VALID_EXT
from api.html_project_browser_backend_v1 import SCHEMA,validate_identity
def main():
    project=os.environ["PROJECT"];sha=os.environ["SOURCE_SHA"];nonce=os.environ["NONCE"]
    run_id=int(os.environ["GITHUB_RUN_ID"])
    validate_identity(project,sha,nonce)
    root=Path("reviewed-source").resolve()
    if subprocess.check_output(["git","-C",str(root),"rev-parse","HEAD"],text=True).strip()!=sha:
        raise RuntimeError("BROWSER_SOURCE_CHECKOUT_MISMATCH")
    if os.environ.get("GITHUB_SHA")!=sha:raise RuntimeError("BROWSER_WORKFLOW_REVISION_MISMATCH")
    folder=root/"html-projects"/project
    if folder.is_symlink() or not folder.is_dir():raise RuntimeError("BROWSER_PROJECT_SOURCE_MISSING")
    files={}
    for f in sorted(folder.rglob("*")):
        if f.is_symlink():raise RuntimeError("BROWSER_SOURCE_SYMLINK")
        if f.is_file() and f.suffix.lower() in VALID_EXT:
            rel=safe_path(f.relative_to(folder).as_posix())
            files[rel]=f.read_text(encoding="utf-8")
    verify_source(project,files)
    raw=os.environ["MODEL_PROPOSAL_JSON"]
    if len(raw.encode())>48000:raise RuntimeError("BROWSER_PATCH_LIMIT")
    result=apply_proposal(project,files,json.loads(raw),validation=inspect_static)
    candidate={**files,**result["proposedFiles"]}
    hashes=verify_source(project,candidate,expected_hashes=result["afterHashes"])
    receipt={"schema":SCHEMA,"project":project,"sourceSha":sha,"nonce":nonce,"runId":run_id,
             "hashes":hashes,"browserVerified":False,"issues":[],
             "scope":"read-only ephemeral GitHub VM, production CSP, actual Chromium load/render smoke; no task-specific interaction claims"}
    with tempfile.TemporaryDirectory(prefix="swrlz-browser-candidate-") as temp:
        dest=Path(temp)/project
        for rel,body in candidate.items():
            f=dest/rel;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(body.encode())
        out=Path(temp)/"smoke.json"
        # Do not inherit OAuth, GitHub/HF tokens, deployment authority or workflow env.
        env={k:os.environ[k] for k in ("PATH","HOME","LANG","PLAYWRIGHT_BROWSERS_PATH","LD_LIBRARY_PATH") if k in os.environ}
        env["PYTHONDONTWRITEBYTECODE"]="1"
        cmd=[sys.executable,str(Path("scripts/verify_html_project_browser_v1.py").resolve()),
             "--project",project,"--root",str(dest),"--receipt",str(out)]
        try:
            proc=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=85)
            if proc.returncode==0:
                smoke=json.loads(out.read_text())
                if smoke.get("browserVerified") is not True or smoke.get("entrySha256")!=hashes["index.html"]:
                    raise RuntimeError("BROWSER_SMOKE_RECEIPT_MISMATCH")
                receipt.update(browserVerified=True,entrySha256=smoke["entrySha256"],
                               canvasCount=smoke.get("canvasCount",0),interactions=smoke.get("interactions",[]))
            else:
                err=proc.stderr[-8000:]
                runtime_markers=("BROWSER_EXECUTION_FAILED:","BROWSER_BODY_NOT_VISIBLE","BROWSER_CANVAS_EMPTY",
                                 "BROWSER_ENTRY_UNAVAILABLE","TimeoutError:","BROWSER_ENTRY_HASH_MISMATCH")
                if "BrowserType.launch" in err or "Executable doesn't exist" in err or not any(m in err for m in runtime_markers):
                    receipt["infrastructureError"]="BROWSER_HARNESS_FAILED"
                else:
                    last=[line for line in err.splitlines() if any(m in line for m in runtime_markers)]
                    receipt["issues"]=[{"code":"BROWSER_RUNTIME_ERROR","detail":(last[-1] if last else "Browser execution failed")[:1500]}]
        except subprocess.TimeoutExpired:
            receipt["infrastructureError"]="BROWSER_HARNESS_TIMEOUT"
        except (OSError,ValueError,KeyError,RuntimeError):
            receipt["infrastructureError"]="BROWSER_HARNESS_RECEIPT_INVALID"
    Path("browser-receipt.json").write_text(json.dumps(receipt,ensure_ascii=False),encoding="utf-8")
    print("V16_BROWSER_RECEIPT",json.dumps({"verified":receipt["browserVerified"],
          "infrastructureError":receipt.get("infrastructureError"),"issueCount":len(receipt["issues"]),
          "entrySha256":hashes["index.html"]}),flush=True)
if __name__=="__main__":main()
