"""Reusable evidence-led §C research synthesis and bounded claim checks.

This is application logic, not a model-weight update or universal fact checker.
Never treats web passages as executable instructions.
"""
from __future__ import annotations
import re
from typing import Any
from urllib.parse import urlsplit

_STOP=set("a an and are as at be by can classes class character characters for from game have has in is it of on or the this to total two with year was were that them more new original".split())
_WORDS={"zero":0,"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10}
_COUNT=re.compile(r"\b(\d{1,2}|zero|one|two|three|four|five|six|seven|eight|nine|ten)\s+(?:playable\s+|original\s+|new\s+|added\s+|character\s+){0,3}(?:classes|characters|members)\b",re.I)
_ENTRY=re.compile(r"^\s*(?:[-*]|\d{1,2}[.)])\s+(?:\*\*)?(?P<name>[A-Za-z][A-Za-z-]{2,24})(?:\*\*)?(?:\s*[-:—–]\s*(?P<desc>.*))?$")


def repair_repeated_one_lists(text: str) -> str:
    """Correct repeated 1. Markdown bullets only when clearly consecutive."""
    lines=str(text or "").splitlines(keepends=True)
    indices=[i for i,line in enumerate(lines) if re.match(r"^\s*1\.\s+\S",line)]
    if len(indices)>1:
        for i in indices:
            lines[i]=re.sub(r"^(\s*)1\.\s+",r"\1- ",lines[i],count=1)
    return "".join(lines)


def source_ledger(prompt: str, evidence: Any) -> dict[str,Any]:
    cards=evidence.get("evidence",[]) if isinstance(evidence,dict) else []
    sources=[]
    for item in cards[:12]:
        if not isinstance(item,dict):continue
        url=str(item.get("url") or "")
        parsed=urlsplit(url)
        if parsed.scheme!="https" or not parsed.netloc or parsed.username:continue
        excerpt=" ".join(str(item.get("excerpt") or "").split())[:740]
        if not excerpt:continue
        sources.append({
            "id":"S"+str(len(sources)+1),
            "title":str(item.get("title") or "")[:130],
            "url":url[:500],
            "excerpt":excerpt,
            "role":str(item.get("referenceRole") or "supporting_source"),
            "member":str(item.get("referenceMember") or "")[:40],
        })
    return {"question":" ".join(str(prompt or "").split())[:300],
            "sources":sources,"sourceCount":len(sources),
            "coverage":str(evidence.get("coverage") or "unverified") if isinstance(evidence,dict) else "unverified",
            "verification":"excerpts_only_not_automatic_semantic_entailment"}


def instruction_for_synthesis(facts: Any) -> str:
    count=facts.get("total") if isinstance(facts,dict) else None
    return (
        "TRUSTED SOURCE-BOUND RESEARCH ANSWERING: Answer the user naturally, "
        "taking relevant recent conversation history into account. Use only "
        "the supplied evidence for factual assertions, not remembered guesses. "
        "Give a direct answer then readable grouped Markdown bullet lists with "
        "short explanations supported by source excerpts. Do not number every "
        "item as 1. Avoid a rigid identical answer template. "
        "Do not invent class mechanics, additional people, items, counts, dates "
        "or citations. If the evidence only supplies a name, give only the name. "
        "Use a couple of clear paragraphs, not an enormous essay. "
        "When the evidence is insufficient, say exactly what is missing. "
        "Do not claim the model's internal weights or long-term memory changed. "
        +("VERIFIED MEMBER SET: "+str(count)+" members. Keep the exact member names "
          "and the distinction between original and expansion. "
          if count is not None else "")
        +"The server will append validated source links."
    )


def _terms(value: str) -> set[str]:
    return {w.lower().rstrip("s") for w in re.findall(r"[A-Za-z][A-Za-z'-]{2,}",str(value or ""))
            if w.lower() not in _STOP}


def member_description_supported(name: str, text: str, ledger: dict[str,Any]) -> bool:
    requested=_terms(text)
    if not requested:return True
    matches=[
        item for item in ledger.get("sources",[])
        if item.get("role")=="historical_roster_member_detail"
        and item.get("member","").lower()==name.lower()
    ]
    if not matches:return False
    known=set().union(*(_terms(item["excerpt"]) for item in matches))
    extra=requested-known
    return len(extra)<=max(1,len(requested)//3)


def validate_roster_answer(answer: str, facts: Any, ledger: dict[str,Any]) -> dict[str,Any]:
    if not isinstance(facts,dict):
        return {"status":"NOT_APPLICABLE","reasons":["no_verified_roster"]}
    text=str(answer or "").strip()
    expected=[str(n) for n in facts.get("classes",[])]
    if not text or not expected:
        return {"status":"REJECT","reasons":["missing_answer"]}
    reasons=[]
    for name in expected:
        if not re.search(r"\b"+re.escape(name)+r"\b",text,re.I):
            reasons.append("missing_name:"+name)
    valid_counts={len(expected),len(facts.get("baseClasses",[])),len(facts.get("addedClasses",[]))}
    for match in _COUNT.finditer(text):
        value=match.group(1).lower()
        count=int(value) if value.isdigit() else _WORDS.get(value)
        if count not in valid_counts:
            reasons.append("unsupported_count:"+match.group(0))
    expected_names={name.lower() for name in expected}
    enumerated=[]
    for line in text.splitlines():
        match=_ENTRY.match(line)
        if not match:continue
        name=match.group("name")
        if name.lower() not in expected_names:
            if name.lower() not in ("sources","original","expansion","note"):
                reasons.append("unexpected_list_member:"+name)
        else:
            enumerated.append(name.lower())
            desc=match.group("desc") or ""
            if desc and not member_description_supported(name,desc,ledger):
                reasons.append("unsupported_member_detail:"+name)
    if len(enumerated)!=len(expected) or set(enumerated)!=expected_names:
        reasons.append("incomplete_or_extra_member_list")
    # A correct bullet roster is not a license to invent unsupported facts
    # about one of its members elsewhere in the explanation.
    for line in text.splitlines():
        if _ENTRY.match(line):continue
        if not re.search(r"\b(?:can|uses|wields|transforms|shapeshifts|summons|"
                         r"specializes|casts|attacks)\b",line,re.I):
            continue
        for name in expected:
            if re.search(r"\b"+re.escape(name)+r"\b",line,re.I):
                if not member_description_supported(name,line,ledger):
                    reasons.append("unsupported_narrative_detail:"+name)
    return {"status":"REJECT" if reasons else "PASS",
            "reasons":list(dict.fromkeys(reasons))[:16],
            "verifiedScope":"membership_count_and_description_lexical_support_only"}


def source_links(ledger: dict[str,Any],max_sources:int=9)->str:
    result=[];seen=set()
    for card in ledger.get("sources",[]):
        url=card["url"]
        if url in seen:continue
        seen.add(url)
        title=card["title"].replace("[","").replace("]","")
        result.append("["+title+"]("+url+")")
        if len(result)>=max_sources:break
    return ("\n\n**Sources checked**\n"+"\n".join("- "+item for item in result)) if result else ""


def fallback_from_verified_facts(facts:Any, ledger:dict[str,Any])->str:
    if not isinstance(facts,dict):
        return ("The available references do not establish a complete answer. "
                "I won't fill gaps with guesses."+source_links(ledger))
    base=[str(x) for x in facts.get("baseClasses",[])]
    added=[str(x) for x in facts.get("addedClasses",[])]
    subject=str(facts.get("subject") or "The original game")
    total=int(facts.get("total") or len(base)+len(added))
    lines=["**"+subject+": "+str(total)+" verified playable classes.**"]
    for heading,group in (("Original game",base),("Expansion additions",added)):
        if not group:continue
        lines.append("**"+heading+" ("+str(len(group))+"):**")
        for name in group:
            matches=[item for item in ledger.get("sources",[])
                     if item.get("role")=="historical_roster_member_detail"
                     and item.get("member","").lower()==name.lower()]
            if matches:
                original=matches[0]["excerpt"]
                # Publisher pages often repeat the character title. Avoid
                # rendering the same name twice before its description.
                original=re.sub(r"^(?:The\s+)?"+re.escape(name)+r"\s+",
                                "",original,flags=re.I)
                words=original.split()
                excerpt=" ".join(words[:14]).rstrip(".,;:")
                lines.append("- **"+name+"** — "+excerpt+".")
            else:lines.append("- **"+name+"**")
        lines.append("")
    lines.append("This applies to the historical version named in the question, "
                 "not automatically to later remasters or downloadable updates.")
    return "\n".join(lines).strip()+source_links(ledger)


def strip_generated_links(text: str) -> str:
    """Replace generated Markdown links; server source URLs remain authoritative."""
    cleaned=re.sub(r"\[([^\]\n]{1,120})\]\(https?://[^)\s]+\)",r"\1",str(text or "")).strip()
    # Generated URLs are not source authority; replace trailing model-made
    # bibliography with one built from actual server source cards.
    cleaned=re.sub(r"(?mis)^\s*(?:#{1,3}\s*)?\*{0,2}Sources\*{0,2}\s*:\s*.*$",
                   "",cleaned).rstrip()
    return cleaned
