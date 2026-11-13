"""Check live restart guard: stale/transition workers are not new-code regressions."""
from hf_chat_qwen35_coder_prefill_v6_release import is_live_version_accepted,PROFILE
base={"terminal":"COMPLETE","isCode":True,"coderRouteSeen":True,"status":"PASS"}
assert is_live_version_accepted(base|{"flags":[]}) is False
assert is_live_version_accepted(base|{"flags":[],"terminal":"FAILED","status":None}) is False
assert is_live_version_accepted(base|{"flags":[PROFILE]}) is True
assert is_live_version_accepted(base|{"flags":["swrlz-coder-prefill-v6-standard"]}) is False
for changed in (
  {"terminal":"FAILED"},{"isCode":False},
  {"coderRouteSeen":False},{"status":"REJECT"},
):
    try:
        is_live_version_accepted(base|changed|{"flags":[PROFILE]})
    except RuntimeError:
        pass
    else:
        raise AssertionError("Invalid NEW coder version wrongly accepted: "+str(changed))
print("CODER_V6_HF_RESTART_GATE_TEST_PASS")
