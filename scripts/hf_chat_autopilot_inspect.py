"""Read-only inspection of the exact active §C coding and checkpoint implementation."""
from __future__ import annotations

import ast
import hashlib
import json
import os
from huggingface_hub import HfApi, hf_hub_download

SPACE = "kamiloki/Swyrlz"
FILES = ("qwen_coder_engine.py", "station.py")
MARKERS = {
    "qwen_coder_engine.py": [
        "def _swrlz_code_candidate_preview(",
        "def _swrlz_pause_code_events(",
        "def _swrlz_resume_code_events(",
        "def generate_events(",
        "max_segments=8",
        "CODE_OUTPUT_CHECKPOINT",
        "code_delivery",
    ],
    "station.py": [
        'elif kind=="CODE_OUTPUT_CHECKPOINT"',
        "pendingCodeGeneration",
        "resume_code",
        "def _run_generation(",
        "def _generate(",
        "def _coder_generate(",
        "def _commit_revision(",
    ],
}

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def main() -> None:
    token = os.environ.get("HF_TOKEN") or None
    api = HfApi(token=token)
    info = api.repo_info(SPACE, repo_type="space")
    revision = info.sha
    print("ACTIVE_SPACE", json.dumps({"repo": SPACE, "revision": revision}))
    for name in FILES:
        source = open(hf_hub_download(SPACE, name, repo_type="space",
                                      revision=revision, token=token), "rb").read()
        text = source.decode("utf-8")
        tree = ast.parse(text, filename=name)
        lines = text.splitlines()
        functions = {node.name: [node.lineno, node.end_lineno]
                     for node in ast.walk(tree)
                     if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
        print("ACTIVE_FILE", json.dumps({
            "path": name, "sha256": digest(source), "lines": len(lines),
            "functions": {k: v for k, v in functions.items()
                          if ("code" in k or "generation" in k
                              or "preview" in k or "resume" in k or "patch" in k)}
        }, ensure_ascii=False))
        selected = (("_swrlz_auto_code_chain", "_swrlz_complete_code_followup", "live_code_control",
                     "stream_generation") if name == "station.py" else
                    ("_swrlz_code_candidate_preview", "_swrlz_pause_code_events"))
        for function in selected:
            bounds = functions.get(function)
            if not bounds:
                print("FUNCTION_MISSING", name, function)
                continue
            start, stop = bounds
            if function == "_swrlz_code_candidate_preview":
                stop = min(stop, start + 130)
            if function == "stream_generation":
                start = min(stop, start + 30)
                stop = min(stop, start + 65)
            print("FUNCTION_INSPECT", json.dumps({
                "file": name, "name": function, "start": start, "end": stop,
                "lines": [f"{i + 1}: {lines[i]}" for i in range(start - 1, stop)]
            }, ensure_ascii=False))
        for marker in MARKERS[name]:
            hits = [i for i, line in enumerate(lines) if marker in line]
            print("ANCHOR", json.dumps({"file": name, "marker": marker, "count": len(hits)}))
            for line_index in hits[:2]:
                start = max(0, line_index - 7)
                stop = min(len(lines), line_index + 15)
                print("CONTEXT", json.dumps({
                    "file": name, "line": line_index + 1,
                    "lines": [f"{i + 1}: {lines[i]}" for i in range(start, stop)]
                }, ensure_ascii=False))

if __name__ == "__main__":
    main()
