#!/usr/bin/env python3
"""Release only the GitHub review JS and two anchored live HTML edits."""
import argparse, hashlib, io, json, os
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
SPACE="kamiloki/Swyrlz"
HTML="chat/§wyrlz/index.html"
ASSET="chat/§wyrlz/assets/github-change-review-v1.js"
SOURCE=Path("chat/github-change-review-v1.js")
REPORT=Path("reports/github-review-receipt-v2")
OLD='if(!window.SwrlzGithubWorkView?.render(card,widget)){'
NEW='queueMicrotask(()=>window.SwrlzGithubChangeReviewV1?.reconcileReceipt(card,String(activeThreadId||"")));\n            '+OLD
def sha(b):return hashlib.sha256(b).hexdigest()
def patch(s):
    assert s.count(OLD)==1,"Live GitHub receipt renderer changed"
    assert "reconcileReceipt(card,String(activeThreadId" not in s,"Already integrated"
    assert s.count("github-change-review-v1.js?v=1")==1,"Asset version changed"
    return s.replace(OLD,NEW,1).replace("github-change-review-v1.js?v=1","github-change-review-v1.js?v=2",1)
def main(mode):
    api=HfApi(token=os.getenv("HF_TOKEN"))
    revision=api.repo_info(SPACE,repo_type="space").sha
    current=Path(hf_hub_download(SPACE,HTML,repo_type="space",revision=revision)).read_bytes()
    asset=SOURCE.read_bytes()
    if mode=="verify":
        assert "reconcileReceipt(card,String(activeThreadId" in current.decode()
        assert "github-change-review-v1.js?v=2" in current.decode()
        remote=Path(hf_hub_download(SPACE,ASSET,repo_type="space",revision=revision)).read_bytes()
        assert remote==asset
        print("REVIEW_RECEIPT_LIVE_VERIFIED",revision,flush=True)
        return
    new=patch(current.decode()).encode()
    assert b"reconcileReceipt" in asset and b"Exact bytes verified" in asset
    REPORT.mkdir(parents=True,exist_ok=True)
    (REPORT/"previous.html").write_bytes(current)
    print("REVIEW_RECEIPT_PREFLIGHT",json.dumps({"revision":revision,"htmlBefore":sha(current),"htmlAfter":sha(new),"asset":sha(asset)}),flush=True)
    if mode=="snapshot":return
    assert os.getenv("SWRLZ_REVIEW_RECEIPT_APPROVED")=="1"
    assert os.getenv("HF_TOKEN")
    assert api.repo_info(SPACE,repo_type="space").sha==revision,"Space changed during review"
    commit=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=revision,
      operations=[CommitOperationAdd(path_in_repo=HTML,path_or_fileobj=io.BytesIO(new)),
                  CommitOperationAdd(path_in_repo=ASSET,path_or_fileobj=io.BytesIO(asset))],
      commit_message="fix(§C): resolve GitHub review card from verified work receipt")
    for path,expected in ((HTML,new),(ASSET,asset)):
        got=Path(hf_hub_download(SPACE,path,repo_type="space",revision=commit.oid)).read_bytes()
        assert got==expected,"Release readback failed: "+path
    print("REVIEW_RECEIPT_PUBLISHED",commit.oid,flush=True)
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=["snapshot","publish","verify"])
    main(parser.parse_args().mode)
