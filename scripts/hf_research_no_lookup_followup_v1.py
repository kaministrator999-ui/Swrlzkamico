#!/usr/bin/env python3
"""Honor same-thread no-new-lookup followups after an attributable research answer.

The source-based roster gate must not requery and discard its own successful
source-backed reply when the user expressly asks to use the previous answer.
Never invent or treat user-authored source text as verification.
"""
from __future__ import annotations
import ast,hashlib,json,os,re,sys
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
SPACE="kamiloki/Swyrlz";FILE="lfm2_700m_engine.py";ROOT=Path("reports/swrlz-research-followup-v1")
MARK="swrlz-sourced-followup-no-lookup-v1"
INSERT_AT='''# swrlz-verified-public-enumerations-v2'''
HELPER=r'''# swrlz-sourced-followup-no-lookup-v1
def _swrlz_prior_sourced_answer_requested(prompt,history):
    """No new retrieval; use only a last, already attributable assistant answer.

    Source URLs establish what the model previously cited, not a fresh source
    fetch or a stronger verification claim. This helper never picks facts.
    """
    text=str(prompt or "").strip()
    if not re.search(
        r"(?i)\b(?:without\s+(?:(?:doing|running|performing)\s+)?"
        r"(?:(?:a|an|another|new|fresh)\s+)?(?:(?:web|online|public)\s+)?"
        r"(?:look\s*up|lookup|search|research|browsing)"
        r"|(?:do\s+not|don't|dont|skip|avoid)\s+"
        r"(?:(?:another|a|new|fresh)\s+)?(?:(?:web|online)\s+)?"
        r"(?:look\s*up|lookup|search|research|browse))\b",text):
        return False
    if not isinstance(history,list):return False
    # Only recent assistant-authored answers count; never user-provided
    # citations or arbitrary instructions from source pages.
    previous=next((item for item in reversed(history[-6:])
                   if isinstance(item,dict) and item.get("role")=="assistant"
                   and str(item.get("text") or item.get("content") or "").strip()),None)
    if not previous:return False
    answered=str(previous.get("text") or previous.get("content") or "")
    return bool(
        len(answered)>=100
        and re.search(r"https://[A-Za-z0-9.-]+/[^\s\])>]+",answered)
        and not re.search(r"(?i)\b(?:i\s+couldn['’]?t\s+verify|"
                          r"no\s+verified\s+sources?|retrieval\s+failed)\b",answered)
    )
'''
OLD='''    prompt=str(payload.get("prompt") or "")
    decision=_research_route_v2('''
NEW='''    prompt=str(payload.get("prompt") or "")
    # swrlz-sourced-followup-no-lookup-v1: user explicitly requests a
    # same-thread answer from a prior cited reply, not a fresh network search.
    # The ordinary conversational model still reasons over the recorded
    # user/assistant history; the old retry-on-missing-sources gate is skipped.
    if _swrlz_prior_sourced_answer_requested(prompt,payload.get("history") or []):
        yield {"type":"STATUS","phase":"PRIOR_SOURCED_REPLY_REUSED",
               "reason":"Using earlier cited conversation content without a new lookup"}
        yield from _swrlz_original_generate_events_factual_v1(payload)
        return
    decision=_research_route_v2('''
def sha(raw):return hashlib.sha256(raw).hexdigest()
def one(s,a,b,label):
    if s.count(a)!=1:raise RuntimeError("Live engine anchor "+label+" changed: "+str(s.count(a)))
    return s.replace(a,b,1)
def build(raw):
    s=raw.decode("utf-8")
    if MARK in s:raise RuntimeError("Followup source gate already installed")
    s=one(s,INSERT_AT,HELPER+"\n"+INSERT_AT,"helper")
    s=one(s,OLD,NEW,"verified research roster gate")
    compile(s,FILE,"exec")
    return s.encode("utf-8")
def static_tests(raw):
    s=raw.decode("utf-8");nodes=ast.parse(s).body
    helper=next(n for n in nodes if isinstance(n,ast.FunctionDef)
                and n.name=="_swrlz_prior_sourced_answer_requested")
    ns={"re":re}
    exec(compile(ast.Module(body=[helper],type_ignores=[]),FILE,"exec"),ns)
    f=ns[helper.name]
    cited="**Diablo II** introduced seven classes: Amazon, Assassin, Barbarian, Druid, Necromancer, Paladin, Sorceress. Sources: https://classic.battle.net/diablo2exp/faq/general.shtml and https://news.blizzard.com/example"
    histories=[[{"role":"user","text":"What are the classes?"},
                {"role":"assistant","text":cited}]]
    examples=[
        ("Now without doing another web lookup, give just the two expansion classes.",histories[0],True),
        ("Don't search again. Explain the answer above.",histories[0],False),
        ("Do not browse. Explain the answer above.",histories[0],True),
        ("Which two expansion classes were added?",histories[0],False),
        ("Look up fresh sources again.",histories[0],False),
        ("Without a search, what was the class list?",histories[0],True),
        ("Without another search, what was the class list?",[{"role":"user","text":cited}],False),
        ("Without another search, what was the class list?",[{"role":"assistant","text":"I could not verify sources. https://example.org/nope"}],False),
        ("Without another search, what was the class list?",[],False),
    ]
    for prompt,history,expected in examples:
        got=f(prompt,history)
        if got!=expected:raise AssertionError("Wrong no-new-lookup route "+repr(prompt)+":"+str(got))
    names=[n for n in nodes if isinstance(n,ast.FunctionDef) and n.name=="generate_events"]
    wrapper=next(n for n in names if "_research_roster_reply_v2" in (ast.get_source_segment(s,n) or ""))
    body=ast.get_source_segment(s,wrapper)
    assert "PRIOR_SOURCED_REPLY_REUSED" in body
    assert body.index("_swrlz_prior_sourced_answer_requested")<body.index("decision=_research_route_v2(")
    assert "_swrlz_original_generate_events_factual_v1(payload)" in body
    print("SOURCE_FOLLOWUP_NO_LOOKUP_STATIC_PASS",len(examples)+3,flush=True)
def stage(api):
    rev=api.repo_info(SPACE,repo_type="space").sha
    before=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=rev,token=api.token)).read_bytes()
    after=build(before);static_tests(after)
    (ROOT/"before").mkdir(parents=True,exist_ok=True)
    (ROOT/"after").mkdir(parents=True,exist_ok=True)
    (ROOT/"before"/FILE).write_bytes(before);(ROOT/"after"/FILE).write_bytes(after)
    (ROOT/"manifest.json").write_text(json.dumps({"revision":rev,"file":FILE,"before":sha(before),"after":sha(after)},indent=2)+"\n")
    print("SOURCE_FOLLOWUP_PREFLIGHT",rev,sha(before),sha(after),flush=True)
    return rev,before,after
def publish(api):
    if os.getenv("SWRLZ_FOLLOWUP_APPROVED")!="1":raise RuntimeError("Release approval unavailable")
    if not api.token:raise RuntimeError("HF_TOKEN missing")
    rev,before,after=stage(api)
    if api.repo_info(SPACE,repo_type="space").sha!=rev:raise RuntimeError("Concurrent Space update")
    oid=None
    try:
        commit=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
           operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(ROOT/"after"/FILE))],
           commit_message="§C preserve prior cited research on explicitly no-lookup followups")
        oid=str(commit.oid)
        actual=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=oid,token=api.token)).read_bytes()
        if actual!=after:raise RuntimeError("Published source hash mismatch")
        manifest=json.loads((ROOT/"manifest.json").read_text());manifest["publishedRevision"]=oid
        (ROOT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
        print("SOURCE_FOLLOWUP_PUBLISHED",rev,oid,flush=True)
    except Exception:
        if oid and api.repo_info(SPACE,repo_type="space").sha==oid:
            reverted=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=oid,
                operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(ROOT/"before"/FILE))],
                commit_message="Rollback §C prior-source reuse")
            print("SOURCE_FOLLOWUP_REVERT",str(reverted.oid),flush=True)
        raise
def rollback(api):
    if os.getenv("SWRLZ_FOLLOWUP_APPROVED")!="1":raise RuntimeError("Rollback approval unavailable")
    manifest=json.loads((ROOT/"manifest.json").read_text())
    rev=manifest.get("publishedRevision")
    if not rev or api.repo_info(SPACE,repo_type="space").sha!=rev:raise RuntimeError("Source head changed; refuse rollback")
    before=(ROOT/"before"/FILE).read_bytes()
    if sha(before)!=manifest["before"]:raise RuntimeError("Backup changed")
    result=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
       operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(ROOT/"before"/FILE))],
       commit_message="Restore §C research context after failed acceptance")
    assert Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=str(result.oid),token=api.token)).read_bytes()==before
    print("SOURCE_FOLLOWUP_ACCEPTANCE_ROLLBACK",rev,str(result.oid),flush=True)
if __name__=="__main__":
    cmd=sys.argv[1:] or ["preflight"]
    if cmd not in (["preflight"],["publish"],["rollback"]):raise SystemExit("preflight|publish|rollback")
    api=HfApi(token=os.environ.get("HF_TOKEN") or None)
    if cmd==["preflight"]:stage(api)
    elif cmd==["publish"]:publish(api)
    else:rollback(api)
