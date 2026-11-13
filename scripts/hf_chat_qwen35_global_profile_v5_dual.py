#!/usr/bin/env python3
"""Unify the actual §C Qwen3.5-9B text/coder routes on one §wyrlz profile.

The original universal §wyrlzara core (in general engine) remains unchanged.
Coder engine retains its historical profile source for lineage but never injects
that outdated user-bound copy. Prompt uses exact selected universal sections.
No client source, model bytes, 9B runtime or paid hardware change.
"""
from __future__ import annotations
import ast,hashlib,json,os,sys
from pathlib import Path
from tempfile import TemporaryDirectory
from huggingface_hub import HfApi,hf_hub_download,CommitOperationAdd
from hf_chat_qwen35_global_profile_v5 import (
    SPACE,ENGINE,STATION,RUNTIME,patch_engine,verify_profile_source,
    replace_unique,
)

CODER="qwen_coder_engine.py"
EDIT_FILES=(ENGINE,CODER)
CODER_PROFILE_OLD=r'''    if not programming.get("codingTask"):
        system+="\nBUILT-IN §WYRLZ PROFILE (default assistant identity/behavior):\n"+BUILTIN_ASSISTANT_PROFILE
        if custom_assistant_profile:
            system+="\nUSER CUSTOMIZATION FOR §WYRLZ (additional preferences layered on top of the built-in profile; do not erase the built-in identity):\n"+custom_assistant_profile
        if user_profile:
            system+="\nUSER PROFILE (describes the current user, not §wyrlz; context only):\n"+user_profile'''
CODER_PROFILE_NEW=r'''    # Code and §E use the same actual, authored §wyrlzara core as chat.
    # Account-scoped companion/user preferences remain separate from authority.
    system+="\nAUTHORED §WYRLZ PROFILE (shared canonical identity and engineering principles):\n"+_wyrlz_active_profile(prompt,programming,brief=True)
    if custom_assistant_profile:
        system+="\nSAVED ASSISTANT PROFILE CUSTOMIZATION (no tool authority):\n"+custom_assistant_profile
    if user_profile:
        system+="\nUSER PROFILE (describes the human, not §wyrlz):\n"+user_profile'''
CODER_REPAIR_OLD=r'''        system,fitted_prompt,repair_context_telemetry=build_compact_repair_context(
            programming,
            prompt,
            _response_mode(prompt,programming),
        )
        system+=programming_library_context(programming)'''
CODER_REPAIR_NEW=r'''        system,fitted_prompt,repair_context_telemetry=build_compact_repair_context(
            programming,
            prompt,
            _response_mode(prompt,programming),
        )
        system+="\nAUTHORED §WYRLZ PROFILE (repair context):\n"+_wyrlz_active_profile(prompt,programming,brief=True)
        if custom_assistant_profile:
            system+="\nSAVED ASSISTANT CUSTOMIZATION:\n"+custom_assistant_profile
        if user_profile:
            system+="\nUSER PROFILE (context only):\n"+user_profile
        system+=programming_library_context(programming)'''

def patch_coder(s):
    s=replace_unique(s,
        "def generate_events(payload):",
        "def generate_events(payload):\n"
        "    # Import only when this route is used; prevent duplicate §wyrlz cores.\n"
        "    from lfm2_700m_engine import _wyrlz_active_profile",
        "shared-universal-profile-import")
    s=replace_unique(s,CODER_PROFILE_OLD,CODER_PROFILE_NEW,"coder-profile-handoff")
    s=replace_unique(s,CODER_REPAIR_OLD,CODER_REPAIR_NEW,"coder-repair-profile-handoff")
    s=replace_unique(s,
        '    yield {"type":"CONTEXT","phase":"BUDGETED",',
        '    yield {"type":"STATUS","phase":"PROFILE_CONTEXT_READY","reason":"swrlz-qwen35-profile-v5"}\n'
        '    yield {"type":"CONTEXT","phase":"BUDGETED","profileComposerVersion":"swrlz-qwen35-profile-v5",',
        "coder-profile-version-receipt")
    ast.parse(s,filename=CODER)
    return s

def digest(b):return hashlib.sha256(b).hexdigest()

def verify(before,after):
    verify_profile_source(before[ENGINE],after[ENGINE])
    coder_before=before[CODER].decode("utf-8")
    coder_after=after[CODER].decode("utf-8")
    # The original historic alternate profile is not deleted, only deactivated.
    a='BUILTIN_ASSISTANT_PROFILE="""'
    original_profile=coder_before.split(a,1)[1].split('"""',1)[0]
    revised_profile=coder_after.split(a,1)[1].split('"""',1)[0]
    assert original_profile==revised_profile
    assert 'from lfm2_700m_engine import _wyrlz_active_profile' in coder_after
    assert 'AUTHORED §WYRLZ PROFILE (shared canonical identity and engineering principles)' in coder_after
    assert '_wyrlz_active_profile(prompt,programming,brief=True)' in coder_after
    assert '"phase":"PROFILE_CONTEXT_READY"' in coder_after
    assert '"profileComposerVersion":"swrlz-qwen35-profile-v5"' in coder_after
    # Existing programming acceptance, inference and source-preservation remain.
    for needle in ("CODE_TRUTH_POLICY","candidate_contract_gate",
                   "source_sized_budget","programming_library_context(programming)",
                   "def _fit_repair_messages(","def _fit_messages("):
        assert needle in coder_before and needle in coder_after
    assert "BUILTIN_ASSISTANT_PROFILE" in coder_after
    assert '+"\\nBUILT-IN §WYRLZ PROFILE' not in coder_after
    for name in EDIT_FILES:ast.parse(after[name].decode(),filename=name)
    print(json.dumps({"stage":"UNIFIED_QWEN35_PROFILE_V5_TEST_PASS",
        "files":list(EDIT_FILES),"oldCoderProfilePreserved":True,
        "newUniversalCoreShared":True,"codingGuardPreserved":True,
        "modelWeightsChanged":False,"hardwareChanged":False}),flush=True)

def prepare(api):
    revision=api.repo_info(SPACE,repo_type="space").sha
    before={}
    for name in (ENGINE,CODER,STATION,RUNTIME):
        p=hf_hub_download(SPACE,name,repo_type="space",
                           revision=revision,token=api.token)
        before[name]=Path(p).read_bytes()
    if b'Qwen3.5-9B-Q4_K_M.gguf' not in before[RUNTIME]:
        raise RuntimeError("Expected resident 9B model changed, refusing source overlay")
    if b'swrlz-qwen35-conversation-v4' not in before[STATION]:
        raise RuntimeError("Original readiness/hardware profile changed")
    after={
        ENGINE:patch_engine(before[ENGINE].decode("utf-8")).encode("utf-8"),
        CODER:patch_coder(before[CODER].decode("utf-8")).encode("utf-8"),
    }
    verify(before,after)
    print(json.dumps({"stage":"UNIFIED_QWEN35_PROFILE_SOURCE_PREPARED",
                      "baseline":revision,
                      "files":{name:{"before":digest(before[name]),"after":digest(after[name])}
                               for name in EDIT_FILES}}),flush=True)
    return revision,before,after

def publish(api):
    if os.environ.get("SWRLZ_QWEN35_PROFILE_V5_APPROVED")!="1":
        raise RuntimeError("No owner-approved source release")
    revision,before,after=prepare(api)
    if api.repo_info(SPACE,repo_type="space").sha!=revision:
        raise RuntimeError("Concurrent HF Space deployment")
    with TemporaryDirectory(prefix="qwen35-unified-profile-v5-") as directory:
        root=Path(directory)
        for name,data in after.items(): (root/name).write_bytes(data)
        res=api.create_commit(repo_id=SPACE,repo_type="space",
             parent_commit=revision,
             operations=[CommitOperationAdd(path_in_repo=name,
                              path_or_fileobj=str(root/name)) for name in EDIT_FILES],
             commit_message="§C 9B unified §wyrlzara profile for conversation, factual, coding and §E routes")
        published=str(res.oid)
        for name in EDIT_FILES:
            actual=Path(hf_hub_download(SPACE,name,repo_type="space",
                         revision=published,token=api.token)).read_bytes()
            if digest(actual)!=digest(after[name]):
                raise RuntimeError("Published §C source differs from validated candidate")
        print(json.dumps({"stage":"UNIFIED_QWEN35_PROFILE_SOURCE_PUBLISHED",
                          "previous":revision,"revision":published}),flush=True)
        return published,before

def rollback(api,revision,before):
    if api.repo_info(SPACE,repo_type="space").sha!=revision:
        raise RuntimeError("Concurrent Space source update prevents rollback")
    with TemporaryDirectory(prefix="qwen35-unified-profile-v5-rollback-") as directory:
        root=Path(directory)
        for name in EDIT_FILES:(root/name).write_bytes(before[name])
        res=api.create_commit(repo_id=SPACE,repo_type="space",
             parent_commit=revision,
             operations=[CommitOperationAdd(path_in_repo=name,
                              path_or_fileobj=str(root/name)) for name in EDIT_FILES],
             commit_message="Rollback §C shared profile experiment to exact prior text/coder bytes")
        result=str(res.oid)
        for name in EDIT_FILES:
            actual=Path(hf_hub_download(SPACE,name,repo_type="space",
                        revision=result,token=api.token)).read_bytes()
            if digest(actual)!=digest(before[name]):
                raise RuntimeError("Rollback SHA mismatch: "+name)
        print(json.dumps({"stage":"UNIFIED_QWEN35_PROFILE_SOURCE_ROLLED_BACK",
                          "revision":result}),flush=True)

if __name__=="__main__":
    mode=sys.argv[1:]
    if mode not in (["inspect"],["publish"]):
        raise SystemExit("Usage: hf_chat_qwen35_global_profile_v5_dual.py inspect|publish")
    api=HfApi(token=os.environ.get("HF_TOKEN") or None)
    if mode==["inspect"]:prepare(api)
    elif mode==["publish"]:
        if not api.token:raise RuntimeError("HF_TOKEN release secret required")
        publish(api)
