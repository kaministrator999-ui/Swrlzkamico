"""Bounded conversational response cognition for §wyrlz HF engines.

This module classifies how the current user turn relates to supplied canonical history.
It does not execute actions, persist hidden reasoning, or replace programming intent.
"""
from __future__ import annotations

import re
from typing import Any

SCHEMA = "swrlz-response-cognition-v1"

_CONFIRM_EXACT = {
    "yes","yep","yup","yeah","yea","exactly","right","correct","okay","ok","sounds good",
    "perfect","bet","true","facts","mhm","uh huh",
}
_DECLINE_EXACT = {
    "no","nope","nah","no thanks","nah thanks","not now","pass","im good","i'm good",
    "nah im good","nah i'm good","leave it","skip it",
}
_CONTINUE_EXACT = {
    "continue","keep going","go on","more","again","next","another","do it","go ahead",
    "keep it going","carry on","finish it","keep cooking","run it","send it",
}
_CREATIVE_DELEGATION = (
    "you pick","surprise me","freestyle","do your thing","whatever you want","your choice",
    "get creative","make it wild","choose for me","you choose",
)

def _clean(text: Any) -> str:
    return " ".join(str(text or "").strip().split())

def _low(text: Any) -> str:
    return _clean(text).casefold()

def _latest_index(history: list[dict[str, Any]], role: str) -> int | None:
    for idx in range(len(history) - 1, -1, -1):
        item = history[idx]
        if str(item.get("role") or "").casefold() == role and _clean(item.get("content") or item.get("text")):
            return idx
    return None

def _requested_count(text: str) -> int | None:
    m = re.search(r"\b(?:give|make|write|show|list|do|create)?\s*(\d{1,2})\s+(?:steps?|options?|examples?|ideas?|versions?|ways?|reasons?|questions?|items?|attempts?)\b", text, re.I)
    if not m:
        return None
    value = int(m.group(1))
    return value if 1 <= value <= 50 else None

def _operation(text: str, relation: str) -> str:
    p = text.casefold()
    if relation == "correction":
        return "correct"
    if relation in ("continuation","expansion","return-to-prior"):
        return "continue"
    if relation == "selection":
        return "select"
    if relation == "confirmation":
        return "confirm"
    if relation == "decline":
        return "decline"
    if re.search(r"\b(?:translate|translation)\b", p):
        return "translate"
    if re.search(r"\b(?:rewrite|rephrase|polish|proofread|edit this|make this sound)\b", p):
        return "rewrite"
    if re.search(r"\b(?:summari[sz]e|summary|tl;dr|tldr)\b", p):
        return "summarize"
    if re.search(r"\b(?:compare|versus|vs\.?|difference between|pros and cons)\b", p):
        return "compare"
    if re.search(r"\b(?:explain|teach|how does|how do|what does|what is|why does|why is|meaning of)\b", p):
        return "explain"
    if re.search(r"\b(?:analy[sz]e|review|evaluate|inspect|diagnose)\b", p):
        return "analyze"
    if re.search(r"\b(?:recommend|suggest|best|which should|what should i)\b", p):
        return "recommend"
    if re.search(r"\b(?:calculate|compute|solve|how much|how many)\b", p):
        return "calculate"
    if re.search(r"\b(?:write|draft|create|make|generate|design|compose|freestyle|story|poem|rap|song|lyrics)\b", p):
        return "create"
    if re.search(r"\b(?:fix|debug|repair|code|implement|function|script|compiler|test failure|runtime error)\b", p):
        return "code"
    if "?" in text or re.match(r"^(?:who|what|when|where|why|how|can|could|would|should|is|are|do|does|did)\b", p):
        return "answer"
    return "respond"

def classify_response_cognition(
    prompt: str,
    history: list[dict[str, Any]] | None = None,
    programming: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return bounded, deterministic turn-relationship metadata."""
    history = list(history or [])
    text = _clean(prompt)
    p = text.casefold()
    words = re.findall(r"[a-z0-9§']+", p)
    has_history = bool(history)
    relation = "standalone"
    explicit_reference = bool(re.search(
        r"\b(?:that|this|it|those|these|same|one|ones|previous|last|earlier|above|before|again|another|next)\b", p
    ))

    topic_reset = bool(re.search(r"^(?:new topic|different topic|different question|separate question|unrelated question)\b", p))
    return_prior = bool(re.search(r"\b(?:back to|go back to|return to|going back to)\b", p))
    decline = p in _DECLINE_EXACT or bool(re.match(r"^(?:no thanks|not now|nah[, ]+i(?:'m| am)? good)\b", p))
    correction = bool(re.match(
        r"^(?:actually\b|i meant\b|meant\b|correction\b|no[,! ]+(?!thanks\b)|nah[,! ]+(?!i(?:'m| am)? good\b)|nope[,! ]+|not what i|that's not|thats not|you misunderstood|i said\b)",
        p,
    ))
    selection = bool(re.match(
        r"^(?:(?:option|choice|number)\s*(?:#?\d+|one|two|three|four|five)|#?\d+|(?:the\s+)?(?:first|second|third|fourth|fifth)(?:\s+one)?|do\s+(?:number|option)\s*#?\d+)\s*[.!]*$",
        p,
    ))
    creative = any(cue in p for cue in _CREATIVE_DELEGATION)
    expansion = bool(re.search(
        r"\b(?:more detail|go deeper|expand(?: on)?|elaborate|explain more|break it down|how so|why though|what do you mean|what does that mean)\b",
        p,
    ))
    continuation = (
        p in _CONTINUE_EXACT
        or bool(re.match(r"^(?:and\b|also\b|plus\b|but\b|so\b|then\b|what about\b|how about\b|same\b|again\b|another\b|next\b|keep\b)", p))
        or (has_history and explicit_reference and len(words) <= 12)
    )
    confirmation = p in _CONFIRM_EXACT

    if topic_reset:
        relation = "topic-reset"
    elif has_history and return_prior:
        relation = "return-to-prior"
    elif has_history and decline:
        relation = "decline"
    elif has_history and correction:
        relation = "correction"
    elif has_history and selection:
        relation = "selection"
    elif has_history and creative:
        relation = "creative-delegation"
    elif has_history and expansion:
        relation = "expansion"
    elif has_history and continuation:
        relation = "continuation"
    elif has_history and confirmation:
        relation = "confirmation"

    detail_mode = "normal"
    if re.search(r"\b(?:brief|briefly|short|quick|concise|one sentence|few words)\b", p):
        detail_mode = "compact"
    elif re.search(r"\b(?:detailed|detail|deep|thorough|comprehensive|in depth|step by step|walk me through)\b", p):
        detail_mode = "expanded"
    elif relation == "expansion":
        detail_mode = "expanded"

    output_only = bool(
        re.search(r"\b(?:only|just)\s+(?:the\s+)?(?:answer|code|lyrics|list|steps|result|translation|rewrite)\b", p)
        or re.search(r"\b(?:no explanation|without explanation|don't explain|do not explain)\b", p)
    )
    hard_preserve = bool(re.search(r"\b(?:keep|preserve|same|unchanged|do not change|don't change|only change|just change)\b", p))
    question_like = "?" in text or bool(re.match(r"^(?:who|what|when|where|why|how|can|could|would|should|is|are|do|does|did)\b", p))

    user_anchor = _latest_index(history, "user")
    assistant_anchor = _latest_index(history, "assistant")
    operation = _operation(text, relation)

    return {
        "schema": SCHEMA,
        "relation": relation,
        "operation": operation,
        "historyAvailable": has_history,
        "historyTurns": len(history),
        "anchorUserIndex": user_anchor,
        "anchorAssistantIndex": assistant_anchor,
        "explicitReference": explicit_reference,
        "questionLike": question_like,
        "detailMode": detail_mode,
        "requestedCount": _requested_count(text),
        "outputOnly": output_only,
        "preserveConstraint": hard_preserve,
        "programming": bool((programming or {}).get("codingTask")),
    }

def response_cognition_policy(state: dict[str, Any]) -> str:
    """Render compact model-facing response rules from bounded state."""
    relation = str(state.get("relation") or "standalone")
    operation = str(state.get("operation") or "respond")
    detail = str(state.get("detailMode") or "normal")
    count = state.get("requestedCount")
    output_only = bool(state.get("outputOnly"))
    preserve = bool(state.get("preserveConstraint"))

    lines = [
        "RESPONSE COGNITION (deterministic current-turn relationship; current user message always has final authority):",
        f"relation={relation}; operation={operation}; detail={detail}; requestedCount={count if count is not None else 'none'}; outputOnly={str(output_only).lower()}; preserveConstraint={str(preserve).lower()}.",
        "Resolve grammar and explicit scope in the CURRENT user turn before using history. Never let an older topic override a newer correction or topic reset.",
    ]
    if relation == "standalone":
        lines.append("Treat this as self-contained unless the wording explicitly references history; do not force the previous topic into the answer.")
    elif relation == "topic-reset":
        lines.append("The user intentionally changed topics. Drop prior task constraints unless the current turn explicitly imports them.")
    elif relation == "continuation":
        lines.append("Continue the nearest compatible active task/subject without reintroducing it from scratch. Preserve established format, tone, and hard constraints unless changed now.")
    elif relation == "correction":
        lines.append("Apply the newest correction as a delta. Preserve unaffected requirements, avoid defending the earlier interpretation, and do not restart the whole answer unless the correction requires it.")
    elif relation == "expansion":
        lines.append("Add the requested depth or missing rung to the existing answer. Avoid repeating already-established material except where needed to connect the expansion.")
    elif relation == "selection":
        lines.append("Bind the selection to the most recent compatible option/list in assistant history. If no unambiguous compatible option exists and guessing would materially change the result, ask one concise clarification.")
    elif relation == "confirmation":
        lines.append("Treat the confirmation as applying to the most recent compatible proposal or question. Proceed only with what that context supports; do not invent a new action or commitment.")
    elif relation == "decline":
        lines.append("Respect the decline and do not continue the declined action. Answer any remaining content in the current message normally.")
    elif relation == "creative-delegation":
        lines.append("The user delegated optional creative choices. Choose them yourself and deliver the creation instead of asking for optional details.")
    elif relation == "return-to-prior":
        lines.append("Return to the explicitly referenced earlier subject. Ignore intervening unrelated constraints while preserving still-relevant requirements from that subject.")

    if detail == "compact":
        lines.append("Keep the answer compact while still complete.")
    elif detail == "expanded":
        lines.append("Provide deeper explanation and useful connective reasoning without padding or repetitive restatement.")
    if output_only:
        lines.append("Honor the requested output-only shape: omit preamble and unrelated explanation.")
    if count is not None:
        lines.append(f"Produce exactly {count} requested items unless safety or impossibility prevents it.")
    if preserve:
        lines.append("Treat keep/preserve/same/do-not-change language as a hard boundary around unaffected material.")
    lines.append("Prefer the smallest complete answer that satisfies the current operation. Do not end with a routine follow-up question when the request is already answerable.")
    return "\n".join(lines)

def response_cognition_camera(state: dict[str, Any]) -> dict[str, Any]:
    """Privacy-bounded camera payload: classifications/indices only, no prompt/history text."""
    keys = (
        "schema","relation","operation","historyAvailable","historyTurns","anchorUserIndex",
        "anchorAssistantIndex","explicitReference","questionLike","detailMode","requestedCount",
        "outputOnly","preserveConstraint","programming",
    )
    return {key: state.get(key) for key in keys}
