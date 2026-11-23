#!/usr/bin/env python3
"""CAS-scoped live §C HTML publishing command and approval UI release."""
from __future__ import annotations
import argparse, ast, hashlib, io, json, os, subprocess, tempfile, time
import urllib.error, urllib.request
from pathlib import Path

SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
STATION="station.py"
ACTIONS="github_conversation_actions_v264.py"
HTML="chat/§wyrlz/index.html"
MODULE="github_html_publish_action_v1.py"
ASSET="chat/§wyrlz/assets/html-project-publish-review-v1.js"
SOURCES={MODULE:Path("api/github_html_publish_action_v1.py"),
         ASSET:Path("chat/html-project-publish-review-v1.js")}
FILES=(STATION,ACTIONS,HTML)
MARK="swrlz-owner-html-publish-v1"
SMARK="# swrlz-owner-html-command-route-v1"
UMARK='id="swrlz-html-publish-review-v1"'
SANCHOR='    elif _explicit_github_file_mutation(prompt):'
RANCHOR='ROOT=Path(__file__).resolve().parent'
UANCHOR='}else if(widget.kind==="github-change-review"){'

HANDLER=r"""

# swrlz-owner-html-publish-v1
# Only an authenticated owner, within the same thread, can approve dispatch.
import github_html_publish_action_v1 as _swrlz_html_publish
_html_old_is_action=is_file_action
_html_old_has_pending=has_pending
_html_old_pending_kind=pending_kind
_html_old_expire=expire_interrupted
_html_old_handle=handle

def is_file_action(prompt,context=None,history=None):
    return (_swrlz_html_publish.is_request(prompt)
            or _html_old_is_action(prompt,context,history))

def has_pending(user_id,thread_id):
    return (_swrlz_html_publish.has_pending(user_id,thread_id)
            or _html_old_has_pending(user_id,thread_id))

def pending_kind(user_id,thread_id):
    if _swrlz_html_publish.has_pending(user_id,thread_id):
        return "publish-html"
    return _html_old_pending_kind(user_id,thread_id)

def expire_interrupted(user_id,thread_id):
    _swrlz_html_publish.expire(user_id,thread_id)
    return _html_old_expire(user_id,thread_id)

def handle(user_id,thread_id,prompt,context=None,history=None):
    if _swrlz_html_publish.has_pending(user_id,thread_id):
        if _YES.fullmatch(prompt or "") or _NO.fullmatch(prompt or ""):
            accepted=bool(_YES.fullmatch(prompt or ""))
            try:
                receipt=_swrlz_html_publish.confirm(user_id,thread_id,accepted)
            except _swrlz_html_publish.PublishActionError as exc:
                return _out("HTML deployment NOT dispatched ("+exc.code+
                    "). Check connected GitHub Actions access. No live success assumed.")
            if not accepted:
                return _out("HTML deployment rejected; nothing dispatched.")
            return _out("Owner approval accepted for HTML project "+
                _clean_label(receipt["project"])+" at commit "+
                _clean_label(receipt["sourceSha"])+
                ". GitHub accepted the deployment workflow dispatch, "+
                "but publishing is NOT verified yet. "+
                "[View Actions]("+receipt["workflowUrl"]+"). "+
                "Use @GitHub status HTML project "+receipt["project"]+
                " to inspect the run and its public URL.")
        _swrlz_html_publish.expire(user_id,thread_id)
    request=_swrlz_html_publish.command(prompt)
    if request is not None:
        action,slug=request
        if action=="status":
            try:
                status=_swrlz_html_publish.status(user_id,slug)
            except _swrlz_html_publish.PublishActionError as exc:
                return _out("HTML deployment status unavailable ("+exc.code+
                            "). No deployment success assumed.")
            link=status.get("runUrl") or status.get("workflowUrl")
            if status.get("verified"):
                return _out("HTML project "+_clean_label(slug)+
                    " is LIVE: exact source bytes and the opaque-origin CSP sandbox verified. "+
                    "Commit "+_clean_label(status["sourceSha"])+
                    ". [Open website]("+status["url"]+"). [View Actions]("+link+").")
            return _out("HTML project "+_clean_label(slug)+
                ": workflow status "+_clean_label(status.get("status") or "unknown")+
                ", conclusion "+_clean_label(status.get("conclusion") or "not confirmed")+
                ". Live page not verified. [View Actions]("+link+").")
        expire_interrupted(user_id,thread_id)
        try:
            preview=_swrlz_html_publish.prepare(user_id,thread_id,slug)
        except _swrlz_html_publish.PublishActionError as exc:
            return _out("HTML publish preparation failed ("+exc.code+
                        "). Check selected GitHub repository and committed project files. Nothing dispatched.")
        widget={"contract":"swrlz-widget-v1","kind":"github-html-publish-review",
                "title":"Review HTML project publication","provider":"GitHub",
                "data":preview}
        return _out("Review HTML project "+_clean_label(slug)+
            " from immutable GitHub commit "+_clean_label(preview["sourceSha"])+
            ". Destination: existing §C Hugging Face Space. "+
            "Yes to dispatch, no to reject within five minutes. Nothing deployed.",widget)
    return _html_old_handle(user_id,thread_id,prompt,context,history)
"""

SHELP=r"""
# swrlz-owner-html-command-route-v1
def _swrlz_explicit_html_publish_command(prompt):
    return bool(re.fullmatch(
        r"\s*@github\s+(?:publish|deploy|status)\s+(?:html\s+)?project\s+"
        r"[a-z0-9](?:[a-z0-9-]{0,46}[a-z0-9])?\s*[.!]?\s*",
        str(prompt or ""),re.I))
"""
SBRANCH='''    elif _swrlz_explicit_html_publish_command(prompt):
        payload["githubChatFileAction"]={"userId":google_owner,
                                         "threadId":tid,"prompt":prompt,
                                         "githubContext":active_github,"history":history[-10:]}
'''
UIHEAD='''
<style id="swrlz-html-publish-review-v1">
.swrlz-html-publish-review{margin:12px 0;min-width:0;overflow-wrap:anywhere}
.swrlz-html-publish-review>a{color:#94e9ff;text-decoration:underline;font-size:12px}
.swrlz-html-publish-review .swrlz-github-change-actions{display:flex;gap:10px;position:sticky;top:58px;background:#081e30;padding:9px 0;z-index:4}
.swrlz-html-publish-review .swrlz-github-change-actions button{flex:1;min-height:46px}
.swrlz-html-publish-review details{max-height:45vh;overflow:auto}
</style>
<script src="/chat/§wyrlz/assets/html-project-publish-review-v1.js?v=1" defer></script>
'''
UIBRANCH='''}else if(widget.kind==="github-html-publish-review"){
            const reviewThread=String(activeThreadId||"");
            if(!window.SwrlzHtmlPublishReviewV1?.render(card,data,{
              threadId:reviewThread,
              currentThread:()=>String(activeThreadId||""),
              isLatest:wrapper=>Array.from(messageList.querySelectorAll(".swrlz-html-publish-review"))
                .filter(item=>item.isConnected).at(-1)===wrapper,
              confirm:async accepted=>{
                if(sending)return false;
                const decision=accepted?"yes":"no",priorDraft=prompt.value;
                prompt.value=decision;
                const sent=await commitDraftFromPrompt();
                if(sent){
                  if(!prompt.value)prompt.value=priorDraft;
                  resizeComposer();
                  return true;
                }
                if(prompt.value===decision||!prompt.value)prompt.value=priorDraft;
                resizeComposer();
                return false;
              }
            })){
              card.appendChild(Object.assign(document.createElement("p"),{
                textContent:"Approval UI unavailable. Reply yes or no in this thread."
              }));
            }
          }else if(widget.kind==="github-change-review"){'''

def patch(before):
    s=before[STATION].decode()
    if SMARK in s or s.count(SANCHOR)!=1 or s.count(RANCHOR)!=1:
        raise RuntimeError("Live Station routing changed or already patched")
    s=s.replace(RANCHOR,SHELP+"\n"+RANCHOR,1).replace(SANCHOR,SBRANCH+SANCHOR,1)
    ast.parse(s,filename=STATION)
    a=before[ACTIONS].decode()
    if MARK in a or not all(key in a for key in (
            "def handle(","def is_file_action(","def has_pending(",
            "def pending_kind(","def expire_interrupted(","def _out(")):
        raise RuntimeError("Live action handler changed or already patched")
    a=a.rstrip()+HANDLER+"\n"
    ast.parse(a,filename=ACTIONS)
    h=before[HTML].decode()
    if UMARK in h or h.count("</head>")!=1 or h.count(UANCHOR)!=1:
        raise RuntimeError("Chat widget seam changed or already patched")
    h=h.replace("</head>",UIHEAD+"</head>",1).replace(UANCHOR,UIBRANCH,1)
    return {STATION:s.encode(),ACTIONS:a.encode(),HTML:h.encode()}

def h(data):
    return hashlib.sha256(data).hexdigest()

def extras():
    raw={name:path.read_bytes() for name,path in SOURCES.items()}
    ast.parse(raw[MODULE].decode(),filename=MODULE)
    with tempfile.TemporaryDirectory() as directory:
        script=Path(directory)/"widget.js"
        script.write_bytes(raw[ASSET])
        check=subprocess.run(["node","--check",str(script)],
                             capture_output=True,text=True,timeout=25)
        if check.returncode:raise RuntimeError("UI JS syntax: "+check.stderr[-450:])
    return raw

def selftest():
    extras()
    station=("import re\n"+RANCHOR+"\nif True:\n"+SANCHOR+"        pass\n").encode()
    actions=("def is_file_action(*a,**k):pass\n"
             "def has_pending(*a):return False\n"
             "def pending_kind(*a):return None\n"
             "def expire_interrupted(*a):pass\n"
             "def _out(*a,**k):return {}\n"
             "def handle(*a,**k):pass\n").encode()
    html=("<head></head><body>"+UANCHOR+"</body>").encode()
    out=patch({STATION:station,ACTIONS:actions,HTML:html})
    assert SMARK in out[STATION].decode()
    assert MARK in out[ACTIONS].decode()
    assert UMARK in out[HTML].decode()
    print("HTML_DEPLOY_OWNER_UI_PATCH_SELFTEST_PASS",flush=True)

def live_verify():
    with urllib.request.urlopen(BASE+"/chat/%C2%A7wyrlz?__html_publish_probe=1",timeout=20) as response:
        page=response.read(1_000_000).decode("utf-8",errors="replace")
        if response.status!=200 or "html-project-publish-review-v1.js?v=1" not in page:
            raise RuntimeError("Updated HTML deployment UI not served")
    with urllib.request.urlopen(BASE+"/chat/%C2%A7wyrlz/assets/html-project-publish-review-v1.js?v=1",timeout=20) as response:
        text=response.read(150_000).decode("utf-8",errors="replace")
        if response.status!=200 or "SwrlzHtmlPublishReviewV1" not in text:
            raise RuntimeError("HTML deployment widget JS not served")
    print("HTML_DEPLOY_OWNER_UI_LIVE_VERIFIED",flush=True)

def main(mode):
    if mode=="selftest":selftest();return
    addon=extras()
    from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd,CommitOperationDelete
    api=HfApi(token=os.getenv("HF_TOKEN") or None)
    rev=str(api.repo_info(SPACE,repo_type="space").sha)
    files=set(api.list_repo_files(SPACE,repo_type="space",revision=rev))
    if MODULE in files or ASSET in files:
        raise RuntimeError("HTML publication extension already exists; manual drift inspection required")
    original={p:Path(hf_hub_download(SPACE,p,repo_type="space",
                 revision=rev,token=api.token)).read_bytes() for p in FILES}
    after=patch(original)
    after.update(addon)
    print("HTML_DEPLOY_OWNER_PREFLIGHT",json.dumps(
        {"revision":rev,"paths":{p:h(raw) for p,raw in after.items()}},sort_keys=True),flush=True)
    if mode=="preflight":return
    if mode!="publish" or os.getenv("SWRLZ_HTML_CHAT_APPROVED")!="1" or not os.getenv("HF_TOKEN"):
        raise PermissionError("Owner and HF authorization required")
    if str(api.repo_info(SPACE,repo_type="space").sha)!=rev:
        raise RuntimeError("Concurrent Space write; no publish")
    changed=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
        operations=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=io.BytesIO(raw))
                    for p,raw in after.items()],
        commit_message="feat(§C): owner-reviewed GitHub HTML project publish flow")
    published=changed.oid
    print("HTML_DEPLOY_OWNER_SOURCE_COMMITTED",published,flush=True)
    try:
        for path,raw in after.items():
            got=Path(hf_hub_download(SPACE,path,repo_type="space",
                 revision=published,token=api.token)).read_bytes()
            if got!=raw:raise RuntimeError("Published bytes mismatch: "+path)
        for n in range(36):
            try:
                live_verify()
                print("HTML_DEPLOY_OWNER_RELEASE_ACCEPTED",published,flush=True)
                break
            except (RuntimeError,urllib.error.URLError,TimeoutError) as exc:
                if n==35:raise RuntimeError("HTML publish UI never became live") from exc
                time.sleep(10)
    except Exception:
        if str(api.repo_info(SPACE,repo_type="space").sha)==published:
            ops=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=io.BytesIO(raw))
                 for p,raw in original.items()]
            ops.extend(CommitOperationDelete(path_in_repo=p) for p in addon)
            restored=api.create_commit(repo_id=SPACE,repo_type="space",
                parent_commit=published,operations=ops,
                commit_message="rollback(§C): unverified owner HTML publish flow")
            print("HTML_DEPLOY_OWNER_ROLLBACK",restored.oid,flush=True)
        else:
            print("HTML_DEPLOY_OWNER_ROLLBACK_BLOCKED_CONCURRENT_REVISION",flush=True)
        raise

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=("selftest","preflight","publish"))
    main(parser.parse_args().mode)
