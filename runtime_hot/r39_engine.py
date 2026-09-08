"""Hot R39 v14 reasoning-control shim.

Operationalizes the LALM v1.2 control contract and reconstructs deterministic
control turns for historical user messages so continued conversations retain a
stable transformed prefix for recurrent-state reuse.
"""
from __future__ import annotations

import re
import types
import urllib.request

_IMPL_URL = "https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/dev/runtime_hot/r39_engine_impl.py"
_req = urllib.request.Request(_IMPL_URL, headers={"User-Agent": "swrlz-hot-r39-v14"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _source = _response.read(4_000_001)
if len(_source) > 4_000_000:
    raise RuntimeError("R39_IMPL_TOO_LARGE")
_source.decode("utf-8")
_impl = types.ModuleType("swrlz_hot_r39_engine_impl_v11")
_impl.__file__ = _IMPL_URL
exec(compile(_source, _IMPL_URL, "exec"), _impl.__dict__)

_impl.HOT_SERVER_VERSION = "2.1.23"
_impl.HOT_REVISION = "2.1.23-hot-boundary-v14-operational-reasoning-control-v1.2"
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
        "axes": codes,
        "modes": modes,
        "objectives": objectives,
        "mutation": mutation,
        "verification": verification,
        "length": "RESULT_ONLY" if "PV0" in codes else "BRIEF" if "C2" in codes else "CONCISE" if "C1" in codes else "NORMAL",
        "depth": "HIGH" if "D3" in codes else "MEDIUM" if "D2" in codes else "NORMAL",
        "technicality": "HIGH" if "T3" in codes else "TECHNICAL" if "T2" in codes else "NORMAL",
        "evidence": "HIGH" if verification in {"V3", "V4"} or "DIAGNOSTIC" in modes else "MEDIUM" if verification == "V2" else "NORMAL",
    }

def _contract_directive(contract: dict) -> str:
    modes = contract["modes"] or ["GENERAL"]
    objective = contract["objectives"][0] if contract["objectives"] else "SATISFY_INTENT"
    parts = [
        f"LALM control v1.2. Mode={'+'.join(modes)}; objective={objective}.",
        f"Depth={contract['depth']}; technicality={contract['technicality']}; evidence={contract['evidence']}.",
    ]
    if "DIAGNOSTIC" in modes:
        parts.append("Compare plausible causes against available evidence, reject weak causes, and report the best-supported root cause rather than a generic symptom.")
    if "VERIFICATION" in modes:
        parts.append("Separate observed facts from inference and state material uncertainty.")
    if "ARCHITECTURE" in modes:
        parts.append("Preserve requirements and invariants, compare alternatives and failure modes, then select the best-supported design.")
    if contract["length"] in {"BRIEF", "CONCISE", "RESULT_ONLY"}:
        parts.append("Keep the visible answer short and dense without reducing analytical depth or omitting decisive evidence.")
    if contract["mutation"] == "M0":
        parts.append("Read-only authority: do not claim changes, execution, or deployment were authorized or performed.")
    elif contract["mutation"] == "M1":
        parts.append("Proposal authority only: suggest changes without claiming execution.")
    return " ".join(parts)

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
    yield {"type": "STATUS", "phase": "REASONING_CONTRACT", "reason": f"v1.2 axes={axes} · mode={modes} · objective={objectives} · depth={contract['depth']} · technicality={contract['technicality']} · evidence={contract['evidence']} · mutation={contract['mutation']} · verify={contract['verification']} · presentation={contract['length']}"}
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
        result["reasoningControlSpecVersion"] = "1.2"
        result["reasoningControlArchitecture"] = "intent -> reasoning -> execution/verification -> presentation"
        result["reasoningPresentationSeparated"] = True
        result["mutationAuthoritySeparated"] = True
        result["reasoningContractTelemetry"] = True
        result["reasoningControlOperationalPrompts"] = True
        result["reasoningControlStableHistoricalReconstruction"] = True
        result["reasoningControlPrefixCompatible"] = True
    return result
