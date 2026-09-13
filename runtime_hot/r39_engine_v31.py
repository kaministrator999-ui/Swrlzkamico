"""R39 hot v31: compact-social directive preservation over v30.

Fixes a prompt-rendering defect where exact greeting turns such as ``Hey 👋`` were
classified as compact social turns and then silently dropped Chat's responseDirective.
Client/project policy now survives for every task, including compact social turns.
Approved request-time clock/daypart are hardened as fixed factual anchors for social
greetings so a time-of-day greeting cannot contradict the supplied daypart.
"""
from __future__ import annotations
import urllib.request

_V30_COMMIT = "c2a014016ec6755b2652a081407109f0ca38d128"
_V30_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V30_COMMIT}/runtime_hot/r39_engine_v30.py"
_req = urllib.request.Request(_V30_URL, headers={"User-Agent": "swrlz-hot-r39-v31"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _source = _response.read(4_000_001)
if len(_source) > 4_000_000:
    raise RuntimeError("R39_V30_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"), _V30_URL + "#v31", "exec"), globals(), globals())

_V30_INSPECT = globals().get("inspect_engine")
_V30_GENERATE = globals().get("generate_events")
if not callable(_V30_INSPECT) or not callable(_V30_GENERATE):
    raise RuntimeError("R39_V31_BASE_CONTRACT_MISSING")

HOT_SERVER_VERSION = "2.1.41"
HOT_REVISION = "2.1.41-hot-social-directive-temporal-anchor-v31"
_impl.HOT_SERVER_VERSION = HOT_SERVER_VERSION
_impl.HOT_REVISION = HOT_REVISION


def _social_temporal_contract(payload, task):
    if str(task or "") != "social":
        return ""
    approved = _approved_temporal_context(payload)
    if not approved:
        return (
            " Social temporal contract: approved user-local time is unavailable. "
            "Do not use morning, afternoon, evening, night, or any other time-specific greeting unless the user explicitly supplied it."
        )
    clock = _display_clock(approved.get("localTime"))
    daypart = str(approved.get("daypart") or "").strip().lower()
    parts = ["Social temporal contract:"]
    if clock:
        parts.append(f"approved request-time local clock is {clock};")
    if daypart:
        parts.append(f"approved request-time daypart is {daypart};")
        parts.append(
            f"treat {daypart!r} as a fixed fact. If a time-of-day greeting is used, it MUST agree with {daypart!r}; "
            "never substitute morning, afternoon, evening, night, or another contradictory daypart."
        )
    else:
        parts.append("no approved daypart is available, so avoid a time-of-day greeting.")
    return " " + " ".join(parts)


def _engine_render_chat_prompt_v31(payload):
    clone = dict(payload)
    prompt = str(clone.get("prompt") or "").strip()
    client_policy = str(clone.get("responseDirective") or "").strip()
    task = str(clone.get("_swrlzTaskProfile") or _classify_task(clone))
    clock = _rmcca_clock(clone)
    policy = _BASE_POLICY + " " + _TASK_POLICIES.get(task, _TASK_POLICIES["general"])
    if str(clock.get("resolutionDepth") or "").lower() == "deep":
        policy += " Deep-resolution mode: integrate the relevant domains and explain causal structure without padding."
    if "correction-refinement" in {str(x).lower() for x in (clock.get("structuralRoles") or [])}:
        policy += " Correction mode: revise only the affected interpretation; preserve still-valid prior context."
    policy += _time_note(clone)
    policy += _social_temporal_contract(clone, task)
    # v22 excluded client policy for compact greetings. That exclusion was the defect:
    # greeting-specific policy must be preserved, not discarded.
    if client_policy:
        policy += " Client/project policy (mandatory): " + client_policy
    clone["responseDirective"] = policy
    return _impl._ORIGINAL_RENDER_CHAT_PROMPT(clone)


_impl.base.render_chat_prompt = _engine_render_chat_prompt_v31


def inspect_engine():
    result = _V30_INSPECT()
    if isinstance(result, dict):
        result.update({
            "hotServerVersion": HOT_SERVER_VERSION,
            "hotRevision": HOT_REVISION,
            "compactSocialClientDirectivePreserved": True,
            "socialTemporalAnchorContract": "request-time-fixed-fact-v1",
            "contradictorySocialDaypartForbidden": True,
            "clientDirectiveAppliesToAllTaskProfiles": True,
            "v30SourceCommit": _V30_COMMIT,
        })
    return result


def generate_events(payload, is_cancelled=None):
    for event in _V30_GENERATE(payload, is_cancelled):
        yield event
