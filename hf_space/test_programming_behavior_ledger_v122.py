from pathlib import Path

from brain_programming import (
    _code_fingerprint,
    candidate_contract_gate,
    programming_intent,
)
from programming_repair_context import (
    build_compact_repair_context,
    strategy_change_directive,
)


def check(condition, message):
    if not condition:
        raise AssertionError(message)


best_source = """```python
import re
import unicodedata

def make_slug(text):
    value = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")
```
"""
regressed_source = """```python
import re
import unicodedata

def make_slug(text):
    value = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^A-Za-z0-9]+", "-", value)
    return value.strip("-")
```
"""
new_candidate = """```python
import re
import unicodedata

def make_slug(text):
    value = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").casefold()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")
```
"""

seed_prompt = """Fix this Python function. Do not install anything; use only the Python standard library.
```python
from slugify import slugify

def make_slug(text):
    return slugify(text)
```
ModuleNotFoundError: No module named 'slugify'
"""
seed = programming_intent(seed_prompt, [], [], {})
check("slugify" in ((seed.get("repairConstraints") or {}).get("unavailableDependencies") or []), seed)

history1 = [{
    "id": "assistant-r1",
    "role": "assistant",
    "text": best_source,
    "meta": {
        "codeArtifactId": "artifact-slug",
        "artifactRevision": 1,
        "artifactSourceHash": "1" * 64,
        "artifactSourceSnapshot": best_source,
    },
}]
receipt_5_of_9 = """{
  "passed": 5,
  "total": 9,
  "cases": [
    {"test":"test_00","passed":false,"expected":"hello-web-42","actual":"hello-web-42-"},
    {"test":"test_01","passed":false,"expected":"github-pages","actual":"github--pages"},
    {"test":"test_02","passed":false,"expected":"caf","actual":"cafe"},
    {"test":"test_03","passed":true},
    {"test":"test_04","passed":true},
    {"test":"test_05","passed":true},
    {"test":"test_06","passed":true},
    {"test":"test_07","passed":false,"expected":"x","actual":"x-"},
    {"test":"test_api_signature","passed":true}
  ]
}"""
state1 = programming_intent(receipt_5_of_9, history1, [], seed)
ledger1 = state1.get("behaviorLedger") or {}
check(ledger1.get("currentScore") == {"passed":5,"total":9,"failed":4}, ledger1)
check(ledger1.get("bestKnownScore") == {"passed":5,"total":9,"failed":4}, ledger1)
check((ledger1.get("bestKnownArtifact") or {}).get("revision") == 1, ledger1)
check(state1.get("behaviorRepairBase",{}).get("mode") == "latest-failing-source", state1.get("behaviorRepairBase"))

history2 = history1 + [{
    "id": "assistant-r2",
    "role": "assistant",
    "text": "Updated pinned code artifact to revision 2.",
    "meta": {
        "codeArtifactId": "artifact-slug",
        "updatedCodeArtifactId": "artifact-slug",
        "artifactRevision": 2,
        "artifactSourceHash": "2" * 64,
        "artifactSourceSnapshot": regressed_source,
    },
}]
receipt_4_of_9 = """{
  "passed": 4,
  "total": 9,
  "cases": [
    {"test":"test_00","passed":false,"expected":"hello-web-42","actual":"Hello-Web-42"},
    {"test":"test_01","passed":false,"expected":"github-pages","actual":"GitHub-Pages"},
    {"test":"test_02","passed":false,"expected":"caf","actual":"Cafe"},
    {"test":"test_03","passed":true},
    {"test":"test_04","passed":true},
    {"test":"test_05","passed":false,"expected":"a1b2","actual":"A1B2"},
    {"test":"test_06","passed":true},
    {"test":"test_07","passed":false,"expected":"x","actual":"X"},
    {"test":"test_api_signature","passed":true}
  ]
}"""
state2 = programming_intent(receipt_4_of_9, history2, [], state1)
ledger2 = state2.get("behaviorLedger") or {}
base2 = state2.get("behaviorRepairBase") or {}

check(ledger2.get("currentScore") == {"passed":4,"total":9,"failed":5}, ledger2)
check(ledger2.get("bestKnownScore") == {"passed":5,"total":9,"failed":4}, ledger2)
check("test_05" in (ledger2.get("regressedCases") or []), ledger2)
check("test_05" in (ledger2.get("preservePassingCases") or []), ledger2)
check(ledger2.get("rebaseRecommended") is True, ledger2)
check((ledger2.get("bestKnownArtifact") or {}).get("revision") == 1, ledger2)
check((ledger2.get("currentTestedArtifact") or {}).get("revision") == 2, ledger2)
check(base2.get("mode") == "best-known-tested-source", base2)
check(base2.get("revision") == 1, base2)
check(str(state2.get("behaviorRepairBaseSource") or "").strip() == best_source.strip(), state2.get("behaviorRepairBaseSource"))
check(base2.get("sourceFingerprint") == _code_fingerprint(best_source), base2)

# Returning the best tested source unchanged is not accepted as a new repair:
# the latest receipt still contains unresolved failures.
same_best_gate = candidate_contract_gate(best_source, state2, history2)
check(same_best_gate.get("status") == "REJECT", same_best_gate)
check("behavior-repair-base-unchanged" in (same_best_gate.get("reasons") or []), same_best_gate)

# A materially new source can pass structural gates, but remains explicitly
# unverified until a fresh external receipt arrives.
new_gate = candidate_contract_gate(new_candidate, state2, history2)
check("behavior-repair-base-unchanged" not in (new_gate.get("reasons") or []), new_gate)
check(new_gate.get("executionVerified") is False, new_gate)
check(new_gate.get("verificationState") == "AWAITING_EXTERNAL_RECEIPT", new_gate)
gate_ledger = new_gate.get("behaviorLedger") or {}
check("test_05" in (gate_ledger.get("regressedCases") or []), gate_ledger)
check(gate_ledger.get("repairBaseMode") == "best-known-tested-source", gate_ledger)

system, fitted_prompt, context_meta = build_compact_repair_context(
    state2,
    receipt_4_of_9,
    "RESPONSE MODE: CODE-COMPLETE.",
)
check("BEST KNOWN TESTED REPAIR BASE" in system, system)
check("test_05" in system, system)
check("preservePassingCases" in system, system)
check(context_meta.get("behaviorRepairBaseMode") == "best-known-tested-source", context_meta)
check((context_meta.get("behaviorCurrentScore") or {}).get("passed") == 4, context_meta)
check((context_meta.get("behaviorBestKnownScore") or {}).get("passed") == 5, context_meta)
check(context_meta.get("behaviorRegressionCount") >= 1, context_meta)

directive = strategy_change_directive(state2, same_best_gate, 2)
check("REGRESSION DETECTED" in directive, directive)
check("test_05" in directive, directive)
check("best-known tested source" in directive.lower(), directive)

# Camera wiring: summaries are persisted, source body is not copied into the
# durable telemetry schema.
root = Path(__file__).resolve().parent
station = (root / "station.py").read_text(encoding="utf-8")
qwen = (root / "qwen_coder_engine.py").read_text(encoding="utf-8")
large = (root / "lfm2_700m_engine.py").read_text(encoding="utf-8")
for owner in (qwen, large):
    check('"behaviorLedger":{' in owner, "repair diagnostic behavior camera missing")
    check('"behaviorRepairBase":dict(programming.get("behaviorRepairBase")' in owner, "repair-base camera missing")
    check('"behaviorLedger","structuredReceipt"' in owner, "candidate behavior camera propagation missing")
check('g["behaviorLedger"]=copy.deepcopy(behavior)' in station, "Station behavior camera missing")
check('"behaviorLedger":behavior_camera' in station, "durable behavior camera missing")
check('"behaviorRepairBase":copy.deepcopy(intent.get("behaviorRepairBase") or {})' in station, "durable repair-base camera missing")
check('"behaviorRepairBaseSource"' not in station[station.find('github_telemetry={'):station.find('g["githubTelemetryPersistence"]')], "source body leaked into durable camera schema")

print("programming-behavior-ledger-v122 PASS")
