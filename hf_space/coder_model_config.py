"""One lightweight coder selection for inference, catalogue and UI labels.

Known official GGUF variants use immutable revisions and verified artifact bytes.
Explicit custom environment selections retain their prior unpinned behavior and
are not described as verified official artifacts.
"""
from __future__ import annotations
import hashlib
import os
from pathlib import Path

KNOWN_MODELS = {'Qwen/Qwen2.5-Coder-7B-Instruct-GGUF': {'repo': 'Qwen/Qwen2.5-Coder-7B-Instruct-GGUF', 'file': 'qwen2.5-coder-7b-instruct-q4_k_m.gguf', 'revision': '13fb94bfda8c8cf22497dc57b78f391a9acb426a', 'bytes': 4683073536, 'sha256': '509287f78cb4d4cf6b3843734733b914b2c158e43e22a7f4bf5e963800894d3c'}}
DEFAULT_REPO = "Qwen/Qwen2.5-Coder-7B-Instruct-GGUF"
MODEL_REPO = os.environ.get("SWRLZ_CODER_MODEL_REPO", DEFAULT_REPO)
MODEL_FILE = os.environ.get("SWRLZ_CODER_MODEL_FILE", KNOWN_MODELS.get(MODEL_REPO, KNOWN_MODELS[DEFAULT_REPO])["file"])
_SELECTED = KNOWN_MODELS.get(MODEL_REPO)
if _SELECTED and _SELECTED["file"] != MODEL_FILE:
    _SELECTED = None
MODEL_REVISION = _SELECTED["revision"] if _SELECTED else None
MODEL_LABEL = MODEL_REPO.rsplit("/", 1)[-1].removesuffix("-GGUF").replace("-Instruct", " Instruct") + " Q4_K_M" if _SELECTED else MODEL_REPO + "/" + MODEL_FILE
MODEL_CHECKPOINT = MODEL_REPO + ("@" + MODEL_REVISION if MODEL_REVISION else "") + "/" + MODEL_FILE


def download_arguments():
    options = {"repo_id": MODEL_REPO, "filename": MODEL_FILE}
    if MODEL_REVISION:
        options["revision"] = MODEL_REVISION
    return options


def verify_artifact(path):
    """Check a known selected artifact once before native model construction."""
    if not _SELECTED:
        return
    source = Path(path)
    if source.stat().st_size != _SELECTED["bytes"]:
        raise ValueError("Coder artifact length does not match the pinned model")
    digest = hashlib.sha256()
    with source.open("rb") as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(block)
    if digest.hexdigest() != _SELECTED["sha256"]:
        raise ValueError("Coder artifact checksum does not match the pinned model")
