#!/usr/bin/env python3
"""Pin explicit GitHub file mutations ahead of read-only source intelligence."""
import argparse,ast,hashlib,io,os,re
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
SPACE="kamiloki/Swyrlz"; PATH="station.py"
MARK="# swrlz-explicit-github-write-routing-v1"
HELPER=r'''
# swrlz-explicit-github-write-routing-v1
def _explicit_github_file_mutation(prompt):
    """Only explicit @GitHub file edit/create requests; never authorize a write."""
    import re
    text=str(prompt or "").strip()
    return bool(re.match(
        r"(?is)^@github\s+(?:edit|update|modify|create|add)\s+(?:the\s+)?"
        r"(?:existing\s+)?file\s+[^\s]+\s*(?:\n|$)",
        text))
'''
def transform(source):
    assert MARK not in source,"Already patched"
    anchor='    elif github_report_explain_v236.is_report_request(prompt):'
    assert source.count(anchor)==1,"Owner routing changed; inspect live source"
    assert 'payload["githubChatFileAction"]' in source,"Owner file action missing"
    # An explicit file mutation is a proposal, never direct execution. The
    # existing owner-scoped handler still enforces OAuth and human confirmation.
    route='''    elif _explicit_github_file_mutation(prompt):
        payload["githubChatFileAction"]={"userId":google_owner,
                                         "threadId":tid,"prompt":prompt,
                                         "githubContext":active_github,"history":history[-10:]}
'''
    source=source.replace(anchor,route+anchor,1)
    # Put helper before Station's first module-level route decorator/function.
    location='ROOT=Path(__file__).resolve().parent'
    assert source.count(location)==1
    source=source.replace(location,HELPER+"\n"+location,1)
    ast.parse(source)
    return source
def main(mode):
    api=HfApi(token=os.getenv("HF_TOKEN"))
    rev=api.repo_info(SPACE,repo_type="space").sha
    files=set(api.list_repo_files(SPACE,repo_type="space",revision=rev))
    assert PATH in files
    before=Path(hf_hub_download(SPACE,PATH,repo_type="space",revision=rev)).read_bytes()
    source=before.decode()
    if mode=="verify":
        assert MARK in source
        assert '_explicit_github_file_mutation(prompt):' in source
        print("GITHUB_WRITE_ROUTING_LIVE_VERIFIED",rev,flush=True)
        return
    after=transform(source).encode()
    print("GITHUB_WRITE_ROUTING_PREFLIGHT",rev,hashlib.sha256(before).hexdigest(),hashlib.sha256(after).hexdigest(),flush=True)
    if mode=="snapshot":return
    assert mode=="publish" and os.getenv("HF_TOKEN") and os.getenv("SWRLZ_WRITE_ROUTING_APPROVED")=="1"
    assert api.repo_info(SPACE,repo_type="space").sha==rev
    commit=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
      operations=[CommitOperationAdd(path_in_repo=PATH,path_or_fileobj=io.BytesIO(after))],
      commit_message="fix(§C): route explicit GitHub file edits to owner approval handler")
    got=Path(hf_hub_download(SPACE,PATH,repo_type="space",revision=commit.oid)).read_bytes()
    assert got==after
    print("GITHUB_WRITE_ROUTING_PUBLISHED",commit.oid,flush=True)
if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("mode",choices=("snapshot","publish","verify"))
    main(parser.parse_args().mode)
