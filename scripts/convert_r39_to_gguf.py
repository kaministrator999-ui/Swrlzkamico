"""Experimental lossless R39 tensor substitution into the pinned LFM2 GGUF envelope.

Fail-closed: exact tensor names, shapes, GGML types and tokenizer IDs must match.
Does not alter the original file or publish the result. A successful conversion
is NOT logit parity and must not be promoted to Chat without runtime tests.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import shutil
from pathlib import Path
from inspect_r39_gguf import Reader, GGUF_TYPES, sha256

BLOCK = {"f32":(1,4),"f16":(1,2),"bf16":(1,2),"q4_0":(32,18),"q8_0":(32,34),"q4_k":(256,144),"q6_k":(256,210)}

def size_for(shape, kind):
    if kind not in BLOCK:raise ValueError(f"Unsupported quantizer: {kind}")
    block, width=BLOCK[kind]
    n=1
    for dim in shape:n*=dim
    if n%block:raise ValueError(f"Non-integral quantization block: {shape} {kind}")
    return n//block*width

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--r39",type=Path,required=True)
    ap.add_argument("--stock",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    from swyrlz.r39_inference import R39Model, MODEL_SHA256
    if sha256(args.r39)!=MODEL_SHA256:raise ValueError("R39 source SHA256 mismatch")
    if args.output.resolve() in (args.r39.resolve(),args.stock.resolve()):raise ValueError("Output cannot replace a source model")
    model=R39Model(args.r39)
    try:
        original=Reader(args.stock).inspect()
        meta=original["metadata"]
        if meta.get("general.architecture")!="lfm2":raise ValueError("Original GGUF is not LFM2")
        tensors=original["tensors"]
        if set(tensors)!=set(model.desc):raise ValueError(f"Tensor names differ: missing={sorted(set(model.desc)-set(tensors))[:12]}, extra={sorted(set(tensors)-set(model.desc))[:12]}")
        if model.tokenizer.tokens!=meta.get("tokenizer.ggml.tokens"):raise ValueError("Tokenizer IDs differ; unsafe to reuse stock GGUF metadata")
        if model.tokenizer_spec.get("merges",[])!=meta.get("tokenizer.ggml.merges",[]):raise ValueError("BPE merges differ; unsafe to reuse stock GGUF metadata")
        for key,stock_key in (("bosTokenId","tokenizer.ggml.bos_token_id"),("eosTokenId","tokenizer.ggml.eos_token_id")):
            if key in model.tokenizer_spec and int(model.tokenizer_spec[key])!=int(meta.get(stock_key,-1)):
                raise ValueError(f"Tokenizer special ID mismatch: {key}")
        alignment=int(meta.get("general.alignment",32))
        if alignment<=0 or alignment&(alignment-1):raise ValueError("Invalid GGUF alignment")
        header_end=original["tensorDataStart"]
        data_start=(header_end+alignment-1)//alignment*alignment
        original_size=args.stock.stat().st_size
        operations=[]
        for name,entry in tensors.items():
            d=model.desc[name]
            kind=d["kind"]
            if list(d["shape"])!=entry["shape"] or kind!=entry["type"]:
                raise ValueError(f"Tensor layout mismatch: {name}: R39 {d['shape']} {kind}; GGUF {entry['shape']} {entry['type']}")
            size=size_for(entry["shape"],kind)
            if size!=int(d["storedLengthBytes"]):raise ValueError(f"Tensor byte length mismatch: {name}")
            destination=data_start+entry["offset"]
            source=d["section"].offset+int(d["dataOffsetBytes"])
            if destination< data_start or destination+size>original_size:raise ValueError(f"GGUF tensor bounds invalid: {name}")
            operations.append((destination,source,size,name))
        ordered=sorted(operations)
        for prev,next_ in zip(ordered,ordered[1:]):
            if prev[0]+prev[2]>next_[0]:raise ValueError("GGUF tensor offsets overlap")
        args.output.parent.mkdir(parents=True,exist_ok=True)
        temp=args.output.with_name(args.output.name+".part")
        try:
            shutil.copyfile(args.stock,temp)
            with args.r39.open("rb") as src,temp.open("r+b") as dst:
                for offset,source,length,name in operations:
                    src.seek(source);dst.seek(offset)
                    remaining=length
                    while remaining:
                        chunk=src.read(min(1024*1024,remaining))
                        if not chunk:raise ValueError(f"Truncated R39 tensor: {name}")
                        dst.write(chunk);remaining-=len(chunk)
            os.replace(temp,args.output)
        finally:temp.unlink(missing_ok=True)
        result={"status":"EXPERIMENTAL_UNVERIFIED","format":"GGUF","architecture":"lfm2",
                "sourceR39Sha256":MODEL_SHA256,"stockEnvelopeSha256":sha256(args.stock),
                "convertedSha256":sha256(args.output),"tensorCount":len(operations),
                "note":"Exact byte-layout substitution only; compare logits and outputs before serving."}
        args.output.with_suffix(args.output.suffix+".provenance.json").write_text(json.dumps(result,indent=2)+"\n")
        print(json.dumps(result))
    finally:model.close()

if __name__=="__main__":main()
