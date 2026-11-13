"""Exercises actual 9B CPU-profile logic without downloading or running the model."""
import ast
from pathlib import Path
from types import SimpleNamespace
from scripts.hf_qwen35_free_cpu_tune import patch_runtime, patch_station, test_profile

source=Path("scripts/hf_chat_qwen35_9b_runtime.py").read_text("utf-8")
test_profile(source)
tree=ast.parse(source)
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=="_cpu_threads")
isolated=ast.Module(body=[fn],type_ignores=[])
ast.fix_missing_locations(isolated)
def run(affinity, quota, period=100000):
    fake_os=SimpleNamespace(sched_getaffinity=lambda _:[*range(affinity)],cpu_count=lambda:affinity)
    fake_path=lambda _:SimpleNamespace(read_text=lambda:f"{quota} {period}")
    env={"os":fake_os,"Path":fake_path}
    exec(compile(isolated,"<cpu-capacity>","exec"),env)
    return env["_cpu_threads"]()

assert run(64,1600000)==16
assert run(64,200000)==2
assert run(64,400000)==4
assert run(4,1600000)==4
assert run(2,"max")==2
assert run(64,50000)==1
assert run(64,1600000,0)==16
assert run(1,1600000)==1
assert run(64,"corrupted")==16
assert source.count("swrlz-qwen35-cpu-v2")==2
assert "MODEL_REPO = \"twoody/Qwen3.5-9B-GGUF\"" in source
assert "PARALLEL_REQUESTS = 1" in source
assert "CONTEXT_TOKENS = 8192" in source
assert "--threads-batch" in source
print("QWEN35_PROFILE_QUOTA_TESTS_PASS 16CPU=10/16, 2CPU=2/2")
