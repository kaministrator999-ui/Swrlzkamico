#!/usr/bin/env python3
"""Source-pinned §C dedicated repair grammar and real model smoke release."""
from __future__ import annotations
import argparse, ast, hashlib, io, json, os, time, urllib.request
from pathlib import Path

SPACE = "kamiloki/Swyrlz"
BASE = "https://kamiloki-swyrlz.hf.space"
CHECK = "/api/html-project-agent-v10/runtime-check"
AGENT = "html_project_agent_v1.py"
RUNTIME = "html_project_agent_runtime_v1.py"
CODER = "qwen_coder_engine.py"
STATION = "station.py"
LOCAL = {AGENT:Path("api")/AGENT, RUNTIME:Path("api")/RUNTIME}
PINS = {AGENT:"1fd489983ed8f8ae29a6d7363d43af403d32fa34",
        RUNTIME:"28ed1887166d4e04cdc57e20340e43e7ea94127a"}
PROTOCOL = "swrlz-exact-patches-v10"
SCHEMA = {"type":"object","required":["patches"],"additionalProperties":False,
          "properties":{"patches":{"type":"array","minItems":1,"maxItems":12,
              "items":{"type":"object","required":["path","op","anchor","code"],
                       "additionalProperties":False,"properties":{
                           "path":{"type":"string"},"op":{"type":"string","enum":["insert_before","insert_after","replace_once","append"]},
                           "anchor":{"type":"string"},"code":{"type":"string"}}}},
                        "rationale":{"type":"string"}}}
MARKER = "# swrlz-repair-patch-grammar-v10"
PROBE_MARKER = "# swrlz-real-patch-probe-v10"
PROBE = '''
# swrlz-real-patch-probe-v10
import threading as _swrlz_patch_probe_threading
_swrlz_patch_probe_lock = _swrlz_patch_probe_threading.Lock()
_swrlz_patch_probe_receipt = None

@app.get("/api/html-project-agent-v10/runtime-check", include_in_schema=False)
def _swrlz_patch_protocol_v10_health():
    # Fixed, bounded, read-only fixture; no caller-supplied prompts, source,
    # credentials or authority. At most one model test per worker lifetime.
    global _swrlz_patch_probe_receipt
    if _swrlz_patch_probe_receipt is not None:
        return _swrlz_patch_probe_receipt
    if not _swrlz_patch_probe_lock.acquire(blocking=False):
        return {"schema":"swrlz-exact-patches-v10","state":"running"}
    try:
        if _swrlz_patch_probe_receipt is not None:
            return _swrlz_patch_probe_receipt
        active = _swrlz_verified_repair_runtime_v7()
        source = "<html><head><title>Probe</title></head><body><p>old</p></body></html>"
        files = {"index.html":source}
        failures = []
        for attempt in range(2):
            try:
                messages = active.prompt_messages(
                    "repair-grammar-probe",files,[],
                    "Change only the paragraph text from old to repaired. Preserve every other byte.",
                    prior_failures=failures)
                raw = active._model_patch(_coder_generate,{"modelId":"coder"},messages)
                bound = active.bind_model_edits("repair-grammar-probe",files,raw)
                result = active.apply_proposal("repair-grammar-probe",files,bound,
                                               validation=active.inspect_static)
                if result["proposedFiles"].get("index.html") != source.replace(">old<",">repaired<"):
                    raise ValueError("PROBE_WRONG_EDIT")
                _swrlz_patch_probe_receipt = {"schema":"swrlz-exact-patches-v10","state":"passed",
                    "realModel":True,"patchApplied":True,"attempts":attempt+1,
                    "committed":False,"deployed":False}
                return _swrlz_patch_probe_receipt
            except Exception as exc:
                failures.append(str(exc)[:180])
        _swrlz_patch_probe_receipt = {"schema":"swrlz-exact-patches-v10","state":"failed",
            "errors":failures,"committed":False,"deployed":False}
        return _swrlz_patch_probe_receipt
    finally:
        _swrlz_patch_probe_lock.release()


'''
def sha(raw):
    return hashlib.sha256(raw).hexdigest()
def blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+bytes([0])+raw).hexdigest()
def once(s,a,b):
    if s.count(a)!=1: raise RuntimeError("SOURCE_ANCHOR_DRIFT: "+a[:100])
    return s.replace(a,b,1)
def patch_coder(source):
    if MARKER in source:
        if source.count(MARKER)!=1 or PROTOCOL not in source:
            raise RuntimeError("PARTIAL_CODER_PATCH_PROTOCOL")
        ast.parse(source); return source
    tree=ast.parse(source)
    candidates=[n for n in ast.walk(tree) if isinstance(n,ast.Assign)
                and any(isinstance(t,ast.Name) and t.id=="source_format" for t in n.targets)
                and "source_change_response_format" in ast.get_source_segment(source,n)]
    if len(candidates)!=1: raise RuntimeError("LIVE_CODER_FORMAT_ANCHOR_DRIFT")
    n=candidates[0]; lines=source.splitlines(keepends=True)
    if "model.create_chat_completion" not in "".join(lines[n.end_lineno:n.end_lineno+4]):
        raise RuntimeError("LIVE_CODER_STREAM_ANCHOR_DRIFT")
    print("LIVE_CONFLICTING_GRAMMAR_SOURCE", ast.get_source_segment(source,n),flush=True)
    indent=" "*n.col_offset
    extension=(indent+MARKER+"\n"+indent+'if payload.get("repairPatchProtocol") == '+repr(PROTOCOL)+":\n"+
               indent+"    source_format = "+repr({"response_format":{"type":"json_object","schema":SCHEMA}})+"\n")
    lines.insert(n.end_lineno,extension)
    out="".join(lines); ast.parse(out); return out
def patch_station(source):
    if PROBE_MARKER in source:
        if source.count(PROBE_MARKER)!=1 or source.count(CHECK)!=1: raise RuntimeError("PARTIAL_PROBE")
        ast.parse(source); return source
    if "/api/html-project-agent-v9/runtime-check" not in source: raise RuntimeError("LIVE_V9_REQUIRED")
    source=once(source,'                and callable(run)\n',
        '                and "repairPatchProtocol" in active._model_patch.__code__.co_consts\n'
        '                and callable(run)\n')
    out=once(source,"def _swrlz_execute_model_repair_v7(",PROBE+"def _swrlz_execute_model_repair_v7(")
    ast.parse(out);return out
def selftest():
    fixture='def generate(payload, model, messages, response_tokens, temperature, source_change_mode):\n    source_format = ({"response_format": source_change_response_format(source_change_mode, payload.get("sourceChangeIdentity"))} if source_change_mode else {})\n    for chunk in model.create_chat_completion(messages=messages,max_tokens=response_tokens,temperature=temperature,stream=True,**source_format):\n        yield chunk\n'
    code=patch_coder(fixture)
    assert patch_coder(code)==code
    class Model:
        def create_chat_completion(self,**kwargs):
            yield kwargs
    ns={"source_change_response_format":lambda *a:{"type":"old"}}
    exec(code,ns)
    assert next(ns["generate"]({"repairPatchProtocol":PROTOCOL},Model(),[],10,0,False))["response_format"]["schema"]==SCHEMA
    assert next(ns["generate"]({},Model(),[],10,0,True))["response_format"]=={"type":"old"}
    station='def probe():\n    return (True\n                and callable(run)\n            )\n# /api/html-project-agent-v9/runtime-check\ndef _swrlz_execute_model_repair_v7():\n    pass\n'
    assert patch_station(patch_station(station))==patch_station(station)
    print("PATCH_PROTOCOL_V10_SELFTEST_PASS",flush=True)
def live_check():
    with urllib.request.urlopen(urllib.request.Request(BASE+CHECK,headers={"Cache-Control":"no-cache"}),timeout=360) as r:
        receipt=json.load(r)
    print("PATCH_PROTOCOL_V10_LIVE_RECEIPT",json.dumps(receipt),flush=True)
    if receipt.get("state")=="failed":
        raise ValueError("REAL_MODEL_REPAIR_FAILED: "+repr(receipt))
    if not (receipt.get("schema")==PROTOCOL and receipt.get("state")=="passed"
            and receipt.get("realModel") is True and receipt.get("patchApplied") is True
            and receipt.get("committed") is False and receipt.get("deployed") is False):
        raise RuntimeError("REAL_MODEL_PROBE_NOT_READY")
def release(mode):
    selftest()
    if mode=="selftest": return
    from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
    token=os.getenv("HF_TOKEN") or None; api=HfApi(token=token)
    rev=str(api.repo_info(SPACE,repo_type="space").sha)
    def read(name,revision):
        return Path(hf_hub_download(SPACE,name,repo_type="space",revision=revision,token=token)).read_bytes()
    original={n:read(n,rev) for n in (AGENT,RUNTIME,CODER,STATION)}
    candidate={n:p.read_bytes() for n,p in LOCAL.items()}
    if mode=="preflight" and b"from html_project_dependency_tool_v1 import" in candidate[AGENT]:
        if b"repairPatchProtocol" not in original[RUNTIME] or b"bind_model_edits" not in original[AGENT]:
            raise RuntimeError("LIVE_V10_SOURCE_DRIFT")
        print("V10_NEWER_DEPENDENCY_TOOL_PREFLIGHT",rev,flush=True);return
    for n in LOCAL:
        if original[n]!=candidate[n] and blob(original[n])!=PINS[n]:
            raise RuntimeError("LIVE_SOURCE_DRIFT: "+n)
    candidate[CODER]=patch_coder(original[CODER].decode()).encode()
    candidate[STATION]=patch_station(original[STATION].decode()).encode()
    changed={n:v for n,v in candidate.items() if original[n]!=v}
    print("PATCH_PROTOCOL_V10_PREFLIGHT",rev,json.dumps({n:{"before":sha(original[n]),"after":sha(v)} for n,v in candidate.items()}),flush=True)
    if mode=="preflight": return
    if mode=="verify":
        if changed: raise RuntimeError("V10_NOT_DEPLOYED")
        live_check(); return
    if mode!="publish" or not token or os.getenv("SWRLZ_PATCH_PROTOCOL_V10_APPROVED")!="1":
        raise PermissionError("V10_RELEASE_NOT_APPROVED")
    if not changed: live_check(); return
    def add(n,v): return CommitOperationAdd(path_in_repo=n,path_or_fileobj=io.BytesIO(v))
    new=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
          operations=[add(n,v) for n,v in changed.items()],
          commit_message="fix(§C): dedicated exact repair patch grammar").oid
    print("PATCH_PROTOCOL_V10_COMMITTED",new,flush=True)
    try:
        for n,v in candidate.items():
            if read(n,new)!=v: raise RuntimeError("V10_READBACK_MISMATCH: "+n)
        api.restart_space(SPACE)
        for attempt in range(48):
            try:
                live_check()
                print("PATCH_PROTOCOL_V10_DEPLOYED_VERIFIED",new,flush=True);return
            except ValueError:
                raise
            except Exception as exc:
                if attempt==47: raise
                print("PATCH_PROTOCOL_V10_WAIT",attempt,type(exc).__name__,flush=True)
                time.sleep(8)
    except Exception:
        if str(api.repo_info(SPACE,repo_type="space").sha)==new:
            restored=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=new,
                operations=[add(n,original[n]) for n in changed],
                commit_message="rollback(§C): repair grammar real-model probe failed").oid
            print("PATCH_PROTOCOL_V10_ROLLBACK",restored,flush=True);api.restart_space(SPACE)
        raise
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("mode",choices=("selftest","preflight","publish","verify"))
    release(p.parse_args().mode)
