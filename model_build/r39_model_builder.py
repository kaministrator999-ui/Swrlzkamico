#!/usr/bin/env python3
"""Canonical R39 .§wyrlzx model-update builder scaffold.

This is deliberately fail-closed. It inspects the current canonical artifact, training
corpus, and writable tensor set, then emits a build plan. It MUST NOT claim a candidate
model until a real optimizer has produced tensor updates and the writer has repacked
the artifact with new section/root hashes.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
from swyrlz.r39_inference import R39Model

DEFAULT_CORPUS=Path("training/r39_consolidation_v74_v90.jsonl")

def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def load_corpus(path:Path):
    rows=[]
    for n,line in enumerate(path.read_text(encoding="utf-8").splitlines(),1):
        if not line.strip(): continue
        row=json.loads(line)
        if not isinstance(row,dict) or not row.get("id") or not row.get("capability"):
            raise ValueError(f"invalid corpus row {n}")
        rows.append(row)
    if not rows: raise ValueError("empty consolidation corpus")
    return rows

def inspect(model_path:Path,corpus_path:Path):
    rows=load_corpus(corpus_path)
    model=R39Model(model_path)
    try:
        kinds={}
        tensor_bytes=0
        for d in model.desc.values():
            kinds[d["kind"]]=kinds.get(d["kind"],0)+1
            tensor_bytes+=int(d["storedLengthBytes"])
        caps={}
        for r in rows:caps[r["capability"]]=caps.get(r["capability"],0)+1
        return {
            "contract":"swrlz-r39-canonical-build-plan-v1",
            "parent":{"path":str(model_path),"sha256":sha256(model_path),"modelId":model.manifest.get("modelId"),"fileBytes":model.header["fileBytes"]},
            "architecture":{"tensors":len(model.desc),"quantizers":kinds,"tensorStoredBytes":tensor_bytes,"tokens":len(model.tokenizer.tokens),"graphNodes":len(model.graph.get("nodes",[]))},
            "corpus":{"path":str(corpus_path),"sha256":sha256(corpus_path),"examples":len(rows),"capabilities":caps},
            "candidate":{"status":"NOT_BUILT","reason":"Optimizer/requantizer/repacker must produce real updated tensor bytes before a candidate .§wyrlzx may be declared."},
            "requiredNext":["define trainable tensor policy","implement loss/teacher-target encoding for consolidation examples","implement optimizer update against dequantized trainable tensors","requantize updated tensors using supported SWRLZX quantizers","repack sections/TOC/header and recompute integrity hashes","load candidate with R39Model and run behavioral equivalence gates"]
        }
    finally:model.close()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("model",type=Path)
    ap.add_argument("--corpus",type=Path,default=DEFAULT_CORPUS)
    ap.add_argument("--plan-out",type=Path)
    args=ap.parse_args()
    plan=inspect(args.model,args.corpus)
    text=json.dumps(plan,indent=2,ensure_ascii=False)+"\n"
    if args.plan_out:
        args.plan_out.parent.mkdir(parents=True,exist_ok=True);args.plan_out.write_text(text,encoding="utf-8")
    print(text,end="")
if __name__=="__main__":main()
