from pathlib import Path

from brain_programming import (
    _code_fingerprint,
    _receipt_semantics,
    candidate_contract_gate,
    programming_intent,
)
from programming_repair_context import (
    build_compact_repair_context,
    enforce_strategy_change,
    strategy_change_directive,
)


def check(condition, message):
    if not condition:
        raise AssertionError(message)


# 1) Guidance after a real receipt must carry the canonical source/evidence while
# compacting the model-facing context instead of depending on old history.
seed = """Write a Python function named checkout_total(cents) that returns dollars and cents.
Preserve exact built-in integer validation and reject bool.
```python
def checkout_total(cents):
    if type(cents) is not int:
        raise TypeError("cents must be int")
    return str(cents // 100)
```
AssertionError: expected '12.34', got '12'
"""
first = programming_intent(seed, [], [], {})
check(first.get("failureEvidence"), first)
guidance = programming_intent(
    "Keep the exact built-in int validation. Use integer arithmetic for the fractional cents; do not use floating point.",
    [],
    [],
    first,
)
check(guidance.get("canonicalCarry") is True, guidance)
check(guidance.get("failureEvidence"), guidance)
check((guidance.get("failureEvidence") or {}).get("continuedByGuidance") is True, guidance)
system, fitted_prompt, context_meta = build_compact_repair_context(
    guidance,
    "Keep the exact built-in int validation. Use integer arithmetic for the fractional cents; do not use floating point.",
    "RESPONSE MODE: CODE-COMPLETE.",
)
check("CANONICAL SOURCE UNDER REPAIR" in system, system)
check("def checkout_total" in system, system)
check("expected '12.34', got '12'" in system, system)
check("integer arithmetic" in fitted_prompt.lower(), fitted_prompt)
check(len(fitted_prompt) <= 1600, len(fitted_prompt))
check(len(system) < 18000, len(system))
check(context_meta.get("mode") == "compact-repair", context_meta)


# 2) Missing-dependency receipts become a hard candidate gate and a targeted
# strategy-change directive instead of three identical retries.
slug_prompt = """Fix this Python without installing anything; use the standard library.
```python
from slugify import slugify

def make_slug(value):
    return slugify(value)
```
ModuleNotFoundError: No module named 'slugify'
"""
slug_intent = programming_intent(slug_prompt, [], [], {})
slug_evidence = slug_intent.get("failureEvidence") or {}
slug_semantics = slug_evidence.get("receiptSemantics") or {}
check("dependency" in (slug_semantics.get("categories") or []), slug_semantics)
check("slugify" in (slug_semantics.get("reportedDependencies") or []), slug_semantics)
same_slug = """```python
from slugify import slugify

def make_slug(value):
    return slugify(value)
```
"""
same_gate = candidate_contract_gate(same_slug, slug_intent, [])
check(same_gate.get("status") == "REJECT", same_gate)
check("dependency-still-referenced:slugify" in (same_gate.get("reasons") or []), same_gate)
directive = strategy_change_directive(slug_intent, same_gate, 2).lower()
check("remove the unavailable dependency" in directive, directive)
check("slugify" in directive, directive)
check("standard library" in directive or "built-ins" in directive, directive)

different_validation = enforce_strategy_change(
    {"status":"PASS","reasons":[]},
    "new-fingerprint",
    "broken-fingerprint",
    "new-fingerprint",
)
check(different_validation.get("status") == "REJECT", different_validation)
check("strategy-repeat-previous-attempt" in (different_validation.get("reasons") or []), different_validation)


# 3) unittest failure tracking records actual tests, never the summary tuple.
unittest_receipt = """FAIL: test_01_currency (tests.test_checkout.CheckoutTests.test_01_currency)
FAIL: test_02_bool (tests.test_checkout.CheckoutTests.test_02_bool)
----------------------------------------------------------------------
FAILED (failures=2)
"""
unittest_semantics = _receipt_semantics(unittest_receipt)
names = unittest_semantics.get("failingTests") or []
check("tests.test_checkout.CheckoutTests.test_01_currency" in names, names)
check("tests.test_checkout.CheckoutTests.test_02_bool" in names, names)
check(not any("failures=" in name for name in names), names)


# 4) Exact artifact revision/source-hash lineage survives through Brain intent.
artifact_source = """```python
def add(a, b):
    return a + b
```
"""
artifact_hash = "abc123-artifact-source-hash"
history = [{
    "id":"assistant-rev2",
    "role":"assistant",
    "text":"Updated pinned code artifact to revision 2.",
    "meta":{
        "codeArtifactId":"artifact-xyz",
        "artifactRevision":2,
        "artifactSourceHash":artifact_hash,
        "artifactSourceSnapshot":artifact_source,
    },
}]
prior = programming_intent("Write a Python add function.", [], [], {})
repair = programming_intent(
    "AssertionError: expected add(2, 3) == 6, got 5",
    history,
    [],
    prior,
)
evidence = repair.get("failureEvidence") or {}
check(evidence.get("repairTargetArtifactId") == "artifact-xyz", evidence)
check(evidence.get("repairTargetArtifactRevision") == 2, evidence)
check(evidence.get("repairTargetArtifactSourceHash") == artifact_hash, evidence)
check(repair.get("baseRevision") == 2, repair)
check(repair.get("baseSourceHash") == artifact_hash, repair)
check(evidence.get("repairSourceFingerprint") == _code_fingerprint(artifact_source), evidence)


# 5) Source-level guards exist for convergence, GitHub conflicts, and stale
# artifact commits. Runtime acceptance will exercise the live path.
root = Path(__file__).resolve().parent
qwen = (root / "qwen_coder_engine.py").read_text(encoding="utf-8")
large = (root / "lfm2_700m_engine.py").read_text(encoding="utf-8")
station = (root / "station.py").read_text(encoding="utf-8")

for owner in (qwen, large):
    check("build_compact_repair_context" in owner, "compact repair context not wired")
    check("strategy_change_directive" in owner, "strategy directive not wired")
    check("enforce_strategy_change" in owner, "strategy gate not wired")
    check("re.fullmatch(pattern,normalized" in owner, "explicit convergence signal missing")
    check("confirmed=any(m in lower" not in owner, "substring convergence logic still present")

check("_github_diagnostic_lock=threading.Lock()" in station, "GitHub write serialization missing")
check("max_attempts=4" in station, "bounded GitHub retry missing")
check("exc.code==409" in station, "409-specific retry missing")
check("RUNTIME_DIAGNOSTIC_PERSIST_RETRY" in station, "409 retry camera missing")
check('"errorPreview"' in station, "GitHub error preview receipt missing")
check('"currentSourceHash"' in station, "artifact source hash missing")
check('"artifactSourceSnapshot"' in station, "exact artifact revision snapshot missing")
check('"SOURCE_HASH_CONFLICT"' in station, "stale artifact hash gate missing")
check('"BASE_REVISION_REQUIRED"' in station, "artifact revision requirement missing")
check('"SOURCE_HASH_REQUIRED"' in station, "artifact source-hash requirement missing")

print("programming-repair-v120 PASS")
