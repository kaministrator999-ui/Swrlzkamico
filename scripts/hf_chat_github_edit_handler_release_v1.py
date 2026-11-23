import argparse,ast,hashlib,io,os
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
SPACE="kamiloki/Swyrlz"
TARGET="github_conversation_actions_v264.py"
MARK="# swrlz-github-conversation-edit-v1"
EDIT=r'''
# swrlz-github-conversation-edit-v1
_EDIT_FILE = re.compile(r"(?is)^\s*@github\s+(?:edit|update|modify)\s+(?:the\s+)?(?:existing\s+)?file\s+([^\s]+)")
_EDIT_CONTENT = re.compile(r"(?is)(?:^|\n)\s*content\s*:\s*(.*)")
def _edit_parts(prompt):
    match=_EDIT_FILE.match(prompt or "")
    if not match:return "",None
    path=match.group(1).strip(chr(96))
    field=_EDIT_CONTENT.search(prompt)
    return path,(field.group(1) if field else None)

def _prepare_edit(user_id,thread_id,prompt):
    path,content=_edit_parts(prompt)
    if not path:return _out("Which existing file should I edit? Nothing changed.")
    if content is None:return _out("Provide Content: followed by the replacement text. Nothing changed.")
    try:
        from github_review_update_v1 import prepare
        proposal=prepare(user_id,path,content)
    except CreateFileError as exc:
        return _out(_user_friendly_failure(exc))
    _remember(user_id,thread_id,{"kind":"edit","ticket":proposal["approvalToken"]})
    widget={"contract":"swrlz-widget-v1","kind":"github-change-review",
        "title":"GitHub · review file edit","provider":"GitHub",
        "data":{"operation":"UPDATE_FILE","repo":proposal["repo"],
            "branch":proposal["branch"],"path":proposal["path"],
            "before":proposal["before"],"content":proposal["content"],
            "diff":proposal["diff"],"sha256":proposal["sha256"],
            "bytes":proposal["bytes"],"expiresInSeconds":proposal["expiresInSeconds"]}}
    return _out("Review the proposed edit to "+_clean_label(proposal["path"])+
        ". **Yes** to approve or **no** to reject within five minutes. Nothing changed.",widget)
'''
def transform(src):
    assert MARK not in src,"Already installed"
    anchor='def handle(user_id,thread_id,prompt,context=None,history=None):'
    assert src.count(anchor)==1
    src=src.replace(anchor,EDIT+"\n\n"+anchor,1)
    old='    if _RENAME.search(prompt):\n        return _prepare_rename(user_id,thread_id,prompt,context,history)'
    assert src.count(old)==1
    src=src.replace(old,'    if _EDIT_FILE.match(prompt):\n        return _prepare_edit(user_id,thread_id,prompt)\n'+old,1)
    old='            elif pending["kind"]=="create":\n                create.confirm(user_id,pending["ticket"],False)'
    assert src.count(old)==1
    src=src.replace(old,old+'\n            elif pending["kind"]=="edit":\n                from github_review_update_v1 import confirm\n                confirm(user_id,pending["ticket"],False)',1)
    old='        receipt=create.confirm(user_id,pending["ticket"],True)'
    assert src.count(old)==1
    src=src.replace(old,'''        if pending["kind"]=="edit":
            from github_review_update_v1 import confirm
            receipt=confirm(user_id,pending["ticket"],True)
            return _out("Updated "+_clean_label(receipt["path"])+
                ". Verified exact committed Git blob bytes. "+
                "[View commit](https://github.com/"+receipt["repo"]+
                "/commit/"+receipt["commitSha"]+").",
                {"contract":"swrlz-widget-v1","kind":"github-change-receipt",
                 "title":"GitHub · verified file edit","provider":"GitHub",
                 "data":{"operation":"UPDATE_FILE","repo":receipt["repo"],
                     "branch":receipt["branch"],"path":receipt["path"],
                     "commitSha":receipt["commitSha"],"sha256":receipt["sha256"],
                     "bytesWritten":receipt["bytesWritten"],"verified":True}})
'''+old,1)
    ast.parse(src)
    return src
def main(mode):
    api=HfApi(token=os.getenv("HF_TOKEN"))
    rev=api.repo_info(SPACE,repo_type="space").sha
    files=set(api.list_repo_files(SPACE,repo_type="space",revision=rev))
    assert TARGET in files, "Live conversation handler missing"
    before=Path(hf_hub_download(SPACE,TARGET,repo_type="space",revision=rev)).read_bytes()
    if mode=="verify":
        assert MARK in before.decode()
        print("GITHUB_EDIT_HANDLER_LIVE_VERIFIED",rev,flush=True);return
    after=transform(before.decode()).encode()
    print("GITHUB_EDIT_HANDLER_PREFLIGHT",rev,hashlib.sha256(before).hexdigest(),hashlib.sha256(after).hexdigest(),flush=True)
    if mode=="snapshot":return
    assert mode=="publish" and os.getenv("HF_TOKEN") and os.getenv("SWRLZ_EDIT_HANDLER_APPROVED")=="1"
    assert api.repo_info(SPACE,repo_type="space").sha==rev
    commit=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
        operations=[CommitOperationAdd(path_in_repo=TARGET,path_or_fileobj=io.BytesIO(after))],
        commit_message="fix(§C): connect explicit GitHub edit requests to existing approval flow")
    got=Path(hf_hub_download(SPACE,TARGET,repo_type="space",revision=commit.oid)).read_bytes()
    assert got==after
    print("GITHUB_EDIT_HANDLER_PUBLISHED",commit.oid,flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mode",choices=("snapshot","publish","verify"))
    main(p.parse_args().mode)
