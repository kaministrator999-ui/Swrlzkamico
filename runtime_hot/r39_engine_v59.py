"""R39 v59: acceptance-driven completion + trajectory diagnostics.

Builds on v58's planner/base namespace repairs and the complete v56 conversation-planning lineage.
This event adds:
- safer continuation disambiguation for temporal "next ..." phrases;
- referential micro-turn bridging ("do that too", "same thing") without allowing old
  scope to tunnel through a genuinely new substantive task;
- semantic completion floors for explicitly deep/massive work;
- premature-generic-EOS protection for active work stances;
- response-quality telemetry for phrase repetition and prompt echo;
- deterministic in-engine conversation acceptance self-tests.

The acceptance suite tests behavior classes, not user-specific literal phrases.
"""
from __future__ import annotations
import urllib.request
import re

_V58_COMMIT="cf569a7b03c2695b8a9b3ea02d0821110eb44df0"
_V58_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V58_COMMIT}/runtime_hot/r39_engine_v58.py"
_req=urllib.request.Request(_V58_URL,headers={"User-Agent":"swrlz-r39-v59"})
with urllib.request.urlopen(_req,timeout=20) as _response:_source=_response.read(4_000_001)
if len(_source)>4_000_000:raise RuntimeError("R39_V58_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"),_V58_URL+"#v59","exec"),globals(),globals())

_V58_INSPECT=inspect_engine
_V58_GENERATE=generate_events
_V58_CONVERSATION_STATE=_conversation_state
_V58_PLAN_RESPONSE_BUDGET=_plan_response_budget
_V58_RESPONSE_CONTRACT=_response_contract
_V58_RESPONSE_CONTRACT_GAPS=_response_contract_gaps
_V58_IS_CONTINUATION=_is_continuation
_V58_BRIDGE_TURN=_bridge_turn

HOT_SERVER_VERSION="2.1.70"
HOT_REVISION="2.1.70-hot-acceptance-completion-diagnostics-v59"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION

_TEMPORAL_NEXT_RE=re.compile(
    r"^\s*next\s+(?:week|month|year|day|morning|afternoon|evening|night|"
    r"monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b",
    re.I,
)
_REFERENTIAL_BRIDGE_RE=re.compile(
    r"^\s*(?:(?:can|could|would|will)\s+you\s+)?"
    r"(?:do|make|fix|change|add|remove|use|try|keep)\s+"
    r"(?:that|this|it|the\s+same|that\s+too|this\s+too|it\s+too)\b|"
    r"^\s*(?:same|same\s+thing|that\s+too|this\s+too|it\s+too|also\s+that)\b",
    re.I,
)
_GENERIC_ACK_RE=re.compile(
    r"^\s*(?:got\s+it|understood|okay|ok|alright|sure|absolutely|exactly|"
    r"you(?:'re|\s+are)\s+right|yep|yeah|right|no\s+problem|will\s+do)"
    r"(?:[.!,:;\-\s]|$)",
    re.I,
)
_TOKENISH_RE=re.compile(r"[A-Za-z0-9_§𓆩𓆪]+(?:['’-][A-Za-z0-9_]+)?",re.UNICODE)


_FROM_SCRATCH_RE=re.compile(r"\bfrom\s+scratch\b",re.I)

def _scope_of(text):
    value=str(text or "")
    # "From scratch" describes lineage/reset breadth. It does not by itself mean
    # "write the longest possible answer." Treat it as detailed unless an independent
    # massive cue is also present.
    if _FROM_SCRATCH_RE.search(value):
        without=_FROM_SCRATCH_RE.sub(" ",value)
        if _MASSIVE_SCOPE_RE.search(without):return "massive"
        if _DETAILED_SCOPE_RE.search(without):return "detailed"
        return "detailed"
    if _MASSIVE_SCOPE_RE.search(value):return "massive"
    if _DETAILED_SCOPE_RE.search(value):return "detailed"
    return "normal"


def _is_continuation(text):
    value=str(text or "").strip()
    if not value:return False
    # "Next" is a useful continuation cue, but temporal phrases such as "next week"
    # are ordinary content and must not inherit an unrelated trajectory.
    if _TEMPORAL_NEXT_RE.search(value):return False
    return _V58_IS_CONTINUATION(value)


def _bridge_turn(text):
    value=str(text or "").strip()
    if _V58_BRIDGE_TURN(value):return True
    # Short deictic actions/questions can modify the active work without becoming a
    # new trajectory. Requiring an explicit referential form keeps this conservative.
    if len(value.split())<=12 and _REFERENTIAL_BRIDGE_RE.search(value):
        return True
    return False


def _conversation_state(payload):
    state=dict(_V58_CONVERSATION_STATE(payload))
    latest=_latest_user_text(payload) if isinstance(payload,dict) else ""
    prior=_recent_prior_user_texts(payload,8) if isinstance(payload,dict) else []
    # Recompute cue membership because v57/v56's cue compiler resolves the global
    # _is_continuation dynamically after this override.
    state["temporalNextSuppressed"]=bool(_TEMPORAL_NEXT_RE.search(latest))
    state["referentialBridge"]=bool(_REFERENTIAL_BRIDGE_RE.search(latest))
    # A deictic micro-turn ("do that too") points at the active work just as strongly
    # as a continuation cue. It may inherit scope from the nearest substantive target,
    # but never tunnels past a reset or a newer substantive task.
    if state["referentialBridge"] and str(state.get("scope") or "normal")=="normal":
        for distance,previous in enumerate(prior,start=1):
            if _RESET_RE.search(previous):break
            if _bridge_turn(previous):continue
            candidate=_scope_of_v56(previous)
            if candidate!="normal":
                state["scope"]=candidate
                state["scopeInherited"]=True
                state["scopeDistance"]=distance
                state["scopeInheritanceSource"]="referential-bridge"
            break
    bridge_depth=0
    for previous in prior:
        if _RESET_RE.search(previous):break
        if _bridge_turn(previous):
            bridge_depth+=1
            continue
        break
    state["bridgeDepth"]=bridge_depth
    return state


def _minimum_completion_words(state,budget):
    scope=str(state.get("scope") or "normal")
    if scope=="massive":
        # A deliberately massive request should not terminate as a polished fragment.
        return 120
    if scope=="detailed":
        return 64
    # For normal continuations only enforce a small floor when the inherited response
    # plan itself says this is substantial work. Simple "next" creative turns remain free.
    if state.get("continuation") and int((budget or {}).get("planned") or 0)>=320:
        return 48
    return 0


def _response_contract(payload):
    contract=dict(_V58_RESPONSE_CONTRACT(payload))
    state=_conversation_state(payload)
    budget=_V58_PLAN_RESPONSE_BUDGET(payload)
    contract.update({
        "responseStance":state.get("responseStance"),
        "conversationScope":state.get("scope"),
        "minimumCompletionWords":_minimum_completion_words(state,budget),
        "continuation":bool(state.get("continuation")),
        "repair":state.get("repair"),
        "multiAct":bool(state.get("multiAct")),
        "genericFragmentGuard":True,
        "acceptanceCompletionContract":"swrlz_acceptance_completion_v1",
    })
    return contract


def _substantive_words(text):
    return _TOKENISH_RE.findall(str(text or ""))


def _response_contract_gaps(text,contract):
    gaps=list(_V58_RESPONSE_CONTRACT_GAPS(text,contract))
    value=str(text or "").strip()
    word_count=len(_substantive_words(value))
    floor=max(0,int((contract or {}).get("minimumCompletionWords") or 0))
    if floor and word_count<floor:
        gaps.append("scope-completion-floor")
    stance=str((contract or {}).get("responseStance") or "")
    active_stances={
        "continue-work","continue-and-act","fulfill","answer-and-fulfill",
        "confirm-and-fulfill","repair-and-act",
    }
    # Do not reject a genuinely concise direct answer. This guard only fires when a
    # work-bearing stance produces essentially an acknowledgement and stops.
    if stance in active_stances and word_count<=18 and _GENERIC_ACK_RE.search(value):
        gaps.append("generic-ack-without-work")
    # Stable de-duplication keeps the inherited contract reason list readable.
    out=[]
    for gap in gaps:
        if gap not in out:out.append(gap)
    return out


def _ngram_repeat_ratio(words,n):
    if n<=1 or len(words)<n:return 0.0
    grams=[tuple(words[i:i+n]) for i in range(len(words)-n+1)]
    if not grams:return 0.0
    repeated=len(grams)-len(set(grams))
    return round(repeated/len(grams),4)


def _prompt_echo_ratio(prompt,response):
    p=[w.lower() for w in _substantive_words(prompt)]
    r=[w.lower() for w in _substantive_words(response)]
    if not p or not r:return 0.0
    # Set overlap is diagnostic only; technical terms can legitimately repeat.
    ps=set(p)
    return round(sum(1 for w in r if w in ps)/len(r),4)


def _response_quality(prompt,response):
    words=[w.lower() for w in _substantive_words(response)]
    return {
        "wordCount":len(words),
        "repeat3":_ngram_repeat_ratio(words,3),
        "repeat4":_ngram_repeat_ratio(words,4),
        "promptEcho":_prompt_echo_ratio(prompt,response),
        "genericAckOpening":bool(_GENERIC_ACK_RE.search(str(response or "").strip())),
    }


def _acceptance_self_test():
    cases=[]
    def check(name,payload,expect):
        try:
            state=_conversation_state(payload)
            budget=_plan_response_budget(payload)
            contract=_response_contract(payload)
            observed={"state":state,"budget":budget,"contract":contract}
            failures=[]
            for path,want in expect.items():
                group,key=path.split(".",1)
                got=observed[group].get(key)
                if callable(want):
                    if not want(got):failures.append(f"{path}={got!r}")
                elif got!=want:
                    failures.append(f"{path}={got!r} expected {want!r}")
            cases.append({"name":name,"ok":not failures,"failures":failures})
        except Exception as exc:
            cases.append({"name":name,"ok":False,"failures":[f"{type(exc).__name__}: {exc}"]})

    check(
        "massive-continuation",
        {"prompt":"Keep going","history":[
            {"role":"user","text":"Do a massive comprehensive architecture review with as much depth as you can."},
            {"role":"assistant","text":"First section complete."},
        ]},
        {
            "state.scope":"massive",
            "state.scopeInherited":True,
            "state.responseStance":"continue-work",
            "budget.planned":lambda v:int(v or 0)>=768,
            "contract.minimumCompletionWords":lambda v:int(v or 0)>=120,
        },
    )
    check(
        "brief-overrides-massive",
        {"prompt":"Keep going, but keep it short","history":[
            {"role":"user","text":"Make this massive and comprehensive."},
            {"role":"assistant","text":"Part one."},
        ]},
        {
            "state.scope":"brief",
            "budget.kind":"brief-explicit",
            "contract.minimumCompletionWords":0,
        },
    )
    check(
        "temporal-next-is-not-continuation",
        {"prompt":"Next week I have another appointment.","history":[
            {"role":"user","text":"Give me a massive breakdown of this code."},
            {"role":"assistant","text":"Done."},
        ]},
        {
            "state.continuation":False,
            "state.temporalNextSuppressed":True,
        },
    )
    check(
        "referential-micro-turn",
        {"prompt":"Can you do that too?","history":[
            {"role":"user","text":"Make the error logger comprehensive and massive, including request IDs."},
            {"role":"assistant","text":"Implemented the first target."},
        ]},
        {
            "state.referentialBridge":True,
            "state.scope":"massive",
            "state.scopeInherited":True,
            "budget.planned":lambda v:int(v or 0)>=768,
        },
    )
    check(
        "local-correction",
        {"prompt":"No, not that one, use the other one.","history":[]},
        {
            "state.repair":"local",
            "state.responseStance":"repair",
        },
    )
    check(
        "reset",
        {"prompt":"Start over from scratch with a different approach.","history":[]},
        {
            "state.repair":"reset",
            "state.responseStance":"new-task",
            "state.scope":"detailed",
        },
    )
    check(
        "multi-act-answer-and-action",
        {"prompt":"Why is that happening, and can you fix it?","history":[]},
        {
            "state.multiAct":True,
            "state.responseStance":"answer-and-fulfill",
        },
    )
    check(
        "social-advance",
        {"prompt":"Exactly lol","history":[]},
        {
            "state.responseStance":"social-advance",
            "budget.kind":"brief-social-state",
        },
    )

    # Contract-only probes: these specifically protect against premature polished fragments.
    deep_payload={"prompt":"Keep going","history":[
        {"role":"user","text":"Give me a massive comprehensive analysis."},
        {"role":"assistant","text":"Part one."},
    ]}
    deep_contract=_response_contract(deep_payload)
    gaps=_response_contract_gaps("Got it.",deep_contract)
    cases.append({
        "name":"generic-ack-cannot-finish-deep-work",
        "ok":"generic-ack-without-work" in gaps and "scope-completion-floor" in gaps,
        "failures":[] if ("generic-ack-without-work" in gaps and "scope-completion-floor" in gaps) else [repr(gaps)],
    })

    passed=sum(1 for case in cases if case["ok"])
    return {
        "ok":passed==len(cases),
        "passed":passed,
        "total":len(cases),
        "failures":[case for case in cases if not case["ok"]],
        "contract":"swrlz_conversation_acceptance_v1",
    }


def inspect_engine():
    result=_V58_INSPECT()
    if isinstance(result,dict):
        acceptance=_acceptance_self_test()
        result.update({
            "hotServerVersion":HOT_SERVER_VERSION,
            "hotRevision":HOT_REVISION,
            "temporalNextDisambiguation":True,
            "referentialMicroTurnBridging":True,
            "semanticCompletionFloor":True,
            "genericAckCompletionGuard":True,
            "responseQualityTelemetry":True,
            "responseRepeat3Telemetry":True,
            "responseRepeat4Telemetry":True,
            "promptEchoTelemetry":True,
            "conversationAcceptanceSelfTest":acceptance,
            "conversationAcceptanceContract":"swrlz_conversation_acceptance_v1",
            "v58SourceCommit":_V58_COMMIT,
        })
    return result


def generate_events(payload,is_cancelled=None):
    request_id=_request_id(payload) if isinstance(payload,dict) else ""
    prompt=_latest_user_text(payload) if isinstance(payload,dict) else ""
    state=_conversation_state(payload) if isinstance(payload,dict) else {}
    budget=_plan_response_budget(payload) if isinstance(payload,dict) else {}
    contract=_response_contract(payload) if isinstance(payload,dict) else {}
    _camera(
        request_id,"acceptance-completion",
        contract="swrlz_acceptance_completion_v1",
        stance=state.get("responseStance"),
        scope=state.get("scope"),
        completionFloorWords=contract.get("minimumCompletionWords"),
        temporalNextSuppressed=bool(state.get("temporalNextSuppressed")),
        referentialBridge=bool(state.get("referentialBridge")),
        bridgeDepth=state.get("bridgeDepth"),
        plannedTokens=budget.get("planned"),
        hardCap=budget.get("hard"),
    )
    parts=[]
    for event in _V58_GENERATE(payload,is_cancelled):
        if isinstance(event,dict) and event.get("type")=="DELTA":
            parts.append(str(event.get("text") or ""))
        if isinstance(event,dict) and event.get("type")=="COMPLETED":
            quality=_response_quality(prompt,"".join(parts))
            gaps=_response_contract_gaps("".join(parts),contract)
            event=dict(event)
            event["responseQuality"]=quality
            event["acceptanceContractGaps"]=gaps
            _camera(
                request_id,"response-quality",
                contract="swrlz_response_quality_v1",
                wordCount=quality.get("wordCount"),
                repeat3=quality.get("repeat3"),
                repeat4=quality.get("repeat4"),
                promptEcho=quality.get("promptEcho"),
                genericAckOpening=quality.get("genericAckOpening"),
                remainingContractGaps=gaps,
            )
        yield event
