#!/usr/bin/env python3
"""Scoped CAS release of GitHub review UI and receipt styling to live §C."""
import argparse,hashlib,io,os
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
SPACE="kamiloki/Swyrlz"
ASSET="chat/§wyrlz/assets/github-change-review-v1.js"
PAGE="chat/§wyrlz/index.html"
CSS="""
.swrlz-github-change-review .swrlz-github-change-summary{font-size:13px;font-weight:650;overflow-wrap:anywhere}
.swrlz-github-change-review .swrlz-github-change-actions{display:flex;gap:10px;position:sticky;top:60px;z-index:3;background:#081e30;padding:8px 0;border-bottom:1px solid #2b546b}
.swrlz-github-change-review .swrlz-github-change-actions button{flex:1;min-height:46px}
.swrlz-github-change-review details{min-width:0;border:1px solid #294d65;border-radius:9px;padding:8px}
.swrlz-github-change-review summary{cursor:pointer;font-weight:600;padding:5px 2px}
.swrlz-github-change-review .swrlz-github-change-receipt{border:1px solid #2f987e;border-radius:10px;padding:12px;background:#103b3a}
.swrlz-github-change-review .swrlz-github-change-receipt[hidden]{display:none}
.swrlz-github-change-review .swrlz-github-change-receipt a{color:#7bdcff;text-decoration:underline}
@media(max-width:680px){.swrlz-github-change-review{gap:8px;padding:10px}.swrlz-github-change-review .swrlz-github-change-actions{top:56px}}
"""
MARK="/* swrlz-github-review-mobile-v2 */"
def transform_page(src):
    old='<script src="/chat/§wyrlz/assets/github-change-review-v1.js?v=2" defer></script>'
    assert src.count(old)==1,"Live script anchor drift"
    assert MARK not in src,"Already installed"
    close='</style>'
    start=src.index('<style id="swrlz-github-review-v1">')
    end=src.index(close,start)
    src=src[:end]+MARK+"\n"+CSS+"\n"+src[end:]
    src=src.replace(old,old.replace('v=2','v=3'),1)
    return src
def main(mode):
    api=HfApi(token=os.getenv("HF_TOKEN"))
    rev=api.repo_info(SPACE,repo_type="space").sha
    live_asset=Path(hf_hub_download(SPACE,ASSET,repo_type="space",revision=rev)).read_bytes()
    live_page=Path(hf_hub_download(SPACE,PAGE,repo_type="space",revision=rev)).read_bytes()
    new_asset=Path("chat/github-change-review-v1.js").read_bytes()
    if mode=="verify":
        assert live_asset==new_asset,"Live asset differs"
        assert MARK in live_page.decode()
        print("GITHUB_REVIEW_UI_LIVE_VERIFIED",rev,flush=True)
        return
    # Fail closed if live asset diverges from known pre-release component.
    baseline=Path("chat/github-change-review-v1.js").read_text()
    assert 'wrapper.insertBefore(actions,reviewDetails)' in baseline
    assert 'function reconcileReceipt(card,threadId)' in live_asset.decode()
    assert 'wrapper.append(reject,approve);' in live_asset.decode(),"Live component drift: inspect before replacing"
    assert 'receiptPanel.hidden=false' not in live_asset.decode(),"Already upgraded"
    updated_page=transform_page(live_page.decode()).encode()
    print("GITHUB_REVIEW_UI_PREFLIGHT",rev,hashlib.sha256(live_asset).hexdigest(),hashlib.sha256(new_asset).hexdigest(),flush=True)
    if mode=="snapshot":return
    assert mode=="publish" and os.getenv("HF_TOKEN") and os.getenv("SWRLZ_GITHUB_UI_APPROVED")=="1"
    assert api.repo_info(SPACE,repo_type="space").sha==rev,"Live source changed"
    commit=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
        operations=[CommitOperationAdd(path_in_repo=ASSET,path_or_fileobj=io.BytesIO(new_asset)),
                    CommitOperationAdd(path_in_repo=PAGE,path_or_fileobj=io.BytesIO(updated_page))],
        commit_message="ui(§C): compact GitHub review and verified receipt")
    assert Path(hf_hub_download(SPACE,ASSET,repo_type="space",revision=commit.oid)).read_bytes()==new_asset
    assert Path(hf_hub_download(SPACE,PAGE,repo_type="space",revision=commit.oid)).read_bytes()==updated_page
    print("GITHUB_REVIEW_UI_PUBLISHED",commit.oid,flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mode",choices=("snapshot","publish","verify"))
    main(p.parse_args().mode)
