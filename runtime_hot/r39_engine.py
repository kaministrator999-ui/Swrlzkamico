"""Hot-swappable R39 engine entrypoint.

This module is the performance/tuning boundary for LOCAL_R39. The stable server owns
routing/auth/contracts; inference experiments live here on non-deploying `dev` and are
loaded into /tmp by /api/hot/sync without a Vercel redeploy.

Public contract: ENGINE_ID, MODEL_SHA256, inspect_engine(), generate_events().
"""
from __future__ import annotations

import numpy as np

import swyrlz.r39_inference as base
import swyrlz.r39_tokenizer_patch  # noqa: F401

ENGINE_ID = base.ENGINE_ID
MODEL_SHA256 = base.MODEL_SHA256
HOT_REVISION = "2.1.16-hot-boundary-v2"

# Keep the bundled implementation as the correctness oracle/fallback ABI, but move
# performance-sensitive policy here so future tuning is a dev hot-sync, not a deploy.
_ORIGINAL_MATRIX = base.R39Model.matrix
_ORIGINAL_RENDER_CHAT_PROMPT = base.render_chat_prompt


def _cache(self: base.R39Model) -> dict[str, np.ndarray]:
    cache = getattr(self, "_hot_tensor_cache", None)
    if cache is None:
        cache = {}
        self._hot_tensor_cache = cache
    return cache


def _hot_matrix(self: base.R39Model, name: str) -> np.ndarray:
    d = self.desc[name]
    shape = d["shape"]
    elements = 1
    for dim in shape:
        elements *= int(dim)
    # Cache only small tensors (norm vectors, tiny conv kernels, etc.). Large model
    # matrices stay bounded-memory and are never permanently materialized.
    if elements <= 262_144:
        cache = _cache(self)
        hit = cache.get(name)
        if hit is not None:
            return hit
        value = _ORIGINAL_MATRIX(self, name)
        cache[name] = value
        return value
    return _ORIGINAL_MATRIX(self, name)


def _hot_vector(self: base.R39Model, name: str) -> np.ndarray:
    return _hot_matrix(self, name).reshape(-1)


def _hot_matvec(self: base.R39Model, name: str, x: np.ndarray) -> np.ndarray:
    d = self.desc[name]
    shape = d["shape"]
    cols = int(shape[0])
    rows = int(shape[1]) if len(shape) > 1 else 1
    if x.size != cols:
        raise base.R39InferenceError("R39_MATVEC_SHAPE_MISMATCH", f"{name}: expected {cols}, got {x.size}")
    rb = self._row_bytes(d["kind"], cols)
    raw = self._raw(name)
    # Hot knob: larger bounded dequant batches reduce Python loop overhead while
    # preserving the no-full-matrix materialization invariant.
    target_bytes = 16 * 1024 * 1024
    batch_rows = max(1, min(rows, max(64, target_bytes // max(4 * cols, 1))))
    out = np.empty(rows, dtype=np.float32)
    for start in range(0, rows, batch_rows):
        count = min(batch_rows, rows - start)
        block = raw[start * rb:(start + count) * rb]
        matrix = base._deq(d["kind"], block, (cols, count))
        out[start:start + count] = matrix @ x
    return out


def _hot_render_chat_prompt(payload):
    # The bridge directive is already enforced by stream/event contracts. Avoid paying
    # recurrent prefill cost for verbose boilerplate on every local request.
    clone = dict(payload)
    directive = str(clone.get("responseDirective") or "").strip()
    if directive.startswith("Answer directly and truthfully."):
        clone["responseDirective"] = "Answer directly and truthfully."
    return _ORIGINAL_RENDER_CHAT_PROMPT(clone)


# Install tuning on the bundled ABI at import time. generate_events() and
# inspect_engine() below therefore execute through this hot policy immediately.
base.R39Model.matrix = _hot_matrix
base.R39Model.vector = _hot_vector
base.R39Model.matvec = _hot_matvec
base.render_chat_prompt = _hot_render_chat_prompt


def inspect_engine():
    state = base.inspect_engine()
    if isinstance(state, dict):
        state = {**state, "hotRevision": HOT_REVISION, "tuningBoundary": "runtime_hot/dev"}
    return state


def generate_events(payload, is_cancelled=None):
    yield from base.generate_events(payload, is_cancelled)
