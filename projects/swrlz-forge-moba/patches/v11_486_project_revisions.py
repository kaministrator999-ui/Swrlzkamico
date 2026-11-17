"""§E v11.486: rolling revision history and same-project model updates.
History is embedded in the existing authenticated account document, not a
new project record. Native starter cloning and cloud optimistic concurrency stay.
"""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
MARKER="SWYRL_ENGINE_DEPLOY_MARKER: V11_486_PROJECT_REVISIONS"

def once(s,old,new,tag):
    count=s.count(old)
    if count!=1:raise AssertionError(("v11.486 anchor",tag,count,old[:130]))
    return s.replace(old,new,1)

def apply(html):
    assert "SWYRL_ENGINE_DEPLOY_MARKER: V11_485_ONE_CLOTH_SORTING_HAT" in html
    rev=(ROOT/"runtime/project_revisions_v11_486.js").read_text("utf8")
    native=(ROOT/"runtime/project_revision_actions_v11_486.js").read_text("utf8")
    asset=(ROOT/"runtime/studio_asset_revisions_v11_486.js").read_text("utf8")
    for token in ("async function prepare(", "async function recordLocal(", "async function unpack("):
        assert token in rev,token
    for token in ("async function se486ImportProjectUpdate", "se486NativeProjectHistory"):
        assert token in native,token

    # Shared revision codec is available before both authenticated and
    # standalone studio adapters. No credentials or new account routes.
    html=once(html,"/* SE468_STANDALONE_STUDIO_ASSETS_START */",
              rev+"\n/* SE468_STANDALONE_STUDIO_ASSETS_START */",
              "revision core ahead of studio asset library")

    # Every explicit project save gets a bounded on-device recovery snapshot.
    # The existing 350 ms autosave intentionally bypasses this path.
    html=once(html,
        """ await se175Store([row]);
 if(typeof markSaved==='function')markSaved();""",
        """ await se175Store([row]);
 try{await window.SWYRL_ENGINE_REVISIONS_486.recordLocal(row.id,row.data);}
 catch(error){console.warn('§E local revision archive unavailable',error);}
 if(typeof markSaved==='function')markSaved();""",
        "manual-save-only local project history")

    # Replace only the compiled native account save body, preserving its public
    # function name, CAS RPC and the already-installed se371 wrapper.
    # Earlier patches may have reformatted the original body, so anchor on
    # adjacent function declarations rather than historical indentation.
    save_start=html.index(" async function saveCloud(){")
    save_end=html.index(" async function listCloud(){",save_start)
    previous_save=html[save_start:save_end]
    for required in ("cloud.save", "cloudRefs.set(", "MAX_RAW", "cloudBusy"):
        assert required in previous_save,("cloud save contract changed",required)
    save_replacement=""" async function saveCloud(){
   if(cloudBusy)return;cloudBusy=true;
   try{
     revoke('Saving project.');
     const projectId=getProjectId(),previous=cloudRefs.get(projectId);
     let native=window.SWYRL_ENGINE_AGENT.inspectScene();
     if(previous){
       const remote=await rpc('cloud.load',{projectId:previous.id});
       if(remote.project?.id!==previous.id||remote.project?.revision!==previous.revision)
         throw Error('Account revision changed. Reopen the latest project before saving.');
       if(!(remote.bytes instanceof ArrayBuffer)||remote.bytes.byteLength>MAX_RAW)
         throw Error('Account project recovery unavailable.');
       const old=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(remote.bytes));
       if(old.project?.instanceId&&old.project.instanceId!==projectId)
         throw Error('Account project identity differs from the active project.');
       native=(await window.SWYRL_ENGINE_REVISIONS_486.prepare(
        old,native,previous.revision,MAX_RAW)).payload;
     }else{
       native.se486History={schema:window.SWYRL_ENGINE_REVISIONS_486.SCHEMA,limit:8,entries:[]};
     }
     const bytes=new TextEncoder().encode(JSON.stringify(native));
     if(bytes.byteLength>MAX_RAW)
       throw Error('This project exceeds the 96 MiB account limit. Local copy remains available.');
     setStatus('Saving native project and revision history to your account…');
     const result=await rpc('cloud.save',{bytes:bytes.buffer,
       name:summaryName(currentProject.name)||'§E project',
       ...(previous?{projectId:previous.id,expectedRevision:previous.revision}:{expectedRevision:0})},
       [bytes.buffer]);
     const stored=result.project;
     if(!stored?.id||!Number.isInteger(stored.revision)||result.durable!==true)
       throw Error('Cloud save was not confirmed. Keep your local project.');
     cloudRefs.set(projectId,stored);
     setStatus('Saved to your account · revision '+stored.revision+'.');
   }catch(error){setStatus('Account save failed: '+error.message,true);}
   finally{cloudBusy=false;}
 }
"""
    html=html[:save_start]+save_replacement+html[save_end:]

    # Native project commands live beside established buttons; this is the
    # same signed-in host closure as se371 and its asset-safe save routes.
    html=once(html,"window.SWYRL_ENGINE_SAFE_PROJECTS_371=Object.freeze({",
              native+"\nwindow.SWYRL_ENGINE_SAFE_PROJECTS_371=Object.freeze({",
              "native project revision actions")

    # Standalone model/particle cloud assets already use stable working
    # asset IDs from v11.470; record old versions inside that exact record.
    asset_start=html.index(" async function save(type,cloud){",html.index("/* SE468_STANDALONE_STUDIO_ASSETS_START */"))
    asset_end=html.index(" async function loadAccountAsset(type,id){",asset_start)
    block=html[asset_start:asset_end]
    block=once(block,
        """    const payload=new TextEncoder().encode(JSON.stringify(envelope(record)));
    if(payload.byteLength>MAX)throw Error('Asset exceeds the 8 MiB account limit.');
    const remote=working?.remote||null;""",
        """    const remote=working?.remote||null;
    let document=envelope(record);
    if(remote){
     const prior=await api().load(remote.id);
     if(prior.project?.id!==remote.id||prior.project?.revision!==remote.revision)
       throw Error('Account asset revision changed. Reload the latest saved asset first.');
     if(!(prior.bytes instanceof ArrayBuffer)||prior.bytes.byteLength>MAX)
       throw Error('Previous asset snapshot unavailable.');
     const old=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(prior.bytes));
     if(old.assetRecord?.id!==record.id)throw Error('Account asset identity mismatch.');
     document=(await window.SWYRL_ENGINE_REVISIONS_486.prepare(old,document,remote.revision,MAX)).payload;
    }else document.se486History={schema:window.SWYRL_ENGINE_REVISIONS_486.SCHEMA,limit:8,entries:[]};
    const payload=new TextEncoder().encode(JSON.stringify(document));
    if(payload.byteLength>MAX)throw Error('Asset exceeds the 8 MiB account limit.');""",
        "same-asset revision archive via existing cloud bridge")
    block=once(block,
        """   return true;
  }catch(error){status('Save failed: '+error.message,true);return false;}""",
        """   try{await window.SWYRL_ENGINE_REVISIONS_486.recordLocal('asset-'+record.id,envelope(record));}
   catch(error){console.warn('§E local asset revision archive unavailable',error);}
   return true;
  }catch(error){status('Save failed: '+error.message,true);return false;}""",
        "local asset manual-save history")
    html=html[:asset_start]+block+html[asset_end:]

    # The asset picker is already context-aware and present in Model Studio;
    # only add commands in the same existing bar, not a floating duplicate.
    html=once(html,"  setInterval(refresh,1500);\n  refresh();",
              "  setInterval(refresh,1500);\n  se486InstallAssetActions(bar);\n  refresh();",
              "existing standalone asset actions")
    html=once(html," window.SWYRL_ENGINE_ASSET_LIBRARY=Object.freeze({",
              asset+"\n window.SWYRL_ENGINE_ASSET_LIBRARY=Object.freeze({",
              "studio asset version tools")

    # Version/build/source provenance must stay one coherent release.
    for old,new,tag in (
        ("SWYRL_ENGINE_DEPLOY_MARKER: V11_485_ONE_CLOTH_SORTING_HAT",MARKER,"marker"),
        ("ENGINE · MAKER v11.485","ENGINE · MAKER v11.486","visible header"),
        ("v11.485 · unified sculpted Sorting Hat",
         "v11.486 · rolling project revisions and in-place model updates","headline"),
        ("window.SWRLZ_FORGE_BUILD={version:'v11.485'",
         "window.SWRLZ_FORGE_BUILD={version:'v11.486'","runtime build"),
        ("<title>§wyrl§ Engine · Maker v11.485</title>",
         "<title>§wyrl§ Engine · Maker v11.486</title>","title")
    ):
        html=once(html,old,new,tag)
    prior=" source.engine='§wyrl§ Engine · Maker v11.485';source.version=11.485;"
    count=html.count(prior)
    if count!=5:raise AssertionError(("provenance v11.486",count))
    html=html.replace(prior," source.engine='§wyrl§ Engine · Maker v11.486';source.version=11.486;")
    key="const SE_RELEASE_NOTES="
    start=html.index(key)+len(key)
    notes,width=json.JSONDecoder().raw_decode(html[start:])
    notes["history"]=[n for n in notes.get("history",[]) if n.get("version")!="v11.485"]
    notes["history"].insert(0,{"version":"v11.485","changes":notes.get("changes",[])})
    notes.update(version="v11.486",date="2026-11-17",
      title="Eight rolling project revisions and in-place model updates",
      changes=[
        "Saved account projects and Model/Particle assets retain up to eight explicit revisions, including the current revision, inside the same account record.",
        "History is compressed and quota-aware; older revisions are pruned when necessary rather than failing or duplicating account projects.",
        "Every explicit device save also records a bounded history separate from ordinary autosave, without changing existing local project storage.",
        "History shows revisions and can restore one as the newest save; older data is not overwritten in place.",
        "Project/model update packages carry the exact local/account identity and base revision, rejecting wrong-project and stale uploads.",
        "Existing starter copies, project geometry, texture/UV data, native editor, cloud concurrency guards and VR workspace remain unchanged."
      ])
    return html[:start]+json.dumps(notes,ensure_ascii=False,separators=(",",":")).replace("</",r"<\/")+html[start+width:]
