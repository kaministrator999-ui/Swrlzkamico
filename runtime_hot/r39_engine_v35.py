"""R39 hot v35: intent-preserving contextual repair + presentation intent over v34.

This layer teaches semantic anomaly repair without mutating user receipts. Optional input
provenance is treated as evidence only. Presentation intent controls whether user-facing
artifacts should be emitted in copyable fenced blocks.
"""
from __future__ import annotations

import json
import urllib.request

_V34_COMMIT = "de5893c791bec594bef1475e3af290edbf1d45cb"
_V34_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V34_COMMIT}/runtime_hot/r39_engine_v34.py"
_req = urllib.request.Request(_V34_URL, headers={"User-Agent": "swrlz-hot-r39-v35"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _source = _response.read(4_000_001)
if len(_source) > 4_000_000:
    raise RuntimeError("R39_V34_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"), _V34_URL + "#v35", "exec"), globals(), globals())

# Append policy rather than replacing the existing adaptive-response controller.
_PERSISTENT_ROUTINE += (
    " Intent-preserving contextual repair is a general language-understanding capability. Preserve the exact "
    "received user wording as the conversational receipt. First test literal validity, then semantic fit against "
    "the recent conversational trajectory. A grammatically valid token can still be a likely transcription, "
    "typing, autocorrect, omission, or word-choice error. When one small plausible repair is substantially more "
    "coherent and confidence is high, reason using the probable intended meaning and make the correction visible "
    "when useful (for example, 'I think you meant depth'). Never silently rewrite meaning when multiple readings "
    "remain plausible. Preserve slang, established coined words, unusual deliberate phrasing, and intentional "
    "literal meanings. Input provenance such as speech modality, STT confidence, uncertain spans, and candidate "
    "alternatives is additional evidence only; it does not decide the interpretation. "
    "Presentation is separate from semantic intent. When the user asks you to produce a copyable artifact such as "
    "a song, lyrics, poem, prompt, template, letter, message, configuration, command sequence, or source code, put "
    "the artifact itself in a fenced block so the UI can offer a block-level Copy action. Keep ordinary explanation "
    "outside the fence. Do not wrap ordinary conversation in code fences just because fenced blocks are available."
)

_V35_BASE_CONTROLLED = _controlled_payload


def _compact_provenance(value):
    if not isinstance(value, dict):
        return None
    modality = str(value.get("modality") or "unknown")[:32]
    provider = str(value.get("provider") or "")[:64]
    confidence = value.get("overall_confidence", value.get("overallConfidence"))
    try:
        confidence = float(confidence) if confidence is not None else None
    except (TypeError, ValueError):
        confidence = None
    alternatives = value.get("candidate_alternatives", value.get("candidateAlternatives"))
    clean_alts = []
    if isinstance(alternatives, list):
        for item in alternatives[:8]:
            if isinstance(item, str):
                text = item.strip()[:160]
                if text:
                    clean_alts.append({"text": text})
            elif isinstance(item, dict):
                text = str(item.get("text") or "").strip()[:160]
                if text:
                    clean_alts.append({"text": text, "confidence": item.get("confidence")})
    uncertain = value.get("uncertain_spans", value.get("uncertainSpans"))
    clean_uncertain = []
    if isinstance(uncertain, list):
        for item in uncertain[:8]:
            if isinstance(item, dict):
                clean_uncertain.append({k: item[k] for k in ("start", "end", "text", "confidence") if k in item})
    return {
        "modality": modality,
        "provider": provider or None,
        "overallConfidence": confidence,
        "candidateAlternatives": clean_alts,
        "uncertainSpans": clean_uncertain,
    }


def _controlled_payload(payload):
    clone, contract, info = _V35_BASE_CONTROLLED(payload)
    provenance = _compact_provenance(payload.get("inputProvenance"))
    presentation = str(payload.get("presentationIntent") or "PROSE").upper()
    if presentation not in {"PROSE", "COPYABLE_BLOCK", "CODE", "MIXED"}:
        presentation = "PROSE"

    dynamic_evidence = []
    if provenance and (
        provenance.get("modality") not in {None, "unknown"}
        or provenance.get("overallConfidence") is not None
        or provenance.get("candidateAlternatives")
        or provenance.get("uncertainSpans")
    ):
        dynamic_evidence.append(
            {
                "role": "SYSTEM",
                "text": (
                    "INPUT_PROVENANCE_EVIDENCE "
                    + json.dumps(provenance, ensure_ascii=False, separators=(",", ":"))
                    + " Preserve the literal current user turn. Use this only as evidence while resolving intent."
                ),
            }
        )
    if presentation != "PROSE":
        dynamic_evidence.append(
            {
                "role": "SYSTEM",
                "text": (
                    f"PRESENTATION_CONTRACT mode={presentation}. "
                    "If producing a user-copyable artifact, fence the artifact itself; keep explanatory prose outside."
                ),
            }
        )
    if dynamic_evidence:
        clone["history"] = list(clone.get("history") or []) + dynamic_evidence

    behavior = dict(clone.get("_conversationBehavior") or {})
    behavior.update(
        {
            "intentPreservingRepair": True,
            "receivedTextImmutable": True,
            "inputProvenanceEvidence": bool(provenance),
            "presentationIntent": presentation,
        }
    )
    clone["_conversationBehavior"] = behavior
    return clone, contract, info


_impl.HOT_SERVER_VERSION = "2.1.44"
_impl.HOT_REVISION = "2.1.44-hot-boundary-v35-intent-preserving-contextual-repair-v5.1"
HOT_SERVER_VERSION = _impl.HOT_SERVER_VERSION
HOT_REVISION = _impl.HOT_REVISION
_V35_BASE_INSPECT = inspect_engine


def inspect_engine():
    result = _V35_BASE_INSPECT()
    if isinstance(result, dict):
        result.update(
            {
                "hotServerVersion": HOT_SERVER_VERSION,
                "hotRevision": HOT_REVISION,
                "intentPreservingContextualRepair": True,
                "receivedTextImmutable": True,
                "semanticRepairBeforeTokenizer": True,
                "inputProvenanceEvidence": True,
                "sttSpecificRepairLogic": False,
                "presentationIntent": True,
                "copyableArtifactFencing": True,
                "repairConfidencePolicy": ["HIGH_REPAIR_VISIBLE_WHEN_USEFUL", "AMBIGUOUS_PRESERVE", "LOW_CLARIFY"],
                "v34SourceCommit": _V34_COMMIT,
            }
        )
    return result
