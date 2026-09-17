"""R39 v56: trajectory-bound continuity + response stance planning.

Builds on v55. Tightens continuation inheritance so an old deep-scope request cannot
bleed through a newer unrelated task, adds explicit brief-scope overrides, and emits
a compact response-stance cue without collapsing multi-act turns into one label.
"""
from __future__ import annotations
import urllib.request
import re

_V55_COMMIT="ab0b368d871f168c4cf8ae906572d4d4fe2beac8"
_V55_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V55_COMMIT}/runtime_hot/r39_engine_v55.py"
_req=urllib.request.Request(_V55_URL,headers={"User-Agent":"swrlz-r39-v56"})
with urllib.request.urlopen(_req,timeout=20) as _response:_source=_response.read(4_000_001)
if len(_source)>4_000_000:raise RuntimeError("R39_V55_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"),_V55_URL+"#v56","exec"),globals(),globals())

_V55_INSPECT=inspect_engine
_V55_GENERATE=generate_events
_V55_CONVERSATION_STATE=_conversation_state
_V55_PLAN_RESPONSE_BUDGET=_plan_response_budget
_V55_RESPONSE_CONTRACT=_response_contract

HOT_SERVER_VERSION="2.1.67"
HOT_REVISION="2.1.67-hot-trajectory-bound-response-planning-v56"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION

_BRIEF_SCOPE_RE=re.compile(
    r"\b(?:brief|briefly|short|shorter|concise|compact|just\s+the\s+answer|keep\s+it\s+short|"
    r"no\s+explanation|without\s+explanation|don(?:'t|\s+not)\s+explain)\b",
    re.I,
)


def _scope_of_v56(text):
    value=str(text or "")
    if _BRIEF_SCOPE_RE.search(value):return "brief"
    return _scope_of(value)


def _bridge_turn(text):
    value=str(text or "").strip()
    if not value:return True
    cues=set(_cue_set(value))
    if "reset" in cues:return False
    if "continuation" in cues:return True
    # Short acknowledgement/correction/social turns can connect two work turns. A
    # substantive fresh action/question is a trajectory boundary even if it also jokes.
    if len(value.split())<=14 and not ({"action","question"}&cues):
        if cues & {"acceptance","correction","humor","contrast","compact-reference","uncertainty"}:
            return True
    return False


def _trajectory_scope(payload,latest,base_state):
    explicit=_scope_of_v56(latest)
    if explicit!="normal":
        return explicit,False,None,"explicit"
    if not base_state.get("continuation"):
        return "normal",False,None,"none"
    for distance,previous in enumerate(_recent_prior_user_texts(payload,8),start=1):
        if _RESET_RE.search(previous):break
        candidate=_scope_of_v56(previous)
        if candidate!="normal":
            return candidate,True,distance,"continuity-chain"
        if not _bridge_turn(previous):
            # First substantive prior work turn defines the active trajectory. If it
            # did not request special depth, do not tunnel farther backward for scope.
            break
    return "normal",False,None,"none"


def _response_stance(cues,repair,continuation):
    values=set(cues or [])
    if "reset" in values:return "new-task"
    if continuation and "action" in values:return "continue-and-act"
    if continuation:return "continue-work"
    if repair=="local" and "action" in values:return "repair-and-act"
    if repair=="local":return "repair"
    if "acceptance" in values and "action" in values:return "confirm-and-fulfill"
    if "question" in values and "action" in values:return "answer-and-fulfill"
    if "action" in values:return "fulfill"
    if "question" in values:return "answer"
    if values and values <= {"acceptance","humor","compact-reference","contrast","uncertainty"}:return "social-advance"
    return "respond-to-observation"


def _conversation_state(payload):
    state=dict(_V55_CONVERSATION_STATE(payload))
    latest=_latest_user_text(payload) if isinstance(payload,dict) else ""
    scope,inherited,distance,source=_trajectory_scope(payload,latest,state)
    state["scope"]=scope
    state["explicitScope"]=_scope_of_v56(latest)
    state["scopeInherited"]=inherited
    state["scopeDistance"]=distance
    state["scopeInheritanceSource"]=source
    state["scopeSource"]=""
    state["responseStance"]=_response_stance(state.get("cues"),state.get("repair"),state.get("continuation"))
    return state


def _state_prompt(state):
    cues=",".join(state.get("cues") or ["none"])
    inherited=""
    if state.get("scopeInherited"):
        inherited=f" inherited_from_continuity_turn={state.get('scopeDistance')}"
    return (
        "[SWRLZ_CONVERSATION_STATE v3] Conservative routing evidence only; literal user wording wins. "
        f"cues={cues}; stance={state.get('responseStance')}; scope={state.get('scope')}{inherited}; "
        f"repair={state.get('repair')}; correction_pressure={state.get('correctionPressure')}; "
        f"reference_density={state.get('referenceDensity')}; multi_act={str(bool(state.get('multiAct'))).lower()}. "
        "Keep simultaneous acts alive. Continuity may inherit scope only through the active trajectory; never reach past a newer substantive task. "
        "An explicit brief/concise instruction overrides older deep scope. Local correction changes the rejected slot, not unrelated accepted structure. "
        "Use stance as a response-order hint, not a substitute for understanding."
    )


def _plan_response_budget(payload):
    # Call the pre-v56 planner, then correct it with the stricter trajectory-bound state.
    budget=dict(_V55_PLAN_RESPONSE_BUDGET(payload))
    generation=payload.get("generation") if isinstance(payload,dict) and isinstance(payload.get("generation"),dict) else {}
    if str(generation.get("budgetMode") or "").lower()=="manual":return budget
    state=_conversation_state(payload)
    scope=state.get("scope")

    # v55 may have inherited scope by scanning farther back. Rebuild a neutral current
    # budget when v56 finds that a substantive trajectory boundary should block it.
    if state.get("continuation") and scope=="normal" and str(budget.get("kind") or "") in {"massive-continuation","detailed-continuation"}:
        base_current=dict(_V54_PLAN_RESPONSE_BUDGET(payload))
        prior=_prior_budget_candidate(payload,state)
        if prior:
            base_current["planned"]=max(int(base_current.get("planned",0)),int(prior.get("planned",0)))
            base_current["wrapAt"]=max(int(base_current.get("wrapAt",0)),int(prior.get("wrapAt",0)))
            base_current["hard"]=max(int(base_current.get("hard",0)),int(prior.get("hard",0)))
            base_current["kind"]="continuation-inherited-"+str(prior.get("kind") or "normal")
        budget=base_current

    if scope=="brief":
        budget.update({"kind":"brief-explicit","planned":96,"wrapAt":72,"hard":192})
    elif scope=="massive":
        budget["kind"]="massive-continuation" if state.get("scopeInherited") else "massive"
        budget["planned"]=max(int(budget.get("planned",0)),768)
        budget["wrapAt"]=max(int(budget.get("wrapAt",0)),624)
        budget["hard"]=max(int(budget.get("hard",0)),1024)
    elif scope=="detailed":
        budget["kind"]="detailed-continuation" if state.get("scopeInherited") else "detailed"
        budget["planned"]=max(int(budget.get("planned",0)),448)
        budget["wrapAt"]=max(int(budget.get("wrapAt",0)),352)
        budget["hard"]=max(int(budget.get("hard",0)),704)

    # Acceptance/humor-only turns should not receive a mini-essay just because default
    # normal budget is 128 tokens. Preserve room for a natural response, not a lecture.
    latest=_latest_user_text(payload)
    cue_set=set(state.get("cues") or [])
    if scope=="normal" and len(latest.split())<=10 and cue_set and cue_set <= {"acceptance","humor","compact-reference","contrast","uncertainty"}:
        budget.update({"kind":"brief-social-state","planned":64,"wrapAt":48,"hard":160})

    budget["hard"]=min(_ABSOLUTE_RESPONSE_HARD_CAP,max(int(budget.get("hard",0)),int(budget.get("planned",0))+32))
    budget["planned"]=min(int(budget.get("planned",0)),budget["hard"])
    budget["wrapAt"]=min(max(1,int(budget.get("wrapAt",1))),budget["planned"])
    return budget


def _response_contract(payload):
    contract=dict(_V55_RESPONSE_CONTRACT(payload))
    state=_conversation_state(payload)
    contract["conversationScope"]=state.get("scope")
    contract["responseStance"]=state.get("responseStance")
    contract["trajectoryBoundScope"]=True
    return contract


def inspect_engine():
    result=_V55_INSPECT()
    if isinstance(result,dict):result.update({
        "hotServerVersion":HOT_SERVER_VERSION,
        "hotRevision":HOT_REVISION,
        "trajectoryBoundScopeInheritance":True,
        "scopeInheritanceStopsAtSubstantiveTaskBoundary":True,
        "explicitBriefScopeOverride":True,
        "responseStancePlanning":True,
        "responseStancePreservesMultiAct":True,
        "acceptanceOnlyBudgetCompression":True,
        "conversationPlanningContract":"swrlz_conversation_state_v3",
        "v55SourceCommit":_V55_COMMIT,
    })
    return result


def generate_events(payload,is_cancelled=None):
    request_id=_request_id(payload) if isinstance(payload,dict) else ""
    # v55's inherited generator calls _with_conversation_state dynamically; the
    # overridden v56 state/prompt functions therefore apply without duplicating the
    # state preface.
    state=_conversation_state(payload) if isinstance(payload,dict) else {}
    budget=_plan_response_budget(payload) if isinstance(payload,dict) else {}
    _camera(
        request_id,"trajectory-bound-state",
        contract="swrlz_conversation_state_v3",
        cues=list(state.get("cues") or []),
        stance=state.get("responseStance"),
        scope=state.get("scope"),
        scopeInherited=bool(state.get("scopeInherited")),
        scopeDistance=state.get("scopeDistance"),
        repair=state.get("repair"),
        plannedTokens=budget.get("planned"),
        hardCap=budget.get("hard"),
    )
    for event in _V55_GENERATE(payload,is_cancelled):yield event
