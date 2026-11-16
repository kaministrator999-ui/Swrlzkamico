#!/usr/bin/env python3
"""§C read-only, exact-source candidate for a shared response-quality policy.

The live Hugging Face Space is authoritative. This tool patches only an
in-memory copy of lfm2_700m_engine.py for preflight analysis. It never uploads,
commits, deploys, rewrites historical model weights, or alters user data.
The quality overlay is appended to the canonical authored profile selector
shared by the actual conversation and coder engines, not a new persona.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from pathlib import Path

SPACE = "kamiloki/Swyrlz"
ENGINE = "lfm2_700m_engine.py"
TAG = "swrlz-response-quality-contract-v1"
FUNCTION_ANCHOR = 'def _wyrlz_active_profile(prompt="", programming=None, brief=False):'
RETURN_ANCHOR = '    return lead+"\\n\\n"+"\\n\\n".join(_wyrlz_authored_section(h) for h in headings)'
CONTRACT_NAME = "SWRLZ_RESPONSE_QUALITY_CONTRACT_V1"
CONTRACT = (
    "\nRESPONSE QUALITY (apply alongside existing task/safety constraints):\n"
    "Resolve the user's actual intent before answering. In follow-ups, keep "
    "previous constraints and change only what the user updated. "
    "Distinguish supplied facts, researched evidence, inference, and unknowns; "
    "never invent sources, verification, tool actions, completed work, or memories. "
    "For exhaustive questions check coverage, uniqueness, and numbering; for "
    "calculations check assumptions and units; for comparisons state evidence "
    "and meaningful tradeoffs. If a claim cannot be verified, specify what "
    "is unknown rather than confidently filling the gap. "
    "Keep simple answers concise, but provide sufficient detail for complex "
    "requests. Avoid canned filler, repeated paragraphs, and empty reassurance. "
    "For songs and creative outputs honor requested structure, distinctive "
    "sections, continuity, and deliberate rather than runaway repetition."
)
OVERLAY = (
    f"# {TAG}: source-attached guidance, no model or routing override.\n"
    f"{CONTRACT_NAME} = {CONTRACT!r}\n\n"
)

def _one(source: str, original: str, replacement: str, label: str) -> str:
    count = source.count(original)
    if count != 1:
        raise ValueError(f"SOURCE_DRIFT_{label}: found {count}, expected 1")
    return source.replace(original, replacement, 1)

def patch_engine(source: str) -> str:
    if TAG in source:
        raise ValueError("QUALITY_POLICY_ALREADY_PRESENT")
    if "BUILTIN_ASSISTANT_PROFILE" not in source:
        raise ValueError("ORIGINAL_AUTHORED_PROFILE_MISSING")
    if "def generate_events(payload):" not in source:
        raise ValueError("ACTIVE_ENGINE_GENERATOR_MISSING")
    original = source
    source = _one(source, FUNCTION_ANCHOR, OVERLAY + FUNCTION_ANCHOR, "PROFILE_ENTRY")
    source = _one(source, RETURN_ANCHOR, RETURN_ANCHOR + "+" + CONTRACT_NAME, "PROFILE_RETURN")
    ast.parse(source, filename=ENGINE)
    # All original source bytes, including historic authored profile, recover
    # exactly by reversing our two uniquely anchored insertions.
    recovered = source.replace(OVERLAY + FUNCTION_ANCHOR, FUNCTION_ANCHOR, 1)
    recovered = recovered.replace(RETURN_ANCHOR + "+" + CONTRACT_NAME, RETURN_ANCHOR, 1)
    if recovered != original:
        raise AssertionError("UNRELATED_SOURCE_BYTES_CHANGED")
    return source

def test_shared_profile(original: str, candidate: str) -> None:
    parsed = ast.parse(candidate, filename=ENGINE)
    constants = [n for n in parsed.body if isinstance(n, ast.Assign) and
                 any(isinstance(t, ast.Name) and t.id == CONTRACT_NAME for t in n.targets)]
    helpers = [n for n in parsed.body if isinstance(n, ast.FunctionDef) and
               n.name == "_wyrlz_active_profile"]
    if len(constants) != 1 or len(helpers) != 1:
        raise AssertionError("PROFILE_SYMBOL_MISMATCH")
    namespace = {
        "re": re,
        "BUILTIN_ASSISTANT_PROFILE": "Original §wyrlz header\n\nOriginal section text",
        "_wyrlz_authored_section": lambda heading: heading + ": original text",
    }
    ast_helpers = ast.Module(body=[constants[0], helpers[0]], type_ignores=[])
    exec(compile(ast.fix_missing_locations(ast_helpers), "<profile-contract>", "exec"), namespace)
    select = namespace["_wyrlz_active_profile"]
    for prompt,programming,brief in (
        ("Hello", {}, True),
        ("Compare these sources", {}, False),
        ("Write a complete original song", {}, False),
        ("Fix this function", {"codingTask": True}, True),
    ):
        result = select(prompt,programming,brief)
        assert result.startswith("Original §wyrlz header")
        assert result.count("RESPONSE QUALITY") == 1
        assert "change only what the user updated" in result
        assert "never invent sources" in result
    assert original.count("BUILTIN_ASSISTANT_PROFILE") >= 1
    assert candidate.count(OVERLAY) == 1

def inspect() -> dict:
    # HF is accessed in read-only mode; never infer source from old Github
    # snapshots or generated build artifacts.
    from huggingface_hub import HfApi, hf_hub_download
    api = HfApi()
    revision = str(api.repo_info(SPACE, repo_type="space").sha)
    raw = Path(hf_hub_download(SPACE, ENGINE, repo_type="space",
                               revision=revision)).read_bytes()
    updated = patch_engine(raw.decode("utf-8")).encode("utf-8")
    test_shared_profile(raw.decode("utf-8"), updated.decode("utf-8"))
    result = {
        "contract": TAG,
        "space": SPACE,
        "revision": revision,
        "file": ENGINE,
        "originalSha256": hashlib.sha256(raw).hexdigest(),
        "candidateSha256": hashlib.sha256(updated).hexdigest(),
        "verified": True,
        "published": False,
        "changes": ["append shared quality guidance to existing profile selection"],
        "unchanged": ["all other original source", "model weights", "native context",
                      "auth", "history", "online research", "§E", "deployment"],
    }
    report = Path("reports/chat-response-quality-v1")
    report.mkdir(parents=True, exist_ok=True)
    (report / "manifest.json").write_text(json.dumps(result, indent=2)+"\n")
    print("SWRLZ_QUALITY_SOURCE_PREFLIGHT", json.dumps(result), flush=True)
    return result

def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("mode", choices=["inspect"])
    args=parser.parse_args()
    if args.mode == "inspect":
        inspect()

if __name__ == "__main__":
    main()
