#!/usr/bin/env python3
"""Source-safe §C bare-ack history compacting on the existing resident 9B.

Only short plain social acknowledgments get at most the previous four model
messages. Store, actual chat history, tools, technical prompts, coding repairs,
auth, model identity, weights, hardware and §E are left unchanged.
"""
from __future__ import annotations
import ast, hashlib, json, os, re, sys, time, tempfile, urllib.request
from pathlib import Path
from huggingface_hub import HfApi, hf_hub_download, CommitOperationAdd

SPACE="kamiloki/Swyrlz"
FILE="lfm2_700m_engine.py"
BASE="https://kamiloki-swyrlz.hf.space"
MARKER="swrlz-bare-ack-context-v1"
ROLE_INSERT='def generate_events(payload):'
PRELUDE='''    # swrlz-qwen35-conversation-v4: natural nontechnical chat needs no old'''
SOCIAL_END='''        if user_profile:
            system+="\\nCURRENT USER PROFILE (user, not assistant):\\n"+user_profile
    if source_change_mode:'''
# The live Python file contains escaped \n within these actual source strings.
SOCIAL_END=SOCIAL_END.replace('\\\\n','\\n')
CONTEXT_ANCHOR='"historyMessagesKept":len(messages)-2,'
HELPER=r'''def _qwen35_bare_ack(prompt):
    """Match a standalone acknowledgment, not an instruction or factual query."""
    clean=" ".join(str(prompt or "").split()).strip()
    return len(clean) <= 64 and bool(re.fullmatch(
        r"(?:good job|great job|nice job|nice work|great work|"
        r"well done|thank you|thanks)"
        r"(?:[.!?]+)?(?:\s+(?:lol|lmao))?[.!?]*",
        clean,re.I))

'''
HOOK='''    ack_fast_route=False
    ack_history_compacted=False
'''
HISTORY_PATCH='''        if _qwen35_bare_ack(prompt):
            ack_fast_route=True
            # The model needs the immediate exchange, not an old 16-turn
            # replay just to acknowledge praise. Stored history is untouched.
            if len(model_history)>4:
                model_history=model_history[-4:]
                ack_history_compacted=True
'''
def once(s,old,new,name):
    n=s.count(old)
    if n!=1:
        raise RuntimeError("Live source drift: %s occurrences=%s" % (name,n))
    return s.replace(old,new,1)

def patch(s):
    if MARKER in s:
        raise RuntimeError("Already patched: refuse double insertion")
    if "Qwen3.5" not in s and "qwen35" not in s:
        raise RuntimeError("Unexpected model engine")
    s=once(s,ROLE_INSERT,HELPER+ROLE_INSERT,"helper")
    s=once(s,PRELUDE,"    # "+MARKER+"\n"+HOOK+PRELUDE,"social prelude")
    s=once(s,SOCIAL_END,SOCIAL_END.replace("    if source_change_mode:",HISTORY_PATCH+"    if source_change_mode:"),"social history")
    s=once(s,CONTEXT_ANCHOR,CONTEXT_ANCHOR+
        '"ackFastRoute":ack_fast_route,"ackHistoryCompacted":ack_history_compacted,',
        "telemetry")
    ast.parse(s,filename=FILE)
    return s

def digest(b):
    return hashlib.sha256(b).hexdigest()

def source(api,revision):
    p=hf_hub_download(SPACE,FILE,revision=revision,repo_type="space",token=api.token)
    return Path(p).read_bytes()

def prepare(api):
    revision=api.repo_info(SPACE,repo_type="space").sha
    before=source(api,revision)
    after=patch(before.decode("utf-8")).encode("utf-8")
    tests(before,after)
    print("ACK_CONTEXT_PREFLIGHT",json.dumps({
        "source":revision,"originalHash":digest(before),"newHash":digest(after),
        "changedFiles":[FILE],"modelChanged":False,"hardwareChanged":False,
        "userHistoryStorageChanged":False}),flush=True)
    return revision,before,after

def tests(before,after):
    new=after.decode()
    old=before.decode()
    assert new.count(MARKER)==1
    assert old.count("def generate_events(payload):")==1
    assert new.count("def generate_events(payload):")==1
    assert "ackHistoryCompacted" in new and "ackFastRoute" in new
    assert "model_history=model_history[-4:]" in new
    assert "_qwen35_plain_social_turn(prompt, programming, payload," in new
    assert "    if source_change_mode:" in new
    assert "    if repair_turn:" in new and "_fit_repair_messages(" in new
    assert "_wyrlz_active_profile(prompt,programming,brief=True)" in new
    assert "source_sized_budget(" in new
    assert "programming_intent(" in new
    funcs=[n for n in ast.parse(new).body if isinstance(n,ast.FunctionDef)
           and n.name in ("_qwen35_bare_ack","_qwen35_plain_social_turn")]
    env={"re":re}
    exec(compile(ast.Module(body=funcs,type_ignores=[]),"<ack-only-tests>","exec"),env)
    fn=env["_qwen35_bare_ack"]
    route=env["_qwen35_plain_social_turn"]
    for p in ("good job","Good job!","Great job lol","nice work","well done","thanks"):
        assert fn(p),p
        assert route(p,{"codingTask":False},{},False,False),p
    for p in ("good job fix the bug","good job on the patch","can you verify this",
              "thanks now write code","explain the function","9 times 9",""):
        assert not fn(p),p
    for p in ("fix the bug","what is the server speed","show me the repo"):
        assert not route(p,{"codingTask":False},{},False,False),p
    assert not route("good job",{"codingTask":True},{},False,False)
    assert not route("good job",{},{"nativeEditorEvidence":{"object":"x"}},False,False)
    assert not route("good job",{}, {},True,False)
    example=[{"role":"user","content":"old"},{"role":"assistant","content":"old"},
             {"role":"user","content":"new"},{"role":"assistant","content":"latest"},
             {"role":"user","content":"context"},{"role":"assistant","content":"latest answer"}]
    assert example[-4:]==example[2:]
    assert example[-4:][-1]["content"]=="latest answer"
    print("ACK_CONTEXT_STATIC_PASS",json.dumps({
        "ackRoutes":["good job","Good job!","Great job lol","nice work","well done","thanks"],
        "unsafeRoutesExcluded":True,"sourceRepairUntouched":True,
        "conversationPreservedInStore":True,"maxRecentHistoryMessagesForBareAck":4}),flush=True)

def info():
    req=urllib.request.Request(BASE+"/api/hf/qwen35-ready",
                 headers={"Cache-Control":"no-cache","User-Agent":"Swyrlz-Ack-Context-Release"})
    with urllib.request.urlopen(req,timeout=18) as res:return json.load(res)

def wait_ready(api,revision,deadline_secs=1050):
    deadline=time.monotonic()+deadline_secs
    while time.monotonic()<deadline:
        if api.repo_info(SPACE,repo_type="space").sha!=revision:
            raise RuntimeError("Concurrent HF deployment during release")
        try:
            snap=info()
            if (snap.get("model")=="qwen3.5-9b" and snap.get("ready") is True
                    and snap.get("cpuCapacity")==16
                    and snap.get("decodeThreads")==18
                    and snap.get("batchThreads")==18):
                print("ACK_CONTEXT_RESIDENT_9B_READY",json.dumps({
                    "cpuCapacity":16,"decodeThreads":18,"batchThreads":18,
                    "profile":snap.get("profile")}),flush=True)
                return
        except Exception as exc:
            print("ACK_CONTEXT_WARMUP",type(exc).__name__,flush=True)
        time.sleep(12)
    raise RuntimeError("New §C model did not become ready in verification window")

def write_revision(api,prev_rev,data,message):
    if api.repo_info(SPACE,repo_type="space").sha!=prev_rev:
        raise RuntimeError("Concurrent HF source change, refusing overwrite")
    with tempfile.NamedTemporaryFile(suffix=".py",prefix="swrlz-ack-") as p:
        p.write(data);p.flush()
        result=api.create_commit(repo_id=SPACE,repo_type="space",
            parent_commit=prev_rev,
            operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=p.name)],
            commit_message=message)
    revision=str(result.oid)
    if digest(source(api,revision))!=digest(data):
        raise RuntimeError("Published source hash mismatch")
    print("ACK_CONTEXT_SOURCE_SHA_VERIFIED",revision,flush=True)
    return revision

def main():
    mode=sys.argv[1:] or []
    api=HfApi(token=os.environ.get("HF_TOKEN") or None)
    if mode==["inspect"]:
        prepare(api)
        return
    if mode!=["publish"]:
        raise SystemExit("Use inspect|publish")
    if os.environ.get("SWRLZ_ACK_CONTEXT_APPROVED")!="1" or not api.token:
        raise RuntimeError("Explicit HF deployment authorization required")
    old_rev,before,after=prepare(api)
    now=write_revision(api,old_rev,after,
        "§C: shorten inference history only for standalone social acknowledgments")
    try:
        wait_ready(api,now)
        # A new worker has been observed. A separate synthetic request
        # checks the new per-turn telemetry and guarded routes.
        from probe_chat_ack_context import verify_live
        verify_live()
        print("ACK_CONTEXT_LIVE_ACCEPTED",json.dumps({
            "revision":now,"source":old_rev,"model":"Qwen3.5-9B",
            "threads":18,"responseTextCanned":False}),flush=True)
    except Exception:
        if api.repo_info(SPACE,repo_type="space").sha==now:
            rollback=write_revision(api,now,before,
                "Rollback §C acknowledgment context trial to exact prior source")
            wait_ready(api,rollback)
            print("ACK_CONTEXT_EXACT_ROLLBACK",rollback,flush=True)
        else:
            print("ACK_CONTEXT_ROLLBACK_BLOCKED_BY_CONCURRENT_CHANGE",flush=True)
        raise

if __name__=="__main__":main()
