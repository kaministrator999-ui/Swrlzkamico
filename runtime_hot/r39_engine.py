"""Hot-swappable R39 engine entrypoint.

v16 keeps the pipelined/checkpointed R39 path, tightens programming-response
completion, treats assistant identity as metadata rather than output boilerplate,
and shortens the stable directive to reduce first-turn prefill work.
"""
from __future__ import annotations

import re
import threading
import time
from collections import OrderedDict
from typing import Any

import numpy as np

import swyrlz.r39_inference as base
import swyrlz.r39_tokenizer_patch  # noqa: F401
from swyrlz import r39_native as native_bridge

ENGINE_ID = "swrlz_r39_native_qmatvec_v1" if native_bridge.available() else base.ENGINE_ID
MODEL_SHA256 = base.MODEL_SHA256
HOT_SERVER_VERSION = "2.1.25"
HOT_REVISION = "2.1.25-hot-boundary-v16-strict-code-live-contract"

_ORIGINAL_MATRIX = base.R39Model.matrix
_ORIGINAL_ROW = base.R39Model.row
_ORIGINAL_RENDER_CHAT_PROMPT = base.render_chat_prompt

_MODEL_LOCK = threading.RLock()
_MODEL: base.R39Model | None = None
_MODEL_READY_AT = 0.0

_TENSOR_CACHE_LOCK = threading.RLock()
_CACHE_BUDGET_BYTES = 96 * 1024 * 1024
_CACHE_ITEM_MAX_BYTES = 12 * 1024 * 1024
_TOKEN_ROW_CACHE_MAX = 512

_CONTEXT_LOCK = threading.RLock()
_CONTEXTS: dict[str, dict[str, Any]] = {}
_CONTEXT_TTL_SECONDS = 20 * 60
_CONTEXT_MAX_ENTRIES = 2
_CONTEXT_MAX_TOKENS = 2048
_CONTEXT_MAX_CHECKPOINTS = 10
_PREFILL_CHECKPOINT_EVERY = 32
_LIVE_CHECKPOINT_EVERY = 16

_JOB_LOCK = threading.RLock()
_JOBS: dict[str, dict[str, Any]] = {}
_JOB_TTL_SECONDS = 15 * 60
_MAX_JOBS = 12

_ABSOLUTE_RESPONSE_HARD_CAP = 768
_RESPONSE_EXTENSION_STEP = 64
_STABLE_RESPONSE_DIRECTIVE = (
    "Assistant name metadata: §wyrlz. Do not greet, introduce, or sign with the name unless the user explicitly asks about the name or identity. "
    "Answer directly, completely, naturally, and satisfy every requested part. "
    "For programming requests, provide runnable code first, then any requested explanation; silently verify syntax, formulas, I/O behavior, and code/explanation consistency before ending."
)


def _cache(self: base.R39Model) -> dict[str, np.ndarray]:
    cache = getattr(self, "_hot_tensor_cache", None)
    if cache is None:
        cache = {}
        self._hot_tensor_cache = cache
        self._hot_tensor_cache_bytes = 0
    return cache


def _hot_matrix(self: base.R39Model, name: str) -> np.ndarray:
    d = self.desc[name]
    elements = 1
    for dim in d["shape"]:
        elements *= int(dim)
    decoded_bytes = elements * 4
    if decoded_bytes <= _CACHE_ITEM_MAX_BYTES:
        with _TENSOR_CACHE_LOCK:
            cache = _cache(self)
            hit = cache.get(name)
            if hit is not None:
                return hit
            used = int(getattr(self, "_hot_tensor_cache_bytes", 0))
            if used + decoded_bytes <= _CACHE_BUDGET_BYTES:
                value = _ORIGINAL_MATRIX(self, name)
                cache[name] = value
                self._hot_tensor_cache_bytes = used + int(value.nbytes)
                return value
    return _ORIGINAL_MATRIX(self, name)


def _hot_vector(self: base.R39Model, name: str) -> np.ndarray:
    return _hot_matrix(self, name).reshape(-1)


def _hot_row(self: base.R39Model, name: str, row: int) -> np.ndarray:
    if name != "token_embd.weight":
        return _ORIGINAL_ROW(self, name, row)
    cache = getattr(self, "_hot_token_row_cache", None)
    if cache is None:
        cache = OrderedDict()
        self._hot_token_row_cache = cache
    key = int(row)
    value = cache.get(key)
    if value is not None:
        cache.move_to_end(key)
        return value
    value = _ORIGINAL_ROW(self, name, row).astype(np.float32, copy=False)
    cache[key] = value
    if len(cache) > _TOKEN_ROW_CACHE_MAX:
        cache.popitem(last=False)
    return value


def _fallback_matvec(self: base.R39Model, name: str, x: np.ndarray) -> np.ndarray:
    d = self.desc[name]
    shape = d["shape"]
    cols = int(shape[0])
    rows = int(shape[1]) if len(shape) > 1 else 1
    if x.size != cols:
        raise base.R39InferenceError("R39_MATVEC_SHAPE_MISMATCH", f"{name}: expected {cols}, got {x.size}")
    rb = self._row_bytes(d["kind"], cols)
    raw = self._raw(name)
    batch_rows = max(1, min(rows, max(64, (16 * 1024 * 1024) // max(4 * cols, 1))))
    out = np.empty(rows, dtype=np.float32)
    for start in range(0, rows, batch_rows):
        count = min(batch_rows, rows - start)
        block = raw[start * rb:(start + count) * rb]
        matrix = base._deq(d["kind"], block, (cols, count))
        out[start:start + count] = matrix @ x
    return out


def _hot_matvec(self: base.R39Model, name: str, x: np.ndarray) -> np.ndarray:
    if native_bridge.available():
        out = native_bridge.matvec(self, name, x)
        if out is not None:
            return out
    return _fallback_matvec(self, name, x)


def _hot_render_chat_prompt(payload):
    clone = dict(payload)
    directive = str(clone.get("responseDirective") or "").strip()
    if (
        not directive
        or directive.startswith("Answer directly and truthfully.")
        or directive.startswith("You are §wyrlz. Answer directly")
        or directive.startswith("Assistant name metadata:")
        or "SWRLZ_RESPONSE_BUDGET" in directive
    ):
        clone["responseDirective"] = _STABLE_RESPONSE_DIRECTIVE
    return _ORIGINAL_RENDER_CHAT_PROMPT(clone)


base.R39Model.matrix = _hot_matrix
base.R39Model.vector = _hot_vector
base.R39Model.row = _hot_row
base.R39Model.matvec = _hot_matvec
base.render_chat_prompt = _hot_render_chat_prompt


def _prepare_static(model: base.R39Model) -> dict[str, Any]:
    static = getattr(model, "_hot_static_tensors", None)
    if static is not None:
        return static
    with _MODEL_LOCK:
        static = getattr(model, "_hot_static_tensors", None)
        if static is not None:
            return static
        layers = []
        for i, kvh in enumerate(base.LAYER_KV):
            item = {
                "attn_norm": model.vector(f"blk.{i}.attn_norm.weight"),
                "ffn_norm": model.vector(f"blk.{i}.ffn_norm.weight"),
            }
            if kvh == 0:
                item["conv_weight"] = model.matrix(f"blk.{i}.shortconv.conv.weight")
            else:
                item["q_norm"] = model.vector(f"blk.{i}.attn_q_norm.weight")
                item["k_norm"] = model.vector(f"blk.{i}.attn_k_norm.weight")
            layers.append(item)
        static = {"layers": layers, "final_norm": model.vector("token_embd_norm.weight")}
        model._hot_static_tensors = static
        return static


def _get_model() -> base.R39Model:
    global _MODEL, _MODEL_READY_AT
    if _MODEL is not None:
        return _MODEL
    with _MODEL_LOCK:
        if _MODEL is not None:
            return _MODEL
        load = base.ensure_r39()
        if not load.get("modelReady"):
            raise base.R39InferenceError(str(load.get("code", "R39_LOAD_FAILED")), str(load.get("detail", "R39 reconstruction failed.")))
        _MODEL = base.R39Model(base.RAW)
        _prepare_static(_MODEL)
        _MODEL_READY_AT = time.time()
        return _MODEL


def _clone_state(state: base.RecurrentState) -> base.RecurrentState:
    clone = base.RecurrentState()
    clone.pos = int(state.pos)
    clone.conv = {i: value.copy() for i, value in state.conv.items()}
    clone.kv = {i: [(k.copy(), v.copy()) for k, v in values] for i, values in state.kv.items()}
    return clone


def _cleanup_contexts(now: float | None = None) -> None:
    now = time.time() if now is None else now
    with _CONTEXT_LOCK:
        expired = [k for k, v in _CONTEXTS.items() if now - float(v.get("updatedAt", now)) > _CONTEXT_TTL_SECONDS]
        for key in expired:
            _CONTEXTS.pop(key, None)
        if len(_CONTEXTS) > _CONTEXT_MAX_ENTRIES:
            ordered = sorted(_CONTEXTS.items(), key=lambda item: float(item[1].get("updatedAt", 0)))
            for key, _ in ordered[: max(0, len(_CONTEXTS) - _CONTEXT_MAX_ENTRIES)]:
                _CONTEXTS.pop(key, None)


def _resume_context(thread_id: str, tokens: list[int]) -> tuple[base.RecurrentState, int, np.ndarray | None, str]:
    if not thread_id:
        return base.RecurrentState(), 0, None, "no-thread-id"
    _cleanup_contexts()
    with _CONTEXT_LOCK:
        entry = _CONTEXTS.get(thread_id)
        if entry is None:
            return base.RecurrentState(), 0, None, "miss"
        best = None
        for checkpoint in entry.get("checkpoints") or []:
            cached_tokens = checkpoint.get("tokens")
            cached_state = checkpoint.get("state")
            if not isinstance(cached_tokens, tuple) or cached_state is None:
                continue
            n = len(cached_tokens)
            if n > len(tokens) or tuple(tokens[:n]) != cached_tokens:
                continue
            if n == len(tokens) and not isinstance(checkpoint.get("logits"), np.ndarray):
                continue
            if best is None or n > len(best.get("tokens") or ()):
                best = checkpoint
        if best is None:
            return base.RecurrentState(), 0, None, "prefix-mismatch"
        entry["updatedAt"] = time.time()
        best["updatedAt"] = entry["updatedAt"]
        logits = best.get("logits")
        return _clone_state(best["state"]), len(best["tokens"]), logits.copy() if isinstance(logits, np.ndarray) else None, str(best.get("kind") or "hit")


def _store_context(thread_id: str, tokens: list[int], state: base.RecurrentState, logits: np.ndarray | None, *, kind: str = "prompt") -> bool:
    if not thread_id or not tokens or len(tokens) > _CONTEXT_MAX_TOKENS:
        return False
    token_tuple = tuple(tokens)
    now = time.time()
    checkpoint = {
        "tokens": token_tuple,
        "state": _clone_state(state),
        "logits": logits.copy() if isinstance(logits, np.ndarray) else None,
        "kind": kind,
        "updatedAt": now,
    }
    with _CONTEXT_LOCK:
        entry = _CONTEXTS.setdefault(thread_id, {"checkpoints": [], "updatedAt": now})
        checkpoints = entry.setdefault("checkpoints", [])
        checkpoints[:] = [cp for cp in checkpoints if cp.get("tokens") != token_tuple]
        checkpoints.append(checkpoint)
        checkpoints.sort(key=lambda cp: (len(cp.get("tokens") or ()), float(cp.get("updatedAt", 0))), reverse=True)
        del checkpoints[_CONTEXT_MAX_CHECKPOINTS:]
        entry["updatedAt"] = now
    _cleanup_contexts(now)
    return True


def _context_snapshot() -> list[dict[str, Any]]:
    _cleanup_contexts()
    now = time.time()
    with _CONTEXT_LOCK:
        return [{
            "threadId": key,
            "checkpointTokenCounts": [len(cp.get("tokens") or ()) for cp in value.get("checkpoints") or []],
            "checkpointKinds": [str(cp.get("kind") or "unknown") for cp in value.get("checkpoints") or []],
            "ageSeconds": round(now - float(value.get("updatedAt", now)), 2),
        } for key, value in _CONTEXTS.items()]


def _rms_rows(values: np.ndarray, weight: np.ndarray) -> np.ndarray:
    rows = values.astype(np.float32, copy=False)
    denom = np.sqrt(np.mean(rows * rows, axis=1, dtype=np.float32) + np.float32(1e-5), dtype=np.float32)
    return (rows / denom[:, None] * weight[None, :]).astype(np.float32)


def _forward_hot(model: base.R39Model, token: int, state: base.RecurrentState, *, need_logits: bool) -> np.ndarray | None:
    static = _prepare_static(model)
    x = model.row("token_embd.weight", token)
    for i, kvh in enumerate(base.LAYER_KV):
        layer = static["layers"][i]
        n = base._rms(x, layer["attn_norm"])
        if kvh == 0:
            projected = model.matvec(f"blk.{i}.shortconv.in_proj.weight", n)
            b, c, z = np.split(projected, 3)
            bx = (b * z).astype(np.float32)
            cw = layer["conv_weight"]
            hist = state.conv[i]
            cv = (hist[0] * cw[:, 0] + hist[1] * cw[:, 1] + bx * cw[:, 2]).astype(np.float32)
            state.conv[i][0] = hist[1].copy()
            state.conv[i][1] = bx
            op = model.matvec(f"blk.{i}.shortconv.out_proj.weight", (c * cv).astype(np.float32))
        else:
            q = model.matvec(f"blk.{i}.attn_q.weight", n)
            k = model.matvec(f"blk.{i}.attn_k.weight", n)
            v = model.matvec(f"blk.{i}.attn_v.weight", n)
            q = _rms_rows(q.reshape(16, 64), layer["q_norm"]).reshape(-1)
            k = _rms_rows(k.reshape(8, 64), layer["k_norm"]).reshape(-1)
            q = base._rope(q, 16, 64, state.pos)
            k = base._rope(k, 8, 64, state.pos)
            state.kv[i].append((k.copy(), v.copy()))
            history = state.kv[i]
            keys = np.stack([kk.reshape(8, 64) for kk, _ in history], axis=0)
            values = np.stack([vv.reshape(8, 64) for _, vv in history], axis=0)
            keys_b = keys.transpose(1, 0, 2)
            q_b = q.reshape(8, 2, 64).transpose(0, 2, 1)
            scores_b = np.matmul(keys_b, q_b).astype(np.float32) / np.float32(8.0)
            scores_b -= scores_b.max(axis=1, keepdims=True)
            weights_b = np.exp(scores_b, dtype=np.float32)
            weights_b /= weights_b.sum(axis=1, keepdims=True, dtype=np.float32)
            att = np.matmul(weights_b.transpose(0, 2, 1), values.transpose(1, 0, 2)).astype(np.float32).reshape(16, 64)
            op = model.matvec(f"blk.{i}.attn_output.weight", att.reshape(-1))
        residual = (x + op).astype(np.float32)
        fn = base._rms(residual, layer["ffn_norm"])
        gate = model.matvec(f"blk.{i}.ffn_gate.weight", fn)
        up = model.matvec(f"blk.{i}.ffn_up.weight", fn)
        ff = model.matvec(f"blk.{i}.ffn_down.weight", (base._silu(gate) * up).astype(np.float32))
        x = (residual + ff).astype(np.float32)
    x = base._rms(x, static["final_norm"])
    state.pos += 1
    if not need_logits:
        return None
    return model.matvec("token_embd.weight", x)


def _publish_generated_checkpoint(model, thread_id, prompt, prompt_tokens, generated_text, generated_tokens, state, logits, *, kind):
    if not thread_id or not generated_tokens:
        return False
    try:
        open_tokens = model.tokenizer.encode(prompt + generated_text)
        expected = len(prompt_tokens) + len(generated_tokens)
        if len(open_tokens) != expected or tuple(open_tokens[:len(prompt_tokens)]) != tuple(prompt_tokens) or tuple(open_tokens[len(prompt_tokens):]) != tuple(generated_tokens):
            return False
        return _store_context(thread_id, open_tokens, state, logits, kind=kind)
    except Exception:
        return False


def _speculative_next_turn_warmup(model, thread_id, prompt, prompt_tokens, generated_state, generated_tokens, generated_text) -> None:
    if not thread_id or not generated_tokens:
        return
    try:
        open_text = prompt + generated_text
        open_tokens = model.tokenizer.encode(open_text)
        generated_end = len(prompt_tokens) + len(generated_tokens)
        if len(open_tokens) != generated_end or tuple(open_tokens[:len(prompt_tokens)]) != tuple(prompt_tokens) or tuple(open_tokens[len(prompt_tokens):]) != tuple(generated_tokens):
            return
        state = _clone_state(generated_state)
        closed_text = open_text + "<|im_end|>\n"
        closed_tokens = model.tokenizer.encode(closed_text)
        if tuple(closed_tokens[:generated_end]) != tuple(open_tokens):
            return
        closing = closed_tokens[generated_end:]
        logits = None
        for ordinal, token in enumerate(closing, start=1):
            logits = _forward_hot(model, token, state, need_logits=(ordinal == len(closing)))
        if not closing or logits is None:
            return
        _store_context(thread_id, closed_tokens, state, logits, kind="assistant-closed")
        user_open_text = closed_text + "<|im_start|>user\n"
        user_open_tokens = model.tokenizer.encode(user_open_text)
        if tuple(user_open_tokens[:len(closed_tokens)]) != tuple(closed_tokens):
            return
        suffix = user_open_tokens[len(closed_tokens):]
        if not suffix:
            return
        for ordinal, token in enumerate(suffix, start=1):
            logits = _forward_hot(model, token, state, need_logits=(ordinal == len(suffix)))
        if logits is not None:
            _store_context(thread_id, user_open_tokens, state, logits, kind="next-user-open")
    except Exception:
        return


def _start_speculative_warmup(*args) -> None:
    threading.Thread(target=_speculative_next_turn_warmup, args=args, name="swrlz-prefill-postwarm", daemon=True).start()


def _latest_user_text(payload: dict[str, Any]) -> str:
    return str(payload.get("prompt") or "").strip()


def _plan_response_budget(payload: dict[str, Any]) -> dict[str, Any]:
    text = _latest_user_text(payload)
    lower = text.lower()
    words = len(text.split())
    code_cues = ("code","function","class","method","program","script","html","css","javascript","typescript","python","c++","cpp","java","kotlin","rust","sql","api","json","implement","debug","refactor","main.",".h",".cpp",".py",".js",".ts")
    deep_cues = ("explain","walkthrough","step by step","analyze","compare","detailed","architecture","design","research")
    multi_cues = ("multiple files","multi-file","project","all files","header","interface","tabs","full implementation")
    social_cues = ("hey","hi","hello","thanks","thank you","lol","lmao")
    kind = "normal"; planned, wrap_at, hard = 192, 152, 384
    if any(cue in lower for cue in code_cues):
        kind = "coding"; planned, wrap_at, hard = 384, 300, 576
        if any(cue in lower for cue in multi_cues) or words > 80:
            planned, wrap_at, hard = 512, 416, 704
    elif any(cue in lower for cue in deep_cues) or words > 120:
        kind = "detailed"; planned, wrap_at, hard = 320, 256, 512
    elif words <= 8 and any(lower == cue or lower.startswith(cue + " ") for cue in social_cues):
        kind = "brief-social"; planned, wrap_at, hard = 64, 48, 160
    elif words <= 20:
        planned, wrap_at, hard = 128, 96, 256
    generation = payload.get("generation") if isinstance(payload.get("generation"), dict) else {}
    if str(generation.get("budgetMode") or "").lower() == "manual":
        try:
            manual = max(1, int(generation.get("maxTokens")))
            hard = min(_ABSOLUTE_RESPONSE_HARD_CAP, manual)
            planned = min(planned, hard)
            wrap_at = min(wrap_at, max(1, planned - max(8, planned // 5)))
            kind = "manual"
        except Exception:
            pass
    planned = min(planned, _ABSOLUTE_RESPONSE_HARD_CAP)
    wrap_at = min(max(1, wrap_at), planned)
    hard = min(max(planned + 32, hard), _ABSOLUTE_RESPONSE_HARD_CAP)
    return {"kind": kind, "planned": planned, "wrapAt": wrap_at, "hard": hard}


def _looks_structurally_open(text: str) -> bool:
    value = str(text or "")
    if not value.strip():
        return False
    if value.count("```") % 2:
        return True
    if value.count("{") - value.count("}") > 0 or value.count("(") - value.count(")") > 0 or value.count("[") - value.count("]") > 0:
        return True
    tail = value.rstrip()
    return tail.endswith((":", ",", "\\", "->", "=>"))


def _response_contract(payload: dict[str, Any]) -> dict[str, Any]:
    lower = _latest_user_text(payload).lower()
    coding = any(cue in lower for cue in ("code","function","class","method","program","script","html","css","javascript","typescript","python","c++","cpp","java","kotlin","rust","sql","implement","refactor"))
    explain = any(cue in lower for cue in ("explain","explanation","overview","how it works","how the","walkthrough","briefly"))
    requirements = []
    if coding:
        requirements.extend(("code", "code-consistency"))
    if coding and explain:
        requirements.append("code-explanation")
    if coding and "function" in lower and "main" in lower and explain:
        requirements.append("function-main-explanation")
    if "fahrenheit" in lower and "celsius" in lower:
        requirements.append("fahrenheit-celsius-correctness")
    return {"coding": coding, "explain": explain, "requirements": requirements, "request": lower}


def _split_code_and_prose(text: str) -> tuple[str, str]:
    parts = str(text or "").split("```")
    return "\n".join(parts[1::2]).strip(), "\n".join(parts[::2]).strip()


def _has_real_code(value: str, fenced_code: str) -> bool:
    candidate = fenced_code.strip() if fenced_code.strip() else value
    patterns = (
        r"#include\s*[<\"]", r"\bint\s+main\s*\(", r"\b(?:void|double|float|int|string|bool)\s+[A-Za-z_]\w*\s*\(",
        r"\bdef\s+[A-Za-z_]\w*\s*\(", r"\bclass\s+[A-Za-z_]\w*\s*[:{]", r"\bfunction\s+[A-Za-z_$]\w*\s*\(",
        r"\b(?:const|let|var)\s+[A-Za-z_$]\w*\s*=", r"<html\b", r"\bselect\b.+\bfrom\b", r"\bfun\s+[A-Za-z_]\w*\s*\("
    )
    if any(re.search(pattern, candidate, re.I | re.S) for pattern in patterns):
        return True
    return "{" in candidate and "}" in candidate and ";" in candidate and any(op in candidate for op in ("=", "(", "::", "->"))


def _fahrenheit_formula_looks_correct(code: str) -> bool:
    compact = re.sub(r"\s+", "", code.lower())
    if "fahrenheit" not in compact and "f-32" not in compact:
        return False
    return any(token in compact for token in ("*5.0/9.0","*5/9.0","*5.0/9","*5/9","/1.8","*0.555","*0.556"))


def _response_contract_gaps(text: str, contract: dict[str, Any]) -> list[str]:
    value = str(text or "")
    code, prose = _split_code_and_prose(value)
    code_lower = code.lower()
    prose_lower = prose.lower()
    requirements = list(contract.get("requirements") or [])
    gaps = []
    if "code" in requirements and not _has_real_code(value, code):
        gaps.append("complete-code")
    if "code-explanation" in requirements and len(re.findall(r"[A-Za-z]{2,}", prose)) < 12:
        gaps.append("requested-explanation")
    if "function-main-explanation" in requirements and ("function" not in prose_lower or "main" not in prose_lower):
        gaps.append("function-and-main-explanation")
    if "code-consistency" in requirements and code:
        user_input_claim = "user input" in prose_lower or ("reads" in prose_lower and "user" in prose_lower)
        actual_input = any(marker in code_lower for marker in ("std::cin","scanf(","input(","readline(","prompt("))
        if user_input_claim and not actual_input:
            gaps.append("code-explanation-input-mismatch")
    if "fahrenheit-celsius-correctness" in requirements:
        if not code or not _fahrenheit_formula_looks_correct(code):
            gaps.append("fahrenheit-celsius-formula")
        prose_compact = re.sub(r"\s+", "", prose_lower)
        if "f-32" in prose_compact and ("/5" in prose_compact or "}{5}" in prose_compact) and "/9" not in prose_compact and "}{9}" not in prose_compact:
            gaps.append("fahrenheit-celsius-explanation")
    return gaps


def _generate_hot_events(payload: dict[str, Any], is_cancelled=None):
    request_id = str(payload["requestId"])
    thread_id = str(payload.get("threadId") or "").strip()[:128]
    started = time.monotonic()
    engine_entered_ms = int(time.time() * 1000)
    try:
        client_sent_ms = int(payload.get("clientSentAtMs") or 0)
    except Exception:
        client_sent_ms = 0
    approx_client_to_hot_ms = max(0, engine_entered_ms - client_sent_ms) if client_sent_ms > 0 else None
    try:
        already_warm = _MODEL is not None
        native = native_bridge.available()
        mode = "compiled direct-quantized kernels" if native else "Python/Numpy fallback (native extension not present on this worker)"
        warm_note = "Reusing warm server R39 model." if already_warm else "Opening R39 once for this server worker; subsequent requests reuse the warm model."
        diag = f"Hot engine entered · server {HOT_SERVER_VERSION} · revision {HOT_REVISION} · {mode} · serverEpochMs {engine_entered_ms}"
        if approx_client_to_hot_ms is not None:
            diag += f" · approx client→hot {approx_client_to_hot_ms}ms"
        yield {"type":"STATUS","phase":"HOT_ENGINE_ENTERED","reason":f"{diag}. {warm_note}"}
        model = _get_model()
        yield {"type":"ROUTE","phase":"ROUTE_RESOLVED","reason":f"Hot loader resolved server {HOT_SERVER_VERSION} / {HOT_REVISION}; inference backend: {mode}.","identity":{"route":"LOCAL_R39","engineId":ENGINE_ID,"modelId":str(model.manifest.get("modelId","R39")),"modelSha256":MODEL_SHA256}}
        budget = _plan_response_budget(payload)
        contract = _response_contract(payload)
        yield {"type":"STATUS","phase":"RESPONSE_BUDGET","reason":f"Adaptive response plan · kind={budget['kind']} · planned≈{budget['planned']} · wrap≈{budget['wrapAt']} · emergency ceiling={budget['hard']} token(s)."}
        if contract["requirements"]:
            yield {"type":"STATUS","phase":"RESPONSE_CONTRACT","reason":"Response completion contract armed · required: " + ", ".join(contract["requirements"]) + "."}

        prompt = base.render_chat_prompt(payload)
        tokens = model.tokenizer.encode(prompt)
        if not tokens:
            raise base.R39InferenceError("R39_PROMPT_TOKENIZATION_EMPTY", "Prompt tokenization produced no tokens.")
        generation = payload.get("generation") if isinstance(payload.get("generation"), dict) else {}
        temperature = min(2.0, max(0.0, float(generation.get("temperature", 0.1))))
        top_p = min(1.0, max(0.01, float(generation.get("topP", 0.9))))
        state, reused, cached_logits, cache_reason = _resume_context(thread_id, tokens)
        pending = tokens[reused:]
        if reused:
            yield {"type":"STATUS","phase":"PREFILL","reason":f"Conversation prefill checkpoint hit: reused {reused} token(s); only {len(pending)} new token(s) require prefill."}
        elif cache_reason == "prefix-mismatch":
            yield {"type":"STATUS","phase":"PREFILL","reason":f"No cached checkpoint matches the edited/divergent prefix; safely rebuilding all {len(tokens)} token(s)."}
        else:
            yield {"type":"STATUS","phase":"PREFILL","reason":f"Prefilling {len(tokens)} token(s); progressive recovery checkpoints every {_PREFILL_CHECKPOINT_EVERY} token(s); backend={('native-qmatvec' if native else 'python-fallback')}."}

        logits = cached_logits if not pending else None
        prefill_started = time.monotonic()
        total_new = len(pending)
        for ordinal, token in enumerate(pending, start=1):
            if is_cancelled and is_cancelled():
                raise base.R39InferenceError("REQUEST_CANCELLED", "Generation was cancelled.")
            token_started = time.monotonic()
            need_logits = ordinal == total_new
            step_logits = _forward_hot(model, token, state, need_logits=need_logits)
            if need_logits:
                logits = step_logits
            absolute_prefix = reused + ordinal
            if ordinal < total_new and ordinal % _PREFILL_CHECKPOINT_EVERY == 0:
                _store_context(thread_id, tokens[:absolute_prefix], state, None, kind=f"prefill-progress-{absolute_prefix}")
            elapsed = time.monotonic() - prefill_started
            avg = elapsed / ordinal
            if ordinal <= 2 or ordinal == total_new or ordinal % 32 == 0:
                token_s = time.monotonic() - token_started
                eta = max(0.0, avg * (total_new - ordinal))
                yield {"type":"STATUS","phase":"PREFILL","reason":f"Prefill new {ordinal}/{total_new} · cached {reused} · {token_s:.3f}s token · {avg:.3f}s avg · ETA {eta:.1f}s · backend={('native' if native else 'python')}."}
        if logits is None:
            raise base.R39InferenceError("R39_CONTEXT_CACHE_LOGITS_MISSING", "Conversation context cache did not provide terminal prefill logits.")

        cached = _store_context(thread_id, tokens, state, logits, kind="prompt")
        state = _clone_state(state) if cached else state
        decoder = base.IncrementalDecoder(model.tokenizer)
        generated_tokens: list[int] = []
        response_parts: list[str] = []
        recent: list[int] = []
        first_ms = None
        prefill_time = time.monotonic() - prefill_started
        cache_note = f"reused {reused}, prefetched {total_new}" if reused else f"prefetched {total_new}"
        yield {"type":"STATUS","phase":"GENERATING","reason":f"R39 prefill complete in {prefill_time:.2f}s ({cache_note}); adaptive output plan≈{budget['planned']}, wrap≈{budget['wrapAt']}, emergency ceiling={budget['hard']}; decoding with {('native direct-quantized matvec' if native else 'Python/Numpy fallback')}."}

        ordinal = 0
        current_limit = int(budget["hard"])
        wrap_notified = False
        extended_for_structure = False
        extended_for_contract = False
        eos_deferred = False
        last_gap_signature: tuple[str, ...] = ()
        stopped_on_eos = False
        eos_id = int(model.tokenizer.eos) if model.tokenizer.eos is not None else None
        while ordinal < current_limit:
            ordinal += 1
            if is_cancelled and is_cancelled():
                raise base.R39InferenceError("REQUEST_CANCELLED", "Generation was cancelled.")
            seed = hash(request_id) ^ (state.pos * 0x9E3779B9)
            next_token = base._sample(logits, recent[-64:], temperature, top_p, 50, 1.05, seed)
            if eos_id is not None and next_token == eos_id:
                partial = "".join(response_parts)
                gaps = _response_contract_gaps(partial, contract)
                if gaps and ordinal < _ABSOLUTE_RESPONSE_HARD_CAP:
                    masked = logits.copy()
                    masked[eos_id] = np.float32(-np.inf)
                    next_token = base._sample(masked, recent[-64:], temperature, top_p, 50, 1.05, seed ^ 0x5F3759DF)
                    signature = tuple(gaps)
                    if signature != last_gap_signature:
                        last_gap_signature = signature
                        yield {"type":"STATUS","phase":"RESPONSE_CONTRACT","reason":"EOS deferred because requested or verified response parts remain incomplete/inconsistent: " + ", ".join(gaps) + "."}
                    eos_deferred = True
                    if next_token == eos_id:
                        stopped_on_eos = True
                        break
                else:
                    stopped_on_eos = True
                    break
            text = decoder.push(next_token)
            if first_ms is None:
                first_ms = int((time.monotonic() - started) * 1000)
            if text:
                response_parts.append(text)
                yield {"type":"DELTA","phase":"GENERATING","text":text,"firstDeltaLatencyMs":first_ms}
            generated_tokens.append(next_token)
            recent.append(next_token)
            decode_started = time.monotonic()
            logits = _forward_hot(model, next_token, state, need_logits=True)
            assert logits is not None
            if not wrap_notified and ordinal >= int(budget["wrapAt"]):
                wrap_notified = True
                yield {"type":"STATUS","phase":"RESPONSE_BUDGET","reason":f"Soft wrap point reached at token {ordinal}; generation may continue until the requested response is complete."}
            if ordinal % _LIVE_CHECKPOINT_EVERY == 0 and response_parts:
                _publish_generated_checkpoint(model, thread_id, prompt, tokens, "".join(response_parts), list(generated_tokens), state, logits, kind=f"assistant-live-{ordinal}")
            if ordinal <= 4 or ordinal % 32 == 0:
                yield {"type":"STATUS","phase":"DECODE_PROGRESS","reason":f"Decode step {ordinal} · {time.monotonic()-decode_started:.3f}s · backend={('native' if native else 'python')}."}
            if ordinal >= current_limit and current_limit < _ABSOLUTE_RESPONSE_HARD_CAP:
                partial = "".join(response_parts)
                gaps = _response_contract_gaps(partial, contract)
                structural = _looks_structurally_open(partial)
                if structural or gaps:
                    next_limit = min(_ABSOLUTE_RESPONSE_HARD_CAP, current_limit + _RESPONSE_EXTENSION_STEP)
                    if next_limit > current_limit:
                        current_limit = next_limit
                        extended_for_structure = extended_for_structure or structural
                        extended_for_contract = extended_for_contract or bool(gaps)
                        yield {"type":"STATUS","phase":"RESPONSE_BUDGET","reason":f"Completion headroom extended to {current_limit} token(s) because required content is still incomplete."}

        tail = decoder.finish()
        if tail:
            response_parts.append(tail)
            yield {"type":"DELTA","phase":"GENERATING","text":tail,"firstDeltaLatencyMs":first_ms}
        response_text = "".join(response_parts)
        terminal_published = False
        if generated_tokens and logits is not None:
            terminal_published = _publish_generated_checkpoint(model, thread_id, prompt, tokens, response_text, generated_tokens, state, logits, kind="assistant-terminal-open")
        if generated_tokens:
            _start_speculative_warmup(model, thread_id, prompt, list(tokens), _clone_state(state), list(generated_tokens), response_text)

        completion_bits = ["Local R39 generation completed"]
        if terminal_published:
            completion_bits.append("response-state checkpoint published")
        completion_bits.append("next-turn warmup continues opportunistically")
        if eos_deferred:
            completion_bits.append("semantic completion gate deferred premature EOS")
        if extended_for_structure:
            completion_bits.append("completion headroom was used for open code/syntax")
        if extended_for_contract:
            completion_bits.append("completion headroom was used for requested/verified response parts")
        final_gaps = _response_contract_gaps(response_text, contract)
        if final_gaps:
            completion_bits.append("semantic verification warnings: " + ", ".join(final_gaps))
        elif contract.get("coding"):
            completion_bits.append("strict coding response checks passed")
        if not stopped_on_eos and ordinal >= current_limit:
            completion_bits.append(f"generation reached safety ceiling {current_limit}")
        yield {"type":"COMPLETED","phase":"COMPLETE","reason":"; ".join(completion_bits)+".","totalLatencyMs":int((time.monotonic()-started)*1000)}
    except base.R39InferenceError as exc:
        event_type = "CANCELLED" if exc.code == "REQUEST_CANCELLED" else "FAILED"
        phase = "CANCELLED" if event_type == "CANCELLED" else "ERROR"
        yield {"type":event_type,"phase":phase,"reason":exc.detail,"categories":[exc.code],"totalLatencyMs":int((time.monotonic()-started)*1000)}
    except Exception as exc:
        yield {"type":"FAILED","phase":"ERROR","reason":f"Hot local R39 inference failed ({type(exc).__name__}: {exc}).","categories":["R39_HOT_INFERENCE_RUNTIME_FAILED"],"totalLatencyMs":int((time.monotonic()-started)*1000)}


def _cleanup_jobs(now: float | None = None) -> None:
    now = time.time() if now is None else now
    with _JOB_LOCK:
        expired = [rid for rid, job in _JOBS.items() if job.get("done") and now - float(job.get("updatedAt", now)) > _JOB_TTL_SECONDS]
        for rid in expired:
            _JOBS.pop(rid, None)
        if len(_JOBS) > _MAX_JOBS:
            ordered = sorted(_JOBS.items(), key=lambda item: float(item[1].get("updatedAt", 0)))
            for rid, job in ordered:
                if len(_JOBS) <= _MAX_JOBS:
                    break
                if job.get("done"):
                    _JOBS.pop(rid, None)


def _append_job_event(job: dict[str, Any], event: dict[str, Any]) -> None:
    condition = job["condition"]
    with condition:
        job["events"].append(dict(event))
        job["updatedAt"] = time.time()
        condition.notify_all()


def _run_job(job: dict[str, Any], payload: dict[str, Any], is_cancelled) -> None:
    try:
        for event in _generate_hot_events(payload, is_cancelled):
            _append_job_event(job, event)
    except Exception as exc:
        _append_job_event(job, {"type":"FAILED","phase":"ERROR","reason":f"Detached R39 worker failed: {type(exc).__name__}: {exc}","categories":["R39_DETACHED_WORKER_FAILED"]})
    finally:
        condition = job["condition"]
        with condition:
            job["done"] = True
            job["updatedAt"] = time.time()
            condition.notify_all()


def _job_for(payload: dict[str, Any], is_cancelled):
    request_id = str(payload.get("requestId") or "").strip()
    if not request_id:
        return None
    _cleanup_jobs()
    with _JOB_LOCK:
        existing = _JOBS.get(request_id)
        if existing is not None:
            return existing
        condition = threading.Condition(threading.RLock())
        job = {"requestId":request_id,"createdAt":time.time(),"updatedAt":time.time(),"events":[],"done":False,"condition":condition}
        worker = threading.Thread(target=_run_job, args=(job, dict(payload), is_cancelled), name=f"swrlz-r39-job-{request_id[-16:]}", daemon=True)
        job["thread"] = worker
        _JOBS[request_id] = job
        worker.start()
        return job


def _job_snapshot() -> list[dict[str, Any]]:
    _cleanup_jobs()
    now = time.time()
    with _JOB_LOCK:
        return [{"requestId":rid,"done":bool(job.get("done")),"eventCount":len(job.get("events",[])),"ageSeconds":round(now-float(job.get("createdAt",now)),2),"updatedAgoSeconds":round(now-float(job.get("updatedAt",now)),2)} for rid, job in _JOBS.items()]


def inspect_engine():
    try:
        model = _get_model()
        jobs = _job_snapshot()
        contexts = _context_snapshot()
        native = native_bridge.available()
        return {
            "ok":True,"oneTokenReady":True,"interactiveReady":True,"engineId":ENGINE_ID,
            "modelId":model.manifest.get("modelId","R39"),"modelSha256":MODEL_SHA256,
            "tocCount":model.header["tocCount"],"tensorCount":len(model.desc),"tokenCount":len(model.tokenizer.tokens),"graphNodeCount":len(model.graph.get("nodes",[])),
            "hotServerVersion":HOT_SERVER_VERSION,"hotRevision":HOT_REVISION,"nativeBackendAvailable":native,"nativeDirectQuantizedMatvec":native,"pythonReferenceFallback":True,
            "warmModelResident":True,"warmModelAgeSeconds":round(max(0.0,time.time()-_MODEL_READY_AT),2),"decodedCacheBytes":int(getattr(model,"_hot_tensor_cache_bytes",0)),"decodedCacheBudgetBytes":_CACHE_BUDGET_BYTES,
            "tokenEmbeddingRowCacheEntries":len(getattr(model,"_hot_token_row_cache",{})),"prefillSkipsIntermediateLogits":True,"incrementalConversationPrefill":True,"multiCheckpointConversationPrefill":True,
            "progressivePrefillCheckpoints":True,"progressivePrefillCheckpointEveryTokens":_PREFILL_CHECKPOINT_EVERY,"generationPublishesReusableCheckpoints":True,"terminalAssistantCheckpointBeforeComplete":True,
            "speculativeNextTurnWarmup":True,"nextRequestNeverWaitsForWarmup":True,"liveCheckpointEveryGeneratedTokens":_LIVE_CHECKPOINT_EVERY,"prefillStaticTensorFastPath":True,
            "adaptiveResponseBudget":True,"softWrapAdvisory":True,"structureAwareBudgetOverrun":True,"responseCompletionContract":True,"codingConsistencyGuidance":True,"codingSemanticChecks":True,
            "strictCodePresenceVerification":True,"assistantNameMetadataOnly":True,"shortStableDirective":True,"eosDefersForMissingRequirements":True,"stableResponseDirectiveForCacheReuse":True,
            "vectorizedGroupedAttention":True,"batchedMatmulAttention":True,"absoluteResponseHardCap":_ABSOLUTE_RESPONSE_HARD_CAP,"conversationContextCacheMaxTokens":_CONTEXT_MAX_TOKENS,
            "conversationContextCacheTtlSeconds":_CONTEXT_TTL_SECONDS,"conversationContextMaxCheckpoints":_CONTEXT_MAX_CHECKPOINTS,"conversationContextCaches":contexts,"connectionDiagnostics":True,
            "detachedGeneration":True,"replayableJobs":jobs,"activeDetachedJobs":sum(1 for job in jobs if not job["done"]),
        }
    except base.R39InferenceError as exc:
        return {"ok":False,"oneTokenReady":False,"interactiveReady":False,"code":exc.code,"detail":exc.detail,"hotServerVersion":HOT_SERVER_VERSION,"hotRevision":HOT_REVISION}
    except Exception as exc:
        return {"ok":False,"oneTokenReady":False,"interactiveReady":False,"code":"R39_HOT_ENGINE_PROBE_FAILED","detail":f"{type(exc).__name__}: {exc}","hotServerVersion":HOT_SERVER_VERSION,"hotRevision":HOT_REVISION}


def generate_events(payload, is_cancelled=None):
    job = _job_for(payload, is_cancelled)
    if job is None:
        yield from _generate_hot_events(payload, is_cancelled)
        return
    index = 0
    condition = job["condition"]
    while True:
        event = None
        with condition:
            while index >= len(job["events"]) and not job.get("done"):
                condition.wait(timeout=1.0)
            if index < len(job["events"]):
                event = dict(job["events"][index])
                index += 1
            elif job.get("done"):
                break
        if event is not None:
            yield event
