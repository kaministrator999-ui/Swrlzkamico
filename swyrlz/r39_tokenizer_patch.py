from __future__ import annotations

import re
from typing import Any

from swyrlz import r39_inference as r39

_ORIGINAL_INIT = r39.BpeTokenizer.__init__


def _normalized_kind(spec: dict[str, Any]) -> str:
    raw = str(spec.get("kind") or spec.get("model") or spec.get("type") or "").strip()
    return re.sub(r"[^A-Z0-9]+", "_", raw.upper()).strip("_")


def _structural_bpe(spec: dict[str, Any]) -> bool:
    tokens = spec.get("tokens")
    merges = spec.get("merges")
    if not isinstance(tokens, list) or not tokens or not isinstance(merges, list) or not merges:
        return False
    sample = merges[: min(64, len(merges))]
    return bool(sample) and all(isinstance(item, str) and " " in item for item in sample)


def _compatible_init(self: r39.BpeTokenizer, spec: dict[str, Any]) -> None:
    """Normalize harmless producer labels only when the serialized structure proves byte-level BPE."""
    kind = _normalized_kind(spec)
    aliases = {
        "GGML_BPE", "SWYRLZX_BPE", "BPE", "GPT2_BPE", "GPT_2_BPE",
        "BYTE_BPE", "BYTE_LEVEL_BPE", "BYTELEVEL_BPE", "HF_BPE", "HUGGINGFACE_BPE",
    }
    if kind in {"GGML_BPE", "SWYRLZX_BPE"}:
        return _ORIGINAL_INIT(self, spec)
    if kind in aliases or _structural_bpe(spec):
        normalized = dict(spec)
        normalized["kind"] = "SWYRLZX_BPE"
        _ORIGINAL_INIT(self, normalized)
        self.spec = spec
        self.source_kind = str(spec.get("kind") or spec.get("model") or spec.get("type") or "<structural-bpe>")
        self.resolved_kind = "SWYRLZX_BPE"
        return
    raise r39.R39InferenceError(
        "R39_TOKENIZER_KIND_UNSUPPORTED",
        f"Tokenizer kind {kind or '<missing>'} is not structurally compatible with the byte-level BPE engine.",
    )


r39.BpeTokenizer.__init__ = _compatible_init
