"""R39 hot-engine v18b single-file compatibility wrapper.

The stable hot loader currently hydrates only r39_engine.py. This wrapper preserves
the proven v17 engine by loading the archived v17 source from the local hot folder
when available, or from this repository's runtime branch once and caching it locally.
It then installs the v18 social/identity conversation contract at the engine boundary.
"""
from __future__ import annotations

import importlib.util
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
        request = urllib.request.Request(_ARCHIVE_URL, headers={"User-Agent": "swrlz-r39-hot-loader/2.1.28"})
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

HOT_SERVER_VERSION = "2.1.28"
HOT_REVISION = "2.1.28-hot-social-participation-v18b-single-file-loader"
ENGINE_ID = _impl.ENGINE_ID
MODEL_SHA256 = _impl.MODEL_SHA256

_ENGINE_POLICY = (
    "LALM conversation contract: participate in the user's conversational act instead of describing it. "
    "For a simple greeting or casual social opening, greet back naturally and briefly, match the user's energy and emoji when reasonable, and never explain that the input is a greeting. "
    "Do not default to generic service language such as 'This is a friendly greeting' or 'How can I assist you today?' when the user is simply socializing. "
    "Assistant identity: your name is §wyrlz. The user's name or preferred form of address is never your name. If explicitly asked your name or identity, answer naturally in first person, for example 'I'm §wyrlz.' "
    "If the user says 'You can call me Kami 😜', acknowledge the user's preferred name rather than treating Kami as your own identity. "
    "Examples: User: 'Hey 👋' -> Assistant: 'Hey 👋'; User: 'Hey there' -> Assistant: 'Hey there 😄'; User: 'What's your name?' -> Assistant: 'I'm §wyrlz.' "
    "Answer substantive questions directly and completely. For programming requests, provide correct runnable code when appropriate and keep code, explanation, formulas, and input/output behavior mutually consistent."
)

_impl.HOT_SERVER_VERSION = HOT_SERVER_VERSION
_impl.HOT_REVISION = HOT_REVISION


def _engine_render_chat_prompt(payload):
    clone = dict(payload)
    client_policy = str(clone.get("responseDirective") or "").strip()
    clone["responseDirective"] = _ENGINE_POLICY + ((" Client cognitive policy: " + client_policy) if client_policy else "")
    return _impl._ORIGINAL_RENDER_CHAT_PROMPT(clone)


_impl.base.render_chat_prompt = _engine_render_chat_prompt


def inspect_engine():
    data = _impl.inspect_engine()
    if isinstance(data, dict):
        data["hotServerVersion"] = HOT_SERVER_VERSION
        data["hotRevision"] = HOT_REVISION
        data["engineConversationContract"] = True
        data["socialParticipationContract"] = True
        data["identityDisambiguationContract"] = True
        data["clientDirectivePreservedAsSecondaryPolicy"] = True
        data["v17ArchiveSource"] = _ARCHIVE_SOURCE
    return data


def generate_events(payload, is_cancelled=None):
    yield from _impl.generate_events(payload, is_cancelled)
