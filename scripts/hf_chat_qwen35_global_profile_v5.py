#!/usr/bin/env python3
"""Source-safe §C 9B global profile-aware prompt-efficiency candidate.

The original universal §wyrlzara profile is authoritative and unchanged.
Select exact authored sections per task instead of duplicating a multi-thousand
token manual on every turn. Saved companion/user customization remains
account-scoped, never promoted to tool/admin authority. Keep all 9B weights,
native §E, research, coding contracts, auth, history, tools and hardware.
"""
from __future__ import annotations
import ast,hashlib,json,os,sys
from pathlib import Path
from tempfile import TemporaryDirectory
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
from hf_chat_qwen35_conversation_v4 import CONVERSATION_OVERLAY

SPACE="kamiloki/Swyrlz"
ENGINE="lfm2_700m_engine.py"
STATION="station.py"
RUNTIME="qwen35_single_runtime.py"
PROFILE="swrlz-qwen35-profile-v5"
PROFILE_ANCHOR="_lock=threading.RLock()"
FILES=(ENGINE,)
CORE_SECTIONS=(
    "SELF-KNOWLEDGE & IDENTITY PROVENANCE",
    "DYNAMIC MIRROR",
    "SIMPLE-FIRST",
    "OWNERSHIP BEFORE INFERENCE",
    "EVIDENCE BEFORE AGREEMENT",
    "EVIDENCE & CORRECTION",
    "ADAPTIVE EXPRESSION",
    "NEGATIVE CONSTRAINT SIGIL",
    "§WYRLZ CORE",
    "PHOENIX ARMOR",
)
FAST_SECTIONS=(
    "DYNAMIC MIRROR",
    "SIMPLE-FIRST",
    "EVIDENCE BEFORE AGREEMENT",
    "ADAPTIVE EXPRESSION",
    "§WYRLZ CORE",
)
ENGINEERING_SECTIONS=(
    "PROJECT MODE",
    "CORRECTION ECONOMY",
    "SCOPE CORRECTION PRECEDENCE",
    "COLLABORATIVE DEBUGGING",
)
CREATIVE_SECTIONS=("CREATIVE MODE","CREATIVE DELEGATION")
EXTRA_FUNCTIONS=r'''def _wyrlz_authored_section(heading):
    """Read the actual universal §wyrlz profile, not another invented persona."""
    marker="\n\n"+heading+": "
    if marker not in BUILTIN_ASSISTANT_PROFILE:
        raise RuntimeError("SWRLZ_PROFILE_SOURCE_SECTION_MISSING: "+heading)
    return heading+": "+BUILTIN_ASSISTANT_PROFILE.split(marker,1)[1].split("\n\n",1)[0]

def _wyrlz_active_profile(prompt="", programming=None, brief=False):
    """One source of identity for casual, factual, coding, repair and creative turns.

    Relevant authored sections are selected; nothing changes user-specific
    preferences, saved profile records, history, §E authority, or model weights.
    """
    programming=programming if isinstance(programming,dict) else {}
    headings=list((
        "DYNAMIC MIRROR", "SIMPLE-FIRST", "EVIDENCE BEFORE AGREEMENT",
        "ADAPTIVE EXPRESSION", "§WYRLZ CORE"
    ) if brief else (
        "SELF-KNOWLEDGE & IDENTITY PROVENANCE", "DYNAMIC MIRROR",
        "SIMPLE-FIRST", "OWNERSHIP BEFORE INFERENCE", "EVIDENCE BEFORE AGREEMENT",
        "EVIDENCE & CORRECTION", "ADAPTIVE EXPRESSION",
        "NEGATIVE CONSTRAINT SIGIL", "§WYRLZ CORE", "PHOENIX ARMOR"
    ))
    if programming.get("codingTask"):
        headings.extend((
            "PROJECT MODE","CORRECTION ECONOMY","SCOPE CORRECTION PRECEDENCE",
            "COLLABORATIVE DEBUGGING"
        ))
    elif re.search(r"\b(?:lyrics|freestyle|rap|song|poem|story|creative writing)\b",
                   str(prompt or ""),re.I):
        headings.extend(("CREATIVE MODE","CREATIVE DELEGATION"))
    lead=BUILTIN_ASSISTANT_PROFILE.split("\n\n",1)[0]
    # The identity header and named sections are exact excerpts from the
    # original universal core. No profile is rewritten per route.
    return lead+"\n\n"+"\n\n".join(_wyrlz_authored_section(h) for h in headings)

'''
FULL_PROFILE_OLD=r'''    if not programming.get("codingTask"):
        system+="\nBUILT-IN §WYRLZ PROFILE (default assistant identity/behavior):\n"+_identity_context_profile(identity_response_mode)
        if custom_assistant_profile:
            system+="\nUSER CUSTOMIZATION FOR §WYRLZ (additional preferences layered on top of the built-in profile; do not erase the built-in identity):\n"+custom_assistant_profile
        if user_profile:
            system+="\nUSER PROFILE (describes the current user, not §wyrlz; context only):\n"+user_profile'''
FULL_PROFILE_NEW=r'''    if programming.get("codingTask"):
        # One actual §wyrlz core is present during code/§E work as well.
        # Keep all existing coding and source-repair contracts untouched.
        system+="\nAUTHORED §WYRLZ PROFILE (universal identity and engineering principles):\n"+_wyrlz_active_profile(prompt,programming)
    else:
        system+="\nAUTHORED §WYRLZ PROFILE (universal identity/behavior):\n"+(
            _identity_context_profile(identity_response_mode)
            if concise_identity_turn else _wyrlz_active_profile(prompt,programming))
    if custom_assistant_profile:
        system+="\nSAVED ASSISTANT PROFILE CUSTOMIZATION (no tool authority):\n"+custom_assistant_profile
    if user_profile:
        system+="\nUSER PROFILE (describes the human, not §wyrlz):\n"+user_profile'''
REPAIR_ANCHOR=r'''        system,fitted_prompt,repair_context_telemetry=build_compact_repair_context(
            programming,
            prompt,
            _response_mode(prompt,programming,history),
        )
        system+=programming_library_context(programming)'''
REPAIR_INJECTION=r'''        system,fitted_prompt,repair_context_telemetry=build_compact_repair_context(
            programming,
            prompt,
            _response_mode(prompt,programming,history),
        )
        # Preserve grounded repair contracts; attach the authored
        # universal engineering core after compacting the repair payload.
        system+="\nAUTHORED §WYRLZ ENGINEERING PROFILE:\n"+_wyrlz_active_profile(prompt,programming,brief=True)
        if custom_assistant_profile:
            system+="\nSAVED ASSISTANT CUSTOMIZATION:\n"+custom_assistant_profile
        if user_profile:
            system+="\nUSER PROFILE (context only):\n"+user_profile
        system+=programming_library_context(programming)'''

def replace_unique(text,old,new,label):
    count=text.count(old)
    if count!=1:raise RuntimeError(f"LIVE_SOURCE_DRIFT {label}: expected 1 anchor, found {count}")
    return text.replace(old,new,1)

def patch_engine(source):
    # No change to original profile bytes; one short helper parses exact sections.
    source=replace_unique(source,PROFILE_ANCHOR,EXTRA_FUNCTIONS+PROFILE_ANCHOR,"profile-helper")
    source=replace_unique(source,FULL_PROFILE_OLD,FULL_PROFILE_NEW,"profile-default-and-coding")
    fast=CONVERSATION_OVERLAY
    assert fast.count("+_role_frame(user_profile))")==1
    fast_updated=fast.replace("+_role_frame(user_profile))",
        '+_wyrlz_active_profile(prompt,programming,brief=True)+"\\n"+_role_frame(user_profile))')
    source=replace_unique(source,fast,fast_updated,"social-profile-origin")
    source=replace_unique(source,REPAIR_ANCHOR,REPAIR_INJECTION,"repair-profile")
    ast.parse(source,filename=ENGINE)
    return source

def verify_profile_source(before,after):
    original=before.decode("utf-8")
    patched=after.decode("utf-8")
    start='BUILTIN_ASSISTANT_PROFILE="""'
    end='"""\\n_lock=threading.RLock()'
    assert start in original and start in patched
    # Check that ALL authored profile text survives without changes. The new
    # helper is inserted AFTER the closing triple quote and BEFORE _lock.
    body_original=original.split(start,1)[1].split('"""',1)[0]
    body_after=patched.split(start,1)[1].split('"""',1)[0]
    assert body_original==body_after, "Original §wyrlz profile altered!"
    assert "SWRLZ-A-∞" in body_after and "DYNAMIC MIRROR" in body_after
    assert "NO PREMISE AMPLIFICATION" in body_after
    assert "PROJECT MODE" in body_after and "PHOENIX ARMOR" in body_after
    assert '_wyrlz_active_profile(prompt,programming,brief=True)' in patched
    assert "SAVED ASSISTANT PROFILE CUSTOMIZATION" in patched
    assert "AUTHORED §WYRLZ ENGINEERING PROFILE" in patched
    assert "SAVED ASSISTANT CUSTOMIZATION" in patched
    for anchor in ("def _fit_messages(","def _fit_repair_messages(",
                   "def generate_events(payload):","source_sized_budget(",
                   "programming_library_context(programming)",
                   "creative_music_reference_projection(prompt,history)"):
        assert anchor in original and anchor in patched
    ast.parse(patched,filename=ENGINE)
    print(json.dumps({"status":"PROFILE_V5_SOURCE_PRESERVED",
         "fullUniversalProfileByteIdentical":True,
         "accountCustomizationPreserved":True,
         "codingAndSourceContractsPreserved":True,
         "model": "Qwen3.5-9B (unchanged)"}),flush=True)

def sha(data):return hashlib.sha256(data).hexdigest()

def prepare(api):
    sha_original=api.repo_info(SPACE,repo_type="space").sha
    originals={}
    for filename in (ENGINE,STATION,RUNTIME):
        path=hf_hub_download(SPACE,filename,repo_type="space",revision=sha_original,token=api.token)
        originals[filename]=Path(path).read_bytes()
    assert b'Qwen3.5-9B-Q4_K_M.gguf' in originals[RUNTIME]
    assert b'swrlz-qwen35-conversation-v4' in originals[STATION]
    before=originals[ENGINE]
    after=patch_engine(before.decode("utf-8")).encode("utf-8")
    verify_profile_source(before,after)
    receipt={
        "status":"PROFILE_V5_CANDIDATE_SOURCE_SAFE","space":SPACE,
        "baseline":sha_original,"scope":[ENGINE],
        "beforeSha256":sha(before),"afterSha256":sha(after),
        "otherFilesUnmodified":True,"billingChange":False,
    }
    print(json.dumps(receipt),flush=True)
    return sha_original,originals,after

def publish(api):
    if os.environ.get("SWRLZ_QWEN35_PROFILE_V5_APPROVED")!="1":
        raise RuntimeError("No owner-authorized deployment request")
    rev,originals,new=prepare(api)
    if api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("Concurrent Space release; refusing mutation")
    with TemporaryDirectory(prefix="qwen35-profile-v5-") as td:
        target=Path(td)/ENGINE;target.write_bytes(new)
        result=api.create_commit(
            repo_id=SPACE,repo_type="space",parent_commit=rev,
            operations=[CommitOperationAdd(path_in_repo=ENGINE,path_or_fileobj=str(target))],
            commit_message="§C 9B: use original §wyrlzara profile sections across conversation, code and research",
        )
        newrev=str(result.oid)
        actual=Path(hf_hub_download(SPACE,ENGINE,repo_type="space",revision=newrev,token=api.token)).read_bytes()
        if sha(actual)!=sha(new):raise RuntimeError("Profile source verification mismatch")
        print(json.dumps({"status":"PROFILE_V5_SOURCE_PUBLISHED","previous":rev,"revision":newrev}),flush=True)
        return newrev,originals

def rollback(api,rev,originals):
    if api.repo_info(SPACE,repo_type="space").sha!=rev:
        raise RuntimeError("Concurrent release; refuse unsafe rollback")
    with TemporaryDirectory(prefix="qwen35-profile-v5-rollback-") as td:
        src=Path(td)/ENGINE;src.write_bytes(originals[ENGINE])
        result=api.create_commit(
            repo_id=SPACE,repo_type="space",parent_commit=rev,
            operations=[CommitOperationAdd(path_in_repo=ENGINE,path_or_fileobj=str(src))],
            commit_message="Rollback §C 9B profile-efficiency experiment to exact original source",
        )
        restored=str(result.oid)
        actual=Path(hf_hub_download(SPACE,ENGINE,repo_type="space",revision=restored,token=api.token)).read_bytes()
        if sha(actual)!=sha(originals[ENGINE]):raise RuntimeError("Rollback verification failed")
        print(json.dumps({"status":"PROFILE_V5_ROLLBACK_VERIFIED","revision":restored}),flush=True)

if __name__=="__main__":
    mode=sys.argv[1:]
    if mode not in (["inspect"],["publish"]):raise SystemExit("Usage: ... inspect|publish")
    api=HfApi(token=os.environ.get("HF_TOKEN") or None)
    if mode==["inspect"]:prepare(api)
    elif mode==["publish"]:
        if not api.token:raise RuntimeError("Missing existing HF owner token")
        publish(api)
