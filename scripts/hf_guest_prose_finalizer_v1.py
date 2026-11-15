#!/usr/bin/env python3
"""Guard explicit §C no-code explanations at the final streaming output boundary."""
import ast,hashlib,json,os,re,sys
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
SPACE="kamiloki/Swyrlz"
FILE="qwen_coder_engine.py"
OUT=Path("reports/prose-guard-v1")
MARK="swrlz-explicit-prose-finalizer-v1"
HELPER=r'''def _swrlz_prose_source_breach(text):
    return bool(re.search(r"(?m)^[ \t]*(?:\x60{3,}|~{3,}|def\s+\w+\s*\(|return\s+\S|function\s+\w+\s*\(|(?:const|let|var)\s+\w+\s*=|<(?:html|body|script)\b)",str(text or ""),re.I))

def _swrlz_prose_remove_source(text):
    source=re.sub(r"(?ms)^[ \t]*\x60{3,}[^\n]*\n.*?^[ \t]*\x60{3,}[ \t]*(?:\n|$)","\n",str(text or ""))
    source=re.sub(r"(?ms)^[ \t]*~{3,}[^\n]*\n.*?^[ \t]*~{3,}[ \t]*(?:\n|$)","\n",source)
    clean=[]
    for line in source.splitlines():
        s=line.strip()
        if re.match(r"(?i)^(?:def\s+\w+\s*\(|return\s+\S|function\s+\w+\s*\(|(?:const|let|var)\s+\w+\s*=|<(?:html|body|script)\b)",s):continue
        if s.endswith(":") and re.search(r"(?i)(for example|looks like|return statement to|code as follows|update.*\bto)",s):continue
        clean.append(line)
    result=re.sub(r"\n{3,}","\n\n","\n".join(clean)).strip()
    return result if len(result)>=25 and not _swrlz_prose_source_breach(result) else "I could not produce a complete prose-only explanation. Please ask which aspect you would like clarified."
'''
EXTRA=r'''            if prose_only_output and _swrlz_prose_source_breach(candidate_text):
                yield {"type":"STATUS","phase":"PROSE_FORMAT_RETRY","reason":"Plain-language instruction not followed; rewriting once."}
                revision=[*messages,{"role":"assistant","content":candidate_text[:1800]},
                          {"role":"user","content":"Rewrite your preceding explanation in ordinary prose only. Preserve its actual meaning. No fenced code, function bodies, executable statements or source examples. Return only the concise explanation."}]
                if _token_count(model,revision)+400<CONTEXT_TOKENS-CONTEXT_SAFETY_TOKENS:
                    chunks=[]
                    observation={"finishReason":None,"requestedMaxTokens":320}
                    for part in model.create_chat_completion(messages=revision,max_tokens=320,temperature=0.15,stream=True):
                        if cancel_check():return
                        observe_completion_chunk(observation,part)
                        opts=part.get("choices") or []
                        token=(opts[0].get("delta") or {}).get("content") if opts else None
                        if token:chunks.append(str(token))
                    rewritten="".join(chunks).strip()
                    if rewritten and observation.get("finishReason")=="stop" and not _swrlz_prose_source_breach(rewritten):
                        candidate_text=rewritten
                        stream_observation=observation
            if prose_only_output:
                if _swrlz_prose_source_breach(candidate_text):
                    candidate_text=_swrlz_prose_remove_source(candidate_text)
                if cancel_check():return
                if candidate_text:
                    first_delta=round((time.perf_counter()-started)*1000,3)
                    yield {"type":"DELTA","text":candidate_text}
            attempt_ended=time.perf_counter()
            candidate_check=_candidate_structure_check(candidate_text,programming,history)'''

def replace_one(s,old,new,label):
    if s.count(old)!=1:raise RuntimeError(f"Unsafe source: {label} match count {s.count(old)}")
    return s.replace(old,new,1)

def proposed(original):
    s=original.decode()
    if MARK in s:raise RuntimeError("Patch is already present")
    if "swrlz-prose-only-response-mode-v1" not in s:raise RuntimeError("Required previous mode fix absent")
    s=replace_one(s,"def generate_events(payload):",HELPER+"\n\ndef generate_events(payload):","helper")
    g='    guarded_turn=not source_change_mode and bool(repair_turn or strict_language or code_delivery)'
    s=replace_one(s,g,g+'\n    prose_only_output=bool(not source_change_mode and programming.get("source")=="prose-only-user-direction")',"gate")
    s=replace_one(s,'                    yield {"type":"DELTA","text":delta}',
                     '                    if not prose_only_output:\n                        yield {"type":"DELTA","text":delta}',"stream sink")
    s=replace_one(s,'                    if first_delta is None:first_delta=round((now-started)*1000,3)',
                     '                    if first_delta is None and not prose_only_output:first_delta=round((now-started)*1000,3)',"visible telemetry")
    s=replace_one(s,'            candidate_text="".join(generated_parts)\n            candidate_check=_candidate_structure_check(candidate_text,programming,history)',
                     '            candidate_text="".join(generated_parts)\n'+EXTRA,"completed prose gate")
    compile(s,FILE,"exec")
    return s.encode()

def static_check(after):
    parsed=ast.parse(after.decode())
    defs={x.name:x for x in parsed.body if isinstance(x,ast.FunctionDef)}
    ns={"re":re}
    exec(compile(ast.Module(body=[defs["_swrlz_prose_source_breach"],
                                  defs["_swrlz_prose_remove_source"]],type_ignores=[]),FILE,"exec"),ns)
    breached=ns["_swrlz_prose_source_breach"]
    for t,want in [("Use addition instead of subtraction.",False),
                   ("Use the plus symbol (+).",False),
                   ("Here is code:\n\x60\x60\x60python\ndef add(a,b):\n return a+b\n\x60\x60\x60",True),
                   ("def add(a,b):\n return a+b",True),
                   ("function square(n) { return n*n; }",True),
                   ("The function accepts two numbers.",False)]:
        if breached(t)!=want:raise AssertionError("Source detection "+repr(t))
    raw="Change subtraction to addition.\n\nFor example, it looks like:\n\x60\x60\x60python\ndef add(a,b):\n return a-b\n\x60\x60\x60\n\nThis restores the sum."
    safe=ns["_swrlz_prose_remove_source"](raw)
    if breached(safe) or "Change subtraction to addition" not in safe:raise AssertionError("Unsafe fallback")
    generated=ast.get_source_segment(after.decode(),defs["generate_events"])
    for token in ("if prose_only_output:",'if not prose_only_output:','phase":"PROSE_FORMAT_RETRY'):
        if token not in generated:raise AssertionError("Missing guard "+token)
    print("PROSE_FINALIZER_STATIC_PASS 10",flush=True)

def snapshot(api):
    rev=api.repo_info(SPACE,repo_type="space").sha
    before=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=rev,token=api.token)).read_bytes()
    after=proposed(before);static_check(after)
    (OUT/"before").mkdir(parents=True,exist_ok=True)
    (OUT/"after").mkdir(parents=True,exist_ok=True)
    (OUT/"before"/FILE).write_bytes(before)
    (OUT/"after"/FILE).write_bytes(after)
    digest=lambda b:hashlib.sha256(b).hexdigest()
    (OUT/"manifest.json").write_text(json.dumps({"space":SPACE,"file":FILE,"revision":rev,
        "beforeSHA256":digest(before),"afterSHA256":digest(after)},indent=2))
    print("PROSE_FINALIZER_PREFLIGHT",rev,digest(before),digest(after),flush=True)
    return rev,before,after

def main():
    mode=sys.argv[1] if len(sys.argv)>1 else "preflight"
    if mode not in ("preflight","publish"):raise RuntimeError("Invalid mode")
    if mode=="publish" and os.getenv("SWRLZ_PROSE_FINALIZER_APPROVED")!="1":
        raise RuntimeError("Explicit production approval required")
    api=HfApi(token=os.getenv("HF_TOKEN") or None)
    rev,before,after=snapshot(api)
    if mode=="preflight":return
    if not api.token:raise RuntimeError("HF_TOKEN unavailable")
    if api.repo_info(SPACE,repo_type="space").sha!=rev:raise RuntimeError("Concurrent HF source change")
    oid=None
    try:
        result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
             operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"after"/FILE))],
             commit_message="§C enforce no-code explanation before streaming to guest chat")
        oid=str(result.oid)
        uploaded=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=oid,token=api.token)).read_bytes()
        if uploaded!=after:raise RuntimeError("Published bytes mismatch")
        print("PROSE_FINALIZER_PUBLISHED",rev,oid,flush=True)
    except Exception:
        if oid and api.repo_info(SPACE,repo_type="space").sha==oid:
            back=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=oid,
                operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"before"/FILE))],
                commit_message="Rollback §C no-code finalizer to exact previous bytes")
            print("PROSE_FINALIZER_ROLLBACK",back.oid,flush=True)
        raise
if __name__=="__main__":main()
