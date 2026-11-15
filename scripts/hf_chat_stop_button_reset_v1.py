#!/usr/bin/env python3
"""§C exact Stop->Send terminal reconciliation, preserving server truth.

Only patch live HF Chat UI. No change to model, station, accounts, work queue,
streaming performance, project source, §E or unrelated interfaces.
"""
from __future__ import annotations
import hashlib,json,os,subprocess,sys,tempfile,time,urllib.request,uuid
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
from hf_chat_coding_lifecycle_v1 import check_js
SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
UI="chat/§wyrlz/index.html"
TAG="swrlz-stop-send-terminal-reconcile-v1"
BACKUP=Path("swrlz-stop-send-previous")
def sha(b):return hashlib.sha256(b).hexdigest()
def replace_exact(s,a,b,label):
 n=s.count(a)
 if n!=1:raise RuntimeError("SOURCE_DRIFT "+label+" count="+str(n))
 return s.replace(a,b,1)
def emit(phase,**details):
 print("SWRLZ_STOP_SEND "+json.dumps({"phase":phase,**details},sort_keys=True),flush=True)

def patch(blob):
 s=blob.decode("utf8")
 if TAG in s:raise RuntimeError("Terminal control fix already exists")
 # Immediate UI revalidation when a matching server response settles.
 s=replace_exact(s,
 '''        if(current){
          const terminal=String(state||"").toUpperCase();
          if(["COMPLETE","COMPLETED","FAILED","CANCELLED"].includes(terminal))
            window.dispatchEvent(new CustomEvent("swrlz-voice-state",{detail:{requestId,threadId,terminalType:terminal,text:typeof text==="string"?text:""}}));
        }
      };''',
 '''        if(current){
          const terminal=String(state||"").toUpperCase();
          if(["COMPLETE","COMPLETED","FAILED","CANCELLED"].includes(terminal))
            window.dispatchEvent(new CustomEvent("swrlz-voice-state",{detail:{requestId,threadId,terminalType:terminal,text:typeof text==="string"?text:""}}));
          // swrlz-stop-send-terminal-reconcile-v1: once the exact request
          // reaches a genuine server terminal state, restore Send now.
          // CANCEL_REQUESTED alone is not a completed cancellation.
          syncStationControls();
        }
      };''',
 "terminal settlement controls")
 # A saved assistant message may make live-message rendering exit before its
 # ordinary control reconciliation. That must not leave Stop stuck visible.
 s=replace_exact(s,
 '''          syncComposerCompanionState("station-idle");
          return;
        }
        // Status comes from the acknowledged send or actual Station snapshot,''',
 '''          syncComposerCompanionState("station-idle");
          // The saved response is terminal; restore Send even when this
          // renderer does not need to create an in-progress response.
          syncStationControls();
          return;
        }
        // Status comes from the acknowledged send or actual Station snapshot,''',
 "early-return composer controls")
 return s.encode("utf8")

def check(source):
 text=source.decode("utf8")
 check_js(text)
 assert text.count(TAG)==1
 assert text.count("syncStationControls();")==text.count("syncStationControls();")
 assert "if(current){\n          const terminal" in text
 assert 'syncComposerCompanionState("station-idle");\n          // The saved response is terminal;' in text
 start=text.index("      const stationGenerationActive=()=>")
 end=text.index("      const settleStationGeneration=",start)
 js_source=text[start:end]
 assert 'sendButton.hidden=active;stopButton.hidden=!active;' in js_source
 assert 'const active=stationGenerationActive()||(sending&&!stationGeneration?.terminal);' in js_source
 cases=r"""
const assert=require('node:assert/strict');
const vm=require('node:vm');
const controls=JSON.parse(process.argv[2]);
const execute=(generation,acknowledged,sending,cancel,thread)=>{
  const make=()=>({disabled:false,hidden:false});
  const sendButton=make(),stopButton=make(),imagePickButton=make(),
    micButton=make(),sendControlSpacer=make(),swrlzGuideButton=make(),
    swrlzGuideReceipt=make();
  const scope={sendButton,stopButton,imagePickButton,micButton,
    sendControlSpacer,swrlzGuideButton,swrlzGuideReceipt,stationGeneration:generation,
    stationAcknowledgedRequest:acknowledged,sending,
    stationCancellation:cancel,activeThreadId:thread};
  vm.createContext(scope);
  vm.runInContext(controls+';syncStationControls();',scope);
  return {sendButton,stopButton,swrlzGuideButton};
};
const thread='owned-thread',id='my-request';
let v=execute({requestId:id,threadId:thread,terminal:false}, {requestId:id,threadId:thread},false,null,thread);
assert.equal(v.stopButton.hidden,false);assert.equal(v.sendButton.hidden,true);
v=execute({requestId:id,threadId:thread,terminal:false},{requestId:id,threadId:thread},false,{requestId:id},thread);
assert.equal(v.stopButton.hidden,false);assert.equal(v.stopButton.disabled,true);
v=execute({requestId:id,threadId:thread,terminal:true,terminalType:'CANCELLED'},null,false,null,thread);
assert.equal(v.stopButton.hidden,true);assert.equal(v.sendButton.hidden,false);assert.equal(v.sendButton.disabled,false);
v=execute({requestId:id,threadId:thread,terminal:true,terminalType:'COMPLETE'},null,false,null,thread);
assert.equal(v.stopButton.hidden,true);assert.equal(v.sendButton.hidden,false);
v=execute({requestId:id,threadId:thread,terminal:true,terminalType:'FAILED'},null,false,null,thread);
assert.equal(v.stopButton.hidden,true);assert.equal(v.sendButton.hidden,false);
v=execute(null,null,true,null,thread);
assert.equal(v.stopButton.hidden,false);assert.equal(v.sendButton.disabled,true);
v=execute(null,null,false,null,thread);
assert.equal(v.stopButton.hidden,true);assert.equal(v.sendButton.hidden,false);
console.log('SWRLZ_STOP_SEND_TRANSITIONS_PASS');
"""
 with tempfile.TemporaryDirectory(prefix="chat-stop-send-test-") as d:
  p=Path(d)/"run.js";p.write_text(cases)
  subprocess.run(["node",str(p),json.dumps(js_source)],check=True,timeout=20)
 emit("SOURCE_AND_TERMINAL_TRANSITIONS_PASS",serverOwnedCancel=True,earlyReturn=True,
      noPrematureCancel=True,completedAndFailed=True,preAckAdmission=True)

def snapshot(api):
 revision=api.repo_info(SPACE,repo_type="space").sha
 previous=Path(hf_hub_download(SPACE,UI,repo_type="space",
               revision=revision,token=api.token)).read_bytes()
 candidate=patch(previous)
 check(candidate)
 BACKUP.mkdir(parents=True,exist_ok=True)
 (BACKUP/"previous.html").write_bytes(previous)
 (BACKUP/"sha.json").write_text(json.dumps({"revision":revision,
   "old":sha(previous),"new":sha(candidate)},indent=2))
 emit("PREFLIGHT_PASS",revision=revision,oldSha=sha(previous),newSha=sha(candidate))
 return revision,previous,candidate

def publish(api,expected,blob,message):
 if api.repo_info(SPACE,repo_type="space").sha!=expected:
  raise RuntimeError("Live Space source changed; refuse unsafe update")
 with tempfile.TemporaryDirectory(prefix="stop-send-publish-") as d:
  file=Path(d)/"index.html";file.write_bytes(blob)
  commit=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=expected,
       operations=[CommitOperationAdd(path_in_repo=UI,path_or_fileobj=str(file))],
       commit_message=message)
 deployed=str(commit.oid)
 if sha(Path(hf_hub_download(SPACE,UI,repo_type="space",
            revision=deployed,token=api.token)).read_bytes())!=sha(blob):
  raise RuntimeError("Published source mismatch")
 return deployed

def check_live():
 last="not yet serving"
 for n in range(18):
  try:
   url=BASE+"/chat/%C2%A7wyrlz?stop_send="+uuid.uuid4().hex
   with urllib.request.urlopen(urllib.request.Request(url,
         headers={"User-Agent":"Swyrlz-Stop-Send-Acceptance","Cache-Control":"no-cache"}),timeout=25) as r:
    served=r.read(950000).decode("utf8",errors="replace")
   if TAG in served and "swrlzStopGestureEligible" in served:
    emit("LIVE_SOURCE_PASS",chars=len(served));return
   last="Old HTML still serving"
  except Exception as exc:last=type(exc).__name__
  time.sleep(9)
 raise RuntimeError("Latest UI not served: "+last)

def main():
 if len(sys.argv)!=2 or sys.argv[1] not in ("preflight","publish"):
  raise SystemExit("Usage: python script.py preflight|publish")
 token=os.getenv("HF_TOKEN")
 if not token:raise SystemExit("HF_TOKEN unavailable")
 api=HfApi(token=token)
 revision,prior,next_=snapshot(api)
 if sys.argv[1]=="preflight":return
 if os.getenv("SWRLZ_STOP_SEND_DEPLOY_APPROVED")!="1":
  raise SystemExit("Approved release scope missing")
 deployed=None
 try:
  deployed=publish(api,revision,next_,"§C: switch Stop to Send on genuine server terminal state")
  check_live()
  emit("PUBLISHED_PASS",revision=deployed,parent=revision)
 except Exception:
  if deployed and api.repo_info(SPACE,repo_type="space").sha==deployed:
   restored=publish(api,deployed,prior,"Rollback §C Stop-to-Send terminal reconciliation")
   emit("ROLLBACK",revision=restored)
  raise

if __name__=="__main__":main()
