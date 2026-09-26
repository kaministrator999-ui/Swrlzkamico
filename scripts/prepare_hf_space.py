#!/usr/bin/env python3
"""Prepare an isolated, source-pinned HF candidate without mutating canonical runtime."""
from __future__ import annotations
import argparse, hashlib, json, shutil, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"hf_space"
SOURCES=["accepted_runtime/lalm/r39_engine.py","accepted_runtime/accepted.json","swyrlz/backend.py","swyrlz/r39_inference.py","swyrlz/r39_native.py","swyrlz/r39_matvec_patch.py","swyrlz/r39_tokenizer_patch.py","swyrlz/__init__.py","lalm§wyrlz.transport.json","chat/§wyrlz/index.html","chat/§wyrlz/assets/ice-dragon-adult-wallpaper.png","chat/§wyrlz/assets/kompanion.png"]
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    revision=subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip()
    manifest=json.loads((ROOT/"lalm§wyrlz.transport.json").read_text(encoding="utf-8"))
    assert len(manifest["chunks"])==54 and manifest["sha256"]=="f0a466c869447345eb2e13d8ad4cf267830a1d69f20bb88de4e1ecf3ade863c7"
    assert all((ROOT/c["path"]).is_file() for c in manifest["chunks"]), "Missing source model transport chunk"
    for rel in SOURCES:
        source=ROOT/rel
        assert source.is_file(), f"Missing canonical source: {rel}"
        target=OUT/rel
        if not args.check:
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source,target)
        else:
            assert target.is_file() and hashlib.sha256(target.read_bytes()).digest()==hashlib.sha256(source.read_bytes()).digest(), f"Staged source drift: {rel}"
    provenance={"sourceRepository":"kaministrator999-ui/Swrlzkamico","sourceCommit":revision,"modelFormat":"SWRLZX","rawSha256":"65e4b5d730f66024c44da25aec27730db27aa0019df0df26c0997d17ce58bdee","rawSizeBytes":233637480,"transportSha256":manifest["sha256"],"transportChunks":len(manifest["chunks"]),"modelDelivery":"verified chunk download on startup; no model uploaded by workflow"}
    path=OUT/"MODEL_PROVENANCE.json"
    if args.check: assert json.loads(path.read_text(encoding="utf-8"))==provenance, "Provenance drift"
    else: path.write_text(json.dumps(provenance,indent=2)+"\n",encoding="utf-8")
    print("HF candidate source staging verified:",revision,"chunks:",len(manifest["chunks"]))
if __name__=="__main__": main()
