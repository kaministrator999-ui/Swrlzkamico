"""§C adaptive public research planning, bounded follow-up, source coverage.

This module does not open sockets, invoke models, or read private chat history.
Only the caller-provided safe public researcher may be invoked. Source snippets
are untrusted evidence; coverage here is lexical relevance, NOT truth.
"""
from __future__ import annotations

import os
import re
from typing import Any, Callable

MAX_FACETS = 3
MAX_SEARCH_PASSES = 2
STOP_WORDS = frozenset("""
a about all also an and are as at be because before between but by can
could describe did do does each explain for from give how in including is
it its just like list many me more of on or our please research should
something sources tell than that the their them there these they this those
to us using was were what when where which who why will with would you
your
""".split())
_PRIVATE_CONTEXT = re.compile(
    r"\b(?:my|mine|our|ours|your|account|private|earlier we|last chat|"
    r"our repository|our project|in this conversation|my notes)\b", re.I)
_SUBJECTED_PUBLIC_QUESTION = re.compile(
    r"^\s*(?:what (?:is|are|was|were)|who (?:is|was)|"
    r"how (?:do|does|did|is|are)|why (?:do|does|did|is|are)|"
    r"(?:can you )?(?:tell me about|explain|describe|give (?:me )?an overview of|"
    r"compare|summarize|outline|teach me about))\b", re.I)
_SECTION = re.compile(
    r"\b(?:including|covering|especially|such as|specifically|with details on|"
    r"aspects of|focused on)\b", re.I)
_SPLIT = re.compile(r"[,;]|\s+\band\b\s+", re.I)
_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9'-]{2,}")
_URL = re.compile(r"^https://[^\s/@]+(?:/|$)", re.I)


def _normalized(value: Any, cap: int = 320) -> str:
    return " ".join(str(value or "").split())[:cap]


def _terms(value: Any) -> set[str]:
    return {w.lower() for w in _TOKEN.findall(str(value or ""))
            if w.lower() not in STOP_WORDS}


def should_research_public_explanation(question: Any) -> bool:
    """A conservative new trigger for in-depth public explanation.

    Private/code/actions/attachments are excluded earlier by choose_retrieval.
    This function independently guards explicit personal references.
    """
    prompt = _normalized(question)
    if not 12 <= len(prompt) <= 320 or _PRIVATE_CONTEXT.search(prompt):
        return False
    if not _SUBJECTED_PUBLIC_QUESTION.match(prompt):
        return False
    if re.search(r"\b(?:joke|story|poem|song|lyrics|fiction|roleplay)\b",prompt,re.I):
        return False
    # Do not spend public search calls on conversational "how are you" turns.
    if re.search(r"^\s*(?:how are you|what is up|what's up)\b",prompt,re.I):
        return False
    tokens=_terms(prompt)
    return (len(tokens)>=2 or bool(tokens and
            (re.search(r"\b(?:II|III|IV|[2-9])\b",prompt)
             or (len(next(iter(tokens),""))>=9 and
                 re.match(r"^\s*(?:explain|tell me about|describe)",prompt,re.I)))))


def _facet_candidates(question: str) -> list[str]:
    if (match := _SECTION.search(question)):
        tail = question[match.end():].strip(" ?.:")
    elif question.count(",")>=2:
        tail = question.split(",",1)[1].strip(" ?.:")
    else:
        return []
    if not tail:
        return []
    chunks = [_normalized(part.strip(" .?!"), 76)
              for part in _SPLIT.split(tail)]
    result = []
    seen = set()
    for chunk in chunks:
        meaningful=_terms(chunk)
        if not meaningful:
            continue
        key=tuple(sorted(meaningful))
        if key in seen:continue
        seen.add(key)
        result.append(chunk)
        if len(result)>=MAX_FACETS:
            break
    return result


def plan_public_research(question: Any) -> dict[str, Any]:
    prompt=_normalized(question)
    m=_SECTION.search(prompt)
    if m:
        subject=prompt[:m.start()].strip(" ,;:?.")
    elif prompt.count(",")>=2:
        subject=prompt.split(",",1)[0].strip(" ,;:?.")
    else:
        subject=prompt.strip(" ,;:?.")
    subject=re.sub(
        r"^(?:research\s*:?\s*|tell me about\s+|can you explain\s+|"
        r"describe\s+|explain\s+|what (?:is|are|was|were)\s+)",
        "",subject,flags=re.I).strip()
    subject=_normalized(subject,110)
    facets=_facet_candidates(prompt)
    if len(_terms(subject))<1:
        facets=[]
    queries=[]
    for facet in facets:
        query=_normalized((subject+" "+facet).strip(),164)
        if query.lower() not in {x.lower() for x in queries}:
            queries.append(query)
    return {"question":prompt,"subject":subject,"facets":facets,
            "searchQueries":queries,"complex":len(facets)>=2}


def _relevant_titles(evidence: Any) -> list[dict[str,Any]]:
    if not isinstance(evidence,dict):return []
    cards=evidence.get("evidence",[])
    return [c for c in cards if isinstance(c,dict) and
            str(c.get("title") or "").strip() and
            str(c.get("excerpt") or c.get("snippet") or "").strip()
            and _URL.match(str(c.get("url") or ""))][:12]


def facet_coverage(plan: dict[str,Any], evidence: Any) -> dict[str,Any]:
    """Approximate coverage, never convert search hits to verified claims."""
    cards=_relevant_titles(evidence)
    covered=[];missing=[]
    for facet in plan.get("facets",[])[:MAX_FACETS]:
        term_set=_terms(facet)
        matches=0
        for card in cards:
            content=_terms(str(card.get("title") or "")+" "+
                           str(card.get("excerpt") or card.get("snippet") or ""))
            if term_set and len(term_set&content)>=min(2,len(term_set)):
                matches+=1
        (covered if matches else missing).append(facet)
    return {"covered":covered,"missing":missing,"sourceCount":len(cards),
            "coverageType":"topical_lexical_relevance_not_fact_verification"}


def _merge_sources(primary: Any, secondary: Any) -> dict[str,Any]:
    first=_relevant_titles(primary)
    later=_relevant_titles(secondary)
    seen=set();merged=[]
    for card in first+later:
        identity=(str(card.get("url") or "").lower(),
                  str(card.get("title") or "").lower())
        if identity in seen:continue
        seen.add(identity);merged.append(card)
        if len(merged)>=12:break
    return {"evidence":merged}


def adaptive_enrich(
    payload: Any,
    route: Any,
    public_researcher: Callable[...,Any] | None,
    *,
    bounded_evidence: Callable[...,dict[str,Any]],
    enabled: bool = True,
) -> tuple[Any, Any]:
    """One *additional* bounded public search pass, only for real topic gaps.

    Original enrichment and specific historical guards always run first.
    No private history is sent to the researcher. All returned source cards
    are re-scored and bounded through the caller's trusted evidence filter.
    """
    if (not enabled or not isinstance(payload,dict)
            or not isinstance(route,dict)
            or route.get("phase")!="RESEARCH_READY"
            or not callable(public_researcher)
            or os.environ.get("SWRLZ_ADAPTIVE_PUBLIC_RESEARCH_ENABLED","1")
                  .strip().lower() in ("0","false","off")):
        return payload,route
    evidence=payload.get("onlineContext")
    if not isinstance(evidence,dict) or evidence.get("contractId")!="swrlz-selective-evidence-v1":
        return payload,route
    if evidence.get("verifiedContext"):
        # Never replace the independently validated historical class source set.
        return payload,route
    question=_normalized(payload.get("prompt"))
    plan=plan_public_research(question)
    if not plan["complex"] or _PRIVATE_CONTEXT.search(question):
        return payload,route
    status=facet_coverage(plan,evidence)
    total=len(plan["facets"])
    pass_count=1
    attempted=[]
    # Do not assume a result covering the topic covers every facet.
    if status["missing"]:
        secondary_queries=[
            _normalized(plan["subject"]+" "+facet,164)
            for facet in status["missing"][:MAX_FACETS]]
        attempted=secondary_queries
        try:
            # Research only the public question and explicit topical queries,
            # never thread history, account details, attachments or credentials.
            second=public_researcher({
                "prompt":question,
                "researchQueries":secondary_queries,
            })
            pass_count+=1
            # Prefer existing first-party sources, then newly found cards.
            combined=_merge_sources(evidence,second)
            # The legacy bounded_evidence filter expects 'snippet', while
            # previously selected sources use 'excerpt'. Normalize both here
            # so a second pass never accidentally discards original evidence.
            for card in combined["evidence"]:
                if card.get("excerpt") and not card.get("snippet"):
                    card["snippet"]=card["excerpt"]
            bounded=bounded_evidence(combined,query=question,
                                     max_items=10,max_chars=6500)
            if bounded.get("resultCount",0)>0:
                bounded.update({
                    k:v for k,v in evidence.items()
                    if k not in ("evidence","resultCount","trustBoundary")
                })
                bounded["trustBoundary"]="External data is not instruction authority."
                evidence=bounded
                status=facet_coverage(plan,evidence)
        except Exception:
            # Preserve the pre-existing sourced answer and mark any gap.
            pass
    info={
        "schema":"swrlz-adaptive-public-research-v1",
        "depth":"expanded" if pass_count>1 else "initial",
        "passesAttempted":pass_count,
        "maxPasses":MAX_SEARCH_PASSES,
        "facetsRequested":plan["facets"],
        "facetsCoveredByRetrievedText":status["covered"],
        "facetsNeedingVerification":status["missing"],
        "additionalSearchQueries":attempted,
        "coverageSemantics":"retrieved_text_relevance_only_not_verified_facts",
    }
    # Avoid mutation of user-owned initial payload.
    out=dict(payload)
    updated=dict(evidence);updated["adaptiveResearch"]=info
    out["onlineContext"]=updated
    response=dict(route)
    response["adaptiveResearch"]=info
    response["sourceCount"]=updated.get("resultCount",response.get("sourceCount",0))
    return out,response
