"""Bounded atomic staged source projects across completed Chat turns.

Never executes source or writes to disk. A manifest is a model proposal, NOT
evidence of correctness or of the complete user-intent requirements.
"""
from __future__ import annotations
import copy
import hashlib
import json
import re
from typing import Any
from code_packages import MAX_FILE_BYTES, MAX_FILES, MAX_TOTAL_BYTES, PackageError, build_package, safe_relative_path

SCHEMA="swrlz-staged-project-v1"
MANIFEST_SCHEMA="swrlz-project-manifest-v1"
_MANIFEST_FENCE=re.compile(r"\x60{3}project-manifest[ \t]*\n([\s\S]*?)\x60{3}",re.I)

class WorkspaceError(ValueError):
    """Invalid or conflicting staged project state."""

def _sha(value: str)->str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def _declared_paths(paths: Any)->list[str]:
    if not isinstance(paths,list) or not 2<=len(paths)<=MAX_FILES:
        raise WorkspaceError("A staged project requires 2..32 declared paths")
    seen=set()
    result=[]
    for item in paths:
        try: path=safe_relative_path(item)
        except PackageError as exc: raise WorkspaceError("Invalid required path") from exc
        if path.casefold() in seen: raise WorkspaceError("Duplicate required path")
        seen.add(path.casefold())
        result.append(path)
    for key in seen:
        if any(other!=key and other.startswith(key+"/") for other in seen):
            raise WorkspaceError("File and directory name collision")
    return result

def parse_manifest(response: str)->dict|None:
    matches=list(_MANIFEST_FENCE.finditer(str(response or "")))
    if not matches:return None
    if len(matches)!=1:raise WorkspaceError("Only one project manifest allowed")
    raw=matches[0].group(1)
    if len(raw.encode("utf-8"))>6000:raise WorkspaceError("Manifest too large")
    try: value=json.loads(raw)
    except (ValueError,TypeError) as exc:raise WorkspaceError("Invalid manifest JSON") from exc
    if not isinstance(value,dict) or value.get("schema")!=MANIFEST_SCHEMA:
        raise WorkspaceError("Invalid manifest schema")
    name=value.get("name","project-files")
    if not isinstance(name,str) or not 1<=len(name)<=80 or not re.fullmatch(r"[A-Za-z0-9_.() -]+",name):
        raise WorkspaceError("Invalid project name")
    return {"schema":MANIFEST_SCHEMA,"name":name,"files":_declared_paths(value.get("files"))}

def create_workspace(manifest:dict,workspace_id:str,request_id:str)->dict:
    if not isinstance(manifest,dict) or manifest.get("schema")!=MANIFEST_SCHEMA:
        raise WorkspaceError("Missing typed manifest")
    paths=_declared_paths(manifest.get("files"))
    name=manifest.get("name")
    if not isinstance(name,str) or not 1<=len(name)<=80 or not re.fullmatch(r"[A-Za-z0-9_.() -]+",name):
        raise WorkspaceError("Invalid project name")
    if not isinstance(workspace_id,str) or not re.fullmatch(r"workspace-[a-f0-9]{32}",workspace_id):
        raise WorkspaceError("Invalid workspace id")
    if not isinstance(request_id,str) or not 1<=len(request_id)<=160:
        raise WorkspaceError("Invalid source request")
    body={"schema":MANIFEST_SCHEMA,"name":name,"files":paths}
    return {"schema":SCHEMA,"id":workspace_id,"name":name,"requiredFiles":paths,
        "manifestSha256":_sha(json.dumps(body,sort_keys=True,ensure_ascii=False)),
        "originRequestId":request_id,"lastRequestId":request_id,
        "entries":[],"revision":1,"state":"BUILDING","completion":"INCOMPLETE",
        "verification":"NOT_RUN","canDownload":False,"missingFiles":list(paths),"fileCount":0}

def stage_files(workspace:dict,files:list[dict],*,expected_revision:int,request_id:str,
                artifact_id:str,artifact_revision:int,artifact_source_hash:str,
                allow_replace:bool=False)->tuple[dict,str]:
    """Atomic compare-and-swap; rejects unexpected paths and implicit overwrite."""
    if not isinstance(workspace,dict) or workspace.get("schema")!=SCHEMA:
        raise WorkspaceError("Invalid workspace")
    if not isinstance(expected_revision,int) or isinstance(expected_revision,bool) or expected_revision!=workspace.get("revision"):
        raise WorkspaceError("WORKSPACE_REVISION_CONFLICT")
    if not (isinstance(request_id,str) and 1<=len(request_id)<=160 and
            isinstance(artifact_id,str) and 1<=len(artifact_id)<=160 and
            isinstance(artifact_revision,int) and not isinstance(artifact_revision,bool) and artifact_revision>0 and
            isinstance(artifact_source_hash,str) and re.fullmatch(r"[0-9a-f]{64}",artifact_source_hash)):
        raise WorkspaceError("Missing artifact provenance")
    if not isinstance(files,list) or not 1<=len(files)<=MAX_FILES:
        raise WorkspaceError("No source files to stage")
    required=set(_declared_paths(workspace.get("requiredFiles")))
    incoming={}
    for candidate in files:
        if not isinstance(candidate,dict) or not isinstance(candidate.get("content"),str):
            raise WorkspaceError("Incomplete source file")
        try:path=safe_relative_path(candidate.get("path"))
        except PackageError as exc:raise WorkspaceError("Unsafe source path") from exc
        if path not in required:raise WorkspaceError("UNDECLARED_PROJECT_FILE")
        if path in incoming:raise WorkspaceError("DUPLICATE_PROJECT_FILE")
        content=candidate["content"]
        if not content or len(content.encode("utf-8"))>MAX_FILE_BYTES:
            raise WorkspaceError("Empty or oversized source file")
        incoming[path]={"path":path,"language":str(candidate.get("language") or "text")[:40],
            "content":content,"sha256":_sha(content),
            "sourceRequestId":request_id,"sourceArtifactId":artifact_id,
            "sourceArtifactRevision":artifact_revision,"sourceArtifactHash":artifact_source_hash}
    prior={x["path"]:x for x in workspace.get("entries",[])}
    candidate_entries=copy.deepcopy(prior)
    changed=False
    for path,item in incoming.items():
        old=prior.get(path)
        if old and old["sha256"]!=item["sha256"] and not allow_replace:
            raise WorkspaceError("EXISTING_FILE_CHANGE_REQUIRES_EXPLICIT_EDIT")
        if old and old["sha256"]==item["sha256"]:continue
        candidate_entries[path]=item
        changed=True
    if not changed:return copy.deepcopy(workspace),"UNCHANGED"
    if sum(len(x["content"].encode("utf-8")) for x in candidate_entries.values())>MAX_TOTAL_BYTES:
        raise WorkspaceError("Project size limit exceeded")
    try:build_package([{"path":x["path"],"content":x["content"]} for x in candidate_entries.values()],force_archive=True)
    except PackageError as exc:raise WorkspaceError("Invalid project package") from exc
    result=copy.deepcopy(workspace)
    result["entries"]=sorted(candidate_entries.values(),key=lambda x:x["path"])
    result["revision"]=expected_revision+1
    result["lastRequestId"]=request_id
    result["fileCount"]=len(result["entries"])
    result["missingFiles"]=[p for p in result["requiredFiles"] if p not in candidate_entries]
    result["canDownload"]=not result["missingFiles"]
    result["completion"]="FILES_PRESENT_UNVERIFIED" if result["canDownload"] else "INCOMPLETE"
    result["state"]="FILES_PRESENT" if result["canDownload"] else "BUILDING"
    result["verification"]="NOT_RUN"
    return result,"COMMITTED"

def project_view(workspace:dict)->dict:
    return {"schema":SCHEMA,"id":workspace.get("id"),"name":workspace.get("name"),
        "revision":workspace.get("revision"),"manifestSha256":workspace.get("manifestSha256"),
        "requiredFiles":list(workspace.get("requiredFiles",[])),
        "savedFiles":[{"path":x["path"],"sha256":x["sha256"]} for x in workspace.get("entries",[])],
        "missingFiles":list(workspace.get("missingFiles",[])),"state":workspace.get("state"),
        "completion":workspace.get("completion"),"verification":workspace.get("verification"),
        "canDownload":bool(workspace.get("canDownload")),
        "fileCount":int(workspace.get("fileCount") or 0)}

def package_project(workspace:dict)->dict:
    if not isinstance(workspace,dict) or workspace.get("schema")!=SCHEMA:
        raise WorkspaceError("Invalid project")
    required=set(_declared_paths(workspace.get("requiredFiles")))
    files=workspace.get("entries") or []
    if not workspace.get("canDownload") or len(files)!=len(required) or {x.get("path") for x in files}!=required:
        raise WorkspaceError("PROJECT_FILES_INCOMPLETE")
    for item in files:
        if not isinstance(item.get("content"),str) or item.get("sha256")!=_sha(item["content"]):
            raise WorkspaceError("PROJECT_FILE_HASH_MISMATCH")
    try:return build_package([{"path":x["path"],"content":x["content"]} for x in files],force_archive=True)
    except PackageError as exc:raise WorkspaceError("Invalid project package") from exc
