"""R39 hot-engine v22 batched-prefill + task-aware RMCCA wrapper.

This runtime-only wrapper preserves the proven v17 generation/exact-context core,
v21 task-aware cognition, and single-token decode behavior while adding a safe
vectorized prompt-prefill path plus first-class latency/throughput telemetry.
"""
from __future__ import annotations

import importlib.util
import re
import sys
import urllib.request
from pathlib import Path

_ARCHIVE_NAME = "r39_engine_v17_base.py"
_ARCHIVE_PATH = Path(__file__).with_name(_ARCHIVE_NAME)
_ARCHIVE_URL = "https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/runtime/runtime_hot/r39_engine_v17_base.py"
_ARCHIVE_SOURCE = "local"

_BATCH_LOCAL_NAME = "r39_batch_prefill_v22.py"
_BATCH_PATH = Path(__file__).with_name(_BATCH_LOCAL_NAME)
_BATCH_SOURCE_COMMIT = "569332d9573ffb1c05cce229a56d3adee6c0c704"
_BATCH_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_BATCH_SOURCE_COMMIT}/runtime_hot/r39_batch_prefill.py"
_BATCH_SOURCE = "local"


def _load_v17():
    global _ARCHIVE_SOURCE
    if not _ARCHIVE_PATH.is_file():
        _ARCHIVE_SOURCE = "github-runtime-cache"
        request = urllib.request.Request(
            _ARCHIVE_URL,
            headers={"User-Agent": "swrlz-r39-hot-loader/2.1.32"},
        )
        with urllib.request.urlopen(request, timeout=8) as response:
            source = response.read()
        if not source or b"def generate_events" not in source or b"def inspect_engine" not in source:
            raise RuntimeError("R39_V17_ARCHIVE_INVALID")
        _ARCHIVE_PATH.write_bytes(source)
    spec = importlib.util.spec_from_file_location("swrlz_hot_r39_v17_base", _ARCHIVE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("R39_V17_ARCHIVE_IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_batch_adapter():
    global _BATCH_SOURCE
    if not _BATCH_PATH.is_file():
        _BATCH_SOURCE = "github-pinned-runtime-cache"
        request = urllib.request.Request(
            _BATCH_URL,
            headers={"User-Agent": "swrlz-r39-batch-prefill/2.1.32"},
        )
        with urllib.request.urlopen(request, timeout=8) as response:
            source = response.read(1_000_001)
        if len(source) > 1_000_000 or b"def forward_token_block" not in source or b"def install" not in source:
            raise RuntimeError("R39_BATCH_PREFILL_ADAPTER_INVALID")
        _BATCH_PATH.write_bytes(source)
    spec = importlib.util.spec_from_file_location("swrlz_hot_r39_batch_prefill_v22", _BATCH_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("R39_BATCH_PREFILL_IMPORT_SPEC_FAILED")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_impl = _load_v17()

HOT_SERVER_VERSION = "2.1.32"
HOT_REVISION = "2.1.32-hot-batched-prefill-rmcca-v22"
ENGINE_ID = _impl.ENGINE_ID
MODEL_SHA256 = _impl.MODEL_SHA256

# Exact checkpoints remain aligned with the batch size so a checkpoint is never
# published from a state that is still carrying unflushed prompt tokens.
_impl._PREFILL_CHECKPOINT_EVERY = 96
_impl._LIVE_CHECKPOINT_EVERY = 32
_impl._CONTEXT_MAX_CHECKPOINTS = 6

_BASE_POLICY = (
    "Conversation contract: answer the user's actual request directly, truthfully, and naturally. "
    "Participate in conversation instead of narrating the user's act. "
    "Your name is §wyrlz; never confuse a user-supplied name with your identity. "
    "Use supplied user-local time only when relevant and never contradict it. "
    "Do not invent facts, files, results, tests, or actions. "
    "Prefer the smallest correct answer that fully satisfies the request, then add depth when useful."
)

_TASK_POLICIES = {
    "social": (
        "Social mode: respond naturally and briefly. Mirror obvious humor or warmth without turning the reply "
        "into a service-desk interaction. Do not ask whether the user needs anything else."
    ),
    "coding": (
        "Coding mode: preserve stated architecture and constraints; reason from the actual code/request rather "
        "than generic patterns. Produce complete runnable or directly applicable code when code is requested. "
        "Check syntax, names, control flow, edge cases, interfaces, I/O, and code/explanation consistency before ending. "
        "For debugging, identify the causal fault and make the smallest correct repair instead of masking symptoms."
    ),
    "math": (
        "Math/logic mode: compute before concluding; track units, signs, assumptions, and boundary cases. "
        "Give the result clearly and include only the derivation needed to make it checkable."
    ),
    "research": (
        "Research/factual mode: separate supported facts from inference and uncertainty. "
        "Do not fabricate sources, recency, measurements, or external observations. Compare evidence before concluding."
    ),
    "analysis": (
        "Analysis mode: identify the relevant criteria, causal relationships, constraints, and tradeoffs; "
        "compare alternatives on the same dimensions and finish with a concrete conclusion."
    ),
    "planning": (
        "Planning mode: respect constraints, dependencies, order of operations, and rollback points. "
        "Prefer an actionable sequence over vague advice and do not assume unavailable resources."
    ),
    "creative": (
        "Creative mode: honor the requested form, voice, characters, continuity, and constraints. "
        "Create the artifact directly rather than explaining how one could be created."
    ),
    "general": (
        "General mode: resolve the user's immediate intent first, preserve relevant thread continuity, "
        "and avoid unnecessary framing or repetition."
    ),
}

_GREETING_RE = re.compile(r"^(?:hey|hi|hello|yo|sup|👋)(?:\s|[!,.?👋🙂😊😂😆❤️🫂])*$", re.I)
_CODE_RE = re.compile(
    r"\b(?:code|coding|program|programming|function|class|method|script|debug|bug|fix|refactor|compile|"
    r"html|css|javascript|typescript|python|c\+\+|cpp|java|kotlin|rust|sql|api|json|yaml|regex|git|github|"
    r"server|client|frontend|backend|repository|repo|commit|build|exception|stack trace)\b",
    re.I,
)
_MATH_RE = re.compile(
    r"(?:\b(?:calculate|equation|algebra|geometry|probability|percent|percentage|ratio|average|integral|"
    r"derivative|matrix|formula|logic puzzle|proof)\b|[0-9]\s*[\+\-\*/=^]\s*[0-9])",
    re.I,
)
_RESEARCH_RE = re.compile(
    r"\b(?:research|source|evidence|latest|current|today|online|internet|look up|verify|fact check|study|paper|"
    r"benchmark|documentation|docs)\b",
    re.I,
)
_ANALYSIS_RE = re.compile(
    r"\b(?:analy[sz]e|analysis|compare|comparison|tradeoff|trade-off|pros and cons|why does|why is|evaluate|"
    r"diagnose|architecture|design|optimi[sz]e|improve)\b",
    re.I,
)
_PLANNING_RE = re.compile(
    r"\b(?:plan|roadmap|steps|strategy|schedule|workflow|migration|rollout|deploy|implementation plan|prioriti[sz]e)\b",
    re.I,
)
_CREATIVE_RE = re.compile(
    r"\b(?:write|story|poem|lyrics|rap|song|character|lore|worldbuild|creative|scene|dialogue|caption|"
    r"screenplay|fiction|parody)\b",
    re.I,
)


def _time_note(payload):
    ctx = payload.get("swrlzUserTimeContext") if isinstance(payload, dict) else None
    if not isinstance(ctx, dict):
        return ""
    date = str(ctx.get("localDate") or "").strip()
    time_value = str(ctx.get("localTime") or "").strip()
    daypart = str(ctx.get("daypart") or "").strip()
    zone = str(ctx.get("timeZone") or "").strip()
    offset = str(ctx.get("utcOffset") or "").strip()
    bits = " ".join(x for x in [date, time_value, daypart, zone, ("UTC" + offset) if offset else ""] if x)
    return (" User local time: " + bits + ".") if bits else ""


def _rmcca_clock(payload):
    ctx = payload.get("swrlzCognitiveContext") if isinstance(payload, dict) else None
    clock = ctx.get("cognitiveClock") if isinstance(ctx, dict) else None
    return clock if isinstance(clock, dict) else {}


def _classify_task(payload):
    prompt = str(payload.get("prompt") or "").strip()
    clock = _rmcca_clock(payload)
    domains = [
        str(item.get("domain") or "").lower()
        for item in (clock.get("domains") or [])
        if isinstance(item, dict)
    ]
    roles = {str(x).lower() for x in (clock.get("structuralRoles") or [])}
    topology = str(clock.get("responseTopology") or "").lower()
    if topology == "social-participation" or "social" in domains:
        return "social"
    if "programming" in domains:
        return "coding"
    if any(d in domains for d in ("science", "language")) and "question" in roles:
        return "research"
    if "comparison" in roles or topology in {"comparison", "layered-synthesis", "revision-continuation"}:
        return "analysis"
    if "creative" in domains:
        return "creative"
    if _GREETING_RE.fullmatch(prompt):
        return "social"
    if _CODE_RE.search(prompt):
        return "coding"
    if _MATH_RE.search(prompt):
        return "math"
    if _RESEARCH_RE.search(prompt):
        return "research"
    if _ANALYSIS_RE.search(prompt):
        return "analysis"
    if _PLANNING_RE.search(prompt):
        return "planning"
    if _CREATIVE_RE.search(prompt):
        return "creative"
    return "general"


def _explicit_generation(generation):
    if not isinstance(generation, dict):
        return False
    if str(generation.get("budgetMode") or "").lower() == "manual":
        return True
    return any(key in generation for key in ("temperature", "topP", "top_p"))


def _prepare_payload(payload):
    clone = dict(payload)
    task = _classify_task(clone)
    clone["_swrlzTaskProfile"] = task
    generation = dict(clone.get("generation") or {}) if isinstance(clone.get("generation"), dict) else {}
    if not _explicit_generation(generation):
        default_temp = {
            "coding": 0.12,
            "math": 0.08,
            "research": 0.18,
            "analysis": 0.20,
            "planning": 0.20,
            "social": 0.42,
            "creative": 0.55,
            "general": 0.28,
        }[task]
        generation["temperature"] = default_temp
        generation.setdefault("topP", 0.9)
        clone["generation"] = generation
        clone["_swrlzAdaptiveSampling"] = True
    else:
        clone["_swrlzAdaptiveSampling"] = False
    return clone


def _engine_render_chat_prompt(payload):
    clone = dict(payload)
    prompt = str(clone.get("prompt") or "").strip()
    client_policy = str(clone.get("responseDirective") or "").strip()
    task = str(clone.get("_swrlzTaskProfile") or _classify_task(clone))
    clock = _rmcca_clock(clone)
    compact_social = bool(_GREETING_RE.fullmatch(prompt))
    policy = _BASE_POLICY + " " + _TASK_POLICIES.get(task, _TASK_POLICIES["general"])
    if str(clock.get("resolutionDepth") or "").lower() == "deep":
        policy += " Deep-resolution mode: integrate the relevant domains and explain causal structure without padding."
    if "correction-refinement" in {str(x).lower() for x in (clock.get("structuralRoles") or [])}:
        policy += " Correction mode: revise only the affected interpretation; preserve still-valid prior context."
    policy += _time_note(clone)
    if client_policy and not compact_social:
        policy += " Client/project policy: " + client_policy
    clone["responseDirective"] = policy
    return _impl._ORIGINAL_RENDER_CHAT_PROMPT(clone)


_impl.base.render_chat_prompt = _engine_render_chat_prompt
_impl.HOT_SERVER_VERSION = HOT_SERVER_VERSION
_impl.HOT_REVISION = HOT_REVISION

# The stable hot loader hydrates only r39_engine.py. Fetch the pinned runtime helper
# from its exact commit so v22's vectorized implementation cannot drift underneath it.
_batch = _load_batch_adapter()
_BATCH_INSTALL = _batch.install(_impl, block_tokens=_impl._PREFILL_CHECKPOINT_EVERY)


def inspect_engine():
    data = _impl.inspect_engine()
    if isinstance(data, dict):
        data["hotServerVersion"] = HOT_SERVER_VERSION
        data["hotRevision"] = HOT_REVISION
        data["engineConversationContract"] = True
        data["taskAwareCognitivePolicy"] = True
        data["rmccaCognitiveEnvelopePreferred"] = True
        data["serverIntentClassifierFallback"] = True
        data["taskProfiles"] = sorted(_TASK_POLICIES)
        data["adaptiveTaskSampling"] = True
        data["modelFamilySamplingBaseline"] = "temperature~0.3; repetition_penalty=1.05"
        data["explicitGenerationOverridesPreserved"] = True
        data["prefillCheckpointEveryTokens"] = _impl._PREFILL_CHECKPOINT_EVERY
        data["liveCheckpointEveryGeneratedTokens"] = _impl._LIVE_CHECKPOINT_EVERY
        data["maxConversationCheckpoints"] = _impl._CONTEXT_MAX_CHECKPOINTS
        data["reducedCheckpointClonePressure"] = True
        data["batchedVectorizedPrefill"] = True
        data["batchPrefillSource"] = _BATCH_SOURCE
        data["batchPrefillSourceCommit"] = _BATCH_SOURCE_COMMIT
        data["batchPrefillInstall"] = dict(_BATCH_INSTALL)
        data["batchPrefillDiagnostics"] = _batch.diagnostics(_impl)
        data["prefillPerfTelemetry"] = True
        data["decodePerfTelemetry"] = True
        data["socialParticipationContract"] = True
        data["identityDisambiguationContract"] = True
        data["userLocalTemporalContextContract"] = True
        data["structuredUserTimeMetadata"] = True
        data["clientDirectivePreservedAsSecondaryPolicy"] = True
        data["v17ArchiveSource"] = _ARCHIVE_SOURCE
    return data


def generate_events(payload, is_cancelled=None):
    prepared = _prepare_payload(payload)
    task = prepared.get("_swrlzTaskProfile", "general")
    clock = _rmcca_clock(prepared)
    adaptive = bool(prepared.get("_swrlzAdaptiveSampling"))
    generation = prepared.get("generation") if isinstance(prepared.get("generation"), dict) else {}
    temperature = generation.get("temperature")
    yield {
        "type": "STATUS",
        "phase": "COGNITIVE_ROUTE",
        "reason": (
            f"Task profile={task}; cognitive source={'RMCCA' if clock else 'server-fallback'}; "
            + (f"adaptive temperature={temperature}; " if adaptive else "explicit sampling settings preserved; ")
            + f"prefill mode=batched-{_impl._PREFILL_CHECKPOINT_EVERY}; live checkpoints={_impl._LIVE_CHECKPOINT_EVERY}."
        ),
    }
    yield from _impl.generate_events(prepared, is_cancelled)
