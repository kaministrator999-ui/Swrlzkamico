#!/usr/bin/env python3
"""Guarded §C small-HTML output sizing; retain large page and source-edit budgets."""
import ast,hashlib,json,os,re,sys
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
SPACE="kamiloki/Swyrlz"
FILE="qwen_coder_engine.py"
OUT=Path("reports/swrlz-small-html-budget")
MARK="swrlz-small-html-scope-budget-v1"
ANCHOR='''    delivery_output_limit=(512 if source_change_mode=="plan" else 2048 if source_change_mode else budget_policy["tokens"])'''
INSERT='''    # swrlz-small-html-scope-budget-v1: prevent small examples from inheriting
    # the extended 8192-token multi-file page generation tier.
    # Keep full budgets for complex pages, large prior sources and real projects.
    _small_html=bool(
        web_page_delivery and not source_change_mode
        and len(prompt)<380
        and re.search(r"(?i)\\b(?:short|small|simple|single[- ]page|single[- ]file|"
                      r"counter|color picker|two[- ]column cards|button|reset|decrement)\\b",prompt)
        and not re.search(r"(?i)\\b(?:studio|dashboard|engine|framework|three\\.js|"
                          r"3d|multi[- ]page|complex|extensive|production app|advanced)\\b",prompt)
        and not any(m.get("role")=="assistant" and
                    len(str(m.get("content") or ""))>10000 for m in history[-5:])
    )
    if _small_html:
        budget_policy={**budget_policy,"tokens":min(3072,int(budget_policy["tokens"])),
                       "tier":"compact-complete-html"}
        system+=("\\nCOMPACT WEB EXAMPLE: Implement one complete, self-contained HTML page "
                 "with only the requested working controls and necessary responsive CSS. "
                 "No fake navigation, speculative features, duplicates, empty placeholders "
                 "or long explanatory preambles. Aim for concise code; finish all tags "
                 "and handlers inside the output budget.")
    delivery_output_limit=(512 if source_change_mode=="plan" else 2048 if source_change_mode else budget_policy["tokens"])'''
ANCHOR2='''    if not source_change_mode:
        budget_policy=source_sized_budget(model,programming,history,budget_policy)
        delivery_output_limit=budget_policy["tokens"]'''
INSERT2='''    if not source_change_mode:
        budget_policy=source_sized_budget(model,programming,history,budget_policy)
        if _small_html:
            budget_policy={**budget_policy,"tokens":min(3072,int(budget_policy["tokens"])),
                           "tier":"compact-complete-html"}
        delivery_output_limit=budget_policy["tokens"]'''
def sha(x):return hashlib.sha256(x).hexdigest()
def replace_one(s,a,b,n):
    if s.count(a)!=1:raise RuntimeError(f"Live coder source changed for {n}: {s.count(a)} matches")
    return s.replace(a,b,1)
def build(original):
    s=original.decode("utf-8")
    if MARK in s:raise RuntimeError("Candidate already deployed")
    s=replace_one(s,ANCHOR,INSERT,"pre-model budget")
    s=replace_one(s,ANCHOR2,INSERT2,"post-model budget")
    compile(s,FILE,"exec")
    return s.encode("utf-8")
def static_checks(s):
    t=s.decode()
    root=ast.parse(t)
    fn=next(n for n in root.body if isinstance(n,ast.FunctionDef) and n.name=="generate_events")
    f=ast.get_source_segment(t,fn)
    for q in ("_small_html=bool(", '"tier":"compact-complete-html"', "delivery_output_limit=budget_policy", "source_sized_budget(model,programming,history,budget_policy)","len(prompt)<380"):
        if q not in f:raise RuntimeError("Missing budget boundary "+q)
    for prompt,expected in [
      ("Write a short single-file HTML page with one button.",True),
      ("Create a complete HTML counter with a working + button. Keep it small.",True),
      ("Create a single-page color picker.",True),
      ("Build a 3D game engine in HTML.",False),
      ("Create a complex dashboard with many features.",False)]:
        matched=bool(len(prompt)<380 and re.search(r"(?i)\b(?:short|small|simple|single[- ]page|single[- ]file|counter|color picker|two[- ]column cards|button|reset|decrement)\b",prompt)
             and not re.search(r"(?i)\b(?:studio|dashboard|engine|framework|three\.js|3d|multi[- ]page|complex|extensive|production app|advanced)\b",prompt))
        if matched!=expected:raise AssertionError("Scope mismatch "+prompt)
    print("SMALL_HTML_BUDGET_STATIC_ACCEPTED 10",flush=True)
def preflight(api):
    rev=api.repo_info(SPACE,repo_type="space").sha
    before=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=rev,token=api.token)).read_bytes()
    after=build(before);static_checks(after)
    (OUT/"before").mkdir(parents=True,exist_ok=True);(OUT/"after").mkdir(parents=True,exist_ok=True)
    (OUT/"before"/FILE).write_bytes(before);(OUT/"after"/FILE).write_bytes(after)
    (OUT/"manifest.json").write_text(json.dumps({"revision":rev,"before":sha(before),"after":sha(after),"file":FILE},indent=2))
    print("SMALL_HTML_BUDGET_PREFLIGHT",rev,sha(before),sha(after),flush=True)
    return rev,before,after
def main():
    cmd=sys.argv[1:] or ["preflight"]
    if cmd not in (["preflight"],["publish"],["rollback"]):raise RuntimeError("Expected preflight/publish/rollback")
    if cmd in (["publish"],["rollback"]) and os.environ.get("SWRLZ_SMALL_HTML_APPROVED")!="1":raise RuntimeError("Owner release approval missing")
    api=HfApi(token=os.environ.get("HF_TOKEN") or None)
    if cmd==["rollback"]:
        manifest=json.loads((OUT/"manifest.json").read_text())
        published=str(manifest.get("publishedRevision") or "")
        if not published or api.repo_info(SPACE,repo_type="space").sha!=published:
            raise RuntimeError("Refusing rollback: HF head no longer matches this release")
        original=(OUT/"before"/FILE).read_bytes()
        if sha(original)!=manifest.get("before"):raise RuntimeError("Rollback snapshot checksum mismatch")
        done=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=published,
            operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"before"/FILE))],
            commit_message="Rollback §C short-HTML budget after failed live acceptance")
        written=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=str(done.oid),token=api.token)).read_bytes()
        if written!=original:raise RuntimeError("Post-rollback source mismatch")
        print("SMALL_HTML_BUDGET_ACCEPTANCE_ROLLBACK",published,str(done.oid),flush=True)
        return
    rev,before,after=preflight(api)
    if cmd==["preflight"]:return
    if api.repo_info(SPACE,repo_type="space").sha!=rev:raise RuntimeError("Concurrent Space source change")
    oid=None
    try:
        commit=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=rev,
            operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"after"/FILE))],
            commit_message="§C right-size short HTML generation; preserve full-scale projects")
        oid=str(commit.oid)
        live=Path(hf_hub_download(SPACE,FILE,repo_type="space",revision=oid,token=api.token)).read_bytes()
        if live!=after:raise RuntimeError("Published HTML budget source mismatch")
        manifest=json.loads((OUT/"manifest.json").read_text())
        manifest["publishedRevision"]=oid
        (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
        print("SMALL_HTML_BUDGET_PUBLISHED",rev,oid,flush=True)
    except Exception:
        if oid and api.repo_info(SPACE,repo_type="space").sha==oid:
            b=api.create_commit(repo_id=SPACE,repo_type="space",parent_commit=oid,
                operations=[CommitOperationAdd(path_in_repo=FILE,path_or_fileobj=str(OUT/"before"/FILE))],
                commit_message="Rollback §C compact HTML budget to previous source")
            print("SMALL_HTML_BUDGET_ROLLED_BACK",b.oid,flush=True)
        raise
if __name__=="__main__":main()
