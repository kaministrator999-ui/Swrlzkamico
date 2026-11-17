"""§E v11.491: network-safe same-project update recovery; append-only patch."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER="SWYRL_ENGINE_DEPLOY_MARKER: V11_491_CLOUD_MODEL_UPDATE_RECOVERY"

def once(h,old,new,label):
 count=h.count(old)
 if count!=1:raise AssertionError(("v11.491",label,count,old[:120]))
 return h.replace(old,new,1)

def apply(html):
 assert "SWYRL_ENGINE_DEPLOY_MARKER: V11_490_MODEL_RIG_WORKSPACE" in html
 helper=(ROOT/"runtime/model_account_update_recovery_v11_491.js").read_text("utf8")
 assert "se491SelectedDocument" in helper
 html=once(html,
  " async function updateSelectedModel(record,source,chosen){",
  helper+"\n async function updateSelectedModel(record,source,chosen,onProgress=()=>{}){",
  "safe reader and progress support")
 html=once(html,
  """  if(file.size>LIMIT)throw Error('Update file exceeds 32 MiB');
  const input=JSON.parse(await file.text());
  const {id,doc,metadata}=await NAME.selectedDocument(record,source);""",
  """  if(file.size>LIMIT)throw Error('Update file exceeds 32 MiB');
  if(/\\.zip$/i.test(String(file.name||'')))
   throw Error('ZIP archive selected. Extract the .swyrl.json from the ZIP, then choose that JSON file.');
  onProgress('Reading selected model file…');
  let input;
  try{input=JSON.parse(await file.text());}
  catch{throw Error('Not a valid model JSON file. Extract the .swyrl.json from any ZIP first.');}
  onProgress('Checking the currently saved project revision…');
  const {id,doc,metadata}=await se491SelectedDocument(record,source,onProgress);""",
  "reject zipped imports and retry only cloud read")
 html=once(html,
  """  const changed=sourceModel(input,doc,metadata,source);
  if(!confirm(""",
  """  onProgress('Validating mesh identity, topology, UVs and rig…');
  const changed=sourceModel(input,doc,metadata,source);
  if(!confirm(""",
  "file validation progress")
 html=once(html,
  """   const reply=await rpc('cloud.save',{
    bytes:bytes.buffer,name:metadata.name||record.name,
    projectId:id,expectedRevision:version
   },[bytes.buffer]);""",
  """   onProgress('Saving '+String(metadata.name||record.name)+' · expected revision '+version+'…');
   let reply;
   try{
    reply=await rpc('cloud.save',{
     bytes:bytes.buffer,name:metadata.name||record.name,
     projectId:id,expectedRevision:version
    },[bytes.buffer]);
   }catch(error){
    throw Error('Cloud save confirmation unavailable ('+msg(error)+
     '). The revision MAY have been saved. Refresh My Projects to check the revision before retrying.');
   }""",
  "never retry ambiguous cloud save")
 html=once(html,
  """   await se170Refresh();
   return 'Updated '+String(metadata.name||record.name)+' to revision '+reply.project.revision+
    '. If this project is open, reload it before saving more edits.';""",
  """   let refreshed=true;
   try{await se170Refresh();}
   catch{refreshed=false;}
   return 'Updated '+String(metadata.name||record.name)+' to revision '+reply.project.revision+
    (refreshed?'. If this project is open, reload it before saving more edits.':
      '. The save succeeded, but the project list could not refresh. Do NOT submit the same update again; reopen My Projects later.');""",
  "do not misreport successful save as failure after refresh")
 html=once(html,
  """  button.onclick=async()=>{
   if(button.disabled)return;
   button.disabled=true;status.textContent='Checking selected project…';
   try{status.textContent=await updateSelectedModel(record,source)}
   catch(error){status.textContent='Update failed: '+msg(error);}
   finally{button.disabled=false}
  };""",
  """  let se491RetryFile=null;
  button.onclick=async()=>{
   if(button.disabled)return;
   button.disabled=true;
   let file=se491RetryFile;
   try{
    if(!file){
     status.textContent='Select the extracted .swyrl.json model file…';
     file=await selectFile();
    }
    if(!file){status.textContent='No changes made.';return;}
    status.textContent=await updateSelectedModel(record,source,file,message=>{status.textContent=message;});
    se491RetryFile=null;
    button.textContent='Update Model';
   }catch(error){
    const recoverable=error?.se491Recoverable===true;
    se491RetryFile=recoverable?file:null;
    button.textContent=recoverable?'Retry Update':'Update Model';
    status.textContent='Update failed: '+msg(error);
   }finally{button.disabled=false;}
  };""",
  "keep selected file only for safe cloud-read retry")
 for old,new in (
  ("SWYRL_ENGINE_DEPLOY_MARKER: V11_490_MODEL_RIG_WORKSPACE",MARKER),
  ("ENGINE · MAKER v11.490","ENGINE · MAKER v11.491"),
  ("v11.490 · cloth rig playback and project workspace restoration",
   "v11.491 · resilient model update and clear cloud errors"),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.490'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.491'"),
  ("<title>§wyrl§ Engine · Maker v11.490</title>",
   "<title>§wyrl§ Engine · Maker v11.491</title>")
 ): html=once(html,old,new,"release identity")
 prev=" source.engine='§wyrl§ Engine · Maker v11.490';source.version=11.490;"
 if html.count(prev)!=5:raise AssertionError(("v11.491 provenance",html.count(prev)))
 html=html.replace(prev," source.engine='§wyrl§ Engine · Maker v11.491';source.version=11.491;")
 tag="const SE_RELEASE_NOTES=";at=html.index(tag)+len(tag)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes["history"]=[n for n in notes.get("history",[]) if n.get("version")!="v11.490"]
 notes["history"].insert(0,{"version":"v11.490","changes":notes.get("changes",[])})
 notes.update(version="v11.491",date="2026-11-17",
  title="Recoverable cloud model updates and accurate save confirmation",
  changes=[
   "My Projects Update Model distinguishes ZIP archives from the .swyrl.json input actually accepted; ZIP selections are never sent to storage.",
   "A transient §C cloud.load error safely retries project reads up to three times, never changes revision checks or automatically replays cloud.save.",
   "On repeated cloud read failure, Retry Update retains the previously chosen model file in the active page, with a precise account-reconnection message.",
   "A cloud.save transport error warns that save confirmation is unknown and requires checking the account revision before another attempt.",
   "If the save was confirmed but the subsequent My Projects list refresh fails, the UI reports the successful new revision rather than incorrectly reporting update failure.",
   "Unchanged user mesh, UV, animation data, project identity, eight-entry revision history and account authorization safeguards."
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</",r"<\/")+html[at+width:]
