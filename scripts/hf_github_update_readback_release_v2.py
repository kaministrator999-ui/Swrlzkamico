#!/usr/bin/env python3
"""CAS release of UPDATE_FILE readback fix to exact live Space source."""
import argparse,hashlib,io,os
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
SPACE="kamiloki/Swyrlz"
SOURCE=Path("api/github_review_update_v1.py")
PATHS=("github_review_update_v1.py","api/github_review_update_v1.py")
def main(mode):
    api=HfApi(token=os.getenv("HF_TOKEN"))
    rev=api.repo_info(SPACE,repo_type="space").sha
    files=set(api.list_repo_files(SPACE,repo_type="space",revision=rev))
    targets=[p for p in PATHS if p in files]
    assert len(targets)==1,("Expected exactly one live update module",targets)
    target=targets[0]
    before=Path(hf_hub_download(SPACE,target,repo_type="space",revision=rev)).read_bytes()
    original=before.decode()
    old='    _, text = _read(auth, item["path"])\n    if text.encode("utf-8") != item["content"]:\n        raise CreateFileError("GITHUB_READBACK_MISMATCH", 502)'
    updated=SOURCE.read_text()
    if mode=="verify":
        assert "committed blob SHA" in original
        print("READBACK_LIVE_VERIFIED",rev,flush=True)
        return
    assert original.count(old)==1,"Live readback guard differs; reconcile manually"
    assert 'import requests\n' not in original
    assert 'from urllib.parse import quote\n' not in original
    start=updated.index('    # GitHub\'s successful PUT includes the committed blob SHA.')
    end=updated.index('\n    return {',start)
    patch=updated[start:end]
    after=(original.replace('import time\n','import time\nimport requests\nfrom urllib.parse import quote\n',1)
          .replace(old,patch,1)).encode()
    assert before!=after
    import ast
    ast.parse(after.decode())
    print("READBACK_PREFLIGHT",rev,target,hashlib.sha256(before).hexdigest(),
          hashlib.sha256(after).hexdigest(),flush=True)
    if mode=="snapshot":return
    assert mode=="publish" and os.getenv("HF_TOKEN")
    assert os.getenv("SWRLZ_READBACK_FIX_APPROVED")=="1"
    assert api.repo_info(SPACE,repo_type="space").sha==rev,"Live Space changed"
    commit=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
        operations=[CommitOperationAdd(path_in_repo=target,path_or_fileobj=io.BytesIO(after))],
        commit_message="fix(§C): verify GitHub edits against immutable committed blob")
    readback=Path(hf_hub_download(SPACE,target,repo_type="space",revision=commit.oid)).read_bytes()
    assert readback==after,"Published module readback mismatch"
    print("READBACK_FIX_PUBLISHED",commit.oid,flush=True)
if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=("snapshot","publish","verify"))
    main(parser.parse_args().mode)
