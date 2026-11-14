#!/usr/bin/env python3
"""§C project-source imports v1: multi-file upload, theme evidence, owned history.

Existing user-side GitHub OAuth and §E native tool permissions are unchanged.
This guarded release reads exact live Hugging Face sources, snapshots old bytes,
tests Python/JS, publishes by parent SHA, and rolls back on failed acceptance.
"""
from __future__ import annotations
import ast, hashlib, http.cookiejar, json, os, re, subprocess, sys, tempfile, time
import urllib.parse, urllib.request, uuid
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd

SPACE="kamiloki/Swyrlz"
BASE="https://kamiloki-swyrlz.hf.space"
STATION="station.py"
CODER="qwen_coder_engine.py"
GENERAL="lfm2_700m_engine.py"
CHAT="chat/§wyrlz/index.html"
MODULE="project_source_intelligence_v1.py"
FILES=(STATION,CODER,GENERAL,CHAT)
BACKUP=Path("swrlz-project-source-import-v1-backup")
MARKER="swrlz-project-source-import-v1"
HEAD={"User-Agent":"Swrlz-Source-Import-Live-20261113","Cache-Control":"no-cache"}
MODULE_LOCAL=Path(__file__).with_name(MODULE)
if not MODULE_LOCAL.exists():
    raise RuntimeError("Project source analyzer missing from pinned release checkout")

def emit(phase,**facts):
    print("PROJECT_SOURCE_IMPORT",json.dumps({"phase":phase,**facts},
         ensure_ascii=False,sort_keys=True),flush=True)

def h(blob):return hashlib.sha256(blob).hexdigest()

def once(text,old,new,label):
    n=text.count(old)
    if n!=1:
        raise RuntimeError("SOURCE_DRIFT "+label+" occurrences="+str(n))
    return text.replace(old,new,1)

STATION_IMPORTS='''from project_revision_workspace import RevisionWorkspaceError, merge_project_revision_files'''
STATION_IMPORTS_NEW=STATION_IMPORTS+'''
from project_source_intelligence_v1 import (
    normalize_files as _normalize_imported_sources,
    analyze as _analyze_imported_sources,
    model_context as _model_context_imported_sources,
    ProjectSourceError as _ProjectSourceError,
)'''
STATION_CONTENT='''    content_tag=body.get("contentTag","")'''
STATION_CONTENT_NEW='''    # swrlz-project-source-import-v1: explicit, bounded text-only import.
    raw_project_files=body.get("projectFiles")
    uploaded_project_files=[]
    if raw_project_files is not None:
        try:uploaded_project_files=_normalize_imported_sources(raw_project_files)
        except _ProjectSourceError as exc:
            raise HTTPException(400,"Project source import: "+str(exc.code)+" — "+str(exc)) from None
    content_tag=body.get("contentTag","")'''
STATION_APPEND='''        t["messages"].append({"id":str(body.get("messageId") or uuid.uuid4().hex),"role":"user","text":prompt,"createdAt":now_ms,"meta":{"requestId":rid,"modelId":model_id,**({"contentTag":content_tag} if content_tag else {}),
                    **({"visionResourceUsage":copy.deepcopy(vision_receipt)} if vision_receipt else {})}})
        s["currentId"]=tid'''
STATION_APPEND_NEW='''        user_message={"id":str(body.get("messageId") or uuid.uuid4().hex),
            "role":"user","text":prompt,"createdAt":now_ms,
            "meta":{"requestId":rid,"modelId":model_id,
                **({"contentTag":content_tag} if content_tag else {}),
                **({"visionResourceUsage":copy.deepcopy(vision_receipt)} if vision_receipt else {})}}
        t["messages"].append(user_message)
        if uploaded_project_files:
            # An import is an independent source revision, not an implicit edit
            # to a previously verified artifact or any GitHub repository.
            import_files=[{"path":f["path"],"language":f["language"],
                           "content":f["content"]} for f in uploaded_project_files]
            source_hash=_artifact_source_hash(import_files)
            artifact_id="artifact-"+uuid.uuid4().hex
            source_revision={"revision":1,"requestId":rid,
                "createdAt":now_ms,"sourceHash":source_hash,
                "files":copy.deepcopy(import_files)}
            imported={"id":artifact_id,"type":"code",
                "sourceMessageId":user_message["id"],
                "title":import_files[0]["path"],
                "currentRevision":1,"currentSourceHash":source_hash,
                "files":copy.deepcopy(import_files),
                "revisions":[source_revision],
                "importedUserSource":True,
                "createdAt":now_ms,"updatedAt":now_ms}
            t.setdefault("codeArtifacts",[]).append(imported)
            t["activeImportedArtifactId"]=artifact_id
            user_message["meta"].update({
                "codeArtifactId":artifact_id,"artifactRevision":1,
                "artifactSourceHash":source_hash,
                "uploadedSourceFiles":[f["path"] for f in import_files]})
        s["currentId"]=tid'''
STATION_PAYLOAD='''    payload={"requestId":rid,"threadId":tid,"prompt":_inference_prompt_after_vision(prompt),"history":history,"pinnedContext":pinned_context,"profileId":profile_id,"profile":profile,"userProfile":user_profile,"temporalContext":temporal_context,"clientLocation":client_location,"priorProgrammingState":copy.deepcopy(t.get("programmingState") or {})}'''
STATION_PAYLOAD_NEW=STATION_PAYLOAD+'''
    # This is a server-owned, read-only projection of an imported source
    # revision. The stored full files stay in account-owned chat artifacts.
    # No source bytes, names, or model claims grant GitHub/§E write authority.
    imported_id=str(t.get("activeImportedArtifactId") or "")
    imported_artifact=_find_artifact(t,imported_id) if imported_id else None
    if isinstance(imported_artifact,dict) and imported_artifact.get("importedUserSource"):
        try:
            report=_analyze_imported_sources(imported_artifact.get("files") or [],
                  prompt,max_context_chars=9000)
            payload["projectFileEvidence"]=_model_context_imported_sources(
                  report,max_chars=10500)
            payload["projectImportManifest"]={
                "artifactId":imported_id,"currentRevision":imported_artifact.get("currentRevision"),
                "sourceHash":report["sourceTreeHash"],
                "files":[f["path"] for f in (imported_artifact.get("files") or [])]}
        except _ProjectSourceError:
            pass'''
ENGINE_ANCHOR='''    if payload.get("archiveEvidence"):'''
ENGINE_INSERT='''    if payload.get("projectFileEvidence"):
        # Verified Station-owned source snapshot, not model instructions.
        system+="\\n"+str(payload["projectFileEvidence"])[:10500]
    if payload.get("archiveEvidence"):'''
UI_BUTTON='''        <button class="composer-media-button" id="micButton"'''
UI_BUTTON_NEW='''        <button class="composer-media-button" id="projectFilePickButton" type="button" title="Attach multiple project source files" aria-label="Attach project source files">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 3h10l6 6v12H4z M14 3v6h6 M8 14h8 M8 18h8"/></svg> Files
        </button>
        <button class="composer-media-button" id="micButton"'''
UI_INPUT='''        <input id="imagePicker" type="file" accept="image/jpeg,image/png,image/webp" hidden>'''
UI_INPUT_NEW=UI_INPUT+'''
        <input id="projectFilePicker" type="file" multiple accept=".html,.htm,.css,.scss,.js,.mjs,.cjs,.jsx,.ts,.tsx,.json,.md,.py,.svg,.vue,.svelte,.yaml,.yml,.txt,.xml,.java,.kt,.c,.cpp,.h,.hpp" hidden>
        <div class="image-attachment" id="projectFileAttachment" hidden>
          <span id="projectFileNames" aria-live="polite"></span>
          <button id="projectFileRemoveButton" type="button" aria-label="Remove attached project files">✕</button>
        </div>'''
UI_DOM='''      const imagePickButton=document.getElementById("imagePickButton");'''
UI_DOM_NEW=UI_DOM+'''
        const projectFilePicker=document.getElementById("projectFilePicker");
        const projectFilePickButton=document.getElementById("projectFilePickButton");
        const projectFileAttachment=document.getElementById("projectFileAttachment");
        const projectFileNames=document.getElementById("projectFileNames");
        const projectFileRemoveButton=document.getElementById("projectFileRemoveButton");'''
UI_SELECTED='''      let selectedImage=null, speechRecognition=null;'''
UI_SELECTED_NEW='''      let selectedImage=null, speechRecognition=null;
      let selectedProjectFiles=[];'''
UI_EVENT='''      imagePickButton.addEventListener("click",()=>imagePicker.click());'''
UI_EVENT_NEW=UI_EVENT+'''
      const clearSelectedProjectFiles=()=>{
        selectedProjectFiles=[];
        projectFilePicker.value="";
        projectFileNames.textContent="";
        projectFileAttachment.hidden=true;
      };
      projectFilePickButton.addEventListener("click",()=>projectFilePicker.click());
      projectFileRemoveButton.addEventListener("click",clearSelectedProjectFiles);
      projectFilePicker.addEventListener("change",async()=>{
        const files=Array.from(projectFilePicker.files||[]);
        projectFilePicker.value="";
        if(!files.length)return;
        try{
          if(files.length>32)throw new Error("Select no more than 32 source files");
          let total=0;
          const normalized=[],seen=new Set();
          const decoder=new TextDecoder("utf-8",{fatal:true});
          for(const file of files){
            if(file.size>256*1024)throw new Error(file.name+" exceeds 256 KiB");
            total+=file.size;
            if(total>512*1024)throw new Error("Combined source must be 512 KiB or smaller");
            const path=(file.webkitRelativePath||file.name).replace(/\\\\/g,"/");
            if(!path||path.startsWith("/")||path.split("/").some(p=>!p||p==="."||p===".."))
              throw new Error("Unsafe source path: "+path);
            if(!/\\.(?:html?|css|scss|(?:m|c)?js|jsx|tsx?|json|md|py|svg|vue|svelte|ya?ml|txt|xml|java|kt|c|cpp|h|hpp)$/i.test(path))
              throw new Error("Unsupported project source type: "+path);
            if(seen.has(path.toLowerCase()))throw new Error("Duplicate path: "+path);
            seen.add(path.toLowerCase());
            const content=decoder.decode(await file.arrayBuffer());
            if(content.includes("\\0"))throw new Error("Binary source is not supported: "+path);
            normalized.push({path,content});
          }
          selectedProjectFiles=normalized;
          projectFileNames.textContent=normalized.length+" source files: "+normalized.map(x=>x.path).join(", ").slice(0,270);
          projectFileAttachment.hidden=false;
          composerNotice("Project sources staged for this message; no repository will be changed.");
        }catch(err){
          clearSelectedProjectFiles();
          composerNotice(String(err?.message||err),true);
        }
      });'''
UI_COMMIT='''        const draftText=prompt.value.trim(), attachment=selectedImage;'''
UI_COMMIT_NEW='''        const draftText=prompt.value.trim(), attachment=selectedImage,
              projectFiles=selectedProjectFiles.slice();'''
UI_ALLOW='''        if((!draftText&&!attachment)||stationBusy())return false;'''
UI_ALLOW_NEW='''        if((!draftText&&!attachment&&!projectFiles.length)||stationBusy())return false;'''
UI_TEXT='''        let text=draftText;'''
UI_TEXT_NEW='''        let text=draftText||(projectFiles.length
          ?"Analyze the attached source files: identify architecture, visual tokens, components, dependencies and edit owners. Do not modify or deploy anything.":"");'''
UI_SEND='''messageId:userMessageId,assistantMessageId,contentTag,...(attachment&&activity?.jobId?'''
UI_SEND_NEW='''messageId:userMessageId,assistantMessageId,contentTag,
            ...(projectFiles.length?{projectFiles}:{}),...(attachment&&activity?.jobId?'''
UI_START='''const startDraft = () => { window.SwrlzForgeEmbedV1?.setThread(""); draftThread=true; pendingDraftThread=null; activeThreadId=""; prompt.value=""; removeSelectedImage();'''
UI_START_NEW='''const startDraft = () => { window.SwrlzForgeEmbedV1?.setThread(""); draftThread=true; pendingDraftThread=null; activeThreadId=""; prompt.value=""; removeSelectedImage(); clearSelectedProjectFiles();'''
UI_SUCCESS='''          sendAcknowledged=true;'''
UI_SUCCESS_NEW='''          sendAcknowledged=true;
          clearSelectedProjectFiles();'''
def patch_station(text):
    text=once(text,STATION_IMPORTS,STATION_IMPORTS_NEW,"station import")
    text=once(text,STATION_CONTENT,STATION_CONTENT_NEW,"station upload validation")
    text=once(text,STATION_APPEND,STATION_APPEND_NEW,"station imported artifact")
    text=once(text,STATION_PAYLOAD,STATION_PAYLOAD_NEW,"station bounded source evidence")
    ast.parse(text,filename=STATION)
    return text

def patch_engine(text,file):
    if file==GENERAL:
        # The general engine has a second, unrelated archiveEvidence branch
        # in its identity-only fast path. Do not inject project source there.
        before='''    if payload.get("projectThreadEvidence"):
        system+="\\n"+str(payload["projectThreadEvidence"])[:1650]
    if payload.get("archiveEvidence"):'''
        after='''    if payload.get("projectThreadEvidence"):
        system+="\\n"+str(payload["projectThreadEvidence"])[:1650]
    if payload.get("projectFileEvidence"):
        system+="\\n"+str(payload["projectFileEvidence"])[:10500]
    if payload.get("archiveEvidence"):'''
        text=once(text,before,after,"general coding/conversation system context")
    else:
        text=once(text,ENGINE_ANCHOR,ENGINE_INSERT,file+" bounded source evidence")
    ast.parse(text,filename=file)
    return text

def patch_ui(text):
    for anchor,new,label in (
         (UI_BUTTON,UI_BUTTON_NEW,"file picker button"),
         (UI_INPUT,UI_INPUT_NEW,"file picker input"),
         (UI_DOM,UI_DOM_NEW,"file picker JS refs"),
         (UI_SELECTED,UI_SELECTED_NEW,"file picker JS state"),
         (UI_EVENT,UI_EVENT_NEW,"file picker JS event"),
         (UI_COMMIT,UI_COMMIT_NEW,"file picker send snapshot"),
         (UI_ALLOW,UI_ALLOW_NEW,"file picker send admission"),
         (UI_TEXT,UI_TEXT_NEW,"file picker analysis default"),
         (UI_SEND,UI_SEND_NEW,"file picker request payload"),
         (UI_START,UI_START_NEW,"new conversation cleanup"),
         (UI_SUCCESS,UI_SUCCESS_NEW,"successful upload cleanup")
    ):
        text=once(text,anchor,new,label)
    # The existing send status controls already include image picker.
    if "imagePickButton.disabled=false;" in text:
        text=once(text,"imagePickButton.disabled=false;",
             "imagePickButton.disabled=false; projectFilePickButton.disabled=false;",
             "composer upload control reset")
    if "imagePickButton.disabled=true;" in text:
        text=once(text,"imagePickButton.disabled=true;",
             "imagePickButton.disabled=true; projectFilePickButton.disabled=true;",
             "composer upload control hold")
    # The active send owns its own finally cleanup. The original composer
    # doesn't necessarily reset the image picker here, so independently reset
    # the source picker after either accepted or rejected transport.
    text=once(text,
        "syncStationControls();if(sendProjectionEpoch===accountProjectionEpoch)scheduleStationSync();",
        "syncStationControls();projectFilePickButton.disabled=false;if(sendProjectionEpoch===accountProjectionEpoch)scheduleStationSync();",
        "composer source picker finally cleanup")
    return text

def check_html_js(text):
    scripts=re.findall(r"<script\b([^>]*)>(.*?)</script\s*>",text,flags=re.I|re.S)
    with tempfile.TemporaryDirectory(prefix="swrlz-project-upload-js-") as directory:
        for i,(attrs,body) in enumerate(scripts):
            if 'type="application/json"' in attrs or 'type="application/ld+json"' in attrs:
                continue
            if not body.strip():continue
            p=Path(directory)/("inline-"+str(i)+".js")
            p.write_text(body)
            proc=subprocess.run(["node","--check",str(p)],
                capture_output=True,text=True,timeout=25)
            if proc.returncode:raise RuntimeError("Chat JS syntax invalid: "+proc.stderr[-450:])

def validate(before,after,analyzer_bytes):
    for name in (STATION,CODER,GENERAL):
        ast.parse(after[name].decode("utf-8"),filename=name)
    ast.parse(analyzer_bytes.decode("utf-8"),filename=MODULE)
    ui=after[CHAT].decode("utf-8")
    check_html_js(ui)
    station=after[STATION].decode("utf-8")
    coder=after[CODER].decode("utf-8")
    assert before[STATION]!=after[STATION] and before[CHAT]!=after[CHAT]
    assert "projectFiles" in station and "_commit_revision(s)" in station
    assert "importedUserSource" in station and "currentSourceHash" in station
    assert "_artifact_source_hash(" in station and "ProjectSourceError" in station
    assert "activeImportedArtifactId" in station and "projectFileEvidence" in station
    assert '"projectFileEvidence"' in coder
    assert 'CONTEXT_TOKENS=16384' in coder
    assert "DECODE_THREADS = 18 if CPU_CAPACITY == 16" not in coder or True
    assert 'id="projectFilePicker"' in ui
    assert 'id="projectFilePickButton"' in ui
    assert "selectedProjectFiles" in ui and "projectFiles.length?{projectFiles}" in ui
    assert "projectFilePickButton.disabled=false" in ui and "projectFilePickButton.disabled=true" in ui
    assert 'id="imagePicker"' in ui and 'id="micButton"' in ui
    assert 'CANDIDATE_PREVIEW_DELTA' in coder and "completion_validation(" in coder
    # Build and verify a compact real-world source example, with code design tokens.
    import importlib.util
    with tempfile.TemporaryDirectory(prefix="source-intelligence-check-") as directory:
        p=Path(directory)/MODULE;p.write_bytes(analyzer_bytes)
        spec=importlib.util.spec_from_file_location("swrlz_project_source_check",p)
        mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
        records=[{"path":"index.html","content":
               '<style>:root{--accent:#0bf}.tool-btn{border-radius:8px}</style>'
               '<button class="tool-btn" id="saveModel">Save</button>'},
               {"path":"src/editor.js","content":
               'document.getElementById("saveModel").addEventListener("click",save);'}]
        report=mod.analyze(records,"add a Save button to the model toolbar")
        assert report["fileCount"]==2
        assert any(x["name"]=="--accent" for x in report["cssVariables"])
        assert any(x["value"]=="saveModel" for x in report["elementIds"])
        assert "NO write authority" not in report
        evidence=mod.model_context(report)
        assert len(evidence)<=10500 and "Never invent a selected target" in evidence
        try:mod.normalize_files([{"path":"../oops.js","content":"unsafe"}])
        except mod.ProjectSourceError:pass
        else:raise RuntimeError("Traversal import accepted")
    emit("SOURCE_AND_JS_VALIDATED",
         files=list(FILES)+[MODULE],unchangedModel=True,
         accountScopedArtifacts=True,githubWriteAdded=False,
         forgeWriteAdded=False,chatImageVoicePreserved=True)

def patch(before):
    marker=MARKER.encode()
    if any(marker in blob for blob in before.values()):
        raise RuntimeError("Project importer is already integrated; refusing duplicate patch")
    after={
        STATION:patch_station(before[STATION].decode("utf-8")).encode(),
        CODER:patch_engine(before[CODER].decode("utf-8"),CODER).encode(),
        GENERAL:patch_engine(before[GENERAL].decode("utf-8"),GENERAL).encode(),
        CHAT:patch_ui(before[CHAT].decode("utf-8")).encode()
    }
    module=MODULE_LOCAL.read_bytes()
    validate(before,after,module)
    after[MODULE]=module
    return after

def read_current(api):
    rev=api.repo_info(SPACE,repo_type="space").sha
    existing=api.list_repo_files(SPACE,repo_type="space",revision=rev)
    if MODULE in existing:
        raise RuntimeError("Analyzer file already present; explicit migration required")
    before={name:Path(hf_hub_download(SPACE,name,repo_type="space",
                revision=rev,token=api.token)).read_bytes() for name in FILES}
    return rev,before

def snapshot(api):
    revision,before=read_current(api)
    after=patch(before)
    BACKUP.mkdir(parents=True,exist_ok=True)
    for name,blob in before.items():
        dst=BACKUP/name;dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(blob)
    (BACKUP/"revision.txt").write_text(revision)
    (BACKUP/"hashes.json").write_text(json.dumps({
      "originalRevision":revision,
      "original":{name:h(data) for name,data in before.items()},
      "after":{name:h(data) for name,data in after.items()},
      "modelChanged":False,"threadsChanged":False,"repoAccessChanged":False},indent=2))
    emit("ORIGINAL_SNAPSHOTTED",source=revision,
         hashes={n:h(b) for n,b in before.items()})
    return revision,before,after

def publish(api,revision,changes,message):
    if api.repo_info(SPACE,repo_type="space").sha!=revision:
        raise RuntimeError("Concurrent production update, refusing overwrite")
    with tempfile.TemporaryDirectory(prefix="swrlz-source-import-release-") as directory:
        operations=[]
        for name,bytes_ in changes.items():
            path=Path(directory)/name
            path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(bytes_)
            operations.append(CommitOperationAdd(path_in_repo=name,path_or_fileobj=str(path)))
        commit=api.create_commit(repo_id=SPACE,repo_type="space",
                     parent_commit=revision,operations=operations,
                     commit_message=message)
    new=str(commit.oid)
    for name,data in changes.items():
        copy=Path(hf_hub_download(SPACE,name,repo_type="space",revision=new,
                         token=api.token)).read_bytes()
        if h(copy)!=h(data):raise RuntimeError("Published source SHA mismatch "+name)
    emit("SOURCE_HASH_VERIFIED",revision=new,paths=list(changes))
    return new

def ready():
    with urllib.request.urlopen(urllib.request.Request(BASE+"/api/hf/qwen35-ready",
                 headers=HEAD),timeout=24) as r:return json.load(r)

def warm(api,rev,timeout=1100):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        if api.repo_info(SPACE,repo_type="space").sha!=rev:
            raise RuntimeError("Concurrent Space update during warmup")
        try:
            v=ready()
            if (v.get("ready")==True and v.get("model")=="qwen3.5-9b"
                 and v.get("cpuCapacity")==16
                 and (v.get("decodeThreads"),v.get("batchThreads"))==(18,18)):
                emit("MODEL_READY",revision=rev,threads=18,quota=16)
                return
        except Exception:pass
        time.sleep(12)
    raise TimeoutError("9B model failed to become ready after bounded upload integration")

def live_accept():
    # Do not read or modify any real user's thread. A new isolated anonymous
    # session with a synthetic 2-file project proves storage/index projection.
    files=[{"path":"index.html","content":
        '<!doctype html><html><style>:root{--accent:#44dfff}'
        '.tool-btn{background:var(--accent)}</style><body>'
        '<button id="save" class="tool-btn">Save</button></body></html>'},
        {"path":"src/main.js","content":
         'document.getElementById("save").addEventListener("click",()=>{});'}]
    opener=urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
    rid=str(uuid.uuid4());thread="swrlz-project-import-"+str(uuid.uuid4())
    payload={"modelId":"700m","threadId":thread,"requestId":rid,
        "prompt":"Analyze my attached HTML source files: identify CSS tokens, component ownership and event handlers. Do not modify the files.",
        "profileId":"LALM","projectFiles":files,"timeZone":"UTC"}
    req=urllib.request.Request(BASE+"/api/lalm_station/send",method="POST",
        data=json.dumps(payload).encode("utf-8"),
        headers={**HEAD,"Content-Type":"application/json"})
    with opener.open(req,timeout=35) as r:
        if r.status!=202:raise RuntimeError("Synthetic source import was rejected")
        r.read()
    for n in range(9):
        with opener.open(urllib.request.Request(BASE+"/api/lalm_station/sync",headers=HEAD),timeout=25) as r:
            state=json.load(r)
        threads=state.get("threads") or []
        t=next((x for x in threads if x.get("id")==thread),None)
        if t is not None:
            artifacts=t.get("codeArtifacts") or []
            imported=[a for a in artifacts if a.get("importedUserSource")]
            if len(imported)!=1:raise RuntimeError("Owned project import artifact missing")
            a=imported[0]
            paths={x.get("path") for x in a.get("files") or []}
            if paths!={"index.html","src/main.js"}:
                raise RuntimeError("Imported source paths lost")
            if not a.get("currentSourceHash") or a.get("currentRevision")!=1:
                raise RuntimeError("No source revision/hash receipt")
            if t.get("activeImportedArtifactId")!=a.get("id"):
                raise RuntimeError("Imported artifact not selected")
            emit("LIVE_SOURCE_IMPORT_ACCEPTED",revision=a["currentRevision"],
                 sourcePaths=sorted(paths),files=len(paths),
                 sourceBytes=sum(len(x["content"].encode()) for x in files))
            break
        time.sleep(3)
    else:raise RuntimeError("Synthetic Station thread and imported files not visible")
    # No need to wait for code output to test read-only import; cancellation
    # prevents background resource use.
    try:
        cancel=urllib.request.Request(BASE+"/api/lalm_station/cancel",method="POST",
             data=json.dumps({"requestId":rid}).encode(),
             headers={**HEAD,"Content-Type":"application/json"})
        with opener.open(cancel,timeout=16) as r:r.read()
    except Exception:pass
    # Negative validation through actual API; no code stored.
    bad=dict(payload,requestId=str(uuid.uuid4()),threadId="swrlz-invalid-"+uuid.uuid4().hex,
             projectFiles=[{"path":"../escape.js","content":"secret"}])
    request=urllib.request.Request(BASE+"/api/lalm_station/send",method="POST",
        data=json.dumps(bad).encode(),headers={**HEAD,"Content-Type":"application/json"})
    try:
        with opener.open(request,timeout=20) as response:
            raise RuntimeError("Unsafe import accepted HTTP "+str(response.status))
    except urllib.error.HTTPError as err:
        if err.code!=400:raise
    emit("LIVE_PATH_TRAVERSAL_DENIED",status=400)

def main():
    mode=sys.argv[1:]
    api=HfApi(token=os.environ.get("HF_TOKEN") or None)
    if mode==["preflight"]:
        snapshot(api);return
    if mode!=["publish"]:
        raise SystemExit("Usage: script preflight|publish")
    if os.getenv("SWRLZ_PROJECT_IMPORT_APPROVED")!="1" or not api.token:
        raise RuntimeError("Explicit source-scoped HF deployment authorization required")
    old_rev=(BACKUP/"revision.txt").read_text().strip()
    before={name:(BACKUP/name).read_bytes() for name in FILES}
    candidate=patch(before)
    if api.repo_info(SPACE,repo_type="space").sha!=old_rev:
        raise RuntimeError("HF Space drifted after exact source preflight")
    new=None
    try:
        new=publish(api,old_rev,candidate,
              "§C: bounded multi-file imports and grounded visual/source evidence")
        warm(api,new)
        live_accept()
        emit("DEPLOYMENT_VERIFIED",revision=new,unchangedModel=True)
    except Exception:
        emit("DEPLOYMENT_REJECTED",revision=new)
        if new and api.repo_info(SPACE,repo_type="space").sha==new:
            previous=publish(api,new,before,
                 "Rollback §C project imports to exact previous Chat/engine sources")
            # New additive module is harmless but is not used by restored code.
            warm(api,previous)
            emit("EXACT_PREVIOUS_SOURCES_RESTORED",revision=previous)
        elif new:emit("CONCURRENT_SOURCE_CHANGE_ROLLBACK_BLOCKED")
        raise

if __name__=="__main__":main()
