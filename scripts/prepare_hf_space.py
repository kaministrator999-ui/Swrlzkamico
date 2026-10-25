#!/usr/bin/env python3
"""Prepare an isolated, source-pinned HF candidate without mutating canonical runtime."""
from __future__ import annotations
import argparse, hashlib, json, os, re, shutil, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"hf_space"
SOURCES=["accepted_runtime/lalm/r39_engine.py","accepted_runtime/accepted.json","swyrlz/backend.py","swyrlz/r39_inference.py","swyrlz/r39_native.py","native/r39_native.c","native/r39_batch.c","scripts/build_r39_native.py","swyrlz/r39_matvec_patch.py","swyrlz/r39_tokenizer_patch.py","swyrlz/__init__.py","lalm§wyrlz.transport.json","chat/§wyrlz/index.html","chat/§wyrlz/assets/ice-dragon-adult-wallpaper.png","chat/§wyrlz/assets/kompanion.png","chat/§wyrlz/assets/chatgpt-archive-import-v1.js","chat/§wyrlz/assets/chatgpt-archive-sidebar-v204.js","chat/§wyrlz/assets/github-explorer-v223.js","chat/§wyrlz/assets/source-guides-v245.js","chat/§wyrlz/assets/chat-updates-v1.js","chat/§wyrlz/assets/chat-updates-v1.json","api/online_research.py","accepted_runtime/research/online_research_reasoner.py"]
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    revision=os.environ.get("SWRLZ_SOURCE_COMMIT","").strip() or subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    assert re.fullmatch(r"[0-9a-f]{40}",revision), "Source revision must be a full immutable Git commit"
    manifest=json.loads((ROOT/"lalm§wyrlz.transport.json").read_text(encoding="utf-8"))
    assert len(manifest["chunks"])==54 and manifest["sha256"]=="f0a466c869447345eb2e13d8ad4cf267830a1d69f20bb88de4e1ecf3ade863c7"
    assert all((ROOT/c["path"]).is_file() for c in manifest["chunks"]), "Missing source model transport chunk"
    assert manifest["size_bytes"]==sum(int(c["size_bytes"]) for c in manifest["chunks"]), "Chunk sizes disagree with transport manifest"
    for rel in SOURCES:
        source=ROOT/rel
        assert source.is_file(), f"Missing canonical source: {rel}"
        target=OUT/rel
        if not args.check:
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source,target)
        else:
            # Stage all canonical sources exactly, including Chat; no hidden HF composer injection.
            assert target.is_file() and hashlib.sha256(target.read_bytes()).digest()==hashlib.sha256(source.read_bytes()).digest(), f"Staged source drift: {rel}"
    prepared_research=OUT/"swrzl_prepared_runtime/research/online_research_reasoner.py"
    research_source=ROOT/"accepted_runtime/research/online_research_reasoner.py"
    if args.check:
        assert prepared_research.is_file() and hashlib.sha256(prepared_research.read_bytes()).digest()==hashlib.sha256(research_source.read_bytes()).digest(), "Prepared Online Research reasoner drift"
    else:
        prepared_research.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(research_source,prepared_research)
    provenance={"sourceRepository":"kaministrator999-ui/Swrlzkamico","sourceCommit":revision,"modelFormat":"SWRLZX","rawSha256":"65e4b5d730f66024c44da25aec27730db27aa0019df0df26c0997d17ce58bdee","rawSizeBytes":233637480,"transportSha256":manifest["sha256"],"transportChunks":len(manifest["chunks"]),"modelDelivery":"verified chunk download on startup; no model uploaded by workflow"}
    path=OUT/"MODEL_PROVENANCE.json"
    if args.check: assert json.loads(path.read_text(encoding="utf-8"))==provenance, "Provenance drift"
    else: path.write_text(json.dumps(provenance,indent=2)+"\n",encoding="utf-8")
    # The canonical account-backed Chat already owns model/profile settings and transport.
    # Keep /probe and /legacy mounted separately; never add their developer/test controls
    # into the user conversation composer. Chat export belongs in the side menu.
    ui=OUT/"chat/§wyrlz/index.html"
    canonical=ROOT/"chat/§wyrlz/index.html"
    assert ui.is_file() and ui.read_bytes()==canonical.read_bytes(), "Canonical Chat staging mismatch"
    assert b'href="/api/lalm_station/export"' in ui.read_bytes(), "Side-menu export link missing"
    assert b'id="hfProfile"' not in ui.read_bytes() and b'id="hfUserProfile"' not in ui.read_bytes() and b'id="hfModel"' not in ui.read_bytes(), "HF-only test controls leaked into Chat"
    print("HF candidate source staging verified:",revision,"chunks:",len(manifest["chunks"]))
if __name__=="__main__": main()
