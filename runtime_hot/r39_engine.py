"""Hot R39 v17 append-ready cursor + exact prefix-divergence diagnostics.

Keeps compact deterministic reasoning control and the v16 post-generation recurrent
cursor finalization. v17 adds token-level cache diagnostics before prefix restore so
we can see exactly where a completed hot cursor diverges from the next rendered
request instead of inferring the boundary from reused=N telemetry.
"""
from __future__ import annotations

import re
import types
import urllib.request

_IMPL_URL = "https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/dev/runtime_hot/r39_engine_impl.py"
_req = urllib.request.Request(_IMPL_URL, headers={"User-Agent": "swrlz-hot-r39-v17"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _source = _response.read(4_000_001)
if len(_source) > 4_000_000:
    raise RuntimeError("R39_IMPL_TOO_LARGE")
_source_text = _source.decode("utf-8")

# v16 behavior retained: generation used to stop before forwarding EOS. Commit EOS
# plus canonical trailing newline while the model is already hot, then cache that
# completed cursor as the newest prefix entry.
_old_eos = '''            if model.tokenizer.eos is not None and next_token == int(model.tokenizer.eos):
                yield {"type": "STATUS", "phase": "STOP_DIAGNOSTIC", "reason": f"EOS selected at decode step {ordinal}."}
                break
'''
_new_eos = '''            if model.tokenizer.eos is not None and next_token == int(model.tokenizer.eos):
                sequence_tokens.append(next_token)
                logits = _forward_hot(model, next_token, state, need_logits=True, diag=None)
                if logits is None:
                    raise base.R39InferenceError("R39_CURSOR_EOS_LOGITS_MISSING", "EOS cursor finalization returned no logits.")
                framing_tokens = model.tokenizer.encode("\\n")
                for framing_token in framing_tokens:
                    sequence_tokens.append(framing_token)
                    logits = _forward_hot(model, framing_token, state, need_logits=True, diag=None)
                    if logits is None:
                        raise base.R39InferenceError("R39_CURSOR_FRAME_LOGITS_MISSING", "Post-generation framing returned no logits.")
                yield {"type": "STATUS", "phase": "HOT_CURSOR_READY", "reason": f"EOS selected at decode step {ordinal}; committed EOS + {len(framing_tokens)} end-of-turn framing token(s) into the hot recurrent cursor before waiting for the next user turn."}
                break
'''
if _old_eos not in _source_text:
    raise RuntimeError("R39_V17_EOS_PATCH_TARGET_MISSING")
_source_text = _source_text.replace(_old_eos, _new_eos, 1)

# v17: before normal exact-prefix lookup, compare the current rendered token stream
# with every resident prefix-cache entry. The newest entry is the just-completed hot
# cursor on the normal path. Report full common-prefix lengths and a small token window
# around the first divergence. This is diagnostics only; reuse semantics are unchanged.
_old_prefix_lookup = '''        prefix_len, cached_state, cached_logits = _prefix_get(tokens)
        state = cached_state if cached_state is not None else base.RecurrentState()
'''
_new_prefix_lookup = '''        with _PREFIX_LOCK:
            _diag_entries = [
                {"tokens": list(item.get("tokens") or []), "usedAt": float(item.get("usedAt", 0.0))}
                for item in _PREFIX_CACHE
            ]
        _diag_entries.sort(key=lambda item: item["usedAt"], reverse=True)
        _diag_rows = []
        _best_partial = None
        _now = time.time()
        for _idx, _entry in enumerate(_diag_entries):
            _cached = _entry["tokens"]
            _limit = min(len(_cached), len(tokens))
            _lcp = 0
            while _lcp < _limit and _cached[_lcp] == tokens[_lcp]:
                _lcp += 1
            _age = max(0.0, _now - _entry["usedAt"])
            _diag_rows.append(f"#{_idx}:len={len(_cached)},lcp={_lcp},age={_age:.1f}s")
            if _best_partial is None or _lcp > _best_partial["lcp"] or (_lcp == _best_partial["lcp"] and _entry["usedAt"] > _best_partial["usedAt"]):
                _best_partial = {"index": _idx, "tokens": _cached, "lcp": _lcp, "usedAt": _entry["usedAt"], "age": _age}
        yield {
            "type": "STATUS",
            "phase": "PREFIX_CACHE_DIAGNOSTIC",
            "reason": f"current={len(tokens)} token(s) · resident={len(_diag_entries)} · " + (" · ".join(_diag_rows) if _diag_rows else "cache empty"),
        }
        if _best_partial is not None:
            _cached = _best_partial["tokens"]
            _lcp = int(_best_partial["lcp"])
            if _lcp < min(len(_cached), len(tokens)):
                _cached_id = int(_cached[_lcp])
                _current_id = int(tokens[_lcp])
                _c0, _c1 = max(0, _lcp - 4), min(len(_cached), _lcp + 5)
                _n0, _n1 = max(0, _lcp - 4), min(len(tokens), _lcp + 5)
                _cached_window = " | ".join(f"{i}:{int(_cached[i])}:{_token_text(model, int(_cached[i]))!r}" for i in range(_c0, _c1))
                _current_window = " | ".join(f"{i}:{int(tokens[i])}:{_token_text(model, int(tokens[i]))!r}" for i in range(_n0, _n1))
                yield {
                    "type": "STATUS",
                    "phase": "PREFIX_MISMATCH",
                    "reason": f"best resident entry #{_best_partial['index']} diverges at token index {_lcp} (1-based {_lcp + 1}); cached={_cached_id}:{_token_text(model, _cached_id)!r}, current={_current_id}:{_token_text(model, _current_id)!r}; cachedWindow=[{_cached_window}]; currentWindow=[{_current_window}]",
                }
            elif len(_cached) <= len(tokens):
                yield {
                    "type": "STATUS",
                    "phase": "PREFIX_MATCH",
                    "reason": f"best resident entry #{_best_partial['index']} is an exact {len(_cached)}-token prefix of the {len(tokens)}-token current request; only the appended suffix should require prefill.",
                }
            else:
                yield {
                    "type": "STATUS",
                    "phase": "PREFIX_TRUNCATION",
                    "reason": f"current request ends after {_lcp} token(s) but resident entry #{_best_partial['index']} continues to {len(_cached)} token(s); history/rendering was shortened or replaced.",
                }

        prefix_len, cached_state, cached_logits = _prefix_get(tokens)
        state = cached_state if cached_state is not None else base.RecurrentState()
'''
if _old_prefix_lookup not in _source_text:
    raise RuntimeError("R39_V17_PREFIX_PATCH_TARGET_MISSING")
_source_text = _source_text.replace(_old_prefix_lookup, _new_prefix_lookup, 1)

_impl = types.ModuleType("swrlz_hot_r39_engine_impl_v17")
_impl.__file__ = _IMPL_URL
exec(compile(_source_text, _IMPL_URL, "exec"), _impl.__dict__)

_impl.HOT_SERVER_VERSION = "2.1.26"
_impl.HOT_REVISION = "2.1.26-hot-boundary-v17-exact-prefix-divergence-trace-v1.5"
_impl._REFERENCE_RERANK_CANDIDATES = 6

_original_format_stats = _impl._format_stats
def _format_stats(stats):
    return "skipped" if not stats else _original_format_stats(stats)
_impl._format_stats = _format_stats

_RULES = (
    (r"\b(brief|short)\b", "C2"),
    (r"\b(concise|compact)\b", "C1"),
    (r"\b(exhaustive)\b", "B3"),
    (r"\b(comprehensive)\b", "B2"),
    (r"\b(deep|mechanistic|root cause)\b", "D3"),
    (r"\b(in[- ]depth|detailed)\b", "D2"),
    (r"\b(expert[- ]level|implementation[- ]ready)\b", "T3"),
    (r"\b(technical|technically)\b", "T2"),
    (r"\b(step[- ]by[- ]step|walk me through)\b", "S2"),
    (r"\b(fact[- ]check|verify|verified|validate)\b", "E2"),
    (r"\b(reproduce|cross[- ]check|proof)\b", "E3"),
    (r"\b(just the result|result only|no explanation)\b", "PV0"),
)
_MODE_RULES = (
    (r"\b(diagnose|diagnostic|failure|root cause|why .* fail)\b", "DIAGNOSTIC", "FIND_ROOT_CAUSE"),
    (r"\b(compare|comparative|versus|\bvs\b)\b", "COMPARATIVE", "SELECT_BEST_OPTION"),
    (r"\b(fact[- ]check|verify|validate|audit)\b", "VERIFICATION", "VERIFY"),
    (r"\b(design|architecture|redesign)\b", "ARCHITECTURE", "DESIGN"),
)

def _reasoning_contract(prompt: str) -> dict:
    text = " ".join(str(prompt or "").lower().split())
    by_family = {}
    for pattern, code in _RULES:
        if re.search(pattern, text):
            by_family[re.match(r"[A-Z]+", code).group(0)] = code
    modes, objectives = [], []
    for pattern, mode, objective in _MODE_RULES:
        if re.search(pattern, text):
            modes.append(mode); objectives.append(objective)
    mutation = "M0"
    if re.search(r"\b(deploy|release|publish)\b", text): mutation = "M3"
    elif re.search(r"\b(fix|patch|update|modify|change|implement|build)\b", text): mutation = "M2"
    elif re.search(r"\b(suggest|propose|draft (?:a )?patch)\b", text): mutation = "M1"
    if re.search(r"\b(do not|don't|dont|no) (?:change|modify|patch|deploy|execute|run)\b|\bread[- ]only\b", text): mutation = "M0"
    verification = "V0"
    if re.search(r"\b(audit|audit-grade)\b", text): verification = "V4"
    elif re.search(r"\b(reproduce|cross[- ]check|proof)\b", text): verification = "V3"
    elif re.search(r"\b(verify|validate|test|regression)\b", text): verification = "V2"
    elif re.search(r"\b(sanity[- ]check|check)\b", text): verification = "V1"
    codes = list(by_family.values())
    return {
        "axes": codes, "modes": modes, "objectives": objectives,
        "mutation": mutation, "verification": verification,
        "length": "RESULT_ONLY" if "PV0" in codes else "BRIEF" if "C2" in codes else "CONCISE" if "C1" in codes else "NORMAL",
        "depth": "HIGH" if "D3" in codes else "MEDIUM" if "D2" in codes else "NORMAL",
        "technicality": "HIGH" if "T3" in codes else "TECHNICAL" if "T2" in codes else "NORMAL",
        "evidence": "HIGH" if verification in {"V3", "V4"} or "DIAGNOSTIC" in modes else "MEDIUM" if verification == "V2" else "NORMAL",
    }

def _contract_directive(contract: dict) -> str:
    modes = contract["modes"] or ["GENERAL"]
    bits = ["RC1.5", f"mode={'+'.join(modes)}", f"depth={contract['depth']}", f"tech={contract['technicality']}", f"evidence={contract['evidence']}", f"mutation={contract['mutation']}", f"verify={contract['verification']}", f"output={contract['length']}"]
    if "DIAGNOSTIC" in modes: bits.append("compare-causes>evidence>root-cause")
    if "VERIFICATION" in modes: bits.append("facts!=inference;state-uncertainty")
    if "ARCHITECTURE" in modes: bits.append("preserve-invariants;compare-failures;select-design")
    if contract["mutation"] == "M0": bits.append("read-only")
    elif contract["mutation"] == "M1": bits.append("proposal-only")
    return " ".join(bits)

def _controlled_payload(payload):
    clone = dict(payload)
    transformed = []
    for turn in list(clone.get("history") or []):
        if not isinstance(turn, dict):
            continue
        role = str(turn.get("role", "USER")).upper()
        text = str(turn.get("text", "")).strip()
        if role not in {"ASSISTANT", "AI", "SWRLZ", "SELF", "SYSTEM"} and text:
            transformed.append({"role": "SYSTEM", "text": _contract_directive(_reasoning_contract(text))})
        transformed.append(dict(turn))
    current = _reasoning_contract(str(clone.get("prompt") or ""))
    transformed.append({"role": "SYSTEM", "text": _contract_directive(current)})
    clone["history"] = transformed
    return clone, current

ENGINE_ID = _impl.ENGINE_ID
MODEL_SHA256 = _impl.MODEL_SHA256
HOT_SERVER_VERSION = _impl.HOT_SERVER_VERSION
HOT_REVISION = _impl.HOT_REVISION

def generate_events(payload, is_cancelled=None):
    controlled, contract = _controlled_payload(payload)
    axes = ",".join(contract["axes"]) or "defaults"
    modes = "+".join(contract["modes"]) or "GENERAL"
    objectives = "+".join(contract["objectives"]) or "SATISFY_INTENT"
    yield {"type": "STATUS", "phase": "REASONING_CONTRACT", "reason": f"v1.5 prefix-divergence-trace · axes={axes} · mode={modes} · objective={objectives} · depth={contract['depth']} · technicality={contract['technicality']} · evidence={contract['evidence']} · mutation={contract['mutation']} · verify={contract['verification']} · presentation={contract['length']}"}
    yield from _impl.generate_events(controlled, is_cancelled)

def inspect_engine():
    result = _impl.inspect_engine()
    if isinstance(result, dict):
        result["hotServerVersion"] = HOT_SERVER_VERSION
        result["hotRevision"] = HOT_REVISION
        result["referenceCandidateRerank"] = True
        result["referenceCandidateCount"] = 6
        result["nativeVerifiedFastRerank"] = True
        result["diagnosticSkippedLogitsLabel"] = True
        result["reasoningControl"] = True
        result["reasoningControlSpecVersion"] = "1.5"
        result["reasoningControlArchitecture"] = "intent -> compact control -> reasoning -> execution/verification -> presentation"
        result["reasoningPresentationSeparated"] = True
        result["mutationAuthoritySeparated"] = True
        result["reasoningContractTelemetry"] = True
        result["reasoningControlOperationalPrompts"] = True
        result["reasoningControlStableHistoricalReconstruction"] = True
        result["reasoningControlPrefixCompatible"] = True
        result["reasoningControlCompactHistoricalDirectives"] = True
        result["reasoningControlAvoidsEnglishDirectiveInflation"] = True
        result["postGenerationCursorAdvance"] = True
        result["postGenerationEosCommitted"] = True
        result["appendReadyRecurrentState"] = True
        result["prefixCacheRecoveryFallback"] = True
        result["prefixDivergenceDiagnostics"] = True
        result["prefixMismatchTokenWindows"] = True
        result["prefixCacheInventoryTelemetry"] = True
    return result
