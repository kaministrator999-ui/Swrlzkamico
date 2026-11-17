"""§E v11.492: accept ZIP model update files securely and preserve selected cloud revisions."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
MARKER="SWYRL_ENGINE_DEPLOY_MARKER: V11_492_ZIP_MODEL_UPDATES"
def once(h,old,new):
 n=h.count(old)
 if n!=1:raise AssertionError(("v11.492",n,old[:130]))
 return h.replace(old,new,1)
def apply(html):
 assert "SWYRL_ENGINE_DEPLOY_MARKER: V11_491_CLOUD_MODEL_UPDATE_RECOVERY" in html
 src=(ROOT/"runtime/model_zip_update_v11_492.js").read_text("utf8")
 assert "SWYRL_ENGINE_ZIP_UPDATES_492" in src
 html=once(html,"const se491TransientRead = error =>",src+"\nconst se491TransientRead = error =>")
 html=once(html,
  "input.accept='.json,.swyrl,application/json';",
  "input.accept='.swyrl.json,.json,.swyrl,.zip,application/json,application/zip,application/x-zip-compressed';")
 html=once(html,
  """  if(/\\.zip$/i.test(String(file.name||'')))
   throw Error('ZIP archive selected. Extract the .swyrl.json from the ZIP, then choose that JSON file.');
  onProgress('Reading selected model file…');
  let input;
  try{input=JSON.parse(await file.text());}
  catch{throw Error('Not a valid model JSON file. Extract the .swyrl.json from any ZIP first.');}
  onProgress('Checking the currently saved project revision…');""",
  """  onProgress('Reading selected model or ZIP archive…');
  const input=await se492ModelUpload.parse(file,onProgress);
  onProgress('Checking the currently saved project revision…');""")
 for old,new in (
  ("SWYRL_ENGINE_DEPLOY_MARKER: V11_491_CLOUD_MODEL_UPDATE_RECOVERY",MARKER),
  ("ENGINE · MAKER v11.491","ENGINE · MAKER v11.492"),
  ("v11.491 · resilient model update and clear cloud errors",
   "v11.492 · direct ZIP model updates"),
  ("window.SWRLZ_FORGE_BUILD={version:'v11.491'",
   "window.SWRLZ_FORGE_BUILD={version:'v11.492'"),
  ("<title>§wyrl§ Engine · Maker v11.491</title>",
   "<title>§wyrl§ Engine · Maker v11.492</title>")
 ):html=once(html,old,new)
 prev=" source.engine='§wyrl§ Engine · Maker v11.491';source.version=11.491;"
 if html.count(prev)!=5:raise AssertionError(("v11.492 provenance",html.count(prev)))
 html=html.replace(prev," source.engine='§wyrl§ Engine · Maker v11.492';source.version=11.492;")
 tag="const SE_RELEASE_NOTES=";at=html.index(tag)+len(tag)
 notes,width=json.JSONDecoder().raw_decode(html[at:])
 notes["history"]=[n for n in notes.get("history",[]) if n.get("version")!="v11.491"]
 notes["history"].insert(0,{"version":"v11.491","changes":notes.get("changes",[])})
 notes.update(version="v11.492",date="2026-11-17",title="Upload ZIP model revisions without extracting",
  changes=[
   "Update Model accepts a ZIP containing one native .swyrl.json or JSON model, including the owner's compressed Sorting Hat mesh fixes.",
   "ZIP extraction is on-device; bounds on archive size, entry count, decompressed size, compressed payload and CRC32 prevent corrupted or oversized models from reaching the project updater.",
   "Only a single unambiguous model JSON is selected from the ZIP. Unsafe paths, encrypted, ZIP64, multi-disk and unsupported compression are explicitly rejected.",
   "The same strict selected project mesh ID, account identity, expected cloud revision, rolling history and atomic save behavior remain in force.",
   "Cloud-read retries and confirmation-aware write reporting introduced in v11.491 remain enabled."
  ])
 return html[:at]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</",r"<\/")+html[at+width:]
