#!/usr/bin/env python3
"""Guarded §C generation lifecycle and interactive webpage quality patch.

The current Hugging Face Space revision is authoritative. Patch exactly three
files with source drift checks; never touch model weights, hardware, accounts,
GitHub access, §E or existing project data.
"""
from __future__ import annotations
import ast,hashlib,json,os,re,sys,tempfile,time,urllib.request,uuid
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
from hf_chat_coding_lifecycle_v1 import check_js
SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
ENGINE="qwen_coder_engine.py"
STATION="station.py"
UI="chat/§wyrlz/index.html"
FILES=(ENGINE,STATION,UI)
TAG="swrlz-code-intent-stop-quality-v1"
BACKUP=Path("swrlz-code-intent-stop-original")
def sha(data):return hashlib.sha256(data).hexdigest()
def one(s,old,new,label):
 n=s.count(old)
 if n!=1:raise RuntimeError("SOURCE_DRIFT "+label+" count="+str(n))
 return s.replace(old,new,1)
def emit(key,**fields):
 print("SWRLZ_CODE_LIFECYCLE_QUALITY "+json.dumps({"phase":key,**fields},ensure_ascii=False,sort_keys=True),flush=True)

# The caller's own accepted current source and the existing unverified
# checkpoint determine whether "Continue code" is a resume or a revision.
# Never interpret a missing checkpoint as permission to fabricate old source.
CONTINUE_HELPER=r'''
# swrlz-code-intent-stop-quality-v1: same-thread continuation semantics.
def _swrlz_complete_code_followup(prompt,pending,thread):
    command=re.fullmatch(
        r"(?is)\s*(?:(?:please|now)\s+)?(?:continue(?:\s+(?:the\s+)?(?:code|generation|project|file|output))?|resume(?:\s+(?:the\s+)?(?:code|generation|project|file|output))?|keep\s+generating(?:\s+code)?)\s*[.!]?\s*",
        str(prompt or ""))
    if not command or pending:
        return ""
    messages=thread.get("messages") if isinstance(thread,dict) else []
    found=False
    fence=chr(96)*3
    for message in reversed(messages if isinstance(messages,list) else []):
        if not isinstance(message,dict) or message.get("role")!="assistant":
            continue
        value=str(message.get("text") or "")
        low=value.lower()
        fenced=(fence in value and value.count(fence)>=2
            and re.search(re.escape(fence)+r"(?:html|css|javascript|js|typescript|python)\b",low))
        html_document=("<!doctype html" in low and "</html>" in low)
        if fenced or html_document:
            found=True
            break
    if found:
        return (
            "Continue DEVELOPMENT of the most recent COMPLETE code artifact in this same thread. "
            "There is no unfinished checkpoint to append to; this is a NEW, meaningful revision, "
            "not a no-op or a request to repeat the previous source. Use only source actually present "
            "in this thread's grounded history or account-owned project context. Preserve the prior "
            "page's topic, working interactions, existing code and file identity; implement one "
            "substantial useful enhancement and visual polish. Return the COMPLETE revised code, "
            "not an inert feature-card landing page or fake navigation to nonexistent studios. "
            "Every visible button/link must do something real. If the full prior source is not "
            "available in grounded context, state that limitation and request the source instead "
            "of inventing a replacement."
        )
    return (
        "The user asked to continue code, but this thread has no saved unfinished "
        "checkpoint and no grounded completed code artifact. Explain briefly that "
        "there is no code ready to continue, and ask the user to provide the code "
        "or a specific new project request. Do not fabricate a continuation."
    )

'''
def patch_station(raw):
 s=raw.decode("utf8")
 if TAG in s:raise RuntimeError("Station patch already installed")
 s=one(s,"def _swrlz_auto_code_chain(events,payload,key,request_id):",
     CONTINUE_HELPER+"def _swrlz_auto_code_chain(events,payload,key,request_id):",
     "continue helper insertion")
 # Internal checkpoint may auto-resume thirty-two times under Station. The
 # status must not tell users to manually Continue during active decoding.
 s=one(s,'"reason":"Unverified source safely saved; continue code to resume"',
       '"reason":"Unverified source checkpointed; automatic continuation is active when work remains"',
       "remove misleading in-flight continue dialog")
 s=one(s,
  '        history=_history_projection(t, current_prompt=prompt)',
  '        followup_prompt=_swrlz_complete_code_followup(prompt,pending,t)\n'
  '        history=_history_projection(t, current_prompt=followup_prompt or prompt)',
  "followup current thread provenance")
 s=one(s,
  '"prompt":_inference_prompt_after_vision(prompt),"history":history',
  '"prompt":_inference_prompt_after_vision(followup_prompt or prompt),"history":history',
  "route only genuine completed-code followup")
 ast.parse(s,filename=STATION)
 return s.encode("utf8")

def patch_engine(raw):
 s=raw.decode("utf8")
 if TAG in s:raise RuntimeError("Coder patch already installed")
 # Style hints are scoped to the broad creative HTML request: an explicit
 # studio or business site still uses its own requested scope.
 key='''    if coding:
        explicit_chat=any(x in p for x in ("provide the code","show the code","code in chat","paste the code","code block"))'''
 value='''    if coding:
        # swrlz-code-intent-stop-quality-v1: a broad "cool HTML page"
        # should be one appealing interactive experience, not a fake agency
        # features/CTA template. Explicit project themes still take priority.
        broad_cool_page=(
            bool(re.search(r"\\b(?:html|web\\s*page|webpage|website|site)\\b",p))
            and bool(re.search(r"\\b(?:cool|awesome|interesting|impressive|creative|unique|beautiful)\\b",p))
            and bool(re.search(r"\\b(?:make|create|build|write|design|generate)\\b",p)))
        if broad_cool_page:
            specified_theme=bool(re.search(
                r"\\b(?:studio|dashboard|editor|shop|store|portfolio|game|audio|music|restaurant|business|for my|for a|about|landing page)\\b",p))
            return (
                "RESPONSE MODE: CODE-COMPLETE-INTERACTIVE-WEBPAGE. Deliver one fully usable "
                "self-contained HTML document with thoughtful mobile-first CSS and working "
                "JavaScript interactions, visible focus states and meaningful behavior. "
                "Choose an original coherent visual idea when the user gives no subject. "
                "Make it visually distinctive, intentional and satisfying to explore. "
                "Do not create static marketing cards advertising 'Responsiveness' or "
                "'Interactivity', empty Get Started calls-to-action, placeholder href='#' "
                "links, or invented multi-studio destinations. A button must actually "
                "change a state, control a feature, or navigate to a real section. "
                "Prioritize a modest complete interactive experience over extensive "
                "unimplemented menus and speculative product scaffolding. "
                +("Honor the user's named theme and real requested controls." if specified_theme
                  else "Freestyle the theme; no unrelated landing-page or studio scaffold.")+
                " Deliver the complete single-file source; never claim tests ran without receipts."
            )
        explicit_chat=any(x in p for x in ("provide the code","show the code","code in chat","paste the code","code block"))'''
 s=one(s,key,value,"cool HTML prompt integration")
 # Explain a real checkpoint once, instead of a recurring 'Continue code'
 # instruction when structurally complete source needs validation repair.
 old='''    yield {"type":"STATUS","phase":"CODE_DRAFT_SAVED",
           "reason":"Unverified source saved; next user turn can resume exact code"}
    yield {"type":"DELTA","text":(
        "The code is not finished or accepted yet. I preserved "+
        str(source_size)+" bytes of the unverified draft across "+
        str(segments)+" generation segments in this conversation. "+
        "Send **Continue code** to resume from its ending rather than regenerate it. "+
        "The project will only be marked complete after structural validation."
    )}'''
 new='''    repair_needed=bool(checkpoint.get("repairNeeded"))
    yield {"type":"STATUS","phase":"CODE_DRAFT_SAVED",
           "reason":("Source saved but needs validation repair" if repair_needed else
                     "Source saved at a genuine unfinished generation boundary")}
    yield {"type":"DELTA","text":(
        ("The source has been generated but did not pass code validation. " if repair_needed
         else "The code is still incomplete. ")+
        str(source_size)+" bytes were saved safely in this conversation. "+
        ("Send **Continue code** only to retry repairing this saved source, or specify the correction. "
         if repair_needed else
         "Automatic continuation has stopped at its bounded safety limit. "
         "Send **Continue code** only if you want to resume those saved bytes. ")+
        "No unverified draft is marked as a completed project."
    )}'''
 s=one(s,old,new,"explicit true pause vs generated but validation failed")
 ast.parse(s,filename=ENGINE)
 return s.encode("utf8")

STOP_UI=r'''      // swrlz-code-intent-stop-quality-v1: accept a NEW intentional pointer
      // gesture, not the synthetic click produced when Send becomes Stop.
      // Unlike a time window this does not suppress a fast deliberate Stop.
      const swrlzStopGestureEligible=(event,armed)=>
        !Number(event?.detail||0)||!!armed;
      let swrlzStopPointerArmed=false;
      stopButton.addEventListener("pointerdown",()=>{swrlzStopPointerArmed=true;},{passive:true});
      stopButton.addEventListener("pointercancel",()=>{swrlzStopPointerArmed=false;});
      stopButton.addEventListener("click",async event=>{
        if(!swrlzStopGestureEligible(event,swrlzStopPointerArmed))return;
        swrlzStopPointerArmed=false;
        const requestInAdmission=stationSubmission&&
          !stationAcknowledgedRequest&&
          (!stationGeneration||stationGeneration.terminal||
           stationGeneration.requestId!==stationSubmission.requestId);
        if(requestInAdmission){
          // A real Stop before /send ACK must block model admission, then
          // cancel the worker if the server nevertheless admits the request.
          stationSubmission.cancelRequested=true;
          window.SwrlzForgeEmbedV1?.revoke("generation-cancelled");
          syncStationControls();
          return;
        }
        const rid=String(stationAcknowledgedRequest?.requestId||
          stationGeneration?.requestId||stationSubmission?.requestId||"");
        if(!rid)return;
        if(stationCancellation?.requestId===rid)return;
        const projectionEpoch=accountProjectionEpoch,cancellation={projectionEpoch,requestId:rid};
        stationCancellation=cancellation;
        if(stationSubmission?.requestId===rid)stationSubmission.cancelRequested=true;
        syncStationControls();
        window.SwrlzForgeEmbedV1?.revoke("generation-cancelled");
        try{
          const result=await fetch("/api/lalm_station/cancel",{
            method:"POST",credentials:"same-origin",cache:"no-store",
            headers:{"Content-Type":"application/json"},
            body:JSON.stringify({requestId:rid})
          });
          const outcome=await result.json().catch(()=>({}));
          if(!result.ok||!outcome.ok)throw new Error("Stop not acknowledged by server");
          // Do not kill the transport: the authoritative CANCELLED receipt
          // may arrive shortly afterward and must close the correct request.
          if(projectionEpoch===accountProjectionEpoch)await syncStation(true);
        }catch(_){
          // An undelivered Stop is NOT success. Keep native work visible,
          // explain the error and leave the button ready for a real retry.
          if(stationGeneration?.requestId===rid){
            stationGeneration.status=[...(stationGeneration.status||[]),
              {phase:"STOP_UNCONFIRMED",reason:"Stop did not reach the server. Retry Stop."}];
            renderStationGeneration();
          }
        }finally{
          if(stationCancellation===cancellation&&projectionEpoch===accountProjectionEpoch){
            stationCancellation=null;syncStationControls();scheduleStationSync();
          }
        }
      });
'''
def patch_ui(raw):
 s=raw.decode("utf8")
 if TAG in s:raise RuntimeError("UI patch already installed")
 marker='      stopButton.addEventListener("click",async()=>{'
 end='      // §E Analyze is a user-clicked read-only request;'
 a=s.index(marker);b=s.index(end,a)
 before=s[a:b]
 for token in ('performance.now()-lastTouchSend<350','/api/lalm_station/cancel',
               'stationCancellation','syncStation(true)'):
  if token not in before:raise RuntimeError("SOURCE_DRIFT Stop implementation "+token)
 s=s[:a]+STOP_UI+s[b:]
 # Settling a truly paused generation must NOT throw away the source that the
 # client needs to show and the user may resume later.
 s=one(s,
  '''          stationGeneration={...stationGeneration,terminal:true,terminalType:state,
            previewText:"",...(typeof text==="string"?{text}: {})};''',
  '''          stationGeneration={...stationGeneration,terminal:true,terminalType:state,
            previewText:stationGeneration.codeDraftCheckpoint?.verificationState==="UNVERIFIED_INCOMPLETE"
              ?String(stationGeneration.previewText||""):"",
            ...(typeof text==="string"?{text}: {})};''',
  "preserve paused code after Station terminal state")
 return s.encode("utf8")

def test_logic(files):
 engine=files[ENGINE].decode("utf8");station=files[STATION].decode("utf8");html=files[UI].decode("utf8")
 ast.parse(engine);ast.parse(station);check_js(html)
 helper=next(node for node in ast.parse(station).body if isinstance(node,ast.FunctionDef)
              and node.name=="_swrlz_complete_code_followup")
 scope={"re":re}
 exec(compile(ast.Module(body=[helper],type_ignores=[]),"<station-followup-test>","exec"),scope)
 follow=scope["_swrlz_complete_code_followup"]
 sample=chr(96)*3+"html\n<!doctype html><html><body><button id='a'>A</button></body></html>\n"+chr(96)*3
 t={"messages":[{"role":"assistant","text":sample}]}
 assert follow("Continue code",{"schema":"swrlz-long-code-checkpoint-v1"},t)==""
 assert "meaningful enhancement" in follow("Continue code",None,t)
 assert "no code ready" not in follow("Continue code",None,t)
 assert "no saved unfinished" in follow("Continue code",None,{"messages":[]})
 assert follow("Show me a cube",None,t)==""
 mode=next(node for node in ast.parse(engine).body if isinstance(node,ast.FunctionDef)
           and node.name=="_response_mode")
 scope={"re":re}
 exec(compile(ast.Module(body=[mode],type_ignores=[]),"<mode-test>","exec"),scope)
 hint=scope["_response_mode"]("Make me a cool HTML webpage",{"codingTask":True})
 assert "CODE-COMPLETE-INTERACTIVE-WEBPAGE" in hint and "working" in hint
 assert "placeholder href" in hint
 hint2=scope["_response_mode"]("Write a Python square function",{"codingTask":True})
 assert "CODE-COMPLETE-INTERACTIVE-WEBPAGE" not in hint2
 assert 'Unverified source checkpointed; automatic continuation is active' in station
 assert 'Unverified source safely saved; continue code to resume' not in station
 assert "CODE_DRAFT_SAVED" in engine and "repair_needed=bool(checkpoint.get" in engine
 for token in ('swrlzStopGestureEligible','swrlzStopPointerArmed',
               'stationSubmission.cancelRequested=true','STOP_UNCONFIRMED',
               'stationGeneration.codeDraftCheckpoint?.verificationState'):
  assert token in html,token
 assert 'performance.now()-lastTouchSend<350' not in html
 assert html.count('stopButton.addEventListener("click"')==1
 import subprocess
 js=r"""const assert=require('assert');
const swrlzStopGestureEligible=(event,armed)=>!Number(event?.detail||0)||!!armed;
assert.equal(swrlzStopGestureEligible({detail:1},false),false);
assert.equal(swrlzStopGestureEligible({detail:1},true),true);
assert.equal(swrlzStopGestureEligible({detail:0},false),true);
console.log("EXPLICIT_STOP_GESTURE_PASS");"""
 with tempfile.TemporaryDirectory() as root:
  p=Path(root)/"stop.js";p.write_text(js)
  subprocess.run(["node",str(p)],check=True,timeout=20)
 emit("SOURCE_TEST_PASS",sameThreadOnly=True,stopGesture=True,
      nativeCancelPreserved=True,modelUnchanged=True,workingWebpageHint=True)

def snapshot(api):
 rev=api.repo_info(SPACE,repo_type="space").sha
 prior={p:Path(hf_hub_download(SPACE,p,repo_type="space",revision=rev,token=api.token)).read_bytes() for p in FILES}
 next_={ENGINE:patch_engine(prior[ENGINE]),STATION:patch_station(prior[STATION]),UI:patch_ui(prior[UI])}
 test_logic(next_)
 BACKUP.mkdir(parents=True,exist_ok=True)
 for name,data in prior.items():
  target=BACKUP/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 (BACKUP/"receipt.json").write_text(json.dumps({"previousRevision":rev,
  "old":{x:sha(v) for x,v in prior.items()},
  "next":{x:sha(v) for x,v in next_.items()}},indent=2))
 emit("PREFLIGHT_PASS",revision=rev,changed=list(FILES))
 return rev,prior,next_

def publish(api,expected,files,message):
 if api.repo_info(SPACE,repo_type="space").sha!=expected:
  raise RuntimeError("Concurrent Space edit: refusing to publish stale source")
 with tempfile.TemporaryDirectory() as root:
  ops=[]
  for path,blob in files.items():
   target=Path(root)/path;target.parent.mkdir(parents=True,exist_ok=True)
   target.write_bytes(blob)
   ops.append(CommitOperationAdd(path_in_repo=path,path_or_fileobj=str(target)))
  result=api.create_commit(repo_id=SPACE,repo_type="space",
                           parent_commit=expected,operations=ops,commit_message=message)
 deployed=str(result.oid)
 for name,blob in files.items():
  actual=Path(hf_hub_download(SPACE,name,repo_type="space",
                             revision=deployed,token=api.token)).read_bytes()
  if sha(actual)!=sha(blob):raise RuntimeError("Publish hash mismatch: "+name)
 return deployed

def live_check():
 url=BASE+"/chat/%C2%A7wyrlz?code_stop_quality="+uuid.uuid4().hex
 last=""
 for _ in range(18):
  try:
   with urllib.request.urlopen(urllib.request.Request(
       url,headers={"User-Agent":"Swyrlz-Stop-Quality-Release","Cache-Control":"no-cache"}),timeout=25) as r:
    body=r.read(1000000).decode("utf8",errors="replace")
   if TAG in body and "swrlzStopGestureEligible" in body:
    emit("LIVE_UI_PASS",chars=len(body));return
   last="Old client source still served"
  except Exception as exc:last=type(exc).__name__
  time.sleep(9)
 raise RuntimeError("New Chat UI not visible: "+last)

def main():
 if len(sys.argv)!=2 or sys.argv[1] not in ("preflight","publish"):
  raise SystemExit("Usage: script.py preflight|publish")
 token=os.getenv("HF_TOKEN")
 if not token:raise SystemExit("HF_TOKEN required")
 api=HfApi(token=token);revision,old,new=snapshot(api)
 if sys.argv[1]=="preflight":return
 if os.getenv("SWRLZ_CHAT_STOP_QUALITY_APPROVED")!="1":
  raise SystemExit("Guarded source release approval missing")
 deployed=None
 try:
  deployed=publish(api,revision,new,"§C: correct Stop, Continue code and creative webpage output")
  live_check()
  emit("PUBLISHED_PASS",revision=deployed,original=revision)
 except Exception:
  if deployed and api.repo_info(SPACE,repo_type="space").sha==deployed:
   restored=publish(api,deployed,old,"Restore previous §C Stop/Continue/webpage source")
   emit("ROLLBACK_APPLIED",restored=restored)
  raise

if __name__=="__main__":main()
