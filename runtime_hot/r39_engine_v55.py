"""R39 v55: explicit conversation-state planning + inherited response scope.

Builds on v54 conversation intelligence. This event moves key conversational
behavior out of policy-only prose and into deterministic runtime planning:
- compile conservative multi-act cues from the current turn + recent user turns;
- inherit explicit response scope across continuation turns;
- inherit response-contract requirements across true continuations;
- distinguish local repair from reset requests;
- add bounded n-gram loop pressure on top of v54 frequency/recency decoding;
- raise the hard ceiling only for requests that explicitly justify deeper output.

Heuristics are routing evidence, never semantic authority. The model must still
read the user's actual words and may override a cue when context contradicts it.
"""
from __future__ import annotations
import urllib.request
import re

_V54_COMMIT="3d9559c642f3ff72743607a98a55a1ae3c5821c8"
_V54_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V54_COMMIT}/runtime_hot/r39_engine_v54.py"
_req=urllib.request.Request(_V54_URL,headers={"User-Agent":"swrlz-r39-v55"})
with urllib.request.urlopen(_req,timeout=20) as _response:_source=_response.read(4_000_001)
if len(_source)>4_000_000:raise RuntimeError("R39_V54_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"),_V54_URL+"#v55","exec"),globals(),globals())

_V54_INSPECT=inspect_engine
_V54_GENERATE=generate_events
_V54_PLAN_RESPONSE_BUDGET=_plan_response_budget
_V54_RESPONSE_CONTRACT=_response_contract
_V54_SAMPLE=base._sample

HOT_SERVER_VERSION="2.1.66"
HOT_REVISION="2.1.66-hot-conversation-state-planning-v55"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION

# v17's 768-token absolute cap was reasonable for ordinary turns but physically
# contradicted explicit "massive / extended / comprehensive" requests. Keep the
# ordinary planners conservative and expose extra headroom only when scope earns it.
_ABSOLUTE_RESPONSE_HARD_CAP=1024

_CONTINUATION_RE=re.compile(
    r"^\s*(?:keep\s+going|continue(?:\s+on)?|next|more|go\s+on|another|again|carry\s+on|"
    r"keep\s+(?:finding|improving|building|working|analyzing|analysing|adding)|go\s+deeper|do\s+more)\b",
    re.I,
)
_CORRECTION_RE=re.compile(
    r"^\s*(?:no\b(?!\s+(?:problem|worries|thanks))|nah\b|nope\b|not\s+quite\b|actually\b|"
    r"wait\b|i\s+mean\b|i\s+meant\b|wrong\b|rather\b|instead\b)",
    re.I,
)
_ACCEPTANCE_RE=re.compile(
    r"^\s*(?:exactly\b|yes\b|yep\b|yup\b|correct\b|right\b|that(?:'s|\s+is)\s+it\b|"
    r"hell\s+yeah\b|fuck\s+yeah\b|yeah\b|perfect\b)",
    re.I,
)
_RESET_RE=re.compile(
    r"\b(?:start\s+over|from\s+scratch|reset\s+(?:it|this|that)|ignore\s+(?:that|the\s+previous|previous)|"
    r"new\s+topic|different\s+topic|forget\s+that\s+approach)\b",
    re.I,
)
_MASSIVE_SCOPE_RE=re.compile(
    r"\b(?:massive|comprehensive|exhaustive|extensive|all\s+of\s+it|everything|whole\s+(?:thing|system|project)|"
    r"from\s+scratch|as\s+much\s+as\s+(?:you\s+)?can)\b|\bnot\s+(?:be\s+)?small\b",
    re.I,
)
_DETAILED_SCOPE_RE=re.compile(
    r"\b(?:detailed|in[-\s]?depth|deep\s+dive|thorough|step\s+by\s+step|architecture|full\s+analysis|"
    r"deeply|greatly|extended)\b",
    re.I,
)
_ACTION_RE=re.compile(
    r"\b(?:can\s+you|could\s+you|would\s+you|i\s+want\s+you\s+to|i\s+need\s+you\s+to|please|let(?:'s|\s+us)|"
    r"make|create|build|fix|check|read|look\s+up|analy[sz]e|improve|add|remove|write|implement|refactor|debug)\b",
    re.I,
)
_QUESTION_RE=re.compile(
    r"\?|^\s*(?:what|why|how|when|where|who|which|can|could|would|should|do|does|did|is|are|will|have|has)\b",
    re.I,
)
_HUMOR_RE=re.compile(r"\b(?:lol|lmao|lmfao|haha+|hehe+)\b|[😂🤣😆]",re.I)
_CONTRAST_RE=re.compile(r"\b(?:not\s+only|but|instead|rather\s+than|except|not\s+the|without|other\s+one|yet)\b",re.I)
_REFERENCE_RE=re.compile(r"\b(?:this|that|it|one|that\s+one|the\s+one|other\s+one|same|again|still|there|those|these)\b",re.I)
_UNCERTAINTY_RE=re.compile(r"\b(?:maybe|perhaps|possibly|probably|i\s+think|i\s+guess|not\s+sure|could\s+be|might\s+be)\b",re.I)


def _turn_text(turn):
    if not isinstance(turn,dict):return ""
    return str(turn.get("text") or turn.get("content") or "").strip()


def _turn_role(turn):
    if not isinstance(turn,dict):return ""
    return str(turn.get("role") or "").strip().lower()


def _recent_prior_user_texts(payload,limit=8):
    history=payload.get("history") if isinstance(payload,dict) else None
    out=[]
    for turn in reversed(list(history or [])):
        role=_turn_role(turn)
        if role in {"user","human"}:
            text=_turn_text(turn)
            if text:
                out.append(text)
                if len(out)>=limit:break
    return out


def _scope_of(text):
    value=str(text or "")
    if _MASSIVE_SCOPE_RE.search(value):return "massive"
    if _DETAILED_SCOPE_RE.search(value):return "detailed"
    return "normal"


def _is_continuation(text):
    value=str(text or "").strip()
    if not value:return False
    # Keep the cue broad enough for natural "keep going with X" wording while
    # preventing a random occurrence of "next" in a long new request from inheriting state.
    return bool(_CONTINUATION_RE.search(value)) and len(value.split())<=18


def _cue_set(text):
    value=str(text or "").strip()
    cues=[]
    if _is_continuation(value):cues.append("continuation")
    if _CORRECTION_RE.search(value):cues.append("correction")
    if _ACCEPTANCE_RE.search(value):cues.append("acceptance")
    if _ACTION_RE.search(value):cues.append("action")
    if _QUESTION_RE.search(value):cues.append("question")
    if _HUMOR_RE.search(value):cues.append("humor")
    if _CONTRAST_RE.search(value):cues.append("contrast")
    if _REFERENCE_RE.search(value):cues.append("compact-reference")
    if _UNCERTAINTY_RE.search(value):cues.append("uncertainty")
    if _RESET_RE.search(value):cues.append("reset")
    return cues


def _conversation_state(payload):
    latest=_latest_user_text(payload) if isinstance(payload,dict) else ""
    prior=_recent_prior_user_texts(payload,8)
    cues=_cue_set(latest)
    explicit_scope=_scope_of(latest)
    reset="reset" in cues
    continuation="continuation" in cues and not reset
    inherited_scope="normal"
    scope_distance=None
    inherited_from=""
    if continuation and explicit_scope=="normal":
        for distance,previous in enumerate(prior,start=1):
            if _RESET_RE.search(previous):break
            candidate=_scope_of(previous)
            if candidate!="normal":
                inherited_scope=candidate
                scope_distance=distance
                inherited_from=previous
                break
    scope=explicit_scope if explicit_scope!="normal" else inherited_scope

    # Corrections normally repair a local slot. Only explicit reset language authorizes
    # discarding the larger accepted structure.
    repair="reset" if reset else "local" if "correction" in cues else "none"

    # Track correction pressure conservatively. This is a hint that repeated misses may
    # indicate a missing reasoning rung, not a license to assume what the rung is.
    correction_pressure=1 if "correction" in cues else 0
    if correction_pressure:
        for previous in prior[:3]:
            if _CORRECTION_RE.search(previous):correction_pressure+=1
            else:break

    ref_hits=len(_REFERENCE_RE.findall(latest))
    return {
        "cues":cues,
        "scope":scope,
        "explicitScope":explicit_scope,
        "scopeInherited":bool(inherited_scope!="normal" and explicit_scope=="normal"),
        "scopeDistance":scope_distance,
        "scopeSource":inherited_from,
        "continuation":continuation,
        "repair":repair,
        "correctionPressure":min(4,correction_pressure),
        "referenceDensity":"high" if ref_hits>=3 else "medium" if ref_hits>=1 else "low",
        "contrast":bool("contrast" in cues),
        "uncertainty":bool("uncertainty" in cues),
        "multiAct":len(cues)>=2,
    }


def _state_prompt(state):
    cues=",".join(state.get("cues") or ["none"])
    scope=str(state.get("scope") or "normal")
    inherited=""
    if state.get("scopeInherited"):
        inherited=f" inherited_from_recent_user_turn={state.get('scopeDistance')}"
    return (
        "[SWRLZ_CONVERSATION_STATE v2] Routing cues are evidence, not conclusions; current user wording remains authority. "
        f"cues={cues}; scope={scope}{inherited}; repair={state.get('repair')}; "
        f"correction_pressure={state.get('correctionPressure')}; reference_density={state.get('referenceDensity')}; "
        f"multi_act={str(bool(state.get('multiAct'))).lower()}. "
        "Preserve simultaneous acts when present. On continuation, advance the active work instead of restarting it. "
        "On local correction, replace the rejected slot while preserving unaffected accepted structure. "
        "Do not treat acceptance, humor, uncertainty, or shorthand as permission to invent facts."
    )


def _with_conversation_state(payload):
    if not isinstance(payload,dict):return payload,{}
    state=_conversation_state(payload)
    enriched=dict(payload)
    history=list(enriched.get("history") or [])
    enriched["history"]=[{"role":"system","text":_state_prompt(state)}]+history
    return enriched,state


def _prior_budget_candidate(payload,state):
    if not state.get("continuation"):return None
    for previous in _recent_prior_user_texts(payload,6):
        if _RESET_RE.search(previous):break
        # Skip acknowledgement-only fragments; inherit the first substantive work turn.
        stripped=previous.strip()
        if len(stripped.split())<=5 and (_ACCEPTANCE_RE.search(stripped) or _HUMOR_RE.search(stripped)):
            continue
        clone=dict(payload)
        clone["prompt"]=previous
        generation=clone.get("generation") if isinstance(clone.get("generation"),dict) else {}
        if str(generation.get("budgetMode") or "").lower()=="manual":
            # Manual budget belongs to the current request and should never be inferred backwards.
            clone["generation"]={k:v for k,v in generation.items() if k not in {"budgetMode","maxTokens"}}
        return _V54_PLAN_RESPONSE_BUDGET(clone)
    return None


def _plan_response_budget(payload):
    budget=dict(_V54_PLAN_RESPONSE_BUDGET(payload))
    generation=payload.get("generation") if isinstance(payload,dict) and isinstance(payload.get("generation"),dict) else {}
    if str(generation.get("budgetMode") or "").lower()=="manual":
        return budget
    state=_conversation_state(payload)
    prior_budget=_prior_budget_candidate(payload,state)
    if prior_budget:
        budget["planned"]=max(int(budget.get("planned",0)),int(prior_budget.get("planned",0)))
        budget["wrapAt"]=max(int(budget.get("wrapAt",0)),int(prior_budget.get("wrapAt",0)))
        budget["hard"]=max(int(budget.get("hard",0)),int(prior_budget.get("hard",0)))
        budget["kind"]="continuation-inherited-"+str(prior_budget.get("kind") or "normal")

    scope=state.get("scope")
    if scope=="massive":
        budget["planned"]=max(int(budget.get("planned",0)),768)
        budget["wrapAt"]=max(int(budget.get("wrapAt",0)),624)
        budget["hard"]=max(int(budget.get("hard",0)),1024)
        budget["kind"]="massive-continuation" if state.get("scopeInherited") else "massive"
    elif scope=="detailed":
        budget["planned"]=max(int(budget.get("planned",0)),448)
        budget["wrapAt"]=max(int(budget.get("wrapAt",0)),352)
        budget["hard"]=max(int(budget.get("hard",0)),704)
        budget["kind"]="detailed-continuation" if state.get("scopeInherited") else "detailed"

    budget["hard"]=min(_ABSOLUTE_RESPONSE_HARD_CAP,max(int(budget.get("hard",0)),int(budget.get("planned",0))+32))
    budget["planned"]=min(int(budget.get("planned",0)),budget["hard"])
    budget["wrapAt"]=min(max(1,int(budget.get("wrapAt",1))),budget["planned"])
    return budget


def _response_contract(payload):
    current=dict(_V54_RESPONSE_CONTRACT(payload))
    state=_conversation_state(payload)
    if not state.get("continuation"):
        current["conversationScope"]=state.get("scope")
        return current
    inherited=None
    for previous in _recent_prior_user_texts(payload,6):
        if _RESET_RE.search(previous):break
        if len(previous.split())<=5 and (_ACCEPTANCE_RE.search(previous) or _HUMOR_RE.search(previous)):
            continue
        clone=dict(payload);clone["prompt"]=previous
        inherited=_V54_RESPONSE_CONTRACT(clone)
        break
    if isinstance(inherited,dict):
        requirements=[]
        for value in list(current.get("requirements") or [])+list(inherited.get("requirements") or []):
            if value not in requirements:requirements.append(value)
        current["requirements"]=requirements
        current["coding"]=bool(current.get("coding") or inherited.get("coding"))
        current["explain"]=bool(current.get("explain") or inherited.get("explain"))
        current["inheritedFromPriorTurn"]=True
    current["conversationScope"]=state.get("scope")
    return current


# v54's frequency/recency penalty operates on the history supplied by the decoder.
# The decoder currently supplies 64 recent tokens, so v55 truthfully treats 64 as the
# effective window and adds phrase-level protection over those tokens.
def _ngram_occurrences(history,suffix):
    n=len(suffix)
    if n<=1 or len(history)<n:return 0
    count=0
    target=tuple(suffix)
    for i in range(0,len(history)-n+1):
        if tuple(history[i:i+n])==target:count+=1
    return count


def _ngram_guarded_sample(logits,history,temperature,top_p,top_k,repetition_penalty,seed):
    hist=list(history[-64:]) if history else []
    if len(hist)<2:
        return _V54_SAMPLE(logits,hist,temperature,top_p,top_k,repetition_penalty,seed)
    adjusted=logits.copy()
    candidate_count=min(96,adjusted.size)
    candidates=np.argpartition(adjusted,-candidate_count)[-candidate_count:]
    for raw_tok in candidates:
        tok=int(raw_tok)
        penalty=1.0
        # Strongest pressure on repeated 4-grams, then 3-grams. Bigram pressure is
        # intentionally mild so normal syntax and technical names remain usable.
        for n,strength in ((4,0.24),(3,0.14),(2,0.035)):
            if len(hist)<n-1:continue
            suffix=hist[-(n-1):]+[tok]
            repeats=_ngram_occurrences(hist,suffix)
            if repeats:
                penalty+=strength*min(2,repeats)
        if hist and tok==hist[-1]:penalty+=0.05
        if penalty>1.0:
            if adjusted[tok]<0:adjusted[tok]*=penalty
            else:adjusted[tok]/=penalty
    return _V54_SAMPLE(adjusted,hist,temperature,top_p,top_k,repetition_penalty,seed)

base._sample=_ngram_guarded_sample


def inspect_engine():
    result=_V54_INSPECT()
    if isinstance(result,dict):result.update({
        "hotServerVersion":HOT_SERVER_VERSION,
        "hotRevision":HOT_REVISION,
        "conversationStateCompiler":True,
        "conversationStateMultiAct":True,
        "conversationStateCuesAreEvidence":True,
        "localRepairVsResetRouting":True,
        "continuationScopeInheritance":True,
        "continuationBudgetInheritance":True,
        "continuationResponseContractInheritance":True,
        "explicitMassiveScopePlannedTokens":768,
        "explicitMassiveScopeHardCap":1024,
        "explicitDetailedScopePlannedTokens":448,
        "ngramLoopGuard":True,
        "ngramLoopGuardMaxN":4,
        "adaptiveDecodeEffectiveHistoryTokens":64,
        "absoluteResponseHardCap":_ABSOLUTE_RESPONSE_HARD_CAP,
        "conversationPlanningContract":"swrlz_conversation_state_v2",
        "v54SourceCommit":_V54_COMMIT,
    })
    return result


def generate_events(payload,is_cancelled=None):
    request_id=_request_id(payload) if isinstance(payload,dict) else ""
    enriched,state=_with_conversation_state(payload)
    budget=_plan_response_budget(enriched) if isinstance(enriched,dict) else {}
    _camera(
        request_id,"conversation-state",
        contract="swrlz_conversation_state_v2",
        cues=list(state.get("cues") or []),
        scope=state.get("scope"),
        scopeInherited=bool(state.get("scopeInherited")),
        repair=state.get("repair"),
        correctionPressure=state.get("correctionPressure"),
        multiAct=bool(state.get("multiAct")),
        plannedTokens=budget.get("planned"),
        hardCap=budget.get("hard"),
        ngramLoopGuard=True,
    )
    for event in _V54_GENERATE(enriched,is_cancelled):yield event
