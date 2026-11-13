"""Focused v6 tests: no risky code edit/repair enters short standalone prefill."""
import ast
import json
import re
from hf_chat_qwen35_coder_prefill_v6 import FAST_CODE_ROUTER,patch_coder,test_patched

namespace={
    "re":re,"json":json,
    "_wyrlz_active_profile":lambda prompt,programming,brief:(
         "⚡ §wyrlzara ∞ Mirror Muse\nDYNAMIC MIRROR: Keep the human's current intent"),
    "CODE_TRUTH_POLICY":"Original request = acceptance contract. Return complete source.",
    "_response_mode":lambda prompt,programming:"RESPONSE MODE: CODE-PYTHON",
}
exec(compile(FAST_CODE_ROUTER,"<standalone-coder-prefill>", "exec"),namespace)
qualifies=namespace["_swrlz_standalone_code_prefill"]
short_policy=namespace["_swrlz_compact_standalone_code_system"]
p={"codingTask":True,
   "intentContract":{"originalRequest":"Write a short Python function.",
       "languageContract":{"explicit":True,"language":"python"}}}
example="Write a short Python function that returns the square of an integer, and show one example."
assert qualifies(example,p,{},[],None)
# Production brain_programming always includes schema-shaped default telemetry.
# It must not force a 2,705-token system prompt for a new standalone function.
default_ledger={"schema":"swrlz-behavior-ledger-v1",
                "suiteKey":"","currentPassingCases":[],"currentFailingCases":[],
                "knownPassingCases":[],"regressedCases":[],"bestKnownArtifact":None}
default_repair={"schema":"swrlz-repair-constraints-v1",
                "unavailableDependencies":[],"forbiddenDependencies":[],
                "currentReceiptDependencies":[]}
assert qualifies(example,p|{"behaviorLedger":default_ledger,
                            "repairConstraints":default_repair}, {}, [], None)
assert not qualifies(example,p|{"behaviorLedger":{
   **default_ledger,"currentFailingCases":["square(3)"]}}, {}, [], None)
assert not qualifies(example,p|{"repairConstraints":{
   **default_repair,"unavailableDependencies":["x"]}}, {}, [], None)
assert qualifies(example,p|{"intentContract":{
    "originalRequest":example,
    "must":["Write a short Python function"],
    "languageContract":{"explicit":True,"language":"python"},
    "acceptanceEvidence":["technical-validity"]*18
}}, {}, [], None)
assert qualifies("Create a simple Python function that adds two integers.",p,{},[],None)
assert qualifies("Show a short JavaScript function for reversing a string.",p,{},[],None)
for prompt in (
 "Can you fix my existing function?", "Rewrite code in our repository",
 "Please edit our §E modeling engine", "Refactor the existing backend model",
 "Implement a server API endpoint", "Debug this failing test",
 "What is the difference between CPU and GPU?", 
 "Write a JavaScript component to deploy with GitHub",
):
    assert not qualifies(prompt,p,{},[],None),prompt
assert not qualifies(example,{"codingTask":False},{},[],None)
for progkey in (
    "failureEvidence","canonicalCarry","artifactContinuation",
    "artifactMutationRequested","artifactTargetId","needsFailureEvidence",
    "newProject","failureHistory","activeRepairConstraints",
):
    assert not qualifies(example,p|{progkey:True},{},[],None),progkey
for payloadkey in ("nativeEditorEvidence","onlineContext","projectThreadEvidence",
                   "forgeContext","githubAction","visionReceipt","pinnedContext"):
    assert not qualifies(example,p,{payloadkey:{"a":1}},[],None),payloadkey
assert not qualifies(example,p,{},[{"role":"user","content":"prior source"}],None)
assert not qualifies(example,p,{},[],"candidate")
assert not qualifies(example,p|{"intentContract":{"originalRequest":example,
    "largeData":"x"*6000}}, {},[],None)
assert not qualifies(example,p|{"intentContract":{"languageContract":{
    "artifactType":"repository"}}}, {},[],None)
text=short_policy(example,p,"Prefer precise explanations","Name: Test User")
assert "§wyrlzara ∞ Mirror Muse" in text
assert "SAVED ASSISTANT CUSTOMIZATION" in text
assert "Name: Test User" in text
assert "RESPONSE MODE: CODE-PYTHON" in text
assert "Original request = acceptance contract" in text
assert '"language":"python"' in text
assert '"originalRequest"' not in text
assert len(text)<2500
print("CODER_V6_UNIT_PASS",json.dumps({
   "fastRequestExampleAllowed":True,
   "complexCodingRoutesUnchanged":True,
   "specializedEvidenceExcluded":True,
   "profileAndMandatoryCodePolicyPreserved":True,
   "originalRequestIncludedByUserMessage":True,
   "nativeCandidateValidationPreserved":True,
}),flush=True)
