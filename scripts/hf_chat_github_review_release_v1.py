#!/usr/bin/env python3
"""GitHub review live-release preflight. Never deploy a stale §C/§E snapshot."""
import argparse, hashlib, json, os, pathlib, re

SPACE="kamiloki/Swyrlz"
OUT=pathlib.Path("reports/github-review-live-v1")
LIVE_PATHS=("station.py","chat/§wyrlz/index.html")
NEW_PATHS=("github_review_gate_v1.py","chat/§wyrlz/assets/github-change-review-v1.js")

def snapshot():
    from huggingface_hub import HfApi, hf_hub_download
    api=HfApi(token=os.environ.get("HF_TOKEN"))
    revision=str(api.repo_info(SPACE,repo_type="space").sha)
    if not re.fullmatch(r"[0-9a-f]{40}",revision):
        raise RuntimeError("No immutable live revision; refuse deployment")
    files=set(api.list_repo_files(SPACE,repo_type="space",revision=revision))
    if not set(LIVE_PATHS).issubset(files):
        raise RuntimeError("Current live §C layout differs; refuse deployment")
    OUT.mkdir(parents=True,exist_ok=True)
    manifest={"space":SPACE,"revision":revision,"paths":{},"integration_ready":False}
    for path in LIVE_PATHS:
        raw=pathlib.Path(hf_hub_download(SPACE,path,repo_type="space",revision=revision)).read_bytes()
        manifest["paths"][path]=hashlib.sha256(raw).hexdigest()
        dest=OUT/"before"/path
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_bytes(raw)
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("EXACT_LIVE_SNAPSHOT",json.dumps(manifest,sort_keys=True))
    print("DEPLOYMENT_GUARD: review backend and UI not yet integrated with live Station request lifecycle")

def publish():
    if os.environ.get("SWRLZ_GITHUB_REVIEW_RELEASE_APPROVED")!="1":
        raise PermissionError("Explicit release approval missing")
    manifest=json.loads((OUT/"manifest.json").read_text())
    if not manifest.get("integration_ready"):
        raise RuntimeError("REFUSE_PARTIAL_DEPLOY: no authenticated live Station integration or end-to-end approval proof")
    raise RuntimeError("REFUSE_UNIMPLEMENTED_CAS_RELEASE: publication is disabled until live-compatible patch and rollback are validated")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=("snapshot","publish"))
    args=parser.parse_args()
    snapshot() if args.mode=="snapshot" else publish()
