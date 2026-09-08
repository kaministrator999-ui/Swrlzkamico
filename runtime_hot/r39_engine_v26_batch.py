"""v26-derived engine with an opt-in native batched prompt-prefill path.

This file is staged behind v30 and is not the live hot entrypoint. It reuses the exact
v26 conversational/vectorized engine source, injecting only the prompt-prefill loop.
"""
from __future__ import annotations

import urllib.request

_V26_COMMIT = "3dc70e8d02777fd622db3ae3311fad13b7382e6a"
_V26_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V26_COMMIT}/runtime_hot/r39_engine.py"
_req = urllib.request.Request(_V26_URL, headers={"User-Agent": "swrlz-hot-r39-v26-batch"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _v26 = _response.read(4_000_001)
if len(_v26) > 4_000_000:
    raise RuntimeError("R39_V26_SOURCE_TOO_LARGE")
source = _v26.decode("utf-8")

_anchor = '''_impl=types.ModuleType("swrlz_hot_r39_engine_impl_v26");_impl.__file__=_IMPL_URL
exec(compile(_source_text,_IMPL_URL,"exec"),_impl.__dict__)
'''
_injected = r"""from runtime_hot import r39_batch_prefill as _batch_prefill
_batch_anchor='''        prefill_started = time.monotonic()
        if remaining:
            for absolute_index in range(prefix_len, total):
'''
_batch_replacement='''        prefill_started = time.monotonic()
        batch_used = False
        batch_available = bool(native and callable(getattr(native_bridge, "matmat_available", None)) and native_bridge.matmat_available())
        if remaining and batch_available:
            batch_size = 64
            batch_hidden = None
            batch_processed = 0
            yield {"type":"STATUS","phase":"PREFILL_BATCH_START","reason":f"Native block prefill armed · remaining={remaining} · block={batch_size} · quantized weights reused across token columns."}
            for block_start in range(prefix_len, total, batch_size):
                if is_cancelled and is_cancelled():
                    raise base.R39InferenceError("REQUEST_CANCELLED", "Generation was cancelled.")
                block_end = min(total, block_start + batch_size)
                block_started = time.monotonic()
                block_tokens = tokens[block_start:block_end]
                batch_hidden = _batch_prefill.forward_token_block(base, native_bridge, model, state, block_tokens)
                batch_processed += len(block_tokens)
                block_elapsed = max(1e-9, time.monotonic() - block_started)
                elapsed = max(1e-9, time.monotonic() - prefill_started)
                yield {"type":"STATUS","phase":"PREFILL_BATCH","reason":f"Batch prefill {block_end}/{total} · blockTokens={len(block_tokens)} · blockRate={len(block_tokens)/block_elapsed:.1f} tok/s · aggregateRate={batch_processed/elapsed:.1f} tok/s · reused={prefix_len}."}
            if batch_hidden is not None:
                native_logits = model.matvec("token_embd.weight", batch_hidden)
                logits = _reference_rerank(model, native_logits, batch_hidden, None)
                batch_used = True
        if remaining and not batch_used:
            for absolute_index in range(prefix_len, total):
'''
if _batch_anchor not in _source_text: raise RuntimeError("R39_BATCH_PREFILL_PATCH_TARGET_MISSING")
_source_text=_source_text.replace(_batch_anchor,_batch_replacement,1)
_impl=types.ModuleType("swrlz_hot_r39_engine_impl_v26_batch");_impl.__file__=_IMPL_URL
_impl.__dict__["_batch_prefill"]=_batch_prefill
exec(compile(_source_text,_IMPL_URL,"exec"),_impl.__dict__)
"""
if _anchor not in source:
    raise RuntimeError("R39_V26_IMPL_CREATION_ANCHOR_MISSING")
source = source.replace(_anchor, _injected, 1)
exec(compile(source, _V26_URL + "#batch", "exec"), globals(), globals())
