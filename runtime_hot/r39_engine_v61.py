"""R39 v61: context-focus resolver + activation truth over v60.

Builds on v60's cold-load-safe v59 lineage. Adds a conservative turn-level focus
resolver for deictic/correction micro-turns, publishes context-selection diagnostics,
and makes activation state explicit so published authority cannot be confused with
the revision actually hydrated by production.

No history is discarded in this event. The focus resolver supplies bounded routing
metadata while preserving the complete canonical history as semantic authority.
"""
from __future__ import annotations
import urllib.request
import re

_V60_COMMIT="d248a4dacf2446c1d0d836c54482617f8dedc11f"
_V60_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V60_COMMIT}/runtime_hot/r39_engine_v60.py"
_req=urllib.request.Request(_V60_URL,headers={"User-Agent":"swrlz-r39-v61"})
with urllib.request.urlopen(_req,timeout=20) as _response:_source=_response.read(4_000_001)
if len(_source)>4_000_000:raise RuntimeError("R39_V60_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"),_V60_URL+"#v61","exec"),globals(),globals())

_V60_INSPECT=inspect_engine
_V60_GENERATE=generate_events
_V60_CONVERSATION_STATE=_conversation_state
_V60_WITH_CONVERSATION_STATE=_with_conversation_state

HOT_SERVER_VERSION="2.1.72"
HOT_REVISION="2.1.72-hot-context-focus-activation-truth-v61"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION

_DEICTIC_RE=re.compile(
    r"\b(?:this|that|it|same|same thing|that one|this one|the one|other one|the other one|"
    r"that too|this too|it too|those|these)\b",
    re.I,
)
_OTHER_RE=re.compile(
    r"\b(?:the\s+)?other\s+(?:one|option|version|thing|way|approach)\b|"
    r"\bnot\s+(?:this|that)\s+one\b",
    re.I,
)
_SAME_RE=re.compile(
    r"\b(?:same|same\s+thing|same\s+one|do\s+that\s+too|that\s+too|this\s+too|it\s+too)\b",
    re.I,
)
_GENERIC_HISTORY_ACK_RE=re.compile(
    r"^\s*(?:ok(?:ay)?|got it|understood|sure|right|exactly|yeah|yep|yup|lol|lmao|haha+|"
    r"no problem|sounds good|will do)[.!?\s😂🤣😆]*$",
    re.I,
)
_WORD_RE=re.compile(r"[A-Za-z0-9_§𓆩𓆪]+(?:['’-][A-Za-z0-9_]+)?",re.UNICODE)

def _history_entries(payload,limit=24):
    history=list(payload.get("history") or []) if isinstance(payload,dict) else []
    out=[]
    for reverse_distance,turn in enumerate(reversed(history),start=1):
        if not isinstance(turn,dict):continue
        role=str(turn.get("role") or "").strip().lower()
        text=str(turn.get("text") or turn.get("content") or "").strip()
        if role not in {"user","human","assistant","ai"} or not text:continue
        out.append({
            "role":"user" if role in {"user","human"} else "assistant",
            "text":text,
            "distance":reverse_distance,
        })
        if len(out)>=limit:break
    return out

def _history_turn_substantive(entry):
    text=str((entry or {}).get("text") or "").strip()
    if not text:return False
    if _GENERIC_HISTORY_ACK_RE.fullmatch(text):return False
    words=_WORD_RE.findall(text)
    if words:return True
    return bool(re.search(r"\d|[=<>+\-*/]",text))

def _focus_mode(latest,state):
    value=str(latest or "").strip()
    if str(state.get("repair") or "")=="local":
        return "local-repair"
    if _OTHER_RE.search(value):
        return "contrast-within-active-anchor"
    if _SAME_RE.search(value):
        return "reuse-active-anchor"
    if _DEICTIC_RE.search(value):
        return "deictic-active-anchor"
    if state.get("continuation"):
        return "continuation"
    return "none"

def _context_focus(payload,state=None):
    state=dict(state or _V60_CONVERSATION_STATE(payload))
    latest=_latest_user_text(payload) if isinstance(payload,dict) else ""
    mode=_focus_mode(latest,state)
    entries=_history_entries(payload,24)
    candidates=[]
    for entry in entries:
        if _history_turn_substantive(entry):
            candidates.append(entry)
            if len(candidates)>=4:break

    selected=None
    if mode=="local-repair":
        selected=next((e for e in candidates if e["role"]=="assistant"),None)
        if selected is None and candidates:selected=candidates[0]
    elif mode in {"contrast-within-active-anchor","reuse-active-anchor","deictic-active-anchor"}:
        selected=next((e for e in candidates if e["role"]=="assistant"),None)
        if selected is None and candidates:selected=candidates[0]
    elif mode=="continuation":
        selected=candidates[0] if candidates else None

    distance=int(selected["distance"]) if selected else None
    role=str(selected["role"]) if selected else None
    if selected is None:
        confidence="none"
    elif distance<=2:
        confidence="high"
    elif distance<=5:
        confidence="medium"
    else:
        confidence="low"

    referential=bool(mode in {"local-repair","contrast-within-active-anchor","reuse-active-anchor","deictic-active-anchor"})
    ambiguous=bool(referential and (selected is None or confidence=="low"))
    return {
        "mode":mode,
        "targetRole":role,
        "targetDistance":distance,
        "confidence":confidence,
        "ambiguous":ambiguous,
        "candidateCount":len(candidates),
        "historyTurnsConsidered":len(entries),
        "preservesFullHistory":True,
        "destructivePruning":False,
    }

def _conversation_state(payload):
    state=dict(_V60_CONVERSATION_STATE(payload))
    focus=_context_focus(payload,state)
    state.update({
        "contextFocusMode":focus.get("mode"),
        "contextTargetRole":focus.get("targetRole"),
        "contextTargetDistance":focus.get("targetDistance"),
        "contextFocusConfidence":focus.get("confidence"),
        "contextFocusAmbiguous":focus.get("ambiguous"),
    })
    return state

def _focus_prompt(focus):
    target="none"
    if focus.get("targetRole"):
        target=f"{focus.get('targetRole')}@history_distance_{focus.get('targetDistance')}"
    return (
        "[SWRLZ_CONTEXT_FOCUS v1] Routing evidence only; canonical conversation history remains authority. "
        f"mode={focus.get('mode')}; target={target}; confidence={focus.get('confidence')}; "
        f"ambiguous={str(bool(focus.get('ambiguous'))).lower()}; candidates={focus.get('candidateCount')}. "
        "Use the selected anchor to focus attention, not to discard other turns. "
        "For 'other one' or equivalent contrast, inspect alternatives inside the active anchor before considering older turns. "
        "For local correction, repair the rejected detail in the active assistant output while preserving unaffected accepted structure. "
        "If focus is ambiguous, infer only what the literal history supports and do not manufacture a referent."
    )

def _with_conversation_state(payload):
    enriched,state=_V60_WITH_CONVERSATION_STATE(payload)
    if not isinstance(enriched,dict):
        return enriched,state
    focus=_context_focus(payload,state)
    out=dict(enriched)
    history=list(out.get("history") or [])
    marker={"role":"system","text":_focus_prompt(focus)}
    insert_at=1 if history and str(history[0].get("role") or "").lower()=="system" else 0
    history.insert(insert_at,marker)
    out["history"]=history
    state=dict(state)
    state.update({
        "contextFocusMode":focus.get("mode"),
        "contextTargetRole":focus.get("targetRole"),
        "contextTargetDistance":focus.get("targetDistance"),
        "contextFocusConfidence":focus.get("confidence"),
        "contextFocusAmbiguous":focus.get("ambiguous"),
    })
    return out,state

def _context_acceptance_self_test():
    cases=[]
    def add(name,payload,expected):
        try:
            state=_conversation_state(payload)
            focus=_context_focus(payload,state)
            failures=[]
            for key,want in expected.items():
                got=focus.get(key)
                if callable(want):
                    if not want(got):failures.append(f"{key}={got!r}")
                elif got!=want:failures.append(f"{key}={got!r} expected {want!r}")
            cases.append({"name":name,"ok":not failures,"failures":failures})
        except Exception as exc:
            cases.append({"name":name,"ok":False,"failures":[f"{type(exc).__name__}: {exc}"]})

    add(
        "other-one-stays-inside-active-answer",
        {"prompt":"No, use the other one.","history":[
            {"role":"user","text":"Give me two implementation approaches for the cache."},
            {"role":"assistant","text":"Approach A uses local state. Approach B uses the shared runtime store."},
        ]},
        {"mode":"local-repair","targetRole":"assistant","targetDistance":1,"confidence":"high"},
    )
    add(
        "same-thing-targets-active-answer",
        {"prompt":"Do that too.","history":[
            {"role":"user","text":"Add request IDs to the error logger."},
            {"role":"assistant","text":"The logger now includes request IDs and terminal state."},
        ]},
        {"mode":"reuse-active-anchor","targetRole":"assistant","targetDistance":1},
    )
    add(
        "ack-bridge-is-skipped",
        {"prompt":"Can you do that too?","history":[
            {"role":"user","text":"Make the diagnostics include engine revision."},
            {"role":"assistant","text":"The diagnostics now include the engine revision and request ID."},
            {"role":"user","text":"Yeah"},
            {"role":"assistant","text":"Right."},
        ]},
        {"targetRole":"assistant","targetDistance":3,"confidence":"medium"},
    )
    add(
        "correction-prefers-assistant-output",
        {"prompt":"No, not the icon, the label.","history":[
            {"role":"user","text":"Update the toolbar icon and label."},
            {"role":"assistant","text":"I changed the toolbar icon but left the label unchanged."},
        ]},
        {"mode":"local-repair","targetRole":"assistant","targetDistance":1},
    )
    add(
        "missing-history-stays-ambiguous",
        {"prompt":"Do that too.","history":[]},
        {"ambiguous":True,"targetRole":None,"confidence":"none"},
    )
    passed=sum(1 for case in cases if case["ok"])
    return {
        "ok":passed==len(cases),
        "passed":passed,
        "total":len(cases),
        "failures":[case for case in cases if not case["ok"]],
        "contract":"swrlz_context_focus_acceptance_v1",
    }

def inspect_engine():
    result=_V60_INSPECT()
    if isinstance(result,dict):
        result.update({
            "hotServerVersion":HOT_SERVER_VERSION,
            "hotRevision":HOT_REVISION,
            "contextFocusResolver":True,
            "contextFocusPreservesFullHistory":True,
            "contextFocusDestructivePruning":False,
            "deicticAnchorResolution":True,
            "localCorrectionAssistantAnchor":True,
            "otherOneResolvesWithinActiveAnchor":True,
            "contextFocusAcceptanceSelfTest":_context_acceptance_self_test(),
            "contextFocusContract":"swrlz_context_focus_v1",
            "activationTruthContract":"swrlz_runtime_activation_truth_v1",
            "publishedRevision":HOT_REVISION,
            "v60SourceCommit":_V60_COMMIT,
        })
    return result

def generate_events(payload,is_cancelled=None):
    request_id=_request_id(payload) if isinstance(payload,dict) else ""
    state=_conversation_state(payload) if isinstance(payload,dict) else {}
    _camera(
        request_id,"context-focus",
        contract="swrlz_context_focus_v1",
        mode=state.get("contextFocusMode"),
        targetRole=state.get("contextTargetRole"),
        targetDistance=state.get("contextTargetDistance"),
        confidence=state.get("contextFocusConfidence"),
        ambiguous=bool(state.get("contextFocusAmbiguous")),
        preservesFullHistory=True,
    )
    for event in _V60_GENERATE(payload,is_cancelled):yield event
