"""Bounded observable telemetry helpers for programming candidate generation.

No prompt text, candidate source, hidden reasoning, credentials, or user profile
content is stored here. Engines provide only timing, deterministic gate receipts,
and candidate fingerprints.
"""
from __future__ import annotations

import time
from typing import Any


def observe_completion_chunk(observation: dict[str, Any], chunk: dict[str, Any]) -> None:
    """Retain only provider termination/usage facts, never prompt or source data."""
    for choice in chunk.get("choices") or []:
        reason=choice.get("finish_reason")
        if reason is not None:
            observation["finishReason"]=str(reason)[:64]
    usage=chunk.get("usage")
    if isinstance(usage,dict):
        measured={key:value for key in ("prompt_tokens","completion_tokens","total_tokens")
                  if isinstance((value:=usage.get(key)),int) and not isinstance(value,bool) and value>=0}
        if measured:
            observation["usage"]=measured


def completion_validation(validation: dict[str, Any], observation: dict[str, Any]) -> dict[str, Any]:
    """An observed output limit cannot be promoted into a complete candidate."""
    result=dict(validation or {})
    reason=observation.get("finishReason")
    result["finishReason"]=reason
    result["generationComplete"]=True if reason=="stop" else False if reason=="length" else None
    if reason=="length":
        result["status"]="REJECT"
        result["reasons"]=list(dict.fromkeys([*(result.get("reasons") or []),"model-output-token-limit"]))
    return result


def buffered_chat_completion(model: Any, messages: list[dict[str, Any]], max_tokens: int, temperature: float) -> tuple[str, dict[str, Any]]:
    """Buffer one model attempt while measuring first-token and total attempt latency."""
    started=time.perf_counter()
    first_token_at=None
    parts=[]
    delta_chunks=0
    observation={"finishReason":None,"requestedMaxTokens":int(max_tokens)}
    for chunk in model.create_chat_completion(
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=True,
    ):
        observe_completion_chunk(observation,chunk)
        choices=chunk.get("choices") or []
        delta=(choices[0].get("delta") or {}).get("content") if choices else None
        if delta:
            if first_token_at is None:
                first_token_at=time.perf_counter()
            parts.append(str(delta))
            delta_chunks+=1
    ended=time.perf_counter()
    return "".join(parts), {
        "durationMs":round((ended-started)*1000,3),
        "firstTokenLatencyMs":round((first_token_at-started)*1000,3) if first_token_at is not None else None,
        "deltaChunks":delta_chunks,
        **observation,
    }


def candidate_attempt_receipt(
    attempt: int,
    trigger: str,
    timing: dict[str, Any],
    validation: dict[str, Any],
    fingerprint: str | None,
    previous_attempt_fingerprint: str | None = None,
    repair_target_fingerprint: str | None = None,
) -> dict[str, Any]:
    """Build a privacy-safe receipt for one generated candidate."""
    # Every branch, including buffered identity/creative workers, records the
    # provider's termination fact before it can advertise an accepted attempt.
    checked=completion_validation(validation,timing)
    status=str(checked.get("status") or "UNKNOWN")
    reasons=[str(x)[:160] for x in (checked.get("reasons") or [])[:8]]
    return {
        "schema":"swrlz-candidate-attempt-v1",
        "attempt":int(attempt),
        "trigger":str(trigger or "initial")[:80],
        "durationMs":float(timing.get("durationMs") or 0.0),
        "firstTokenLatencyMs":timing.get("firstTokenLatencyMs"),
        "deltaChunks":int(timing.get("deltaChunks") or 0),
        "finishReason":timing.get("finishReason"),
        "requestedMaxTokens":timing.get("requestedMaxTokens"),
        "usage":dict(timing.get("usage") or {}),
        "candidateFingerprint":fingerprint,
        "changedFromPreviousAttempt":None if previous_attempt_fingerprint is None else bool(fingerprint and fingerprint!=previous_attempt_fingerprint),
        "changedFromRepairTarget":None if repair_target_fingerprint is None else bool(fingerprint and fingerprint!=repair_target_fingerprint),
        "validationStatus":status,
        "validationReasons":reasons,
        "accepted":status=="PASS",
    }


def generation_summary(
    attempts: list[dict[str, Any]],
    total_latency_ms: float,
    load_latency_ms: float,
    visible_first_delta_latency_ms: float | None,
    guarded_turn: bool,
    repair_turn: bool,
    strict_language: bool,
    max_attempts: int = 3,
) -> dict[str, Any]:
    """Summarize bounded candidate attempts, preserving total actual attempt count."""
    limit=max(1,min(6,int(max_attempts)))
    bounded=[dict(x) for x in attempts[:limit] if isinstance(x,dict)]
    accepted=[x for x in bounded if x.get("accepted")]
    total_candidate_ms=round(sum(float(x.get("durationMs") or 0.0) for x in bounded),3)
    return {
        "schema":"swrlz-programming-generation-telemetry-v1",
        "attemptCount":len(bounded),
        "regenerationCount":max(0,len(bounded)-1),
        "firstCandidateRejected":bool(bounded and bounded[0].get("validationStatus")=="REJECT"),
        "finalAcceptedAttempt":int(accepted[-1]["attempt"]) if accepted else None,
        "finalCandidateStatus":str(bounded[-1].get("validationStatus") or "UNKNOWN") if bounded else "UNKNOWN",
        "guardedTurn":bool(guarded_turn),
        "repairTurn":bool(repair_turn),
        "strictLanguage":bool(strict_language),
        "modelLoadLatencyMs":round(float(load_latency_ms or 0.0),3),
        "visibleFirstDeltaLatencyMs":visible_first_delta_latency_ms,
        "engineTotalLatencyMs":round(float(total_latency_ms or 0.0),3),
        "totalCandidateGenerationMs":total_candidate_ms,
        "attempts":bounded,
    }
