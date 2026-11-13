"""Read-only exact live candidate test: both §C 9B engines use one authored core."""
from __future__ import annotations
import ast,json
from pathlib import Path
from huggingface_hub import HfApi,hf_hub_download
from hf_chat_qwen35_global_profile_v5_dual import (
    SPACE,ENGINE,CODER,STATION,RUNTIME,patch_coder,patch_engine,verify,
)
api=HfApi()
rev=api.repo_info(SPACE,repo_type="space").sha
files={}
for name in (ENGINE,CODER,STATION,RUNTIME):
    src=hf_hub_download(SPACE,name,repo_type="space",revision=rev)
    files[name]=Path(src).read_bytes()
updated={ENGINE:patch_engine(files[ENGINE].decode()).encode(),
         CODER:patch_coder(files[CODER].decode()).encode()}
verify(files,updated)
coder=updated[CODER].decode()
engine=updated[ENGINE].decode()
for value in (coder,engine):
    assert '"phase":"PROFILE_CONTEXT_READY"' in value
    assert '"profileComposerVersion":"swrlz-qwen35-profile-v5"' in value
    assert 'SAVED ASSISTANT PROFILE CUSTOMIZATION' in value
    assert 'USER PROFILE (describes the human, not §wyrlz)' in value
assert 'from lfm2_700m_engine import _wyrlz_active_profile' in coder
assert 'AUTHORED §WYRLZ PROFILE (shared canonical identity and engineering principles)' in coder
assert '"qwen3.5-9b"' in files[STATION].decode()
assert 'Qwen3.5-9B-Q4_K_M.gguf' in files[RUNTIME].decode()
print("QWEN35_DUAL_PROFILE_SOURCE_TEST_PASS",json.dumps({"source":rev,
       "generalBytes":len(engine),"coderBytes":len(coder),
       "sourcePreservation":True,"sameCanonicalCore":True}),flush=True)
