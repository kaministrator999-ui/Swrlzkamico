#!/usr/bin/env python3
"""Repair exact live §C generated HTML review, late approvals and chat scroll.

CAS-scoped to Station + HTML only. Preflight exact source markers; don't touch
§E, model engines, GitHub credentials, unrelated chat features or Space files.
"""
from __future__ import annotations
import argparse, ast, hashlib, io, os, subprocess, tempfile, time, urllib.request
from pathlib import Path

SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
STATION="station.py"
ACTIONS="github_conversation_actions_v264.py"
HTML="chat/§wyrlz/index.html"
HANDOFF="github_html_project_handoff_v1.py"
MODULE=Path("api/github_html_project_handoff_v1.py")
FILES=(STATION,ACTIONS,HTML)
MARK="swrlz-html-review-scroll-repair-v1"
HANDOFF_OLD='''    if _swrlz_html_handoff.has_pending(google_owner,tid) and not github_chat_files.is_reply(prompt):
        _swrlz_html_handoff.expire(google_owner,tid)'''
HANDOFF_NEW='''    if _swrlz_html_handoff.has_approval_record(google_owner,tid) and not _swrlz_html_handoff.is_decision(prompt):
        _swrlz_html_handoff.expire(google_owner,tid)'''
ROUTE_OLD='''    elif (_swrlz_html_handoff.has_pending(google_owner,tid)
          and github_chat_files.is_reply(prompt)):
        payload["githubChatFileAction"]={"userId":google_owner,
                                         "threadId":tid,"prompt":prompt,
                                         "githubContext":active_github,"history":history[-10:]}'''
ROUTE_NEW='''    elif (_swrlz_html_handoff.has_approval_record(google_owner,tid)
          and _swrlz_html_handoff.is_decision(prompt)):
        # Late approvals still reach an authoritative expiry rejection.
        payload["githubChatFileAction"]={"userId":google_owner,
                                         "threadId":tid,"prompt":prompt,
                                         "githubContext":active_github,"history":history[-10:]}
    elif (_swrlz_html_handoff.is_decision(prompt)
          and not github_chat_files.has_pending(google_owner,tid)
          and any(isinstance((m.get("meta") or {}).get("htmlProjectHandoff"),dict)
                  for m in reversed((t.get("messages") or [])[-6:])
                  if m.get("role")=="assistant")):
        # Process-restart fallback: the saved review remains the source of
        # evidence, never a stale deployment grant or model-generated success.
        payload["verifiedPrivateAnswer"]=(
            "That HTML project creation approval is no longer active. "
            "No GitHub write or deployment was authorized by this reply. "
            "Request a fresh review of the saved code artifact.")'''
WIDGET_OLD='''                        g.setdefault("widgets",[]).append(copy.deepcopy(review))
                        g["status"].append({"phase":"HTML_GITHUB_CREATE_REVIEW_READY",'''
WIDGET_NEW='''                        g.setdefault("widgets",[]).append(copy.deepcopy(review))
                        # The UI renders committed assistant messages from meta.widgets.
                        # Persist exact proposal on the canonical assistant message,
                        # not only in the temporary generation object.
                        message.setdefault("meta",{})["widgets"]=[copy.deepcopy(review)]
                        g["status"].append({"phase":"HTML_GITHUB_CREATE_REVIEW_READY",'''
ACTION_OLD='''    if _swrlz_html_handoff.has_pending(user_id,thread_id):
        if _YES.fullmatch(prompt or "") or _NO.fullmatch(prompt or ""):
            approved=bool(_YES.fullmatch(prompt or ""))'''
ACTION_NEW='''    if _swrlz_html_handoff.has_approval_record(user_id,thread_id):
        if _swrlz_html_handoff.is_decision(prompt):
            approved=_swrlz_html_handoff.decision_approved(prompt)'''
SCROLL_OLD='''      const syncLatestAffordance=()=>{
        const nearLatest=distanceFromLatest()<72;
        if(responseStartAnchorActive()){followLatest=false;jumpLatest.hidden=nearLatest;return;}
        followLatest=nearLatest;jumpLatest.hidden=followLatest;
      };'''
SCROLL_NEW='''      // swrlz-html-review-scroll-repair-v1: layout growth must never
      // re-enable following after the reader has scrolled away.
      const syncLatestAffordance=()=>{
        const nearLatest=distanceFromLatest()<72;
        if(responseStartAnchorActive()){followLatest=false;jumpLatest.hidden=nearLatest;return;}
        jumpLatest.hidden=followLatest&&nearLatest;
      };'''
SCROLL_LISTENER_OLD='''      let scrollAffordanceFrame=0;
      let trustedScrollPending=false;
      chatViewport.addEventListener("scroll",event=>{
        trustedScrollPending=trustedScrollPending||event.isTrusted;
        if(scrollAffordanceFrame)return;
        scrollAffordanceFrame=requestAnimationFrame(()=>{
          scrollAffordanceFrame=0;
          const wasTrusted=trustedScrollPending;trustedScrollPending=false;
          if(wasTrusted&&responseStartAnchorActive()&&distanceFromLatest()<72)responseStartAnchorRequestId="";
          syncLatestAffordance();
        });
      },{passive:true});'''
SCROLL_LISTENER_NEW='''      let scrollAffordanceFrame=0;
      let trustedScrollPending=false;
      let lastReaderScrollIntent=0;
      const readerScrollIntent=()=>{lastReaderScrollIntent=Date.now();};
      ["touchstart","wheel","pointerdown"].forEach(type=>
        chatViewport.addEventListener(type,readerScrollIntent,{passive:true}));
      chatViewport.addEventListener("keydown",event=>{
        if(["ArrowUp","ArrowDown","PageUp","PageDown","Home","End"," "].includes(event.key))
          readerScrollIntent();
      });
      chatViewport.addEventListener("scroll",event=>{
        trustedScrollPending=trustedScrollPending||event.isTrusted;
        if(scrollAffordanceFrame)return;
        scrollAffordanceFrame=requestAnimationFrame(()=>{
          scrollAffordanceFrame=0;
          const wasTrusted=trustedScrollPending;trustedScrollPending=false;
          // Scripted scroll events may also be trusted. Only genuine recent
          // touch, wheel, pointer, or keyboard input controls auto-follow.
          if(wasTrusted&&Date.now()-lastReaderScrollIntent<1600){
            const nearLatest=distanceFromLatest()<72;
            followLatest=nearLatest;
            if(responseStartAnchorActive()&&nearLatest)responseStartAnchorRequestId="";
          }
          syncLatestAffordance();
        });
      },{passive:true});'''
FOLLOW_OLD='''      const followLatestIfNeeded=()=>{if(responseStartAnchorActive()){syncLatestAffordance();return;}if(followLatest)requestAnimationFrame(()=>scrollToLatest("auto"));else syncLatestAffordance();};'''
FOLLOW_NEW='''      const followLatestIfNeeded=()=>{
        if(responseStartAnchorActive()){syncLatestAffordance();return;}
        if(followLatest)requestAnimationFrame(()=>{
          if(followLatest&&!responseStartAnchorActive())scrollToLatest("auto");
        });
        else syncLatestAffordance();
      };'''
RESPONSE_START_OLD='''        if(!node||!rid||responseStartAnchorRequestId===rid)return;
        responseStartAnchorRequestId=rid;followLatest=false;'''
RESPONSE_START_NEW='''        if(!node||!rid||responseStartAnchorRequestId===rid||!followLatest)return;
        responseStartAnchorRequestId=rid;followLatest=false;'''


def one(src,old,new,label):
    hits=src.count(old)
    if hits!=1:raise RuntimeError("SOURCE_DRIFT_"+label+" hits="+str(hits))
    return src.replace(old,new,1)


def patch(old):
    s=old[STATION].decode("utf-8")
    a=old[ACTIONS].decode("utf-8")
    h=old[HTML].decode("utf-8")
    if MARK in h or "has_approval_record(google_owner,tid)" in s:
        raise RuntimeError("REPAIR_ALREADY_PRESENT_OR_SOURCE_CHANGED")
    if "# swrlz-generated-html-github-handoff-v1" not in s:
        raise RuntimeError("PREVIOUS_HTML_HANDOFF_MISSING")
    s=one(s,HANDOFF_OLD,HANDOFF_NEW,"INTERRUPTED_APPROVAL")
    s=one(s,ROUTE_OLD,ROUTE_NEW,"APPROVAL_ROUTE")
    s=one(s,WIDGET_OLD,WIDGET_NEW,"SAVED_WIDGET")
    a=one(a,ACTION_OLD,ACTION_NEW,"APPROVAL_HANDLER")
    h=one(h,SCROLL_OLD,SCROLL_NEW,"SCROLL_STATE")
    h=one(h,SCROLL_LISTENER_OLD,SCROLL_LISTENER_NEW,"READER_SCROLL_GESTURE")
    h=one(h,FOLLOW_OLD,FOLLOW_NEW,"FOLLOW_LATEST")
    h=one(h,RESPONSE_START_OLD,RESPONSE_START_NEW,"RESPONSE_START")
    ast.parse(s,filename=STATION);ast.parse(a,filename=ACTIONS)
    return {STATION:s.encode(),ACTIONS:a.encode(),HTML:h.encode(),HANDOFF:MODULE.read_bytes()}


def check_local():
    ast.parse(MODULE.read_text(),filename=HANDOFF)
    if "has_approval_record" not in MODULE.read_text() or "GITHUB_CREATE_APPROVAL_EXPIRED" not in MODULE.read_text():
        raise RuntimeError("EXPIRY_GUARD_MISSING")
    print("HTML_REVIEW_SCROLL_REPAIR_SOURCE_VALIDATED",flush=True)


def probe():
    with urllib.request.urlopen(BASE+"/chat/%C2%A7wyrlz?__review_scroll_fix=1",timeout=20) as res:
        if res.status!=200 or MARK not in res.read(3_000_000).decode("utf-8",errors="replace"):
            raise RuntimeError("§C chat corrected scroll code not live")
    print("HTML_REVIEW_SCROLL_REPAIR_LIVE_CHAT_VERIFIED",flush=True)


def main(mode):
    check_local()
    if mode=="selftest":return
    from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd,CommitOperationDelete
    token=os.getenv("HF_TOKEN") or None
    api=HfApi(token=token)
    rev=str(api.repo_info(SPACE,repo_type="space").sha)
    old={p:Path(hf_hub_download(SPACE,p,repo_type="space",revision=rev,token=token)).read_bytes()
         for p in FILES}
    listed=set(api.list_repo_files(SPACE,repo_type="space",revision=rev))
    if HANDOFF not in listed:raise RuntimeError("LIVE_HANDOFF_MODULE_MISSING")
    old[HANDOFF]=Path(hf_hub_download(SPACE,HANDOFF,repo_type="space",revision=rev,token=token)).read_bytes()
    new=patch(old)
    print("HTML_REVIEW_SCROLL_REPAIR_PREFLIGHT",rev,{p:hashlib.sha256(v).hexdigest() for p,v in new.items()},flush=True)
    if mode=="preflight":return
    if mode!="publish" or not token or os.getenv("SWRLZ_HTML_REVIEW_SCROLL_APPROVED")!="1":
        raise PermissionError("GUARDED_RELEASE_NOT_AUTHORIZED")
    if str(api.repo_info(SPACE,repo_type="space").sha)!=rev:
        raise RuntimeError("CONCURRENT_HF_REVISION")
    newrev=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
        operations=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=io.BytesIO(v)) for p,v in new.items()],
        commit_message="fix(§C): persist GitHub review, reject stale approvals, preserve reader scroll").oid
    print("HTML_REVIEW_SCROLL_REPAIR_COMMITTED",newrev,flush=True)
    try:
        for p,v in new.items():
            actual=Path(hf_hub_download(SPACE,p,repo_type="space",revision=newrev,token=token)).read_bytes()
            if actual!=v:raise RuntimeError("HF_SOURCE_BYTES_MISMATCH_"+p)
        for i in range(36):
            try:
                probe()
                print("HTML_REVIEW_SCROLL_REPAIR_DEPLOYED",newrev,flush=True)
                return
            except (OSError,RuntimeError,TimeoutError) as exc:
                if i==35:raise RuntimeError("LIVE_PROBE_FAILED") from exc
                time.sleep(10)
    except Exception:
        if str(api.repo_info(SPACE,repo_type="space").sha)==newrev:
            rollback=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=newrev,
                operations=[CommitOperationAdd(path_in_repo=p,path_or_fileobj=io.BytesIO(v)) for p,v in old.items()],
                commit_message="rollback(§C): failed HTML review/scroll verification")
            print("HTML_REVIEW_SCROLL_REPAIR_ROLLED_BACK",rollback.oid,flush=True)
        else:
            print("HTML_REVIEW_SCROLL_REPAIR_CANNOT_ROLL_BACK_CONCURRENT_UPDATE",flush=True)
        raise


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("mode",choices=("selftest","preflight","publish"))
    main(parser.parse_args().mode)
