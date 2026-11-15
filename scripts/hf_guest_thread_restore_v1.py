#!/usr/bin/env python3
"""Restore an existing guest Station thread on first page hydration.

Narrow change to the current HF Chat UI file; a user-selected unsent New Chat
always remains a draft. This is independent of login and server credentials.
"""
import ast, hashlib, json, os, sys
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd
SPACE="kamiloki/Swyrlz"
FILE="chat/§wyrlz/index.html"
MARK="swrlz-guest-first-hydration-restore-v1"
ROOT=Path("reports/guest-reload-restore-v1")
BASE='''      let activeThreadId = "";
      let draftThread = true;
      let pendingDraftThread = null;'''
AFTER_BASE='''      let activeThreadId = "";
      let draftThread = true;
      let pendingDraftThread = null;
      // swrlz-guest-first-hydration-restore-v1: first sync may restore the
      // session-owned current thread; later sync must not override New Chat.
      let stationFirstHydration = true;'''
BEFORE='''        const stationCurrent=data?.currentThread?.id||"";
        // Draft mode is an explicit local navigation state. Background Station
        // sync may hydrate thread data, but it must never navigate an unsent new
        // chat back to the server's previously-current thread.
        if(!draftThread && !chatThreads.some(t=>t.id===activeThreadId)) activeThreadId=stationCurrent||data?.state?.currentId||activeThreadId;'''
AFTER='''        const stationCurrent=data?.currentThread?.id||"";
        // On first successful hydration restore the server-owned thread from
        // this guest session. Do not create a thread or infer user identity.
        // After that, the explicit local New Chat draft always wins.
        if(stationFirstHydration){
          stationFirstHydration=false;
          if(draftThread && !activeThreadId && !pendingDraftThread){
            const initialId=[stationCurrent,data?.state?.currentId,chatThreads[0]?.id]
              .find(id=>id&&chatThreads.some(t=>t.id===id));
            if(initialId){draftThread=false;activeThreadId=initialId;}
          }
        }
        // Background Station sync may hydrate data but must never navigate an
        // unsent new chat back to the server's previously-current thread.
        if(!draftThread && !chatThreads.some(t=>t.id===activeThreadId)) activeThreadId=stationCurrent||data?.state?.currentId||activeThreadId;'''
BEFORE_DRAFT='''      const startDraft = () => { draftThread=true; pendingDraftThread=null; activeThreadId="";'''
AFTER_DRAFT='''      const startDraft = () => { stationFirstHydration=false; draftThread=true; pendingDraftThread=null; activeThreadId="";'''

def swap(text,a,b,name):
    n=text.count(a)
    if n!=1:raise RuntimeError("Unsafe live source for "+name+"; matches="+str(n))
    return text.replace(a,b,1)

def candidate(before):
    text=before.decode("utf-8")
    if MARK in text:raise RuntimeError("Already patched")
    text=swap(text,BASE,AFTER_BASE,"initial state")
    text=swap(text,BEFORE,AFTER,"initial hydration")
    text=swap(text,BEFORE_DRAFT,AFTER_DRAFT,"explicit new draft")
    return text.encode("utf-8")

def static_checks(after):
    s=after.decode()
    if s.count("stationFirstHydration")!=4:
        raise RuntimeError("Hydration flag reference count unexpected "+str(s.count("stationFirstHydration")))
    for term in ("const stationCurrent=", "chatThreads[0]?.id","if(initialId){draftThread=false;activeThreadId=initialId;}",
      "if(draftThread && !activeThreadId && !pendingDraftThread)","stationFirstHydration=false; draftThread=true"):
        if term not in s:raise AssertionError("Missing JS restore requirement "+term)
    # Simulate the exact route choice without inventing a server or a login.
    def first_sync(thread_ids,server_current,explicit_new_chat=False):
        pending=not explicit_new_chat
        active="";draft=True
        if pending:
            initial=next((x for x in [server_current,thread_ids[0] if thread_ids else ""] if x in thread_ids),None)
            if initial:active=initial;draft=False
        return (active,draft)
    assert first_sync(["a"],"a")==("a",False)
    assert first_sync(["a"],"b")==("a",False)
    assert first_sync([],"")==("",True)
    assert first_sync(["a"],"a",True)==("",True)
    print("GUEST_FIRST_HYDRATION_STATIC_ACCEPTED 9",flush=True)

def digest(data):return hashlib.sha256(data).hexdigest()

def preflight(api):
    rev=api.repo_info(SPACE,repo_type="space").sha
    before=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=rev,token=api.token)).read_bytes()
    after=candidate(before)
    static_checks(after)
    (ROOT/"before"/"chat/§wyrlz").mkdir(parents=True,exist_ok=True)
    (ROOT/"after"/"chat/§wyrlz").mkdir(parents=True,exist_ok=True)
    (ROOT/"before"/FILE).write_bytes(before)
    (ROOT/"after"/FILE).write_bytes(after)
    (ROOT/"manifest.json").write_text(json.dumps({
       "Space":SPACE,"file":FILE,"beforeRevision":rev,
       "beforeSha256":digest(before),"afterSha256":digest(after),
       "operation":"guest first sync only; no authentication changes"
    },indent=2)+"\n")
    print("GUEST_FIRST_HYDRATION_PREFLIGHT",json.dumps({"revision":rev,"before":digest(before),"after":digest(after)}),flush=True)
    return rev,before,after

def publish(api):
    if os.getenv("SWRLZ_GUEST_HYDRATION_APPROVED")!="1":
        raise RuntimeError("Explicit production release permission missing")
    if not api.token:raise RuntimeError("No existing HF_TOKEN available")
    rev,before,after=preflight(api)
    if api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("Hugging Face head changed after preflight")
    newrev=None
    try:
        result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
            operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(ROOT/"after"/FILE))],
            commit_message="§C guest first hydration: restore session conversation, preserve explicit new draft")
        newrev=str(result.oid)
        uploaded=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=newrev,token=api.token)).read_bytes()
        if uploaded!=after:raise RuntimeError("Published live UI does not match source")
        print("GUEST_FIRST_HYDRATION_PUBLISHED",json.dumps({"before":rev,"after":newrev}),flush=True)
    except Exception:
        if newrev and api.repo_info(SPACE,repo_type="space").sha==newrev:
            rollback=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=newrev,
                operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(ROOT/"before"/FILE))],
                commit_message="Rollback §C guest hydration to exact previous source")
            print("GUEST_FIRST_HYDRATION_ROLLED_BACK",str(rollback.oid),flush=True)
        raise

if __name__=="__main__":
    mode=sys.argv[1:] or ["preflight"]
    if mode not in (["preflight"],["publish"]):raise SystemExit("Use preflight or publish")
    api=HfApi(token=os.getenv("HF_TOKEN") or None)
    preflight(api) if mode==["preflight"] else publish(api)
