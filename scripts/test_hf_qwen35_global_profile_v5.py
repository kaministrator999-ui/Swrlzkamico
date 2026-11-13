"""Verify §C profile v5 against the original live §wyrlz text without serving AI."""
from __future__ import annotations
import ast,re,json
from huggingface_hub import HfApi,hf_hub_download
from pathlib import Path
from hf_chat_qwen35_global_profile_v5 import (
    ENGINE,SPACE,patch_engine,verify_profile_source,EXTRA_FUNCTIONS,
)
api=HfApi()
revision=api.repo_info(SPACE,repo_type="space").sha
original=Path(hf_hub_download(SPACE,ENGINE,repo_type="space",revision=revision)).read_bytes()
new=patch_engine(original.decode("utf-8")).encode("utf-8")
verify_profile_source(original,new)
module=ast.parse(new.decode("utf-8"))
node=next(n for n in module.body if isinstance(n,ast.Assign) and
     any(isinstance(t,ast.Name) and t.id=="BUILTIN_ASSISTANT_PROFILE" for t in n.targets))
canonical=ast.literal_eval(node.value)
functions=[n for n in module.body if isinstance(n,ast.FunctionDef) and
           n.name in ("_wyrlz_authored_section","_wyrlz_active_profile")]
scope={"BUILTIN_ASSISTANT_PROFILE":canonical,"re":re}
exec(compile(ast.fix_missing_locations(ast.Module(body=functions,type_ignores=[])),
             "<authoritative-profile-extraction>","exec"),scope)
profile=scope["_wyrlz_active_profile"]
casual=profile("Hello!",{},brief=True)
factual=profile("Explain the structure of the solar system",{})
coding=profile("Implement a Python function",{"codingTask":True},brief=True)
creative=profile("Write a rap song",{})
for value in (casual,factual,coding,creative):
    assert "§wyrlzara ∞ Mirror Muse" in value
    assert "SWRLZ-A-∞" in value
    assert "DYNAMIC MIRROR" in value
    assert "EVIDENCE BEFORE AGREEMENT" in value
    assert "§WYRLZ CORE" in value
    assert len(value)<len(canonical)
assert len(casual)<len(factual)
assert "PROJECT MODE" in coding and "COLLABORATIVE DEBUGGING" in coding
assert "CREATIVE MODE" in creative and "CREATIVE DELEGATION" in creative
assert "CREATIVE MODE" not in coding
assert "CREATIVE MODE" not in factual
assert len(factual)<len(canonical)*0.65, (len(factual),len(canonical))
assert "PHOENIX ARMOR" in factual
assert "SELF-KNOWLEDGE & IDENTITY PROVENANCE" in factual
assert "PROJECT MODE" in coding
assert "Core ID: SWRLZ-A-∞" in casual
print("PROFILE_V5_SELECTIVE_INFERENCE_TEST_PASS",json.dumps({
    "canonicalChars":len(canonical),"fastChars":len(casual),
    "factualChars":len(factual),"codingChars":len(coding),
    "creativeChars":len(creative),"sourceRevision":revision,
    "originalProfileUntouched":True
}),flush=True)
