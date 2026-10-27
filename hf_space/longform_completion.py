"""Bounded, model-authored expansion for explicit ordinary prose length goals.

This module does not stream provisional drafts, pad text, rewrite model output,
or establish factual/document quality. Callers retain the original instruction,
own model execution and must expose unsuccessful completion truthfully.
"""
from __future__ import annotations

import re
from typing import Any, Callable

SCHEMA = "swrlz-longform-completion-v1"
MAX_TARGET_WORDS = 12000
MIN_TARGET_WORDS = 1000
MAX_ATTEMPTS = 2
MIN_EXPANSION_TOKENS = 256
MAX_DRAFT_CHARS = 131072

_WORDS = re.compile(r"\b\w+(?:[’'-]\w+)*\b", re.UNICODE)
_TARGET = re.compile(r"\b(\d{1,3}(?:,\d{3})+|\d{3,7})[ -]+words?\b", re.I)
_UPPER_LIMIT = re.compile(r"\b(?:under|within|limited to|less than|below|at most|no more than|fewer than|up to|max(?:imum)?(?: of)?|about|around|roughly|approximately)\s*$", re.I)
_WORD_RANGE = re.compile(
    r"\b(?:between\s+\d[\d,]*\s+and\s+\d[\d,]*|"
    r"(?:from\s+)?\d[\d,]*\s*(?:[-–—]|to|through)\s*\d[\d,]*)[ -]*words?\b", re.I)


def prose_word_count(text: str) -> int:
    """Count Unicode lexical words; this is not a semantic quality judgment."""
    return sum(1 for _ in _WORDS.finditer(str(text or "")))


def longform_contract(prompt: str, programming: dict[str, Any] | None = None, *,
                      response_mode: str = "", source_change_mode: str = "",
                      creative: bool = False, file_dialogue: bool = False) -> dict | None:
    """Admit only an explicit, bounded ordinary prose word-count deliverable.

    Upper bounds are not minimum targets. Exact formats, code, creative lyrics,
    quoted/transformed source and internal structured tasks remain with their
    existing owners. Very large projects/documents require staged scope rather
    than an impossible whole-document length acceptance check.
    """
    text = str(prompt or "")
    # A single minimum must not reinterpret a range, approximate target or
    # upper bound as an exact lower bound. Those requests keep normal handling.
    if _WORD_RANGE.search(text):
        return None
    if (bool((programming or {}).get("codingTask")) or source_change_mode or creative
            or file_dialogue or any(mode in str(response_mode).upper() for mode in
                ("IDENTITY", "EXACT-", "JSON", "LYRIC", "CODE-"))):
        return None
    if (re.search(r"(?m)^[ \t]{0,3}(?:`{3,}|~{3,})", text)
            or re.search(r"\b(?:lyrics?|rap|freestyle|song|poem|code|pseudocode|json|xml|html|csv|yaml)\b", text, re.I)
            or re.search(r"\b(?:exactly|verbatim|word.for.word|do not change|translate|translation|echo|quote)\b", text, re.I)
            or re.search(r"\b(?:Chinese|Japanese|Korean|Mandarin|Cantonese)\b", text, re.I)):
        return None
    targets = []
    for match in _TARGET.finditer(text):
        if _UPPER_LIMIT.search(text[max(0, match.start()-40):match.start()]):
            continue
        value = int(match.group(1).replace(",", ""))
        if MIN_TARGET_WORDS <= value <= MAX_TARGET_WORDS:
            targets.append((value, match))
    if len(targets) != 1:
        return None
    target, match = targets[0]
    head = text[:match.start()]
    tail = text[match.end():]
    # Require a generation request, not a passing mention of a long document.
    if not (re.search(r"\b(?:write|produce|draft|generate|create|provide|give me)\b[^.!?\n]{0,110}$", head, re.I)
            or (re.search(r"\bin\s*$", head, re.I)
                and re.match(r"\s*[,;:]?\s*(?:please\s+)?(?:explain|describe|discuss|analyse|analyze|write|produce|draft)\b", tail, re.I))):
        return None
    if re.search(r"\b(?:keep|make|be|answer|respond)[ \w-]{0,24}\b(?:brief|concise|short)\b|"
                 r"\b(?:outline|summary)\s+only\b|\b(?:brief|concise|short)\s+(?:answer|response|summary|outline)\b", text, re.I):
        return None
    return {"schema": SCHEMA, "requestedWords": target,
            "minimumWords": target, "maxAttempts": MAX_ATTEMPTS,
            "scope": "requested-length-only-not-document-quality"}


def longform_validation(text: str, contract: dict, timing: dict | None = None) -> dict:
    words = prose_word_count(text)
    target = int(contract["minimumWords"])
    finish = (timing or {}).get("finishReason")
    reasons = []
    if not str(text or "").strip():
        reasons.append("empty-longform-answer")
    if words < target:
        reasons.append(f"longform-underlength:{words}/{target}")
    if finish == "length":
        reasons.append("model-output-token-limit")
    elif finish != "stop":
        reasons.append("longform-completion-not-observed")
    return {"status": "REJECT" if reasons else "PASS", "reasons": reasons,
            "finishReason": finish, "generationComplete": finish == "stop",
            "requestedWords": int(contract["requestedWords"]), "wordCount": words,
            "executionVerified": False,
            "verificationState": "REQUESTED_LENGTH_ONLY"}


def expansion_messages(messages: list[dict], draft: str, contract: dict) -> list[dict]:
    """Preserve all original model messages and the complete unchanged draft."""
    target = int(contract["requestedWords"])
    count = prose_word_count(draft)
    feedback = (
        f"The preceding draft has {count} lexical words; the original request asks "
        f"for {target} words. Write a complete revised document of at least {target} "
        "substantive words, preserving the original topic, requested sections, "
        "constraints and supported facts. Develop missing explanations, distinct "
        "details and relevant concrete examples rather than repeating or padding. "
        "Return the complete revised document itself, with its conclusion at the "
        "end. Do not append commentary about this length check or claim a word "
        "count you have not measured. Do not invent facts or sources to add length."
    )
    return [*[dict(message) for message in messages],
            {"role": "assistant", "content": str(draft)},
            {"role": "user", "content": feedback}]


def complete_longform(*, messages: list[dict], contract: dict, max_output_tokens: int,
                      context_tokens: int, safety_tokens: int, temperature: float,
                      generate: Callable[[list[dict], int, float], tuple[str, dict]],
                      count_message_tokens: Callable[[list[dict]], int],
                      count_text_tokens: Callable[[str], int]) -> dict:
    """Generate at most two full drafts within one overall output allowance.

    The callback runs the real model. Token accounting uses that model's actual
    tokenizer, including rejected drafts. Mandatory original messages and draft
    are never clipped to fit an expansion. Callers publish only the selected
    whole model draft, record each attempt separately and must not turn a final
    REJECT into a successful requested-length completion.
    """
    if (not isinstance(max_output_tokens, int) or isinstance(max_output_tokens, bool)
            or max_output_tokens < MIN_EXPANSION_TOKENS or max_output_tokens > 16384):
        raise ValueError("Invalid bounded long-form output allowance")
    if not 0 <= safety_tokens < context_tokens or context_tokens > 131072:
        raise ValueError("Invalid bounded long-form context")
    attempts = []
    spent = 0
    next_messages = [dict(message) for message in messages]
    stopped_reason = ""
    for index in range(MAX_ATTEMPTS):
        input_tokens = count_message_tokens(next_messages)
        allowance = min(max_output_tokens-spent, context_tokens-safety_tokens-input_tokens)
        if allowance < (1 if index == 0 else MIN_EXPANSION_TOKENS):
            stopped_reason = "longform-expansion-context-or-output-budget"
            break
        text, timing = generate(next_messages, allowance, temperature)
        text = str(text or "")
        visible_tokens = count_text_tokens(text)
        if not isinstance(visible_tokens, int) or isinstance(visible_tokens, bool) or visible_tokens < 0:
            raise ValueError("Invalid tokenizer observation")
        usage_tokens = (timing.get("usage") or {}).get("completion_tokens")
        observed_usage = isinstance(usage_tokens, int) and not isinstance(usage_tokens, bool) and usage_tokens >= 0
        # Provider usage includes terminal tokens when supplied. Otherwise use
        # an explicitly labelled visible-text tokenizer estimate plus one stop
        # token of headroom; do not silently call that exact provider usage.
        tokens = max(visible_tokens, usage_tokens) if observed_usage else visible_tokens + (timing.get("finishReason") == "stop")
        accounting = "provider-completion-tokens" if observed_usage else "visible-text-tokenizer-plus-one-stop-token-estimate"
        spent += tokens
        validation = longform_validation(text, contract, timing)
        if tokens > allowance:
            validation = {**validation, "status": "REJECT",
                          "reasons": [*validation["reasons"], "longform-output-accounting-mismatch"]}
        attempts.append({"attempt": index+1, "text": text, "timing": dict(timing),
                         "validation": validation, "outputTokens": tokens,
                         "outputTokenAccounting": accounting,
                         "requestedMaxTokens": allowance, "inputTokens": input_tokens})
        if validation["status"] == "PASS":
            break
        if (timing.get("finishReason") != "stop" or tokens > allowance
                or len(text) > MAX_DRAFT_CHARS):
            stopped_reason = "longform-incomplete-or-oversized-draft"
            break
        next_messages = expansion_messages(messages, text, contract)
    if not attempts:
        raise ValueError("Original long-form context leaves no output room")
    # A normally stopped draft is preferable to an unfinished replacement.
    # Length only chooses among complete drafts; it does not certify their facts.
    eligible = [attempt for attempt in attempts if attempt["timing"].get("finishReason") == "stop"
                and "longform-output-accounting-mismatch" not in attempt["validation"]["reasons"]]
    selected = max(eligible or attempts, key=lambda item: item["validation"]["wordCount"])
    return {"schema": SCHEMA, "text": selected["text"],
            "validation": selected["validation"], "selectedAttempt": selected["attempt"],
            "attempts": attempts, "spentOutputTokens": spent,
            "maxOutputTokens": max_output_tokens, "expansionAttempted": len(attempts) > 1,
            "stoppedReason": stopped_reason or None}
