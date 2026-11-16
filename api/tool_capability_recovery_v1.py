"""Bounded model-capability recovery at the existing §C generation boundary.

The server (not pretrained model text) owns tool availability. This module is
pure orchestration: no user transcript persistence, no new account store, no
external request until a user task and an actual unsupported tool claim agree.
All output remains buffered only for narrowly eligible tool-sensitive turns.
"""
from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Iterator
from typing import Any

_SCHEMA = "swrlz-tool-capability-recovery-v1"
_AFFIRM = re.compile(r"^\s*(?:yes(?:\s+please)?|yeah|yep|sure|please do|go ahead|do it|let.s do (?:it|that)|absolutely|correct|sounds good)[.!\s]*$", re.I)
_OFFER = re.compile(
    r"(?is)\b(?:would you like(?: me)? to|do you want me to|shall i|"
    r"can i|i can)\b.{0,200}\b(?:rewrite|revise|remix|remaster|"
    r"rework|regenerate|fix|compose|create|write)\b"
)
_MUSIC = re.compile(r"\b(?:remix|song|track|lyrics?|chorus|hook|verse|rap|parody|remaster)\b", re.I)
_RESEARCH = re.compile(r"\b(?:look up|search|research|browse|verify|sources?|cite|"
                       r"latest|current|online|web|fact.check)\b", re.I)
_FALSE_TOOL_CLAIM = re.compile(
    r"(?is)\b(?:i|my (?:model|system))\s+"
    r"(?:can(?:not|'t|’t)|do\s+not|don't|don’t|am\s+unable\s+to|have\s+no\s+ability\s+to|lack\s+the\s+ability\s+to)"
    r".{0,105}?\b(?:browse|search|access (?:to )?(?:the )?(?:internet|web)|"
    r"use (?:the )?(?:web|search)\s+(?:tool|function)|"
    r"fetch (?:from )?(?:the )?(?:internet|web)|live web)\b"
)
_BLOCKED_ON_USER_SOURCE = re.compile(
    r"(?is)\b(?:need|require)\s+(?:you|the user)\s+to\s+(?:give|provide|paste|supply)"
    r".{0,90}\b(?:lyrics?|original|hook|chorus|verse|lines?)\b"
)
_TITLE = re.compile(r"(?i)\b(?:lyrics?\s+(?:to|for|of)|song|track)\s+"
                    r"(?P<title>[^\n.,!?]{2,75}?)\s+by\s+(?P<artist>[^\n.,!?]{2,65})")
_PRIVACY = re.compile(r"(?i)\b(?:my\s+(?:private|personal|bank|medical|email|inbox|"
                      r"account|documents?|files?|messages?|repository|repo)|"
                      r"our\s+(?:private|internal)|password|secret|api\s*key)\b")
_TERMINAL = {"COMPLETED", "FAILED", "CANCELLED"}
_PASS_THROUGH = {"STATUS", "ROUTE", "RESEARCH_SOURCE", "RESEARCH_TRACE",
                 "SOURCE", "WIDGET", "ACTIVITY"}


def _history(payload: dict[str, Any]) -> list[dict[str, Any]]:
    items = payload.get("history")
    return [x for x in items[-16:] if isinstance(x, dict)] if isinstance(items, list) else []


def _text(item: dict[str, Any]) -> str:
    return str(item.get("text") or item.get("content") or "").strip()


def accepted_offer(payload: dict[str, Any]) -> bool:
    """A brief affirmative inherits the immediately pending assistant offer."""
    if not _AFFIRM.fullmatch(str(payload.get("prompt") or "")):
        return False
    items = _history(payload)
    previous = next((item for item in reversed(items) if _text(item)), None)
    return bool(previous and str(previous.get("role") or "").lower() == "assistant"
                and _OFFER.search(_text(previous)))


def _prior_user_task(items: list[dict[str, Any]]) -> str:
    candidates = [_text(item) for item in reversed(items)
                  if str(item.get("role") or "").lower() == "user"
                  and _text(item) and not _AFFIRM.fullmatch(_text(item))]
    # The newest critique constrains a rewrite, but the song identity may be
    # several turns older. Recover both rather than dropping one.
    recent = next((v for v in candidates if _MUSIC.search(v)), "")
    subject = next((v for v in candidates if _TITLE.search(v)), "")
    parts = [recent[:320]] if recent else []
    if subject and subject != recent:
        parts.append("Earlier referenced song: " + subject[:230])
    return "\n".join(parts)



def prepare(payload: dict[str, Any]) -> dict[str, Any]:
    """Resolve a pending affirmative as an actionable instruction, not a question."""
    if not accepted_offer(payload):
        return payload
    items = _history(payload)
    offer = _text(next(item for item in reversed(items) if _text(item)))
    previous = _prior_user_task(items)
    creative = bool(_MUSIC.search(offer + " " + previous))
    if creative:
        task = ("Rewrite the previous remix or song now, incorporating the specific "
                "corrections already discussed in this same conversation. Deliver "
                "a complete original finished composition. Preserve user-requested "
                "section structure and distinct verse flows. Do not copy published "
                "reference lyrics, invent source details, or ask for the original "
                "hook when available public research can establish the needed "
                "abstract structure.")
    else:
        task = ("Carry out the action you just offered and the user accepted, "
                "using the constraints in the preceding conversation. "
                "Do not repeat the offer or ask permission again.")
    if previous:
        task += "\nPrior relevant user instruction: " + previous
    directive = str(payload.get("responseDirective") or "")
    result = dict(payload)
    result["prompt"] = task
    result["receivedText"] = str(payload.get("prompt") or "")
    result["responseDirective"] = (directive + "\nACCEPTED OFFER: The user answered yes "
        "to the immediately preceding action. Execute that action, do not treat "
        "yes as a new unrelated topic.").strip()
    result["_toolRecoveryAcceptedOffer"] = True
    return result


def relevant(payload: dict[str, Any]) -> bool:
    if not isinstance(payload, dict) or payload.get("_toolRecoveryPass"):
        return False
    if payload.get("githubSourceChangeTask") or payload.get("codingTask") or payload.get("nativeEditorEvidence"):
        return False
    if payload.get("privateResearchContext") or payload.get("sourceChangeIdentity"):
        return False
    prompt = str(payload.get("prompt") or "")
    if accepted_offer(payload):
        return True
    if _PRIVACY.search(prompt) and not re.search(r"\bpublic\b", prompt, re.I):
        return False
    return bool(_RESEARCH.search(prompt) or
                (payload.get("onlineContext") and _MUSIC.search(prompt)))


def _subject_query(payload: dict[str, Any]) -> str:
    """Search only a bounded public subject. Never send a private thread to web."""
    current = str(payload.get("prompt") or "")
    items = _history(payload)
    if _PRIVACY.search(current):
        return ""
    relevant_user = [current] + [_text(x) for x in reversed(items)
                                 if str(x.get("role") or "").lower() == "user"]
    for candidate in relevant_user[:10]:
        match = _TITLE.search(candidate)
        if match:
            title = re.sub(r"\s+", " ", match.group("title")).strip(" \"'")
            artist = re.sub(r"\s+", " ", match.group("artist")).strip(" \"'")
            if not _PRIVACY.search(title + " " + artist):
                return (artist + " " + title +
                        " song arrangement sections verse structure music analysis")[:230]
    if current and _RESEARCH.search(current) and not _PRIVACY.search(current):
        # This is an explicit public lookup; the existing bounded search owner
        # validates actual network addresses and downstream evidence.
        return re.sub(r"\s+", " ", current).strip()[:230]
    return ""


def _valid_evidence(data: Any) -> bool:
    if not isinstance(data, dict):
        return False
    ev = data.get("evidence")
    return isinstance(ev, list) and any(
        isinstance(x, dict) and str(x.get("url") or "").startswith(("https://", "http://"))
        and (x.get("snippet") or x.get("title")) for x in ev[:12])


def needs_recovery(answer: str, payload: dict[str, Any]) -> bool:
    text = str(answer or "")
    if not text.strip():
        return False
    if _FALSE_TOOL_CLAIM.search(text):
        return True
    # A creative rewrite blocked on manually supplied published source text
    # should try the available search tool before burdening the user.
    return bool(payload.get("_toolRecoveryAcceptedOffer")
                and _BLOCKED_ON_USER_SOURCE.search(text))


def _cancelled(check: Callable[[], bool]) -> bool:
    try:
        return bool(check())
    except Exception:
        return True


def _draft(generate: Callable[[dict[str, Any]], Iterable[dict[str, Any]]],
           payload: dict[str, Any], cancelled: Callable[[], bool]
           ) -> Iterator[dict[str, Any]]:
    """Hold only text and terminal events. Emit progress without false finality."""
    text_parts: list[str] = []
    tail: dict[str, Any] | None = None
    for event in generate(payload):
        if _cancelled(cancelled):
            yield {"type": "CANCELLED", "phase": "CANCELLED"}
            return
        if not isinstance(event, dict):
            continue
        kind = str(event.get("type") or "").upper()
        if kind == "DELTA":
            text_parts.append(str(event.get("text") or ""))
        elif kind in _TERMINAL:
            tail = event
            break
        elif kind and kind != "CANDIDATE_VALIDATION":
            # Preserve source citations, widget/action receipts, route metadata,
            # and any newer non-text event types. Only draft-specific quality
            # results are withheld until the accepted answer is known.
            yield event
    yield {"_draftText": "".join(text_parts),
           "_draftTerminal": tail or {"type": "FAILED", "phase": "FAILED",
                                      "reason": "Missing generation terminal"}}


def _render(answer: str, terminal: dict[str, Any]) -> Iterator[dict[str, Any]]:
    if answer:
        yield {"type": "DELTA", "text": answer}
    yield terminal


def run(payload: dict[str, Any],
        generate: Callable[[dict[str, Any]], Iterable[dict[str, Any]]],
        research: Callable[[str], dict[str, Any]],
        cancelled: Callable[[], bool]) -> Iterator[dict[str, Any]]:
    """One initial draft, at most one research pass and one revised draft.

    Native Stop wins at every boundary, including after research returns.
    No tool or prompt text is persisted/logged by this helper.
    """
    if not relevant(payload):
        yield from generate(payload)
        return
    active = prepare(payload)
    draft = ""
    terminal = {"type": "FAILED", "phase": "FAILED"}
    for event in _draft(generate, active, cancelled):
        if "_draftText" in event:
            draft = event["_draftText"]
            terminal = event["_draftTerminal"]
        else:
            yield event
    if _cancelled(cancelled):
        yield {"type": "CANCELLED", "phase": "CANCELLED"}
        return
    if terminal.get("type") != "COMPLETED" or not needs_recovery(draft, active):
        yield from _render(draft, terminal)
        return

    yield {"type": "STATUS", "phase": "TOOL_CAPABILITY_RECHECK",
           "reason": "Checking available runtime research after an unsupported model tool claim."}
    evidence = active.get("onlineContext")
    if _valid_evidence(evidence):
        yield {"type": "STATUS", "phase": "RESEARCH_REUSED",
               "reason": "Reusing attributable evidence already available in this turn."}
    else:
        query = _subject_query(payload)
        evidence = None
        if query and not _cancelled(cancelled):
            yield {"type": "STATUS", "phase": "RESEARCH_STARTED",
                   "reason": "Checking a bounded public reference for the pending task."}
            try:
                result = research(query)
                if _valid_evidence(result):
                    evidence = result
            except Exception:
                evidence = None
        if _cancelled(cancelled):
            yield {"type": "CANCELLED", "phase": "CANCELLED"}
            return
        yield {"type": "STATUS", "phase": "RESEARCH_READY" if evidence else "RESEARCH_UNAVAILABLE",
               "reason": ("Public references retrieved; their claims still require evaluation."
                          if evidence else "No usable public reference was retrieved.")}

    revised = dict(active)
    revised["_toolRecoveryPass"] = True
    revised["responseDirective"] = (
        str(active.get("responseDirective") or "") +
        "\nRUNTIME CAPABILITY CORRECTION: This application has public-research "
        "tools. A pretrained claim that browsing or searching is impossible is "
        "not authoritative. Research was " +
        ("retrieved; use its tagged evidence and distinguish verified source "
         "facts from unverified search snippets. " if evidence
         else "attempted or checked but no usable public evidence is available. "
              "Acknowledge missing verification accurately, not a lack of tools. ") +
        "Complete the user's current accepted task; do not ask for lyrics already "
        "provided in the thread or repeat source lyrics while creating an original "
        "remix. Never claim to have accessed tools not actually run.").strip()
    if evidence:
        revised["onlineContext"] = evidence
    second = ""
    second_terminal = {"type": "FAILED", "phase": "FAILED"}
    for event in _draft(generate, revised, cancelled):
        if "_draftText" in event:
            second = event["_draftText"]
            second_terminal = event["_draftTerminal"]
        else:
            yield event
    if _cancelled(cancelled):
        yield {"type": "CANCELLED", "phase": "CANCELLED"}
        return
    if second_terminal.get("type") == "COMPLETED" and second.strip():
        if _FALSE_TOOL_CLAIM.search(second):
            # A second self-limitation hallucination must never become the
            # user-visible answer. Do not pretend the tool succeeded.
            yield {"type": "STATUS", "phase": "TOOL_RECOVERY_INCOMPLETE",
                   "reason": "The revised draft still contradicted runtime tool capabilities."}
            yield from _render(
                "The available public-research tool was checked, but I couldn't "
                "produce a reliable finished answer from the resulting evidence. "
                "I won't invent source details.", second_terminal)
        else:
            yield {"type": "STATUS", "phase": "TOOL_RECOVERY_REGENERATED",
                   "reason": "Replacement draft completed after runtime capability check."}
            yield from _render(second, second_terminal)
        return
    # Avoid publishing a draft known to invent the lack of an actual tool.
    yield from _render(
        "I checked the available research capability but couldn't complete the "
        "requested answer reliably. No unverified source claims were substituted.",
        {"type": "COMPLETED", "phase": "COMPLETE",
         "verification": "TOOL_RECOVERY_INCOMPLETE"})
