"""Pure query-planning helpers for private §wyrlz account history search.

Query filters are interpreted only after the verified-account/opt-in gate.
This parser does not read or retain any conversation content.
"""
from __future__ import annotations
import re

_SOURCE_IMPORTED=re.compile(
    r"(?i)(?:\b(?:only|just|from|within|in|search|show|the)\s+(?:(?:my|our|the)\s+)?"
    r"(?:imported|chatgpt(?:\s+imported)?)\b|"
    r"\b(?:imported|chatgpt)\s+(?:chats|threads|conversations|ones)\s+only\b)")
_SOURCE_NATIVE=re.compile(
    r"(?i)(?:\b(?:only|just|from|within|in|search|show|the)\s+(?:(?:my|our|the)\s+)?"
    r"(?:native|original|§wyrlz|swyrlz)\b|"
    r"\b(?:native|§wyrlz|swyrlz)\s+(?:chats|threads|conversations|ones)\s+only\b)")
_USER_ROLE=re.compile(r"(?i)\b(?:what did i say|where did i say|what i said|my exact words|"
                      r"my (?:reply|message|response)|i (?:said|mentioned|wrote)|"
                      r"only (?:my|user) (?:messages|words|replies)|what did i tell you)\b")
_ASSISTANT_ROLE=re.compile(r"(?i)\b(?:what did you (?:say|tell|reply)|what you said|"
                           r"your (?:reply|response|answer|exact words)|"
                           r"how did you (?:reply|respond)|"
                           r"only (?:your|assistant) (?:messages|words|replies))\b")
_FOCUS={
    "decision":re.compile(r"(?i)\b(?:decisions?|decide|decided|agree|agreed|settled on|chose|"
                          r"chosen|concluded|finalized|finalised)\b"),
    "pending":re.compile(r"(?i)\b(?:unfinished|remaining|pending|todo|to-do|"
                         r"outstanding|next steps?|left off|still (?:have|need|to do)|"
                         r"open tasks?|follow.up items?)\b"),
    "correction":re.compile(r"(?i)\b(?:corrections?|corrected|changed our minds?|"
                            r"changed (?:the|our) plan|misunderstood|"
                            r"clarified|clarifications?|actually meant)\b"),
}
# Evidence text must *itself* signal the desired category.
_EVIDENCE={
    "decision":re.compile(r"(?i)\b(?:we (?:agreed|decided|chose|settled)|"
                          r"(?:decision|final choice|settled on|going with|decided to|"
                          r"finalized|finalised|chose|chosen))\b"),
    "pending":re.compile(r"(?i)\b(?:todo|to-do|next step|still need|need to|"
                         r"remaining|pending|unfinished|not yet|left to do|"
                         r"will (?:finish|do|build|test|add)|follow.up)\b"),
    "correction":re.compile(r"(?i)\b(?:actually|i meant|we meant|not that|"
                            r"instead|correction|corrected|change (?:it|that)|"
                            r"rather than|you misunderstood|i said)\b"),
}
_QUOTE=re.compile(r"(?P<open>[\"“‘'])(?P<phrase>[^\"“”‘’']{3,180})(?P<close>[\"”’'])")
_FOLLOWUP=re.compile(
    r"(?i)^\s*(?:(?:and|but|okay|ok|well|so)\s+)?(?:"
    r"(?:what|how) about\b|(?:just|only|show|give|find|search|filter|"
    r"which (?:thread|chat)|what (?:happened|did you say) next)\b|"
    r"(?:before|after) that\b|(?:the|that|those|same)\s+(?:one|ones|thread|chat|time|day)\b)"
)
_QUESTION=re.compile(
    r"(?i)\b(?:remember|recall|previous conversation|what did (?:we|you|i) "
    r"(?:say|discuss|talk|decide)|search (?:our|my) (?:chat|conversation)|"
    r"where did (?:we|you|i) (?:say|talk|mention)|"
    r"what were we (?:working|talking|discussing)|"
    r"find (?:our|the|my)?\s*(?:decisions|pending|unfinished|corrections|tasks)|"
    r"where did we leave off|what happened last (?:night|weekend))\b"
)


def _extract_phrase(prompt):
    for match in _QUOTE.finditer(prompt):
        phrase=match.group("phrase").strip()
        if phrase and match.group("open") in ('"','“','‘',"'"):
            return phrase[:160]
    return ""


def followup_anchor(prompt,history):
    """Explicit small follow-up only. Never implicitly change topics on a new query."""
    if len(str(prompt or ""))>150 or not _FOLLOWUP.search(str(prompt or "")):
        return ""
    for message in reversed((history or [])[-12:]):
        if not isinstance(message,dict) or message.get("role")!="user":
            continue
        older=str(message.get("text") or message.get("content") or "")[:600]
        if older and _QUESTION.search(older):
            return older
        # Never jump over an unrelated intervening user question. A chain of
        # short search refinements may still inherit the original query.
        if older and not _FOLLOWUP.search(older):
            return ""
    return ""


def parse(prompt,history=None):
    """Return user-visible request facets, with safe limited follow-up inheritance."""
    current=str(prompt or "")[:1600]
    anchor=followup_anchor(current,history)
    combined=(anchor+"\n"+current) if anchor else current

    # New message always wins when filters are explicitly replaced.
    source="all"
    for text in (anchor,current):
        if _SOURCE_IMPORTED.search(text) and not _SOURCE_NATIVE.search(text):
            source="imported"
        elif _SOURCE_NATIVE.search(text) and not _SOURCE_IMPORTED.search(text):
            source="native"
    role="any"
    for text in (anchor,current):
        if _USER_ROLE.search(text) and not _ASSISTANT_ROLE.search(text):role="user"
        elif _ASSISTANT_ROLE.search(text) and not _USER_ROLE.search(text):role="assistant"
    focus=""
    for text in (anchor,current):
        for name,pattern in _FOCUS.items():
            if pattern.search(text):
                focus=name
                break
    phrase=_extract_phrase(current) or _extract_phrase(anchor)
    return {"searchText":combined,"currentText":current,"source":source,"role":role,
            "focus":focus,"exactPhrase":phrase,"followup":bool(anchor)}


def evidence_matches(focus,text):
    if not focus:return True
    return bool(_EVIDENCE[focus].search(str(text or "")))
