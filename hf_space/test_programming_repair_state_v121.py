from brain_programming import _receipt_semantics, candidate_contract_gate, programming_intent
from programming_repair_context import build_compact_repair_context, strategy_change_directive

def check(ok, value):
    if not ok:
        raise AssertionError(value)

json_receipt = """{
  "passed": 6,
  "total": 9,
  "cases": [
    {"test": "null", "passed": true},
    {"test": "whitespace_spaces", "passed": false, "error": "Expected values to be strictly equal: '' !== '(untitled)'"},
    {"name": "whitespace_tabs", "passed": false, "expected": "(untitled)", "received": ""},
    {"id": "whitespace_newline", "success": false, "expected": "(untitled)", "actual": ""}
  ]
}"""
semantics=_receipt_semantics(json_receipt)
structured=semantics.get("structuredReceipt") or {}
check(structured.get("formats")==["json"],structured)
check(structured.get("failedCaseCount")==3,structured)
check("assertion" in (semantics.get("categories") or []),semantics)
check("behavior-mismatch" in (semantics.get("categories") or []),semantics)
for name in ("whitespace_spaces","whitespace_tabs","whitespace_newline"):
    check(name in (semantics.get("failingTests") or []),semantics)
check(len(semantics.get("expectedActual") or [])>=3,semantics)

seed_prompt="""Fix this Python using only the standard library.
```python
from slugify import slugify

def make_slug(value):
    return slugify(value)
```
ModuleNotFoundError: No module named 'slugify'
"""
seed=programming_intent(seed_prompt,[],[],{})
constraints=seed.get("repairConstraints") or {}
check(constraints.get("unavailableDependencies")==["slugify"],constraints)

candidate="""```python
def make_slug(value):
    return "-".join(ch for ch in value if ch.isalnum())
```
"""
history=[{
    "id":"assistant-slug-v2",
    "role":"assistant",
    "text":candidate,
    "meta":{
        "codeArtifactId":"artifact-slug",
        "artifactRevision":2,
        "artifactSourceHash":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "artifactSourceSnapshot":candidate,
    },
}]
behavior="""{
  "passed": 5,
  "total": 9,
  "cases": [
    {"test": "lowercase", "passed": false, "expected": "hello-web-42", "actual": "H-e-l-l-o-W-e-b-4-2"},
    {"test": "ascii", "passed": false, "expected": "caf", "actual": "C-a-f-é"}
  ]
}"""
second=programming_intent(behavior,history,[],seed)
second_semantics=(second.get("failureEvidence") or {}).get("receiptSemantics") or {}
second_constraints=second.get("repairConstraints") or {}
check((second_semantics.get("reportedDependencies") or [])==[],second_semantics)
check("slugify" in (second_constraints.get("unavailableDependencies") or []),second_constraints)
check("slugify" in (second_constraints.get("carriedUnavailableDependencies") or []),second_constraints)

reintroduced="""```python
from slugify import slugify

def make_slug(value):
    return slugify(value)
```
"""
gate=candidate_contract_gate(reintroduced,second,history)
check(gate.get("status")=="REJECT",gate)
check("dependency-still-referenced:slugify" in (gate.get("reasons") or []),gate)
check("slugify" in ((gate.get("activeRepairConstraints") or {}).get("unavailableDependencies") or []),gate)

directive=strategy_change_directive(second,gate,2).lower()
check("slugify" in directive,directive)
check("remove the unavailable dependency" in directive,directive)

system,_,meta=build_compact_repair_context(second,behavior,"RESPONSE MODE: CODE-COMPLETE.")
check('"unavailableDependencies":["slugify"]' in system,system)
check(meta.get("activeUnavailableDependencyCount")==1,meta)
check(meta.get("carriedUnavailableDependencyCount")==1,meta)

guided=programming_intent(
    "Keep the same API. Fix lowercase and separator behavior with the standard library.",
    history,[],second,
)
check("slugify" in ((guided.get("repairConstraints") or {}).get("unavailableDependencies") or []),guided)

released=programming_intent(
    "slugify is now installed and available. Keep the same API and continue the repair.",
    history,[],guided,
)
released_constraints=released.get("repairConstraints") or {}
check("slugify" not in (released_constraints.get("unavailableDependencies") or []),released_constraints)
check("slugify" in (released_constraints.get("releasedDependencies") or []),released_constraints)

from pathlib import Path
root=Path(__file__).resolve().parent
station=(root/"station.py").read_text(encoding="utf-8")
qwen=(root/"qwen_coder_engine.py").read_text(encoding="utf-8")
large=(root/"lfm2_700m_engine.py").read_text(encoding="utf-8")
for owner in (qwen,large):
    check('"repairConstraints":programming.get("repairConstraints")' in owner,owner[:80])
    check('"structuredReceipt":dict((evidence.get("receiptSemantics")' in owner,owner[:80])
    check('"activeRepairConstraints","structuredReceipt"' in owner,owner[:80])
check('g["repairConstraints"]=copy.deepcopy(constraints)' in station,"station repair constraints camera")
check('"repairConstraints":copy.deepcopy(intent.get("repairConstraints") or {})' in station,"durable repair constraints camera")
check('"structuredReceipt":copy.deepcopy' in station,"durable structured receipt camera")
check('"repairConstraints":None' in station,"active generation repair constraints camera")

print("programming-repair-state-v121 PASS")
