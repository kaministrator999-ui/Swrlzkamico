from __future__ import annotations

from typing import Any

import api.chat as chat
from swyrlz.interpretation_contract import normalize_provenance, presentation_mode_for_request


def install(server) -> None:
    """Extend the current chat normalizer without changing the literal user prompt.

    This deliberately installs after the existing chat extension layer so generation controls
    remain intact. Provenance is bounded evidence only; no semantic correction is performed here.
    """

    base_normalize = chat._normalize_chat_request

    def normalize(payload: dict[str, Any]) -> dict[str, Any]:
        normalized = base_normalize(payload)
        provenance = normalize_provenance(payload.get("inputProvenance"))
        normalized["inputProvenance"] = provenance.to_dict()
        normalized["presentationIntent"] = presentation_mode_for_request(normalized.get("prompt", ""))
        normalized["receivedText"] = normalized.get("prompt", "")
        return normalized

    chat._normalize_chat_request = normalize
    server.CAPABILITIES["intent-preserving-input"] = {
        "kind": "request-interpretation",
        "ready": True,
        "receivedTextImmutable": True,
        "provenance": ["typed", "speech", "paste", "unknown"],
        "semanticRepairLocation": "reasoning-controller",
        "tokenizerMutationRequired": False,
    }
    server.CAPABILITIES["presentation-intent"] = {
        "kind": "request-interpretation",
        "ready": True,
        "modes": ["PROSE", "COPYABLE_BLOCK", "CODE", "MIXED"],
    }
    server._write_server_state()
