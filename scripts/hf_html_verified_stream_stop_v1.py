#!/usr/bin/env python3
"""Early verified HTML closure during §C code streaming.

A completed single-page HTML envelope can appear while the resident coder
continues decoding. Terminate only that verified single-document stream,
preserve the actual provider finish reason (which may be unknown), then run
the existing code contract and browser tests. Never affect multi-file projects.
"""
from __future__ import annotations
import ast,hashlib,json,os,re,sys,types
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
SPACE="kamiloki/Swyrlz"
FILES=["qwen_coder_engine.py","programming_telemetry.py"]
ROOT=Path("reports/html-verified-stream-closure")
MARK="swrlz-html-verified-chunk-closure-v1"
BEFORE_Q='''            if addition:
                parts.append(addition)
                preview_buffer+=addition
                # Check only every 24 decoded deltas. Reset preview to the'''
AFTER_Q='''            if addition:
                parts.append(addition)
                preview_buffer+=addition
                # swrlz-html-verified-chunk-closure-v1: a complete single
                # HTML file does not need the remaining output-token budget.
                # Never accept fragments or multiple files, and keep native
                # finishReason untouched (this is a host parser stop).
                tail="".join(parts)[-256:]
                if re.search(r"(?is)</html>\s*(?:\x60{3})?\s*\Z",tail):
                    complete,parsed=_swrlz_close_complete_html_fence("".join(parts))
                    if parsed:
                        part_observation["sourceCompleteByParser"]=True
                        part_observation["sourceClosureKind"]="html-file-envelope"
                        part_observation["stoppedByVerifiedParser"]=True
                        if complete!="".join(parts):
                            parts=[complete]
                            yield {"type":"CANDIDATE_PREVIEW_RESET","attempt":attempt}
                            yield {"type":"CANDIDATE_PREVIEW_DELTA","text":complete,"attempt":attempt}
                            preview_buffer=""
                        break
                # Check only every 24 decoded deltas. Reset preview to the'''
BEFORE_T='''    result["generationComplete"]=(True if reason=="stop" or (reason=="length" and parsed_completion)
                                  else False if reason=="length" else None)'''
AFTER_T='''    # swrlz-html-verified-chunk-closure-v1: a host parser may stop
    # decoding a complete single HTML artifact before the provider sends
    # finish_reason. Record that fact separately; never forge "stop".
    parser_stop=(observation.get("stoppedByVerifiedParser") is True
                 and parsed_completion)
    result["generationComplete"]=(True if reason=="stop" or
                                   (reason=="length" and parsed_completion) or parser_stop
                                  else False if reason=="length" else None)
    result["parserStoppedStream"]=parser_stop'''
BEFORE_RC='''        "finishReason":timing.get("finishReason"),
        "requestedMaxTokens":timing.get("requestedMaxTokens"),'''
AFTER_RC='''        "finishReason":timing.get("finishReason"),
        "parserStoppedStream":bool(timing.get("stoppedByVerifiedParser")),
        "requestedMaxTokens":timing.get("requestedMaxTokens"),'''

def digest(data):return hashlib.sha256(data).hexdigest()
def replace_one(source,old,new,label):
    n=source.count(old)
    if n!=1:raise RuntimeError(f"Live source changed at {label}, expected 1 anchor; got {n}")
    return source.replace(old,new,1)
def proposed(sources):
    q=sources[FILES[0]].decode("utf-8")
    t=sources[FILES[1]].decode("utf-8")
    if MARK in q or MARK in t:
        raise RuntimeError("Verified HTML streaming closure already applied")
    q=replace_one(q,BEFORE_Q,AFTER_Q,"native streamed chunk")
    t=replace_one(t,BEFORE_T,AFTER_T,"complete source acceptance")
    t=replace_one(t,BEFORE_RC,AFTER_RC,"observability")
    compile(q,FILES[0],"exec")
    compile(t,FILES[1],"exec")
    return {FILES[0]:q.encode("utf-8"),FILES[1]:t.encode("utf-8")}

def static_tests(out):
    coder=ast.parse(out[FILES[0]].decode())
    telemetry=ast.parse(out[FILES[1]].decode())
    q_fn=next(n for n in coder.body if isinstance(n,ast.FunctionDef)
              and n.name=="_swrlz_code_candidate_preview")
    text=ast.get_source_segment(out[FILES[0]].decode(),q_fn)
    for phrase in ("stoppedByVerifiedParser","_swrlz_close_complete_html_fence(",
                   'if parsed:',"part_observation",'"CANDIDATE_PREVIEW_RESET"'):
        if phrase not in text:raise AssertionError("Missing guarded streaming branch "+phrase)
    assert text.index('if parsed:')<text.index("delta_chunks%24==0")
    validation=next(n for n in telemetry.body if isinstance(n,ast.FunctionDef)
                    and n.name=="completion_validation")
    ns={"Any":object}
    exec(compile(ast.Module(body=[validation],type_ignores=[]),FILES[1],"exec"),ns)
    grade=ns["completion_validation"]
    examples=[
        ({"status":"PASS","reasons":[]},
         {"finishReason":None,"sourceCompleteByParser":True,"stoppedByVerifiedParser":True},
         True,True),
        ({"status":"PASS","reasons":[]},
         {"finishReason":"length","sourceCompleteByParser":True},
         True,False),
        ({"status":"PASS","reasons":[]},
         {"finishReason":"length","sourceCompleteByParser":False},
         False,False),
        ({"status":"REJECT","reasons":["missing-script"]},
         {"finishReason":None,"sourceCompleteByParser":True,"stoppedByVerifiedParser":True},
         None,False),
        ({"status":"PASS","reasons":[]},
         {"finishReason":"stop"},
         True,False),
        ({"status":"PASS","reasons":[]},
         {"finishReason":None},
         None,False),
    ]
    for base,observation,complete,parser_stop in examples:
        result=grade(base,observation)
        if result["generationComplete"] is not complete or result["parserStoppedStream"] is not parser_stop:
            raise AssertionError("Parser semantics not preserved")
        if result["finishReason"]!=observation.get("finishReason"):
            raise AssertionError("Falsified provider finish reason")
    # Execute the extracted streaming generator with a deterministic fake model.
    # Its parser stub stands for the preexisting full envelope parser; source
    # packaging and runtime safety remain separately tested in production.
    stub=types.ModuleType("code_runaway_guard_v1")
    stub.collapse_repeated_css_rules=lambda x:(x,[])
    previous=sys.modules.get(stub.__name__)
    sys.modules[stub.__name__]=stub
    try:
        def parser(s):
            stripped=s.rstrip()
            complete=bool(re.search(r"(?is)</html>\s*(?:\x60{3})?\s*\Z",stripped)
                          and re.search(r"<html\b",stripped,re.I)
                          and re.search(r"<body\b",stripped,re.I)
                          and stripped.count("<html")==1)
            return (s,complete)
        def observe(o,c):
            reason=(c.get("choices") or [{}])[0].get("finish_reason")
            if reason is not None:o["finishReason"]=reason
        helper=compile(ast.Module(body=[q_fn],type_ignores=[]),FILES[0],"exec")
        import time
        g={"time":time,"re":re,"_swrlz_close_complete_html_fence":parser,
           "_swrlz_trim_code_resume":lambda prior,following:following,
           "_swrlz_resume_tail_messages":lambda prior:[],
           "CONTEXT_TOKENS":16000,"CONTEXT_SAFETY_TOKENS":512,
           "_token_count":lambda *args:10,"MIN_OUTPUT_TOKENS":40,
           "observe_completion_chunk":observe}
        exec(helper,g)
        token_parts=[
            "\x60\x60\x60html file=index.html\n<!doctype html><html><body>",
            "<button onclick='document.body.dataset.clicked=1'>Change</button>",
            "</body></html>",
            "\n\n<!-- NONSOURCE GARBAGE AFTER FINISHED HTML -->"]
        class Model:
            def create_chat_completion(self,**kw):
                for token in token_parts:
                    yield {"choices":[{"delta":{"content":token},"finish_reason":None}]}
                yield {"choices":[{"delta":{},"finish_reason":"stop"}]}
        events=[]
        gen=g["_swrlz_code_candidate_preview"](Model(),[{"role":"system","content":"x"}],1200,0.2,1,
                             allow_continue=False,cancel_check=lambda:False)
        while True:
            try:events.append(next(gen))
            except StopIteration as done:
                output,timing=done.value
                break
        if "NONSOURCE GARBAGE" in output:raise AssertionError("Parser failed to terminate native stream early")
        if "</html>" not in output or not timing.get("stoppedByVerifiedParser"):
            raise AssertionError("No parser-owned complete source stop")
        if timing.get("finishReason") is not None:
            raise AssertionError("Early stop falsely described as provider stop")
    finally:
        if previous is None:sys.modules.pop(stub.__name__,None)
        else:sys.modules[stub.__name__]=previous
    print("HTML_PARSER_STOP_STATIC_ACCEPTED",len(examples)+6,flush=True)

def snapshot(api):
    rev=api.repo_info(SPACE,repo_type="space").sha
    before={}
    for path in FILES:
        before[path]=Path(hf_hub_download(SPACE,path,repo_type="space",
                        revision=rev,token=api.token)).read_bytes()
    after=proposed(before)
    static_tests(after)
    (ROOT/"before").mkdir(parents=True,exist_ok=True)
    (ROOT/"after").mkdir(parents=True,exist_ok=True)
    for path in FILES:
        (ROOT/"before"/path).write_bytes(before[path])
        (ROOT/"after"/path).write_bytes(after[path])
    manifest={"space":SPACE,"revision":rev,"files":{
        path:{"beforeSha256":digest(before[path]),"afterSha256":digest(after[path])}
        for path in FILES},"scope":"single HTML verified stream closure"}
    (ROOT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print("HTML_PARSER_STOP_PREFLIGHT",rev,json.dumps(manifest["files"]),flush=True)
    return rev,before,after

def release(api):
    if os.getenv("SWRLZ_HTML_PARSER_STOP_APPROVED")!="1":
        raise RuntimeError("Explicit guarded source approval unavailable")
    if not api.token:raise RuntimeError("HF_TOKEN missing")
    rev,before,after=snapshot(api)
    if api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("Concurrent HF source update before release")
    newrev=None
    try:
        commit=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
            operations=[CommitOperationAdd(path_in_repo=path,path_or_fileobj=str(ROOT/"after"/path))
                        for path in FILES],
            commit_message="§C stop streaming verified complete HTML without forging model finish reason")
        newrev=str(commit.oid)
        for path in FILES:
            actual=Path(hf_hub_download(SPACE,path,repo_type="space",revision=newrev,token=api.token)).read_bytes()
            if actual!=after[path]:raise RuntimeError("Source bytes differed for "+path)
        manifest=json.loads((ROOT/"manifest.json").read_text())
        manifest["publishedRevision"]=newrev
        (ROOT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
        print("HTML_PARSER_STOP_PUBLISHED",rev,newrev,flush=True)
    except Exception:
        if newrev and api.repo_info(SPACE,repo_type="space").sha==newrev:
            back=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=newrev,
                operations=[CommitOperationAdd(path_in_repo=path,path_or_fileobj=str(ROOT/"before"/path))
                            for path in FILES],
                commit_message="Rollback §C parser stop to byte-exact previous coder and telemetry")
            print("HTML_PARSER_STOP_ROLLED_BACK",str(back.oid),flush=True)
        raise

def rollback(api):
    if os.getenv("SWRLZ_HTML_PARSER_STOP_APPROVED")!="1":raise RuntimeError("No rollback approval")
    manifest=json.loads((ROOT/"manifest.json").read_text())
    published=manifest.get("publishedRevision")
    if not published or api.repo_info(SPACE,repo_type="space").sha!=published:
        raise RuntimeError("Refusing rollback after intervening source change")
    for path in FILES:
        original=(ROOT/"before"/path).read_bytes()
        if digest(original)!=manifest["files"][path]["beforeSha256"]:
            raise RuntimeError("Rollback source corrupted: "+path)
    commit=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=published,
        operations=[CommitOperationAdd(path_in_repo=path,path_or_fileobj=str(ROOT/"before"/path))
                    for path in FILES],
        commit_message="Rollback §C parser stop after failed guest acceptance")
    for path in FILES:
        actual=Path(hf_hub_download(SPACE,path,repo_type="space",revision=str(commit.oid),token=api.token)).read_bytes()
        if actual!=(ROOT/"before"/path).read_bytes():
            raise RuntimeError("Failed to verify restored source "+path)
    print("HTML_PARSER_STOP_ACCEPTANCE_ROLLBACK",published,str(commit.oid),flush=True)

if __name__=="__main__":
    mode=sys.argv[1:] or ["preflight"]
    if mode not in (["preflight"],["publish"],["rollback"]):
        raise SystemExit("preflight|publish|rollback")
    api=HfApi(token=os.environ.get("HF_TOKEN") or None)
    if mode==["preflight"]:snapshot(api)
    elif mode==["publish"]:release(api)
    else:rollback(api)
