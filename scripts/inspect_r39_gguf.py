"""Read-only compatibility gate for the canonical R39 SWRLZX and pinned LFM2 GGUF.

Run from repository root: PYTHONPATH=hf_space python scripts/inspect_r39_gguf.py
This does not convert, publish, or mutate either model.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from collections import Counter
from pathlib import Path

GGUF_TYPES = {0:"f32",1:"f16",2:"q4_0",8:"q8_0",12:"q4_k",14:"q6_k",30:"bf16"}
GGUF_SCALAR = {0:1,1:1,2:1,3:1,4:1,5:1,6:1,7:1,10:8,11:8,12:8}
GGUF_FORMAT = {0:"B",1:"b",2:"H",3:"h",4:"I",5:"i",6:"f",7:"?",10:"Q",11:"q",12:"d"}
MAX_STRING = 8_000_000
MAX_ITEMS = 2_000_000

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(4*1024*1024),b""):h.update(chunk)
    return h.hexdigest()

class Reader:
    def __init__(self, path: Path):
        self.f=path.open("rb")
    def read(self,n):
        b=self.f.read(n)
        if len(b)!=n:raise ValueError("Truncated GGUF")
        return b
    def u32(self):return struct.unpack("<I",self.read(4))[0]
    def u64(self):return struct.unpack("<Q",self.read(8))[0]
    def string(self):
        n=self.u64()
        if n>MAX_STRING:raise ValueError("GGUF string too large")
        return self.read(n).decode("utf-8")
    def value(self,t):
        if t==8:return self.string()
        if t==9:
            inner=self.u32();count=self.u64()
            if count>MAX_ITEMS:raise ValueError("GGUF array too large")
            return [self.value(inner) for _ in range(count)]
        if t not in GGUF_FORMAT:raise ValueError(f"Unsupported GGUF metadata type {t}")
        fmt=GGUF_FORMAT[t]
        return struct.unpack("<"+fmt,self.read(struct.calcsize(fmt)))[0]
    def inspect(self):
        if self.read(4)!=b"GGUF":raise ValueError("Not GGUF")
        version=self.u32();count=self.u64();kv_count=self.u64()
        if version not in (2,3) or count>MAX_ITEMS or kv_count>MAX_ITEMS:raise ValueError("Unsupported GGUF header")
        metadata={}; metadata_spans={}
        for _ in range(kv_count):
            key=self.string(); typ=self.u32(); start=self.f.tell(); metadata[key]=self.value(typ); metadata_spans[key]=(typ,start,self.f.tell())
        tensors={}
        for _ in range(count):
            name=self.string();ndim=self.u32()
            if ndim>8:raise ValueError("Unsupported tensor rank")
            shape=[self.u64() for _ in range(ndim)]
            typ=self.u32();offset=self.u64()
            tensors[name]={"shape":shape,"type":GGUF_TYPES.get(typ,f"ggml_type_{typ}"),"typeId":typ,"offset":offset}
        return {"version":version,"metadata":metadata,"tensors":tensors,"tensorDataStart":self.f.tell(),"metadataSpans":metadata_spans}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--r39",type=Path,help="Already reconstructed, SHA-verified SWRLZX artifact")
    ap.add_argument("--stock",type=Path,help="Already downloaded pinned original GGUF")
    ap.add_argument("--download-stock",action="store_true",help="Download the pinned original with huggingface_hub")
    ap.add_argument("--output",type=Path,default=Path("r39-gguf-compatibility.json"))
    args=ap.parse_args()
    from swyrlz.r39_inference import R39Model, MODEL_SHA256
    from swyrlz.backend import RAW, ensure_r39
    if args.r39 is None:
        state=ensure_r39()
        if not state.get("modelReady"):raise RuntimeError(f"R39 reconstruction failed: {state}")
    raw=args.r39 or RAW
    digest=sha256(raw)
    if digest!=MODEL_SHA256:raise ValueError(f"R39 SHA mismatch: {digest}")
    stock=args.stock
    if stock is None and args.download_stock:
        from huggingface_hub import hf_hub_download
        stock=Path(hf_hub_download(repo_id="LiquidAI/LFM2-350M-GGUF",filename="LFM2-350M-Q4_K_M.gguf",revision="31cd51db1365"))
    if stock is None:raise ValueError("Supply --stock or --download-stock")
    model=R39Model(raw)
    try:
        original=Reader(stock).inspect()
        tensors=original["tensors"]
        r39={name:{"shape":list(d["shape"]),"type":d["kind"]} for name,d in model.desc.items()}
        missing_stock=sorted(set(r39)-set(tensors))
        extra_stock=sorted(set(tensors)-set(r39))
        mismatch={name:{"r39":r39[name],"stock":{"shape":tensors[name]["shape"],"type":tensors[name]["type"]}}
                  for name in sorted(set(r39)&set(tensors))
                  if r39[name]["shape"]!=tensors[name]["shape"] or r39[name]["type"]!=tensors[name]["type"]}
        meta=original["metadata"]
        architecture=meta.get("general.architecture")
        tokenizer=model.tokenizer_spec
        tokens=tokenizer.get("tokens",[])
        stock_tokens=meta.get("tokenizer.ggml.tokens",[])
        token_match=bool(tokens) and tokens==stock_tokens
        token_differences=[{"id":i,"r39":a,"stock":b} for i,(a,b) in enumerate(zip(tokens,stock_tokens)) if a!=b]
        merge_differences=[{"index":i,"r39":a,"stock":b} for i,(a,b) in enumerate(zip(tokenizer.get("merges",[]),meta.get("tokenizer.ggml.merges",[]))) if a!=b]
        report={
            "schema":"swrlz-r39-gguf-compat-v1","r39Sha256":digest,
            "stockRepo":"LiquidAI/LFM2-350M-GGUF","stockRevision":"31cd51db1365",
            "stockSha256":sha256(stock),"ggufVersion":original["version"],
            "architecture":architecture,"r39TensorCount":len(r39),"stockTensorCount":len(tensors),
            "r39Types":dict(Counter(v["type"] for v in r39.values())),
            "stockTypes":dict(Counter(v["type"] for v in tensors.values())),
            "missingInStock":missing_stock,"extraInStock":extra_stock,"shapeOrTypeMismatch":mismatch,
            "r39TokenCount":len(tokens),"stockTokenCount":len(stock_tokens),
            "tokenIdsExactlyEqual":token_match,
            "tokenMismatchCount":len(token_differences)+abs(len(tokens)-len(stock_tokens)),
            "firstTokenMismatches":token_differences[:20],
            "mergeMismatchCount":len(merge_differences)+abs(len(tokenizer.get("merges",[]))-len(meta.get("tokenizer.ggml.merges",[]))),
            "firstMergeMismatches":merge_differences[:10],
            "r39SpecialIds":{k:v for k,v in tokenizer.items() if "token" in k.lower() and "id" in k.lower()},
            "stockSpecialIds":{k:v for k,v in meta.items() if k.startswith("tokenizer.ggml.") and k.endswith("_token_id")},
            "stockArchitectureMetadata":{k:v for k,v in meta.items() if k.startswith(str(architecture)+".")},
            "stockTokenizerModel":meta.get("tokenizer.ggml.model"),
            "stockTokenizerMergesCount":len(meta.get("tokenizer.ggml.merges",[])),
            "r39TokenizerMergesCount":len(tokenizer.get("merges",[])),
            "stockChatTemplate":meta.get("tokenizer.chat_template"),
            "status":"DIRECT_LAYOUT_CANDIDATE" if not missing_stock and not extra_stock and not mismatch and token_match and architecture=="lfm2" else "ADAPTER_REQUIRED",
            "note":"Structural comparison only. Conversion requires byte-layout verification, logit parity, and accepted-overlay preservation."
        }
        args.output.write_text(json.dumps(report,indent=2,ensure_ascii=False,default=str)+"\n",encoding="utf-8")
        print(json.dumps({k:report[k] for k in ("status","architecture","r39TensorCount","stockTensorCount","r39TokenCount","stockTokenCount","tokenIdsExactlyEqual","tokenMismatchCount","firstTokenMismatches","mergeMismatchCount","firstMergeMismatches","missingInStock","extraInStock","shapeOrTypeMismatch")},ensure_ascii=False))
        print(f"Report: {args.output}")
    finally:model.close()

if __name__=="__main__":main()
