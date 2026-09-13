from __future__ import annotations

import json
from typing import Any

MAX_COGNITIVE_CONTEXT_BYTES = 12 * 1024
MAX_TIME_CONTEXT_BYTES = 2 * 1024
_ALLOWED_INTENTS = {"coding", "research", "analysis", "planning", "creative", "math", "social", "general"}


def _bounded_json_size(value: Any, maximum: int) -> bool:
    try:
        return len(json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")) <= maximum
    except (TypeError, ValueError):
        return False


def _validated_cognitive_context(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict) or not _bounded_json_size(value, MAX_COGNITIVE_CONTEXT_BYTES):
        return None
    clock = value.get("cognitiveClock")
    if not isinstance(clock, dict):
        return None
    envelope_id = str(value.get("envelopeId") or "")[:128]
    directive_id = str(value.get("directiveId") or "")[:128]
    if not envelope_id or not directive_id:
        return None
    return {
        "envelopeId": envelope_id,
        "directiveId": directive_id,
        "architecture": "RMCCA",
        "architectureVersion": 4,
        "cognitiveClock": clock,
        "historySource": str(value.get("historySource") or "")[:64],
        "historyMessages": int(value.get("historyMessages") or 0),
        "assistantHistoryUsingModelText": int(value.get("assistantHistoryUsingModelText") or 0),
        "promptChars": int(value.get("promptChars") or 0),
        "prepareStatus": str(value.get("prepareStatus") or "")[:64],
        "prepareError": str(value.get("prepareError") or "")[:512],
        "serverPreserved": True,
    }


def _validated_time_context(value: Any) -> dict[str, str] | None:
    if not isinstance(value, dict) or not _bounded_json_size(value, MAX_TIME_CONTEXT_BYTES):
        return None
    result = {k: str(value.get(k) or "")[:96] for k in ("localDate", "localTime", "daypart", "timeZone", "utcOffset")}
    return result if any(result.values()) else None


def install(chat_extensions) -> None:
    """Preserve validated cognitive metadata after the stable request normalizer.

    The core normalizer intentionally rebuilds an allowlisted request object. This
    wrapper runs last, after resumable-session normalization, and copies only the
    bounded RMCCA/time fields needed by the hot engine. The older history carrier
    remains a compatibility fallback but is no longer the primary transport path.
    """
    chat = chat_extensions.chat
    base_normalize = chat._normalize_chat_request

    def normalize(payload: dict[str, Any]) -> dict[str, Any]:
        normalized = base_normalize(payload)
        cognitive = _validated_cognitive_context(payload.get("swrlzCognitiveContext"))
        if cognitive is not None:
            normalized["swrlzCognitiveContext"] = cognitive
            normalized["_swrlzRmccaDirectPreserved"] = True
        time_context = _validated_time_context(payload.get("swrlzUserTimeContext"))
        if time_context is not None:
            normalized["swrlzUserTimeContext"] = time_context
        intent = str(payload.get("turnIntent") or "").strip().lower()
        if intent in _ALLOWED_INTENTS:
            normalized["turnIntent"] = intent
        if payload.get("_swrlzCarrierAttached") is True:
            normalized["_swrlzCarrierAttached"] = True
        return normalized

    chat._normalize_chat_request = normalize
    chat_extensions.RMCCA_DIRECT_TRANSPORT = {
        "ready": True,
        "contract": "rmcca-direct-v1",
        "carrierFallback": True,
        "maxContextBytes": MAX_COGNITIVE_CONTEXT_BYTES,
    }
