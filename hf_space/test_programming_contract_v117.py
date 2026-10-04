from brain_programming import programming_intent, candidate_contract_gate

def check(condition, message):
    if not condition:
        raise AssertionError(message)

# Explicit requested language is a hard contract.
html_intent=programming_intent("Can you write me an example html page",[],[],{})
html_contract=html_intent["intentContract"]["languageContract"]
check(html_contract["requestedLanguages"]==["html"], html_contract)
check("python" not in html_contract["allowedLanguages"], html_contract)

bad_html="""```python
from flask import Flask
app = Flask(__name__)
```
"""
bad_gate=candidate_contract_gate(bad_html,html_intent,[])
check(bad_gate["status"]=="REJECT", bad_gate)
check("missing-required-language:html" in bad_gate["reasons"], bad_gate)
check("language-contract-mismatch:python" in bad_gate["reasons"], bad_gate)

good_html="""```html
<!doctype html>
<html><body><h1>Hello</h1></body></html>
```
"""
good_gate=candidate_contract_gate(good_html,html_intent,[])
check(good_gate["status"]=="PASS", good_gate)

# The same rule generalizes beyond HTML.
for request,wrong_language,wrong_source,required in (
    ("Write this in Kotlin","java","```java\nclass Demo {}\n```","kotlin"),
    ("Write a C++ function","python","```python\ndef demo():\n    return 1\n```","cpp"),
    ("Write an SQL query","python","```python\nprint('query')\n```","sql"),
    ("Write a Rust function","javascript","```javascript\nfunction demo(){ return 1; }\n```","rust"),
):
    intent=programming_intent(request,[],[],{})
    gate=candidate_contract_gate(wrong_source,intent,[])
    check(gate["status"]=="REJECT",(request,gate))
    check("missing-required-language:"+required in gate["reasons"],(request,gate))
    check("language-contract-mismatch:"+wrong_language in gate["reasons"],(request,gate))

# Returned compiler/runtime evidence rebinds to the exact generated artifact.
original_request="Write a Python function that hashes text with hashlib"
prior=programming_intent(original_request,[],[],{})
history=[
    {"id":"u1","role":"user","text":original_request,"meta":{}},
    {"id":"a1","role":"assistant","text":"```python\ndef digest(value):\n    return hashlib.sha256(value.encode()).hexdigest()\n```","meta":{"codeArtifactId":"artifact-1","artifactRevision":1}},
]
receipt="Traceback (most recent call last):\nNameError: name 'hashlib' is not defined"
repair=programming_intent(receipt,history,[],prior)
check(repair["changeClass"]=="fix",repair)
check(repair["artifactContinuation"] is True,repair)
check(repair["artifactMutationRequested"] is True,repair)
check(repair["artifactTargetId"]=="artifact-1",repair)
check(repair["baseRevision"]==1,repair)
check(repair["failureEvidence"]["receiptSemantics"]["reportedSymbols"]==["hashlib"],repair["failureEvidence"])

still_bad="""```python
def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()
```
"""
bad_repair_gate=candidate_contract_gate(still_bad,repair,history)
check(bad_repair_gate["status"]=="REJECT",bad_repair_gate)

fixed="""```python
import hashlib

def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()
```
"""
fixed_gate=candidate_contract_gate(fixed,repair,history)
check(fixed_gate["status"]=="PASS",fixed_gate)
check(fixed_gate["diagnosticGrounded"] is True,fixed_gate)
check(fixed_gate["executionVerified"] is False,fixed_gate)
check(fixed_gate["verificationState"]=="AWAITING_EXTERNAL_RECEIPT",fixed_gate)

# A vague failure must request evidence rather than hallucinating a diagnosis.
vague=programming_intent("it doesn't work",history,[],prior)
check(vague["needsFailureEvidence"] is True,vague)
check(vague["repairLifecycleState"]=="EVIDENCE_REQUIRED",vague)
check(vague["artifactTargetId"]=="artifact-1",vague)
check(vague["artifactMutationRequested"] is False,vague)
check("Paste the compiler" in vague["evidenceRequest"],vague)

# The evidence-request prose turn must not steal repair ownership from the code artifact.
history_after_request=history+[
    {"id":"a2","role":"assistant","text":vague["evidenceRequest"],"meta":{"requestId":"r2","state":"COMPLETE"}},
]
receipt_after_request=programming_intent(receipt,history_after_request,[],vague)
check(receipt_after_request["artifactTargetId"]=="artifact-1",receipt_after_request)
check(receipt_after_request["artifactTargetMessageId"]=="a1",receipt_after_request)
check(receipt_after_request["artifactMutationRequested"] is True,receipt_after_request)
check(receipt_after_request["failureEvidence"]["repairTargetArtifactId"]=="artifact-1",receipt_after_request["failureEvidence"])

# First-turn user-owned source + compiler receipt is also supported.
inline="""Fix this Python code.
```python
def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()
```
NameError: name 'hashlib' is not defined
"""
user_seed=programming_intent(inline,[],[],{})
check(user_seed["failureEvidence"] is not None,user_seed)
check(user_seed["failureEvidence"]["receiptSourceOwnership"]=="user-seed",user_seed["failureEvidence"])
check("def digest" in user_seed["failureEvidence"]["repairSource"],user_seed["failureEvidence"])
check(user_seed["intentContract"]["languageContract"]["requestedLanguages"]==["python"],user_seed["intentContract"])

print("programming-contract-v117 PASS")
