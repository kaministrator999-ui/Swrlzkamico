#!/usr/bin/env python3
"""§C short explanation decode cap: current-intent only; revision-pinned one-file release.

For a short explicit no-code explanation, prevent the generic large output budget
from tying up the resident CPU model. Preserve all other modes, context, model,
account, §E and routing paths. Never publish without approved source revision.
"""
from __future__ import annotations
import ast,hashlib,json,os,re,sys
from pathlib import Path

SPACE="kamiloki/Swyrlz"
FILE="lfm2_700m_engine.py"
ROOT=Path("reports/short-explanation-budget-v1")
TAG="swrlz-short-explicit-prose-budget-v1"
OLD='''        elif mode.startswith("RESPONSE MODE: CODE-"):'''
NEW='''        # swrlz-short-explicit-prose-budget-v1: a short explanation-only
        # instruction never needs the entire normal/longform decode budget.
        # This does not affect source/factual/coding/music/complex explanations.
        elif (mode.startswith("RESPONSE MODE: EXPLANATION-ONLY")
              and len(prompt)<=220 and re.search(
                  r"(?i)\b(?:for now|briefly|no code yet|"
                  r"without\s+(?:writing\s+)?code|explain\s+the\s+goal)\b",prompt)):
            response_tokens=min(192,available_output_tokens);temperature=0.28
        elif mode.startswith("RESPONSE MODE: CODE-"):'''

def sha(raw):return hashlib.sha256(raw).hexdigest()

def patch(raw):
    source=raw.decode("utf-8")
    if TAG in source:raise RuntimeError("SHORT_PROSE_BUDGET_ALREADY_INSTALLED")
    if source.count(OLD)!=1:raise RuntimeError("SOURCE_DRIFT_EXPLANATION_OUTPUT_GATE")
    if "swrlz-lfm-prose-delivery-v1" not in source:
        raise RuntimeError("EXISTING_EXPLANATION_ONLY_PROFILE_MISSING")
    after=source.replace(OLD,NEW,1)
    ast.parse(after,filename=FILE)
    if after.count(TAG)!=1 or after.replace(NEW,OLD,1)!=source:
        raise AssertionError("NOT_EXACT_ONE_SEAM_REPAIR")
    return after.encode("utf-8")

def tests(raw,new):
    s=new.decode()
    nodes=ast.parse(s).body
    candidates=[n for n in nodes if isinstance(n,ast.FunctionDef)
                and n.name=="generate_events"]
    assert candidates,"No generation entrypoint"
    assert s.count("response_tokens=min(192,available_output_tokens);temperature=0.28")==1
    assert s.count('mode.startswith("RESPONSE MODE: EXPLANATION-ONLY")')==1
    # Exercise operational predicate, including the boundary conditions.
    def cap(prompt,mode):
        return (mode.startswith("RESPONSE MODE: EXPLANATION-ONLY")
                and len(prompt)<=220
                and bool(re.search(
                  r"(?i)\b(?:for now|briefly|no code yet|"
                  r"without\s+(?:writing\s+)?code|explain\s+the\s+goal)\b",prompt)))
    scenarios=[
      ("I eventually want a JavaScript square(n) function. For now explain the goal WITHOUT writing code.","RESPONSE MODE: EXPLANATION-ONLY",True),
      ("An existing Python function add(a,b) incorrectly subtracts. Explain the small repair, no code yet.","RESPONSE MODE: EXPLANATION-ONLY",True),
      ("Now implement square(n) in a code block.","RESPONSE MODE: CODE-COMPLETE",False),
      ("Briefly describe a complicated source-backed factual query.","RESPONSE MODE: SOURCE-FACTS-FIRST",False),
      ("Briefly provide complete original song lyrics with verse and chorus.","RESPONSE MODE: ORIGINAL-SONG",False),
      ("Explain the architecture thoroughly and discuss the details of multiple modules. "*8,"RESPONSE MODE: EXPLANATION-ONLY",False),
    ]
    for prompt,mode,wanted in scenarios:
        if cap(prompt,mode)!=wanted:raise AssertionError("SHORT_PROSE_SCOPE_REGRESSION:"+repr(prompt))
    if new.decode().replace(NEW,OLD,1).encode()!=raw:
        raise AssertionError("ORIGINAL_SOURCE_NOT_RECOVERABLE")
    print("SHORT_PROSE_BUDGET_OFFLINE_PASS",len(scenarios)+3,flush=True)

def snapshot(*,expected=""):
    from huggingface_hub import HfApi,hf_hub_download
    api=HfApi(token=os.getenv("HF_TOKEN") or None)
    rev=str(api.repo_info(SPACE,repo_type="space").sha)
    if expected and rev!=expected:raise RuntimeError("SPACE_REVISION_CHANGED")
    if not re.fullmatch(r"[0-9a-f]{40}",rev):raise RuntimeError("SPACE_REVISION_INVALID")
    before=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=rev,token=api.token)).read_bytes()
    after=patch(before)
    tests(before,after)
    (ROOT/"before").mkdir(parents=True,exist_ok=True)
    (ROOT/"after").mkdir(parents=True,exist_ok=True)
    (ROOT/"before"/FILE).write_bytes(before)
    (ROOT/"after"/FILE).write_bytes(after)
    record={"target":SPACE,"revision":rev,"file":FILE,"beforeSha256":sha(before),
            "afterSha256":sha(after),"published":False,"sourceIntegrity":True}
    (ROOT/"manifest.json").write_text(json.dumps(record,indent=2)+"\n")
    print("SHORT_PROSE_BUDGET_PREFLIGHT",json.dumps(record),flush=True)
    return api,record

def publish():
    if os.getenv("SWRLZ_SHORT_PROSE_APPROVED")!="1":
        raise RuntimeError("OWNER_APPROVAL_REQUIRED")
    expected=os.getenv("SWRLZ_EXPECTED_SPACE_REVISION","")
    if not re.fullmatch(r"[0-9a-f]{40}",expected):
        raise RuntimeError("EXACT_REVISION_REQUIRED")
    if not os.getenv("HF_TOKEN"):raise RuntimeError("HF_TOKEN_REQUIRED")
    from huggingface_hub import CommitOperationAdd,hf_hub_download
    api,record=snapshot(expected=expected)
    before=(ROOT/"before"/FILE).read_bytes()
    after=(ROOT/"after"/FILE).read_bytes()
    if api.repo_info(SPACE,repo_type="space").sha!=expected:
        raise RuntimeError("CONCURRENT_SPACE_SOURCE_CHANGED")
    published=None
    try:
        change=api.create_commit(
            repo_id=SPACE,repo_type="space",parent_commit=expected,
            operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=after)],
            commit_message="§C bound short explicit prose generation after no-code instructions")
        published=str(change.oid)
        verified=Path(hf_hub_download(SPACE,FILE,repo_type="space",
                                      revision=published,token=api.token)).read_bytes()
        if verified!=after or api.repo_info(SPACE,repo_type="space").sha!=published:
            raise RuntimeError("PUBLISHED_SOURCE_INTEGRITY_MISMATCH")
        record.update({"published":True,"publishedRevision":published,"verifiedReadback":True})
        (ROOT/"manifest.json").write_text(json.dumps(record,indent=2)+"\n")
        print("SHORT_PROSE_BUDGET_PUBLISHED",json.dumps(record),flush=True)
    except Exception:
        if published and api.repo_info(SPACE,repo_type="space").sha==published:
            api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=published,
                operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=before)],
                commit_message="Rollback short explanation budget to original source")
        raise

def rollback():
    if os.getenv("SWRLZ_SHORT_PROSE_APPROVED")!="1":
        raise RuntimeError("ROLLBACK_APPROVAL_REQUIRED")
    from huggingface_hub import HfApi,CommitOperationAdd,hf_hub_download
    api=HfApi(token=os.environ["HF_TOKEN"])
    m=json.loads((ROOT/"manifest.json").read_text())
    current=m.get("publishedRevision")
    if not m.get("published") or api.repo_info(SPACE,repo_type="space").sha!=current:
        raise RuntimeError("NEWER_SOURCE_EXISTS_REFUSE_ROLLBACK")
    before=(ROOT/"before"/FILE).read_bytes()
    if sha(before)!=m["beforeSha256"]:raise RuntimeError("BACKUP_CHANGED")
    change=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=current,
        operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=before)],
        commit_message="Rollback §C brief prose budget after failed live evaluation")
    restored=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=str(change.oid),
                                  token=api.token)).read_bytes()
    if restored!=before:raise RuntimeError("ROLLBACK_READBACK_MISMATCH")
    print("SHORT_PROSE_BUDGET_ROLLED_BACK",json.dumps({"from":current,"to":str(change.oid)}))

if __name__=="__main__":
    cmd=sys.argv[1:] or ["inspect"]
    if cmd==["inspect"]:snapshot(expected=os.getenv("SWRLZ_EXPECTED_SPACE_REVISION",""))
    elif cmd==["publish"]:publish()
    elif cmd==["rollback"]:rollback()
    else:raise SystemExit("inspect|publish|rollback")
