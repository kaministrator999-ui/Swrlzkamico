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
import struct
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
        stock_tokens=meta.get("tokenizer.ggml.tokens")
        r39_tokens=model.tokenizer.tokens
        if not isinstance(stock_tokens,list) or len(r39_tokens)!=len(stock_tokens):raise ValueError("Tokenizer vocabulary size differs")
        spans=original["metadataSpans"]
        if "tokenizer.ggml.tokens" not in spans or spans["tokenizer.ggml.tokens"][0]!=9:
            raise ValueError("Cannot safely rewrite GGUF vocabulary metadata")
        def pack_string(s):
            b=s.encode("utf-8")
            return struct.pack("<Q",len(b))+b
        vocabulary=struct.pack("<IQ",8,len(r39_tokens))+b"".join(pack_string(s) for s in r39_tokens)
        _,vocab_start,vocab_end=spans["tokenizer.ggml.tokens"]
        if vocab_end-vocab_start<12:raise ValueError("Invalid original vocabulary span")
        if model.tokenizer_spec.get("merges",[])!=meta.get("tokenizer.ggml.merges",[]):raise ValueError("BPE merges differ; unsafe to reuse stock GGUF metadata")
        for key,stock_key in (("bosTokenId","tokenizer.ggml.bos_token_id"),("eosTokenId","tokenizer.ggml.eos_token_id")):
            if key in model.tokenizer_spec and int(model.tokenizer_spec[key])!=int(meta.get(stock_key,-1)):
                raise ValueError(f"Tokenizer special ID mismatch: {key}")
        alignment=int(meta.get("general.alignment",32))
        if alignment<=0 or alignment&(alignment-1):raise ValueError("Invalid GGUF alignment")
        header_end=original["tensorDataStart"]
        data_start=(header_end+alignment-1)//alignment*alignment
        original_size=args.stock.stat().st_size
        old_data_start=data_start
        with args.stock.open("rb") as template:
            header=template.read(original["tensorDataStart"])
        header=header[:vocab_start]+vocabulary+header[vocab_end:]
        new_data_start=(len(header)+alignment-1)//alignment*alignment
        data_start=new_data_start
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
            if destination<data_start or old_data_start+entry["offset"]+size>original_size:raise ValueError(f"GGUF tensor bounds invalid: {name}")
            operations.append((destination,source,size,name))
        ordered=sorted(operations)
        for prev,next_ in zip(ordered,ordered[1:]):
            if prev[0]+prev[2]>next_[0]:raise ValueError("GGUF tensor offsets overlap")
        args.output.parent.mkdir(parents=True,exist_ok=True)
        temp=args.output.with_name(args.output.name+".part")
        try:
            with args.stock.open("rb") as template,temp.open("wb") as dst:
                dst.write(header)
                dst.write(b"\\0"*(new_data_start-len(header)))
                template.seek(old_data_start)
                shutil.copyfileobj(template,dst,1024*1024)
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
                "convertedSha256":sha256(args.output),"tensorCount":len(operations),"r39VocabularyEntries":len(r39_tokens),"vocabularyEntriesReplaced":sum(a!=b for a,b in zip(r39_tokens,stock_tokens)),
                "note":"Exact byte-layout substitution only; compare logits and outputs before serving."}
        args.output.with_suffix(args.output.suffix+".provenance.json").write_text(json.dumps(result,indent=2)+"\n")
        print(json.dumps(result))
    finally:model.close()

if __name__=="__main__":main()
