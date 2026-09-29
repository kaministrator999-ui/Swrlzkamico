"""R39 v91: offline-first code truth + local web/UI engineering policy.

Preserves v90 factual-evidence behavior. For programming turns, injects one bounded
system policy that makes local artifact reasoning primary: syntax/structure, symbols,
scope/types/contracts, control/data/state flow, DOM/CSS/layout/state invariants, then
repair + re-verification. Provider-specific current facts remain an external-evidence
boundary rather than being guessed.
"""
from __future__ import annotations

_V90_INSPECT_V91=inspect_engine
_V90_V41_GENERATE_V91=_V41_GENERATE
_V91_CONTRACT="r39-v91-offline-code-truth-web-ui-v1"
_V91_PREFIX="[SWRLZ_CODE_TRUTH v1] "
_V91_POLICY=_V91_PREFIX+(
    "Programming is offline-first. Before confident code claims, verify the supplied/local artifact. "
    "Check syntax and structure; declarations/references, scope, imports/exports, callable names, types/contracts; "
    "trace relevant control flow, data/state mutation, returns, errors, async/event paths, and likely runtime failure. "
    "Prefer concrete defects over speculative style/API criticism. Never invent a bug, API rule, runtime result, or no-op fix. "
    "After a repair, re-trace the affected path and confirm the fix materially addresses the cause. "
    "For HTML/CSS/JavaScript UI work also verify semantic structure, DOM selector/reference wiring, flex/grid/positioning, "
    "stacking/overflow/intrinsic sizing, responsive/mobile/dynamic-viewport behavior, accessibility/focus, interaction state, "
    "long-content robustness, security boundaries, and avoid unnecessary DOM/scroll/input work. "
    "For chat UIs explicitly protect: readable last-message clearance above expanded/collapsed composer; stable pinned/collapsible "
    "and code-container state across scroll/re-render; user-controlled auto-scroll; streaming/final-state separation; timestamps/roles; "
    "mobile keyboard/safe-area behavior; loading/error/empty/disconnected states. "
    "For generated pages: derive requirements/invariants, design regions, generate, verify syntax+DOM, trace interactions/state, "
    "check layout/scroll/overflow+responsive/accessibility+security/performance, repair, then re-verify. "
    "Ordinary browser/UI engineering must not require internet. Use local project docs/manifests/types/tests/examples when available. "
    "Separate artifact truth from external-provider truth: Google, Hugging Face, OAuth, hosted SDK endpoints/scopes/versions may require "
    "current authoritative evidence. Without it, design the boundary/mock/failure states but mark provider-specific details unverified."
)

def _v91_is_programming(payload):
    try:
        profile=_programming_profile(payload)
        return bool(isinstance(profile,dict) and profile.get("active"))
    except Exception:
        return False

def _v91_prepare(payload):
    if not isinstance(payload,dict) or not _v91_is_programming(payload):
        return payload,False
    out=dict(payload);history=list(out.get("history") or [])
    found=False;clean=[]
    for item in history:
        if isinstance(item,dict) and str(item.get("role") or "").lower()=="system":
            text=str(item.get("text") or item.get("content") or "")
            if text.startswith(_V91_PREFIX):
                if not found:
                    clean.append({"role":"system","text":_V91_POLICY});found=True
                continue
        clean.append(item)
    if not found:clean.append({"role":"system","text":_V91_POLICY})
    out["history"]=clean
    return out,True

def _v91_v41_generate(payload,is_cancelled=None):
    prepared,active=_v91_prepare(payload)
    request_id=_request_id(payload) if isinstance(payload,dict) else ""
    if active:
        _camera(request_id,"code-truth-policy-applied",contract=_V91_CONTRACT,offlineFirst=True,webUiEngineering=True,externalProviderBoundary=True)
    for event in _V90_V41_GENERATE_V91(prepared,is_cancelled):yield event

_V41_GENERATE=_v91_v41_generate

def _v91_self_test():
    coding={"prompt":"Create a responsive HTML chat page with a collapsible pinned message and composer.","history":[]}
    noncoding={"prompt":"Tell me a joke.","history":[]}
    cp,ca=_v91_prepare(coding);np,na=_v91_prepare(noncoding)
    texts=[str(x.get("text") or x.get("content") or "") for x in cp.get("history",[]) if isinstance(x,dict)]
    twice,_=_v91_prepare(cp)
    twice_texts=[str(x.get("text") or x.get("content") or "") for x in twice.get("history",[]) if isinstance(x,dict)]
    checks={
        "codingDetected":ca,
        "policyInjected":sum(1 for x in texts if x.startswith(_V91_PREFIX))==1,
        "deduplicated":sum(1 for x in twice_texts if x.startswith(_V91_PREFIX))==1,
        "noncodingUntouched":not na and np is noncoding,
        "offlineFirst":("offline-first" in _V91_POLICY and "must not require internet" in _V91_POLICY),
        "syntaxStructure":("syntax and structure" in _V91_POLICY),
        "controlDataState":("control flow, data/state mutation" in _V91_POLICY),
        "chatUiInvariants":("last-message clearance" in _V91_POLICY and "pinned/collapsible" in _V91_POLICY),
        "providerBoundary":("Google, Hugging Face, OAuth" in _V91_POLICY),
        "repairReverify":("re-trace" in _V91_POLICY and "re-verify" in _V91_POLICY),
    }
    return {"ok":all(checks.values()),"checks":checks,"contract":_V91_CONTRACT}

_V91_SELF_TEST=_v91_self_test()
if not _V91_SELF_TEST.get("ok"):raise RuntimeError("R39_V91_CODE_TRUTH_SELF_TEST_FAILED")

def inspect_engine():
    result=_V90_INSPECT_V91()
    if isinstance(result,dict):result.update({
        "hotServerVersion":"2.1.116",
        "hotRevision":"2.1.116-hot-offline-code-truth-web-ui-v91",
        "offlineCodeTruth":True,
        "webUiEngineeringPolicy":True,
        "externalProviderTruthBoundary":True,
        "codeTruthContract":_V91_CONTRACT,
        "codeTruthSelfTest":dict(_V91_SELF_TEST),
    })
    return result

HOT_SERVER_VERSION="2.1.116"
HOT_REVISION="2.1.116-hot-offline-code-truth-web-ui-v91"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION
