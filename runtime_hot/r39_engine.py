"""R39 hot-engine v20 compact social/temporal conversation wrapper.

The stable hot loader currently hydrates only r39_engine.py. This wrapper preserves
the proven v17 engine, keeps social/identity behavior at the model boundary, and
consumes browser-supplied user-local time as structured metadata without rewriting
the user's prompt.
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


def _load_v17():
    global _ARCHIVE_SOURCE
    if not _ARCHIVE_PATH.is_file():
        _ARCHIVE_SOURCE = "github-runtime-cache"
        request = urllib.request.Request(_ARCHIVE_URL, headers={"User-Agent": "swrlz-r39-hot-loader/2.1.30"})
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


_impl = _load_v17()

HOT_SERVER_VERSION = "2.1.30"
HOT_REVISION = "2.1.30-hot-compact-social-temporal-v20"
ENGINE_ID = _impl.ENGINE_ID
MODEL_SHA256 = _impl.MODEL_SHA256

_ENGINE_POLICY = (
    "Conversation contract: participate instead of describing the user's act. "
    "Simple greetings: greet back naturally and briefly; one ordinary follow-up is fine; do not use service-desk closings or ask whether they need anything else. "
    "Your name is §wyrlz; never confuse the user's preferred name with yours. "
    "Use supplied user-local time naturally when relevant and never contradict it. "
    "Answer substantive requests directly; for code, keep code and explanation consistent."
)
_GREETING_RE = re.compile(r"^(?:hey|hi|hello|yo|sup|👋)(?:\s|[!,.?👋🙂😊😂😆❤️🫂])*$", re.I)

_impl.HOT_SERVER_VERSION = HOT_SERVER_VERSION
_impl.HOT_REVISION = HOT_REVISION


def _time_note(payload):
    ctx = payload.get("swrlzUserTimeContext") if isinstance(payload, dict) else None
    if not isinstance(ctx, dict):
        return ""
    date = str(ctx.get("localDate") or "").strip()
    time = str(ctx.get("localTime") or "").strip()
    daypart = str(ctx.get("daypart") or "").strip()
    zone = str(ctx.get("timeZone") or "").strip()
    offset = str(ctx.get("utcOffset") or "").strip()
    bits = " ".join(x for x in [date, time, daypart, zone, ("UTC" + offset) if offset else ""] if x)
    return (" User local time: " + bits + ".") if bits else ""


def _engine_render_chat_prompt(payload):
    clone = dict(payload)
    prompt = str(clone.get("prompt") or "").strip()
    client_policy = str(clone.get("responseDirective") or "").strip()
    compact_social = bool(_GREETING_RE.fullmatch(prompt))
    policy = _ENGINE_POLICY + _time_note(clone)
    if client_policy and not compact_social:
        policy += " Client cognitive policy: " + client_policy
    clone["responseDirective"] = policy
    return _impl._ORIGINAL_RENDER_CHAT_PROMPT(clone)


_impl.base.render_chat_prompt = _engine_render_chat_prompt


def inspect_engine():
    data = _impl.inspect_engine()
    if isinstance(data, dict):
        data["hotServerVersion"] = HOT_SERVER_VERSION
        data["hotRevision"] = HOT_REVISION
        data["engineConversationContract"] = True
        data["socialParticipationContract"] = True
        data["openingTurnNoPrematureClosure"] = True
        data["identityDisambiguationContract"] = True
        data["userLocalTemporalContextContract"] = True
        data["structuredUserTimeMetadata"] = True
        data["compactGreetingDirective"] = True
        data["clientDirectivePreservedAsSecondaryPolicy"] = True
        data["v17ArchiveSource"] = _ARCHIVE_SOURCE
    return data


def generate_events(payload, is_cancelled=None):
    yield from _impl.generate_events(payload, is_cancelled)
