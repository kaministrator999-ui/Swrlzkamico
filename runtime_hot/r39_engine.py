"""Hot R39 v13 reasoning-control shim.

Loads the validated native v11 implementation, preserves the fast top-6 reference
rerank, and adds the LALM v1.2 intent/reasoning/execution/presentation controller.
The controller compiles surface modifiers into a compact contract injected near the
current turn, preserving the reusable conversation prefix instead of growing a large
permanent system prompt.
"""
from __future__ import annotations

import re
import types
import urllib.request

_IMPL_URL = "https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/dev/runtime_hot/r39_engine_impl.py"
_req = urllib.request.Request(_IMPL_URL, headers={"User-Agent": "swrlz-hot-r39-v13"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _source = _response.read(4_000_001)
if len(_source) > 4_000_000:
    raise RuntimeError("R39_IMPL_TOO_LARGE")
_source.decode("utf-8")

_impl = types.ModuleType("swrlz_hot_r39_engine_impl_v11")
_impl.__file__ = _IMPL_URL
exec(compile(_source, _IMPL_URL, "exec"), _impl.__dict__)

_impl.HOT_SERVER_VERSION = "2.1.22"
_impl.HOT_REVISION = "2.1.22-hot-boundary-v13-reasoning-control-v1.2"
_impl._REFERENCE_RERANK_CANDIDATES = 6

_original_format_stats = _impl._format_stats

def _format_stats(stats):
    if not stats:
        return "skipped"
    return _original_format_stats(stats)

_impl._format_stats = _format_stats

# Compact machine curriculum distilled from the supplied LALM Reasoning Architecture
# v1.2. Independent axes deliberately do not collapse into a single verbosity score.
_RULES = (
    (r"\b(minimal|only what(?:'s| is) required)\b", "C3"),
    (r"\b(brief|short)\b", "C2"),
    (r"\b(concise|compact)\b", "C1"),
    (r"\b(exhaustive|every supported|every possible)\b", "B3"),
    (r"\b(comprehensive|all major)\b", "B2"),
    (r"\b(overview|high[- ]level)\b", "B1"),
    (r"\b(deep dive|deep|mechanistic|root cause)\b", "D3"),
    (r"\b(in[- ]depth|detailed)\b", "D2"),
    (r"\b(explain|explanation)\b", "D1"),
    (r"\b(expert[- ]level|implementation[- ]ready)\b", "T3"),
    (r"\b(technical|technically)\b", "T2"),
    (r"\b(beginner[- ]friendly|new to|eli5)\b", "T0"),
    (r"\b(progressive|progressively|staged)\b", "S3"),
    (r"\b(step[- ]by[- ]step|walk me through)\b", "S2"),
    (r"\b(actionable|concrete fixes|next actions?)\b", "A2"),
    (r"\b(implementation[- ]ready)\b", "A3"),
    (r"\b(fact[- ]check|verify|verified|validate)\b", "E2"),
    (r"\b(reproduce|cross[- ]check|proof)\b", "E3"),
    (r"\b(confidence|uncertain|unknown)\b", "U2"),
    (r"\b(safest|conservative)\b", "R2"),
    (r"\b(fail[- ]safe|zero[- ]data[- ]loss)\b", "R3"),
    (r"\b(think carefully|reason deeply|deep reasoning)\b", "RB2"),
    (r"\b(maximum effort|max effort)\b", "RB3"),
    (r"\b(just the result|result only|no explanation)\b", "PV0"),
)

_MODE_RULES = (
    (r"\b(diagnose|diagnostic|failure|root cause|why .* failed)\b", "DIAGNOSTIC", "FIND_ROOT_CAUSE"),
    (r"\b(compare|comparative|versus|\bvs\b)\b", "COMPARATIVE", "SELECT_BEST_OPTION"),
    (r"\b(fact[- ]check|verify|validate|audit)\b", "VERIFICATION", "VERIFY"),
    (r"\b(design|architecture|redesign)\b", "ARCHITECTURE", "DESIGN"),
    (r"\b(explore|possibilities|options)\b", "EXPLORATORY", "EXPLORE_OPTIONS"),
    (r"\b(critical|critically|challenge assumptions)\b", "CRITICAL", "TEST_ASSUMPTIONS"),
)


def _reasoning_contract(prompt: str) -> dict:
    text = " ".join(str(prompt or "").lower().split())
    axes = []
    for pattern, code in _RULES:
        if re.search(pattern, text):
            axes.append(code)
    # Preserve independent dimensions while the most specific/latest match wins
    # only inside the same dimension family.
    by_family = {}
    for code in axes:
        family = re.match(r"[A-Z]+", code).group(0)
        by_family[family] = code

    modes, objectives = [], []
    for pattern, mode, objective in _MODE_RULES:
        if re.search(pattern, text):
            modes.append(mode)
            objectives.append(objective)

    mutation = "M0"
    if re.search(r"\b(deploy|release|publish|migrate all)\b", text):
        mutation = "M3"
    elif re.search(r"\b(fix|patch|update|modify|change|implement|build)\b", text):
        mutation = "M2"
    elif re.search(r"\b(suggest|propose|draft (?:a )?patch|show (?:me )?(?:the )?changes)\b", text):
        mutation = "M1"
    if re.search(r"\b(do not|don't|dont|no) (?:change|modify|patch|deploy|execute|run)\b|\bread[- ]only\b", text):
        mutation = "M0"

    verification = "V0"
    if re.search(r"\b(audit|audit-grade)\b", text): verification = "V4"
    elif re.search(r"\b(reproduce|cross[- ]check)\b", text): verification = "V3"
    elif re.search(r"\b(verify|validate|test|regression)\b", text): verification = "V2"
    elif re.search(r"\b(sanity[- ]check|check)\b", text): verification = "V1"

    return {
        "axes": list(by_family.values()),
        "modes": modes,
        "objectives": objectives,
        "mutation": mutation,
        "verification": verification,
    }


def _contract_directive(contract: dict) -> str:
    axes = ",".join(contract["axes"]) or "defaults"
    modes = "+".join(contract["modes"]) or "GENERAL"
    objectives = "+".join(contract["objectives"]) or "SATISFY_INTENT"
    return (
        "LALM reasoning contract v1.2: "
        f"axes={axes}; modes={modes}; objective={objectives}; "
        f"mutation={contract['mutation']}; verify={contract['verification']}. "
        "Intent first; reasoning depth is independent of response length. "
        "Do not infer stronger mutation/deployment authority. Preserve compatible modifiers."
    )


def _controlled_payload(payload):
    clone = dict(payload)
    contract = _reasoning_contract(str(clone.get("prompt") or ""))
    history = list(clone.get("history") or [])
    history.append({"role": "SYSTEM", "text": _contract_directive(contract)})
    clone["history"] = history
    return clone, contract


ENGINE_ID = _impl.ENGINE_ID
MODEL_SHA256 = _impl.MODEL_SHA256
HOT_SERVER_VERSION = _impl.HOT_SERVER_VERSION
HOT_REVISION = _impl.HOT_REVISION


def generate_events(payload, is_cancelled=None):
    controlled, contract = _controlled_payload(payload)
    yield {
        "type": "STATUS",
        "phase": "REASONING_CONTRACT",
        "reason": _contract_directive(contract),
    }
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
    return result
