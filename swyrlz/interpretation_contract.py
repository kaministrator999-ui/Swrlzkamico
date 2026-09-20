from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Literal

Modality = Literal["typed", "speech", "paste", "unknown"]
RepairStatus = Literal["NONE", "PROBABLE", "AMBIGUOUS", "CLARIFY"]
ConfidenceBand = Literal["HIGH", "MEDIUM", "LOW", "UNKNOWN"]
PresentationMode = Literal["PROSE", "COPYABLE_BLOCK", "CODE", "MIXED"]


@dataclass(frozen=True)
class CandidateAlternative:
    text: str
    confidence: float | None = None
    span_start: int | None = None
    span_end: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class InputProvenance:
    modality: Modality = "unknown"
    provider: str | None = None
    overall_confidence: float | None = None
    uncertain_spans: tuple[dict[str, Any], ...] = ()
    candidate_alternatives: tuple[CandidateAlternative, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["candidate_alternatives"] = [item.to_dict() for item in self.candidate_alternatives]
        return value


@dataclass(frozen=True)
class RepairInference:
    status: RepairStatus = "NONE"
    original_span: str | None = None
    candidate: str | None = None
    confidence: float | None = None
    confidence_band: ConfidenceBand = "UNKNOWN"
    basis: tuple[str, ...] = ()
    visible_correction_recommended: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class InterpretationEnvelope:
    """Semantic metadata that never overwrites the received user text."""

    received_text: str
    provenance: InputProvenance = field(default_factory=InputProvenance)
    repair: RepairInference = field(default_factory=RepairInference)
    interpreted_meaning: str | None = None
    ambiguity: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "receivedText": self.received_text,
            "provenance": self.provenance.to_dict(),
            "interpretation": {
                "repair": self.repair.to_dict(),
                "interpretedMeaning": self.interpreted_meaning,
                "ambiguity": list(self.ambiguity),
            },
        }


def normalize_provenance(value: Any) -> InputProvenance:
    """Normalize optional client evidence without treating it as semantic truth."""
    if not isinstance(value, dict):
        return InputProvenance()

    modality = str(value.get("modality") or "unknown").lower()
    if modality not in {"typed", "speech", "paste", "unknown"}:
        modality = "unknown"

    confidence = value.get("overallConfidence")
    try:
        confidence = float(confidence) if confidence is not None else None
    except (TypeError, ValueError):
        confidence = None
    if confidence is not None:
        confidence = min(1.0, max(0.0, confidence))

    alternatives: list[CandidateAlternative] = []
    raw_alternatives = value.get("candidateAlternatives")
    if isinstance(raw_alternatives, list):
        for item in raw_alternatives[:16]:
            if isinstance(item, str):
                text = item.strip()
                if text:
                    alternatives.append(CandidateAlternative(text=text[:512]))
                continue
            if not isinstance(item, dict):
                continue
            text = str(item.get("text") or "").strip()[:512]
            if not text:
                continue
            alt_conf = item.get("confidence")
            try:
                alt_conf = float(alt_conf) if alt_conf is not None else None
            except (TypeError, ValueError):
                alt_conf = None
            if alt_conf is not None:
                alt_conf = min(1.0, max(0.0, alt_conf))
            start = item.get("spanStart")
            end = item.get("spanEnd")
            try:
                start = int(start) if start is not None else None
                end = int(end) if end is not None else None
            except (TypeError, ValueError):
                start = end = None
            alternatives.append(CandidateAlternative(text=text, confidence=alt_conf, span_start=start, span_end=end))

    uncertain: list[dict[str, Any]] = []
    raw_uncertain = value.get("uncertainSpans")
    if isinstance(raw_uncertain, list):
        for item in raw_uncertain[:32]:
            if not isinstance(item, dict):
                continue
            clean = {k: item[k] for k in ("start", "end", "text", "confidence") if k in item}
            uncertain.append(clean)

    return InputProvenance(
        modality=modality,  # type: ignore[arg-type]
        provider=(str(value.get("provider")).strip()[:96] if value.get("provider") else None),
        overall_confidence=confidence,
        uncertain_spans=tuple(uncertain),
        candidate_alternatives=tuple(alternatives),
    )


def presentation_mode_for_request(text: str) -> PresentationMode:
    """Conservative presentation hint; semantics remain model-controlled."""
    low = " ".join(str(text or "").lower().split())
    code_terms = ("code", "script", "function", "class", "json", "yaml", "sql", "bash", "command", "config")
    copy_terms = ("song", "lyrics", "poem", "prompt", "template", "letter", "message to", "copy", "paste")
    asks_explanation = any(term in low for term in ("explain", "why", "how does", "walk me through"))
    has_code = any(term in low for term in code_terms)
    has_copy = any(term in low for term in copy_terms)
    if has_code and asks_explanation:
        return "MIXED"
    if has_code:
        return "CODE"
    if has_copy and asks_explanation:
        return "MIXED"
    if has_copy:
        return "COPYABLE_BLOCK"
    return "PROSE"


def prompt_evidence_block(envelope: InterpretationEnvelope) -> str:
    """Serialize compact evidence for prompt-time reasoning without mutating the user turn."""
    repair = envelope.repair
    bits = [f"modality={envelope.provenance.modality}"]
    if envelope.provenance.overall_confidence is not None:
        bits.append(f"inputConfidence={envelope.provenance.overall_confidence:.3f}")
    bits.append(f"repairStatus={repair.status}")
    if repair.original_span:
        bits.append(f"originalSpan={repair.original_span!r}")
    if repair.candidate:
        bits.append(f"candidate={repair.candidate!r}")
    if repair.confidence is not None:
        bits.append(f"repairConfidence={repair.confidence:.3f}")
    if envelope.ambiguity:
        bits.append("ambiguity=" + repr(list(envelope.ambiguity)))
    return "INPUT_EVIDENCE " + " · ".join(bits)
