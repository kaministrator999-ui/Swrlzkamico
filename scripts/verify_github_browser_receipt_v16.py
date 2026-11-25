#!/usr/bin/env python3
"""Delivery checks the actual earlier worker run, artifact, and exact reconstructed bytes."""
import argparse,json,os,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from api.html_project_browser_backend_v1 import github_api,fetch_verified_receipt
from api.html_project_agent_v1 import verify_source,VALID_EXT
def main():
    p=argparse.ArgumentParser();p.add_argument("--project",required=True);p.add_argument("--root",required=True);a=p.parse_args()
    root=Path(a.root).resolve()
    files={f.relative_to(root).as_posix():f.read_text(encoding="utf-8") for f in root.rglob("*")
           if f.is_file() and f.suffix.lower() in VALID_EXT}
    hashes=verify_source(a.project,files)
    claimed=json.loads(os.environ["GITHUB_BROWSER_RECEIPT_JSON"])
    if claimed.get("backend")!="github-actions":raise RuntimeError("WRONG_BROWSER_BACKEND")
    claim=claimed["receipt"]
    token=os.environ["GH_TOKEN"]
    actual=fetch_verified_receipt(github_api(token),token,a.project,os.environ["SOURCE_SHA"],claim["nonce"],claim["runId"],hashes)
    if actual!=claim or actual["browserVerified"] is not True:raise RuntimeError("EXACT_PREAPPROVAL_BROWSER_RECEIPT_FAILED")
    Path("browser-candidate-receipt.json").write_text(json.dumps(claimed,indent=2))
    print("V16_PREAPPROVAL_BROWSER_RECEIPT_VERIFIED",actual["runId"],actual["entrySha256"],flush=True)
if __name__=="__main__":main()
