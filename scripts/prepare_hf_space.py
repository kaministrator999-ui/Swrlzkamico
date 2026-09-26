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
    assert manifest["size_bytes"]==sum(int(c["size_bytes"]) for c in manifest["chunks"]), "Chunk sizes disagree with transport manifest"
    for rel in SOURCES:
        source=ROOT/rel
        assert source.is_file(), f"Missing canonical source: {rel}"
        target=OUT/rel
        if not args.check:
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(source,target)
        else:
            assert target.is_file() and (rel=="chat/§wyrlz/index.html" or hashlib.sha256(target.read_bytes()).digest()==hashlib.sha256(source.read_bytes()).digest()), f"Staged source drift: {rel}"
    provenance={"sourceRepository":"kaministrator999-ui/Swrlzkamico","sourceCommit":revision,"modelFormat":"SWRLZX","rawSha256":"65e4b5d730f66024c44da25aec27730db27aa0019df0df26c0997d17ce58bdee","rawSizeBytes":233637480,"transportSha256":manifest["sha256"],"transportChunks":len(manifest["chunks"]),"modelDelivery":"verified chunk download on startup; no model uploaded by workflow"}
    path=OUT/"MODEL_PROVENANCE.json"
    if args.check: assert json.loads(path.read_text(encoding="utf-8"))==provenance, "Provenance drift"
    else: path.write_text(json.dumps(provenance,indent=2)+"\n",encoding="utf-8")
    ui=OUT/"chat/§wyrlz/index.html"
    if not args.check:
        html=ui.read_text(encoding="utf-8")
        marker='<div class="composer-box">'
        assert html.count(marker)==1, "Canonical composer insertion point changed"
        html=html.replace(marker, '<label class="hf-model-picker" for="hfModel"><span>Model</span><select id="hfModel" aria-label="Inference model"><option value="r39">§wyrlz R39 — fixed</option><option value="stock" disabled>Stock reference — not configured</option><option value="compare" disabled>Compare both — not configured</option></select></label>'+marker,1)
        html=html.replace('const sendButton = document.getElementById("sendButton");','const sendButton = document.getElementById("sendButton");\n      const hfModel = document.getElementById("hfModel");',1)
        html=html.replace('profileId:"LALM",ingress:"SWRLZ_LALM_STATION"','profileId:"LALM",modelId:hfModel.value,ingress:"SWRLZ_LALM_STATION"',1)
        html=html.replace("</style>", '.hf-model-picker{display:flex;align-items:center;gap:8px;color:#c2d4e5;font-size:12px;padding:4px 8px}.hf-model-picker select{min-width:0;background:#092038;color:#e6f7ff;border:1px solid #37617a;border-radius:8px;padding:5px}</style>',1)
        ui.write_text(html,encoding="utf-8")
    else:
        html=ui.read_text(encoding="utf-8")
        assert 'id="hfModel"' in html and 'modelId:hfModel.value' in html, "HF model selector missing"
        assert 'option value="stock" disabled' in html, "Unconfigured stock model must remain disabled"
    print("HF candidate source staging verified:",revision,"chunks:",len(manifest["chunks"]))
if __name__=="__main__": main()
