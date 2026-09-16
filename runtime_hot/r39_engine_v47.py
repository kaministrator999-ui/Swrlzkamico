"""R39 v47: correction-aware conversational trajectory policy.

Extends v46 without moving cognition into Chat. The Brain uses bounded canonical
history to recognize likely correction/repair state and injects a compact
interaction policy for normal model inference. Raw user surface text is preserved.
"""
from __future__ import annotations
import re
import urllib.request

_V46_COMMIT="4bc9eda49bd5953345467ab6174e54b4faed79fa"
_V46_URL=f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V46_COMMIT}/runtime_hot/r39_engine_v46.py"
_req=urllib.request.Request(_V46_URL,headers={"User-Agent":"swrlz-r39-v47"})
with urllib.request.urlopen(_req,timeout=20) as _response:_source=_response.read(4_000_001)
if len(_source)>4_000_000:raise RuntimeError("R39_V46_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"),_V46_URL+"#v47","exec"),globals(),globals())

_V46_INSPECT=inspect_engine
_V46_GENERATE=generate_events
HOT_SERVER_VERSION="2.1.58"
HOT_REVISION="2.1.58-hot-conversation-trajectory-repair-v47"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION

_CORRECTION_RE=re.compile(
    r"^(?:no+|nope|nah|wrong|not quite|not that|not what|but no|still|look|wait|hold up|"
    r"i mean|what i mean|i meant|you missed|you forgot|you['’]?re missing|do you not see|"
    r"that['’]?s not|it['’]?s not|you closed|too far|too soon|other one)\b",re.I)
_ACCEPT_RE=re.compile(
    r"^(?:exactly|yep|yup|yes|yeah exactly|there (?:it|you) (?:is|go)|that['’]?s it|"
    r"oh yeah (?:§?wyrlz|swurlz|swyrlz)|fuck yeah)\b",re.I)

_TRAJECTORY_POLICY=(
    "Conversation policy: treat the dialogue as a trajectory, not isolated prompts. "
    "Resolve pronouns, callbacks, compressed wording, deliberate Unicode, punctuation, slang, and coined forms from recent context before asking the user to repeat them. "
    "Preserve raw surface distinctions such as §; do not silently normalize meaningful user notation. "
    "Separate the active conversational thread from mere keyword/topic similarity. "
    "Use callbacks only when they help the current turn. "
    "Calibrate confidence to evidence: commit when recent context supports the inference; do not invent missing facts. "
    "Choose the smallest response shape and length that fully serves the turn; casual banter may be brief while technical work may be structured and deep. "
    "Do not mechanically mirror phrases or profanity; match the current conversational register naturally."
)
_REPAIR_POLICY=(
    "Current-turn repair policy: the latest user turn appears to correct or redirect the preceding interpretation. "
    "Re-read the immediately relevant turns. Identify the smallest invalidated assumption, referent, scope, relation, tone, or abstraction level; preserve unaffected context. "
    "Answer with the corrected substance first. Do not pretend the corrected interpretation was what you meant all along. "
    "Do not over-apologize or restart the whole task when a local repair is enough. "
    "If an earlier correction in the recent trajectory is still unsatisfied, satisfy it now rather than repeating the same conceptual error."
)
_ACCEPT_POLICY=(
    "Current-turn convergence signal: the latest user wording may indicate acceptance or recognition of the preceding response. "
    "Treat that as contextual evidence, not a permanent preference or factual truth. Continue the active thread naturally without re-explaining the accepted point unless useful."
)

def _trajectory_state(payload):
    prompt=str((payload or {}).get("prompt") or "").strip()
    if not prompt:return "neutral"
    if _CORRECTION_RE.search(prompt):return "repair"
    if _ACCEPT_RE.search(prompt):return "accept"
    return "neutral"

def _with_trajectory_context(payload):
    if not isinstance(payload,dict):return payload
    out=dict(payload);history=list(out.get("history") or [])
    state=_trajectory_state(out)
    policies=[{"role":"system","text":_TRAJECTORY_POLICY}]
    if state=="repair":policies.append({"role":"system","text":_REPAIR_POLICY})
    elif state=="accept":policies.append({"role":"system","text":_ACCEPT_POLICY})
    out["history"]=policies+history
    return out

def inspect_engine():
    result=_V46_INSPECT()
    if isinstance(result,dict):result.update({
        "hotServerVersion":HOT_SERVER_VERSION,
        "hotRevision":HOT_REVISION,
        "conversationTrajectoryPolicy":True,
        "conversationTrajectoryOwner":"lalm",
        "conversationTrajectorySource":"bounded-canonical-history-plus-current-turn",
        "correctionRepairPolicy":"minimal-invalidated-state-v1",
        "rawSurfacePreservation":True,
        "confidenceCalibrationPolicy":True,
        "responseShapeCalibration":True,
        "v46SourceCommit":_V46_COMMIT,
    })
    return result

def generate_events(payload,is_cancelled=None):
    state=_trajectory_state(payload)
    request_id=_request_id(payload)
    _camera(request_id,"trajectory-policy",trajectoryState=state,
            correctionAware=state=="repair",acceptanceAware=state=="accept",
            rawSurfacePreserved=True,policyOwner="lalm")
    for event in _V46_GENERATE(_with_trajectory_context(payload),is_cancelled):yield event
