"""R39 v86: bounded prompt-composition attribution at the exact rendered-prefill boundary.

Extends the existing v42/v69 render camera. It never logs prompt text, token text,
hidden reasoning, or secrets. It attributes the exact rendered prompt token total by
semantic owner using cumulative tokenization of the same tokenizer/render framing used
by generation. Marginal segment counts sum to the exact rendered prompt token count.
"""
from __future__ import annotations
import hashlib,time

_V85_INSPECT_V86=inspect_engine
_V85_RENDER_CAMERA_V86=_render_camera
_V86_CONTRACT="r39-v86-prompt-composition-camera-v1"

_POLICY_OWNERS={
    "_EVIDENCE_POLICY":"online-evidence-policy",
    "_RESEARCH_POLICY":"online-research-policy",
    "_PLANNER_POLICY":"research-planner-policy",
    "_CONVERSATION_INTELLIGENCE_POLICY":"conversation-intelligence-policy",
    "_MAP_TO_POINT_POLICY":"map-to-point-policy",
    "_UNICODE_AWARENESS_POLICY":"unicode-awareness-policy",
    "_REASONING_RECOVERY_POLICY":"reasoning-recovery-policy",
    "_TRAJECTORY_POLICY":"trajectory-policy",
    "_REPAIR_POLICY":"repair-policy",
    "_ACCEPT_POLICY":"acceptance-policy",
}

def _v86_owner(role,text):
    role=str(role or "").strip().lower();value=str(text or "")
    if role!="system":return "conversation-assistant" if role in {"assistant","ai","swrlz","self"} else "conversation-user"
    if value.startswith("ONLINE_EVIDENCE_BUNDLE_JSON"):return "online-evidence-data"
    prefixes=(
        ("[SWRLZ_CONVERSATION_STATE ","conversation-state"),
        ("[SWRLZ_CONTEXT_FOCUS ","context-focus"),
        ("[SWRLZ_PROGRAMMING_MODE ","programming-mode"),
        ("[SWRLZ_LIGHTWEIGHT_PROGRAMMING ","lightweight-programming"),
    )
    for prefix,owner in prefixes:
        if value.startswith(prefix):return owner
    for name,owner in _POLICY_OWNERS.items():
        policy=globals().get(name)
        if isinstance(policy,str) and value==policy:return owner
    return "system-other"

def _v86_hash(value):
    return hashlib.sha256(str(value).encode("utf-8","replace")).hexdigest()[:16]

def _v86_segments(payload):
    prepared=_clean_noncoding_history(payload)
    if callable(globals().get("_compact_lightweight_payload")):
        prepared,_=_compact_lightweight_payload(prepared)
    directive=str(prepared.get("responseDirective") or "You are §wyrlz. Answer directly and truthfully.").strip()
    segments=[("render-framing","startoftext","<|startoftext|>")]
    segments.append(("response-directive","system",f"<|im_start|>system\n{directive}<|im_end|>\n"))
    for index,turn in enumerate(prepared.get("history",[]) or []):
        if not isinstance(turn,dict):continue
        role=str(turn.get("role","USER")).upper()
        mapped="assistant" if role in {"ASSISTANT","AI","SWRLZ","SELF"} else "system" if role=="SYSTEM" else "user"
        text=str(turn.get("text","")).strip()
        if not text:continue
        segments.append((_v86_owner(mapped,text),f"history-{index}-{mapped}",f"<|im_start|>{mapped}\n{text}<|im_end|>\n"))
    user=str(prepared.get("prompt","")).strip()
    segments.append(("current-user-request","user",f"<|im_start|>user\n{user}<|im_end|>\n"))
    segments.append(("render-framing","assistant-open","<|im_start|>assistant\n"))
    return prepared,segments

def _v86_composition_camera(payload,request_id):
    started=time.monotonic()
    try:
        prepared,segments=_v86_segments(payload)
        model=_get_model();tokenizer=model.tokenizer
        cumulative="";prior_tokens=0;owner_tokens={};owner_chars={};hash_counts={}
        for index,(owner,label,rendered) in enumerate(segments):
            cumulative+=rendered
            count=len(tokenizer.encode(cumulative))
            marginal=count-prior_tokens
            prior_tokens=count
            owner_tokens[owner]=owner_tokens.get(owner,0)+marginal
            owner_chars[owner]=owner_chars.get(owner,0)+len(rendered)
            fingerprint=_v86_hash(rendered)
            hash_counts[fingerprint]=hash_counts.get(fingerprint,0)+1
            _camera(request_id,"prompt-composition-segment",contract=_V86_CONTRACT,segmentIndex=index,owner=owner,label=label,renderedChars=len(rendered),marginalTokens=marginal,cumulativeTokens=count,fingerprint=fingerprint)
        exact_prompt=base.render_chat_prompt(prepared)
        exact_tokens=len(tokenizer.encode(exact_prompt))
        attributed=sum(owner_tokens.values())
        duplicate_segments=sum(v-1 for v in hash_counts.values() if v>1)
        _camera(request_id,"prompt-composition-summary",contract=_V86_CONTRACT,totalRenderedChars=len(exact_prompt),totalRenderedTokens=exact_tokens,attributedTokens=attributed,segmentCount=len(segments),ownerCount=len(owner_tokens),duplicateSegments=duplicate_segments,exactTotalMatched=bool(exact_tokens==attributed),elapsedMs=int((time.monotonic()-started)*1000))
        for owner in sorted(owner_tokens):
            _camera(request_id,"prompt-composition-owner",contract=_V86_CONTRACT,owner=owner,renderedChars=owner_chars.get(owner,0),tokens=owner_tokens.get(owner,0))
    except Exception as exc:
        _camera(request_id,"prompt-composition-error",contract=_V86_CONTRACT,errorType=type(exc).__name__,elapsedMs=int((time.monotonic()-started)*1000))

def _v86_render_camera(payload,request_id):
    _V85_RENDER_CAMERA_V86(payload,request_id)
    # Prompt-composition attribution is a diagnostic, not part of inference.
    # On the Python/Numpy fallback it re-tokenizes every cumulative segment and
    # then renders/tokenizes the full prompt again before real prefill. That can
    # multiply cold-path work enough to consume the serverless request budget.
    # Keep the camera available for explicit diagnostic runs only.
    if isinstance(payload,dict) and payload.get("_swrlz_prompt_composition_diagnostic") is True:
        _v86_composition_camera(payload,request_id)

_render_camera=_v86_render_camera

def inspect_engine():
    result=_V85_INSPECT_V86()
    if isinstance(result,dict):result.update({
        "hotServerVersion":"2.1.98",
        "hotRevision":"2.1.98-hot-prompt-composition-camera-v86",
        "promptCompositionCamera":True,
        "promptCompositionCameraContract":_V86_CONTRACT,
        "promptCompositionLogsPromptText":False,
        "promptCompositionLogsTokenText":False,
        "promptCompositionExactRenderedTotal":True,
        "promptCompositionMarginalAttribution":True,
    })
    return result

HOT_SERVER_VERSION="2.1.98"
HOT_REVISION="2.1.98-hot-prompt-composition-camera-v86"
_impl.HOT_SERVER_VERSION=HOT_SERVER_VERSION
_impl.HOT_REVISION=HOT_REVISION
