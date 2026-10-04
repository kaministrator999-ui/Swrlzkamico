from brain_programming import (
    _code_fingerprint,
    _failure_receipt_detected,
    _receipt_semantics,
    candidate_contract_gate,
    programming_intent,
)


def check(condition, message):
    if not condition:
        raise AssertionError(message)


# 1) Source/requirements may mention an error type without constituting execution evidence.
clean_html = """Update this HTML example. The requirement text must literally mention TypeError, but this is not an execution log.
```html
<!doctype html>
<html>
<body>
<script>
function validate(value) {
    if (value === null) throw new TypeError("value required");
    return value;
}
</script>
</body>
</html>
```
"""
check(_failure_receipt_detected(clean_html) is False, "clean source was misclassified as a failure receipt")
clean_intent = programming_intent(clean_html, [], [], {})
check(clean_intent.get("codingTask") is True, clean_intent)
check(clean_intent.get("failureEvidence") is None, clean_intent)


# 2) Native TypeScript diagnostic form must bridge into structured repair evidence.
ts_prompt = """Fix this TypeScript function and keep the same signature.
```typescript
function label(value: string | null): string {
    return value.trim();
}
```
src/label.ts(2,12): error TS18047: 'value' is possibly 'null'.
"""
ts_intent = programming_intent(ts_prompt, [], [], {})
ts_evidence = ts_intent.get("failureEvidence") or {}
ts_semantics = ts_evidence.get("receiptSemantics") or {}
check(ts_evidence.get("receiptSourceOwnership") == "user-seed", ts_evidence)
check(ts_evidence.get("repairComparator") == "canonical-repair-source", ts_evidence)
check("typecheck" in (ts_semantics.get("categories") or []), ts_semantics)
check("src/label.ts:2:12" in (ts_semantics.get("sourceLocations") or []), ts_semantics)
check(ts_evidence.get("repairSourceFingerprint") == _code_fingerprint(ts_evidence.get("repairSource") or ""), ts_evidence)
check("error TS18047" in str(ts_evidence.get("evidence") or ""), ts_evidence)


# 3) Native ESLint output must be recognized and retain file/line/column.
eslint_prompt = """Fix this JavaScript without changing the function name.
```javascript
function userLabel(user) {
    const unused = 1;
    return user.name;
}
```
/workspace/user-label.js
  2:11  error  'unused' is assigned a value but never used  no-unused-vars
✖ 1 problem (1 error, 0 warnings)
"""
eslint_intent = programming_intent(eslint_prompt, [], [], {})
eslint_evidence = eslint_intent.get("failureEvidence") or {}
eslint_semantics = eslint_evidence.get("receiptSemantics") or {}
check(eslint_evidence.get("receiptSourceOwnership") == "user-seed", eslint_evidence)
check("lint" in (eslint_semantics.get("categories") or []), eslint_semantics)
check("/workspace/user-label.js:2:11" in (eslint_semantics.get("sourceLocations") or []), eslint_semantics)


# 4) Structured JSON false results are failures, never passing signals.
json_receipt = '{"test":"currency","passed": false, "expected": "12.34", "actual": "12.00"}'
check(_failure_receipt_detected(json_receipt) is True, json_receipt)
json_semantics = _receipt_semantics(json_receipt)
check(any('"passed": false' in x for x in json_semantics.get("failingSignals") or []), json_semantics)
check(not any('"passed": false' in x for x in json_semantics.get("passingSignals") or []), json_semantics)
check("behavior-mismatch" in (json_semantics.get("categories") or []), json_semantics)


# 5) Common test-runner names must survive semantic extraction.
pytest_receipt = """FAILED tests/test_labels.py::test_blank_label - AssertionError: expected 'Unknown', got ''
1 failed, 8 passed in 0.21s
"""
pytest_semantics = _receipt_semantics(pytest_receipt)
check("tests/test_labels.py::test_blank_label" in (pytest_semantics.get("failingTests") or []), pytest_semantics)
check(any("1 failed" in x for x in pytest_semantics.get("failingSignals") or []), pytest_semantics)
check(any("8 passed" in x for x in pytest_semantics.get("passingSignals") or []), pytest_semantics)


# 6) Canonical repair source must remain the broken user seed even when a newer
# assistant candidate already passes. The same broken seed is rejected; the
# assistant's different corrected implementation is not rejected as unchanged.
history = [
    {
        "id": "a-pass",
        "role": "assistant",
        "text": "```python\ndef cents(total):\n    return f\"{total // 100}.{total % 100:02d}\"\n```",
        "meta": {"codeArtifactId": "artifact-pass", "artifactRevision": 1},
    }
]
seed_prompt = """Original user seed:
```python
def cents(total):
    return str(total // 100)
```
AssertionError: expected '12.34', got '12'
"""
seed_intent = programming_intent(seed_prompt, history, [], {})
seed_evidence = seed_intent.get("failureEvidence") or {}
check(seed_evidence.get("receiptSourceOwnership") == "user-seed", seed_evidence)
check(seed_evidence.get("repairTargetMessageId") == "", seed_evidence)
check(seed_evidence.get("repairSourceFingerprint") == _code_fingerprint("def cents(total):\n    return str(total // 100)"), seed_evidence)

same_seed = "```python\ndef cents(total):\n    return str(total // 100)\n```"
same_gate = candidate_contract_gate(same_seed, seed_intent, history)
check(same_gate.get("status") == "REJECT", same_gate)
check("diagnostic-repair-no-executable-change" in (same_gate.get("reasons") or []), same_gate)

corrected = "```python\ndef cents(total):\n    return f\"{total // 100}.{total % 100:02d}\"\n```"
corrected_gate = candidate_contract_gate(corrected, seed_intent, history)
check("diagnostic-repair-no-executable-change" not in (corrected_gate.get("reasons") or []), corrected_gate)


# 7) A later refusal/prose turn must never become the comparator for a new
# explicitly supplied original seed.
history_with_refusal = history + [
    {
        "id": "a-refusal",
        "role": "assistant",
        "text": "I couldn't produce a candidate that satisfies the programming contract, so I did not return the rejected code.",
        "meta": {},
    }
]
slug_prompt = """Original source:
```python
from slugify import slugify

def make_slug(value):
    return slugify(value)
```
ModuleNotFoundError: No module named 'slugify'
"""
slug_intent = programming_intent(slug_prompt, history_with_refusal, [], {})
slug_evidence = slug_intent.get("failureEvidence") or {}
check(slug_evidence.get("receiptSourceOwnership") == "user-seed", slug_evidence)
check(slug_evidence.get("repairSourceFingerprint") == _code_fingerprint("from slugify import slugify\n\ndef make_slug(value):\n    return slugify(value)"), slug_evidence)
check("dependency" in ((slug_evidence.get("receiptSemantics") or {}).get("categories") or []), slug_evidence)


print("programming-receipts-v119 PASS")
