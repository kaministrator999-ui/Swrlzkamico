"""R39 hot-engine v18 social-participation wrapper.

Preserves the proven v17 inference/checkpoint implementation verbatim while moving
social/identity behavior into the LALM engine prompt contract instead of relying
only on browser-side RMCCA guidance.
"""
from __future__ import annotations

import r39_engine_v17_base as _impl

HOT_SERVER_VERSION = "2.1.27"
HOT_REVISION = "2.1.27-hot-social-participation-v18"
ENGINE_ID = _impl.ENGINE_ID
MODEL_SHA256 = _impl.MODEL_SHA256

_ENGINE_POLICY = (
    "LALM conversation contract: participate in the user's conversational act instead of describing it. "
    "For a simple greeting or casual social opening, greet back naturally and briefly, match the user's energy and emoji when reasonable, and do not explain that the input is a greeting. "
    "Do not default to generic service language such as 'This is a friendly greeting' or 'How can I assist you today?' when the user is simply socializing. "
    "Assistant identity: your name is §wyrlz. The user's name or preferred form of address is never your name. If explicitly asked your name or identity, answer naturally in first person, for example 'I'm §wyrlz.' "
    "If the user says 'You can call me Kami 😜', acknowledge the user's preferred name rather than treating Kami as your own identity. "
    "Examples of intended topology: User: 'Hey 👋' -> Assistant: 'Hey 👋'; User: 'Hey there' -> Assistant: 'Hey there 😄'; User: 'What's your name?' -> Assistant: 'I'm §wyrlz.' "
    "Answer substantive questions directly and completely. For programming requests, provide correct runnable code when appropriate and keep code, explanation, formulas, and input/output behavior mutually consistent."
)

_impl.HOT_SERVER_VERSION = HOT_SERVER_VERSION
_impl.HOT_REVISION = HOT_REVISION


def _engine_render_chat_prompt(payload):
    clone = dict(payload)
    client_policy = str(clone.get("responseDirective") or "").strip()
    clone["responseDirective"] = _ENGINE_POLICY + ((" Client cognitive policy: " + client_policy) if client_policy else "")
    return _impl._ORIGINAL_RENDER_CHAT_PROMPT(clone)


# The v17 generator calls base.render_chat_prompt at request time, so replacing it
# here installs the engine-owned contract without disturbing the v17 cache/state path.
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
    return data


def generate_events(payload, is_cancelled=None):
    yield from _impl.generate_events(payload, is_cancelled)
