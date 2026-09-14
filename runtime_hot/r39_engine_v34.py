"""R39 hot v34: Phase 2 mask/human/brain semantic ownership over v33.

Chat is presentation + factual relay + continuity. It no longer classifies turn intent,
derives daypart, canonicalizes identity aliases, reconstructs RMCCA carriers, parses user
requirements, validates code semantics, rewrites model claims, or changes a successful
LALM terminal result into failure. Interpretation and semantic acceptance remain inside
R39; the server remains the execution/authority boundary.

v34 also prevents the inherited implementation acceptance layer from contaminating
non-coding turns. Coding/artifact validation remains available only when the LALM's own
requirement parser finds an actual runnable-code obligation.
"""
from __future__ import annotations
import urllib.request

_V33_COMMIT = "97962919586e3b96a33099b745df225282984f60"
_V33_URL = f"https://raw.githubusercontent.com/kaministrator999-ui/Swrlzkamico/{_V33_COMMIT}/runtime_hot/r39_engine_v33.py"
_req = urllib.request.Request(_V33_URL, headers={"User-Agent": "swrlz-hot-r39-v34"})
with urllib.request.urlopen(_req, timeout=20) as _response:
    _source = _response.read(4_000_001)
if len(_source) > 4_000_000:
    raise RuntimeError("R39_V33_SOURCE_TOO_LARGE")
exec(compile(_source.decode("utf-8"), _V33_URL + "#v34", "exec"), globals(), globals())

_V33_INSPECT = globals().get("inspect_engine")
_V33_GENERATE = globals().get("generate_events")
if not callable(_V33_INSPECT) or not callable(_V33_GENERATE):
    raise RuntimeError("R39_V34_BASE_CONTRACT_MISSING")

HOT_SERVER_VERSION = "2.1.45"
HOT_REVISION = "2.1.45-hot-mask-phase2-contract-scope-v34"
_impl.HOT_SERVER_VERSION = HOT_SERVER_VERSION
_impl.HOT_REVISION = HOT_REVISION

# Identity aliases are interpretation, so they live in the brain rather than a browser
# fetch wrapper that rewrites the user's original text before inference.
if isinstance(globals().get("_BASE_POLICY"), str):
    _BASE_POLICY += (
        " Identity interpretation: common spellings such as swurlz, swrlz, and swyrlz may refer to §wyrlz when conversational context supports that reading. Preserve the user's original wording; infer the referent rather than rewriting input text."
    )

# v27 appended its implementation acceptance contract unconditionally. That leaked
# code-evaluation scaffolding into ordinary social turns. Keep that semantic gate inside
# the brain, but arm it only when the brain's requirement ledger actually requires code.
if callable(globals().get("_implementation_contract")):
    _V33_IMPLEMENTATION_CONTRACT = _implementation_contract

    def _implementation_contract(req, original_prompt):
        requirements = req if isinstance(req, dict) else {}
        if not requirements.get("requireRunnableCode"):
            return ""
        return _V33_IMPLEMENTATION_CONTRACT(requirements, original_prompt)


def inspect_engine():
    result = _V33_INSPECT()
    if isinstance(result, dict):
        result.update({
            "hotServerVersion": HOT_SERVER_VERSION,
            "hotRevision": HOT_REVISION,
            "maskBrainBoundary": "client-relays-server-governs-lalm-interprets-v2",
            "clientTurnIntentClassifierRequired": False,
            "clientDaypartDerivationRequired": False,
            "clientIdentityRewriteRequired": False,
            "clientRmccaCarrierRequired": False,
            "clientSemanticRequirementValidationRequired": False,
            "clientTerminalSemanticOverrideRequired": False,
            "semanticAcceptanceOwner": "lalm",
            "identityAliasInterpretationOwner": "lalm",
            "implementationContractScope": "runnable-code-turns-only",
            "nonCodingImplementationScaffoldingSuppressed": True,
            "rawUserWordingPreservedByClient": True,
            "serverAuthorityBoundaryPreserved": True,
            "v33SourceCommit": _V33_COMMIT,
        })
    return result


def generate_events(payload, is_cancelled=None):
    for event in _V33_GENERATE(payload, is_cancelled):
        yield event
