#!/usr/bin/env python3
"""§C mobile code-preview auto-follow: exact Hugging Face Chat UI patch.

Follows new lines inside provisional and final code boxes only when the reader
is already near the bottom. User scrolling upward pauses follow; returning
to the bottom automatically resumes it. No model/server/project changes.
"""
from __future__ import annotations
import ast,hashlib,json,os,re,subprocess,sys,tempfile,time,urllib.request
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd

SPACE="kamiloki/Swyrlz"
UI="chat/§wyrlz/index.html"
BACKUP=Path("swrlz-code-scroll-follow-backup")
BASE="https://kamiloki-swyrlz.hf.space"
MARK="swrlz-code-scroll-follow-v1"

def emit(phase,**details):
    print("CODE_SCROLL",json.dumps({"phase":phase,**details},sort_keys=True,ensure_ascii=False),flush=True)
def sha(data):return hashlib.sha256(data).hexdigest()
def once(text,a,b,label):
    if text.count(a)!=1:raise RuntimeError("SOURCE_DRIFT "+label+" count="+str(text.count(a)))
    return text.replace(a,b,1)

OLD_CAPTURE='''      const captureCodeViewState=()=>{
        messageList.querySelectorAll(".code-block pre[data-code-key]").forEach(pre=>codeViewState.set(pre.dataset.codeKey,{top:pre.scrollTop,left:pre.scrollLeft}));
      };
      const restoreCodeViewState=()=>{
        messageList.querySelectorAll(".code-block pre[data-code-key]").forEach(pre=>{const state=codeViewState.get(pre.dataset.codeKey);if(state){requestAnimationFrame(()=>{pre.scrollTop=state.top;pre.scrollLeft=state.left;});}});
      };
      const bindCodeViewState=container=>{
        container.querySelectorAll(".code-block pre[data-code-key]").forEach(pre=>{
          const remember=()=>codeViewState.set(pre.dataset.codeKey,{top:pre.scrollTop,left:pre.scrollLeft});
          pre.addEventListener("scroll",remember,{passive:true});pre.addEventListener("touchmove",remember,{passive:true});
        });
      };'''
NEW_CAPTURE='''      // swrlz-code-scroll-follow-v1: follow only when the reader is
      // already near the end. No forced jump while browsing earlier lines.
      const codeViewNearBottom=pre=>!!pre&&pre.scrollHeight-pre.clientHeight-pre.scrollTop<=48;
      const captureCodeViewState=()=>{
        messageList.querySelectorAll(".code-block pre[data-code-key]").forEach(pre=>codeViewState.set(pre.dataset.codeKey,{
          top:pre.scrollTop,left:pre.scrollLeft,follow:codeViewNearBottom(pre)
        }));
      };
      const restoreCodeViewState=()=>{
        messageList.querySelectorAll(".code-block pre[data-code-key]").forEach(pre=>{const state=codeViewState.get(pre.dataset.codeKey);if(state){requestAnimationFrame(()=>{pre.scrollTop=state.top;pre.scrollLeft=state.left;});}});
      };
      const bindCodeViewState=container=>{
        container.querySelectorAll(".code-block pre[data-code-key]").forEach(pre=>{
          const remember=()=>codeViewState.set(pre.dataset.codeKey,{
            top:pre.scrollTop,left:pre.scrollLeft,follow:codeViewNearBottom(pre)
          });
          pre.addEventListener("scroll",remember,{passive:true});pre.addEventListener("touchmove",remember,{passive:true});
        });
      };'''
OLD_DRAFT='''          const code=draftPanel.querySelector("pre");
          if(code&&code.textContent!==draftText)code.textContent=draftText;'''
NEW_DRAFT='''          const code=draftPanel.querySelector("pre");
          if(code&&code.textContent!==draftText){
            const follow=codeViewNearBottom(code);
            code.textContent=draftText;
            if(follow)code.scrollTop=code.scrollHeight;
          }'''
OLD_INLINE='''            if(code&&firstBreak>=0)code.textContent=nextText.slice(firstBreak+1);'''
NEW_INLINE='''            if(code&&firstBreak>=0){
              const pre=code.closest("pre");
              const follow=codeViewNearBottom(pre);
              code.textContent=nextText.slice(firstBreak+1);
              if(pre&&follow)pre.scrollTop=pre.scrollHeight;
            }'''
OLD_RERENDER='''          }else{
            captureCodeViewState();
            const responseThread=chatThreads.find(t=>t.id===String(g.threadId||""));
            const responsePrompt=[...(responseThread?.messages||[])].reverse().find(m=>m.role==="user")?.text||"";
            renderAssistantContent(body,nextText,renderKey,isOriginalSongwritingPrompt(responsePrompt)?"lyrics":"");
            restoreCodeViewState();
          }
          body.dataset.renderedSource=nextText;'''
NEW_RERENDER='''          }else{
            const oldFollow=new Map([...body.querySelectorAll(".code-block pre[data-code-key]")]
              .map(pre=>[pre.dataset.codeKey,codeViewNearBottom(pre)]));
            captureCodeViewState();
            const responseThread=chatThreads.find(t=>t.id===String(g.threadId||""));
            const responsePrompt=[...(responseThread?.messages||[])].reverse().find(m=>m.role==="user")?.text||"";
            renderAssistantContent(body,nextText,renderKey,isOriginalSongwritingPrompt(responsePrompt)?"lyrics":"");
            restoreCodeViewState();
            requestAnimationFrame(()=>{
              body.querySelectorAll(".code-block pre[data-code-key]").forEach(pre=>{
                const key=pre.dataset.codeKey;
                const saved=codeViewState.get(key);
                const follow=oldFollow.has(key)?oldFollow.get(key):(!saved||saved.follow);
                if(follow)pre.scrollTop=pre.scrollHeight;
              });
            });
          }
          body.dataset.renderedSource=nextText;'''

def patch(before):
    source=before.decode("utf-8")
    if MARK in source:raise RuntimeError("Already patched; refusing duplicate listeners")
    for a,b,name in [
       (OLD_CAPTURE,NEW_CAPTURE,"scroll state binding"),
       (OLD_DRAFT,NEW_DRAFT,"provisional draft auto-follow"),
       (OLD_INLINE,NEW_INLINE,"in-place live-code tail follow"),
       (OLD_RERENDER,NEW_RERENDER,"live code re-render follow"),
    ]:source=once(source,a,b,name)
    return source.encode("utf-8")

def test_ui(old,new):
    source=new.decode("utf-8")
    before=old.decode("utf-8")
    for term in ("id=\\"projectFilePicker\\"","id=\\"imagePicker\\"",
                 "const renderStationGeneration=()=>","const renderAssistantContent=(container",
                 "const captureCodeViewState=()=>","const bindCodeViewState=container=>",
                 "const restoreCodeViewState=()=>","CANDIDATE_PREVIEW_DELTA",
                 "previewText","codeViewState"):
        assert term in source,term
    assert source.count("const codeViewNearBottom=pre=>")==1
    assert source.count("if(follow)code.scrollTop=code.scrollHeight;")==1
    assert source.count("if(pre&&follow)pre.scrollTop=pre.scrollHeight;")==1
    assert 'oldFollow.has(key)?oldFollow.get(key):(!saved||saved.follow)' in source
    assert source.count("const renderStationGeneration=()=>")==before.count("const renderStationGeneration=()=>")
    assert len(new)-len(old)<3500 and len(new)>len(old)
    # Run Node's actual parser on inline executable scripts. Existing
    # analytics JSON and module assets are not parsed as plain scripts.
    snippets=re.findall(r"<script\b([^>]*)>([\s\S]*?)</script\s*>",source,flags=re.I)
    parsed=0
    with tempfile.TemporaryDirectory(prefix="swrlz-code-scroll-js-") as folder:
        for i,(attrs,body) in enumerate(snippets):
            if not body.strip() or re.search(r'type\s*=\s*["\\']application/(?:json|ld\\+json)["\\']',attrs,re.I):continue
            path=Path(folder)/("script-"+str(i)+".js")
            path.write_text(body)
            result=subprocess.run(["node","--check",str(path)],capture_output=True,text=True,timeout=35)
            if result.returncode:raise RuntimeError("Chat JS invalid "+result.stderr[-700:])
            parsed+=1
    # Pure decision testing with near-bottom, user-scroll-away and restore
    # semantics, independent of browser scrolling implementation.
    pure='''const codeViewNearBottom=pre=>!!pre&&pre.scrollHeight-pre.clientHeight-pre.scrollTop<=48;
    const assert=require("assert");
    assert(codeViewNearBottom({scrollHeight:1200,clientHeight:400,scrollTop:790}));
    assert(!codeViewNearBottom({scrollHeight:1200,clientHeight:400,scrollTop:300}));
    assert(codeViewNearBottom({scrollHeight:1200,clientHeight:400,scrollTop:800}));
    assert(codeViewNearBottom({scrollHeight:0,clientHeight:0,scrollTop:0}));
    assert(!codeViewNearBottom(null));
    console.log("CODE_SCROLL_NEAR_BOTTOM_TEST_PASS");'''
    with tempfile.TemporaryDirectory(prefix="swrlz-code-follow-unit-") as folder:
        path=Path(folder)/"test.js";path.write_text(pure)
        run=subprocess.run(["node",str(path)],capture_output=True,text=True,timeout=25)
        if run.returncode or "CODE_SCROLL_NEAR_BOTTOM_TEST_PASS" not in run.stdout:
            raise RuntimeError("Scroll near-bottom unit failed "+run.stderr)
    emit("UI_SOURCE_JS_AND_BEHAVIOR_TESTS_PASS",jsScriptsParsed=parsed,
         previewScroll=True,liveCodeScroll=True,manualPause=True,
         originalControlsPreserved=True)

def snapshot(api):
    rev=api.repo_info(SPACE,repo_type="space").sha
    old=Path(hf_hub_download(SPACE,UI,repo_type="space",revision=rev,token=api.token)).read_bytes()
    new=patch(old)
    test_ui(old,new)
    BACKUP.mkdir(parents=True,exist_ok=True)
    (BACKUP/"index.html").write_bytes(old)
    (BACKUP/"revision.txt").write_text(rev)
    (BACKUP/"hashes.json").write_text(json.dumps({"originalRevision":rev,"before":sha(old),
        "after":sha(new),"changedFiles":[UI],"modelChanged":False,
        "stationChanged":False,"repositoryWriteAuthorityChanged":False},indent=2))
    emit("READ_ONLY_PREFLIGHT_PASS",revision=rev,before=sha(old),after=sha(new))
    return rev,old,new

def push(api,old_rev,new,reason):
    if api.repo_info(SPACE,repo_type="space").sha!=old_rev:
        raise RuntimeError("Concurrent Space update; not overriding")
    with tempfile.NamedTemporaryFile(suffix=".html") as tmp:
        tmp.write(new);tmp.flush()
        result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=old_rev,
            operations=[CommitOperationAdd(path_in_repo=UI,path_or_fileobj=tmp.name)],
            commit_message=reason)
    revision=str(result.oid)
    published=Path(hf_hub_download(SPACE,UI,repo_type="space",
                 revision=revision,token=api.token)).read_bytes()
    if sha(published)!=sha(new):
        raise RuntimeError("Published source SHA mismatch")
    emit("SOURCE_HASH_VERIFIED",revision=revision)
    return revision

def served():
    req=urllib.request.Request(BASE+"/chat/%C2%A7wyrlz?code_scroll_check="+str(time.monotonic_ns()),
       headers={"User-Agent":"Swyrlz-Scroll-Source-Verification","Cache-Control":"no-cache"})
    with urllib.request.urlopen(req,timeout=30) as response:
        if response.status!=200:raise RuntimeError("No Chat page")
        return response.read(950000).decode("utf-8",errors="replace")

def live_accept(api,rev,timeout=600):
    deadline=time.monotonic()+timeout
    last={}
    while time.monotonic()<deadline:
        if api.repo_info(SPACE,repo_type="space").sha!=rev:
            raise RuntimeError("Concurrent Space commit during scroll UI verification")
        try:
            source=served()
            last={"preview":MARK in source,
                  "mobile":'id="projectFilePicker"' in source,
                  "chat":'const renderStationGeneration=()=> ' in source or
                          'const renderStationGeneration=()=>{' in source}
            if last["preview"] and last["mobile"] and last["chat"]:
                emit("LIVE_UI_SERVED",revision=rev,scrollFix=True)
                return
        except Exception as exc:last={"error":type(exc).__name__,"detail":str(exc)[:120]}
        time.sleep(12)
    raise RuntimeError("New scrolling UI not visible on live server "+json.dumps(last))

def main():
    api=HfApi(token=os.environ.get("HF_TOKEN") or None)
    if sys.argv[1:]==["preflight"]:
        snapshot(api);return
    if sys.argv[1:]!=["publish"]:raise SystemExit("Usage: script preflight|publish")
    if os.environ.get("SWRLZ_CODE_SCROLL_APPROVED")!="1" or not api.token:
        raise RuntimeError("Authorized HF Chat UI deploy required")
    rev=(BACKUP/"revision.txt").read_text().strip()
    old=(BACKUP/"index.html").read_bytes()
    new=patch(old)
    test_ui(old,new)
    if api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("Source drifted after preflight")
    published=None
    try:
        published=push(api,rev,new,"§C: code draft and live code auto-follow unless reader scrolls up")
        live_accept(api,published)
        emit("LIVE_RELEASE_KEPT",revision=published)
    except Exception:
        emit("LIVE_RELEASE_REJECTED",revision=published)
        if published and api.repo_info(SPACE,repo_type="space").sha==published:
            rollback=push(api,published,old,"Rollback §C code-box follow to exact previous UI")
            emit("EXACT_UI_ROLLBACK_COMPLETED",revision=rollback)
        elif published:emit("CONCURRENT_UPDATE_PREVENTED_ROLLBACK")
        raise

if __name__=="__main__":main()
