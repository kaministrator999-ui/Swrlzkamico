#!/usr/bin/env python3
"""Verify server browser receipt, or render already-verified live bytes on the worker."""
import argparse,json,os,sys,urllib.request
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from api.browser_worker_protocol_v1 import derive_key,verify_envelope,file_hashes
from api.html_project_browser_client_v1 import validate
from api.html_project_agent_v1 import verify_source
from api.lightweight_webpage_inspector_v1 import inspect_files
from urllib.parse import quote
ORIGIN="https://kamiloki-swyrlz.hf.space"
def main():
    p=argparse.ArgumentParser();p.add_argument("mode",choices=["receipt","live"]);p.add_argument("--project",required=True);p.add_argument("--root",required=True);args=p.parse_args()
    root=Path(args.root).resolve()
    files={f.relative_to(root).as_posix():f.read_text(encoding="utf-8") for f in root.rglob("*")
           if f.is_file() and f.suffix.lower() in {".html",".htm",".js",".mjs",".css",".json",".svg"}}
    hashes=verify_source(args.project,files)
    key=derive_key(os.environ.get("HF_TOKEN",""))
    if args.mode=="receipt":
        envelope=json.loads(os.environ["BROWSER_RECEIPT_JSON"])
    else:
        actual={}
        for name,content in files.items():
            req=urllib.request.Request(ORIGIN+"/api/html-projects/"+args.project+"/"+quote(name,safe="/"),headers={"Cache-Control":"no-cache"})
            with urllib.request.urlopen(req,timeout=15) as r:
                body=r.read(1_000_001)
                if r.status!=200 or body!=content.encode():raise RuntimeError("LIVE_ASSET_BYTES_MISMATCH:"+name)
                if name.endswith((".html",".htm")):
                    csp=r.headers.get("Content-Security-Policy","")
                    if "sandbox allow-scripts" not in csp or "allow-same-origin" in csp or "connect-src 'none'" not in csp:
                        raise RuntimeError("LIVE_SANDBOX_POLICY_MISMATCH")
                actual[name]=body.decode()
        envelope=validate(args.project,actual,inspect_files(actual,known_files_complete=True).get("renderingRequiredForFullVerification") is True,key=key)
    receipt=verify_envelope(key,envelope,project=args.project,hashes=hashes)
    if receipt.get("browserVerified") is not True or receipt.get("sandbox") is not True:
        raise RuntimeError("SERVER_BROWSER_VERIFICATION_FAILED:"+repr(receipt.get("issues")))
    name="browser-candidate-receipt.json" if args.mode=="receipt" else "browser-live-receipt.json"
    Path(name).write_text(json.dumps(envelope,indent=2))
    print("SERVER_BROWSER_RECEIPT_VERIFIED",args.mode,receipt["screenshotSha256"],flush=True)
if __name__=="__main__":main()
