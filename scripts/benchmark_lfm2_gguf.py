"""Fair CPU llama.cpp comparison of stock LFM2-350M and LFM2-700M GGUF.
Does not touch R39 or publish a Hugging Face Space.
"""
from __future__ import annotations
import argparse, gc, hashlib, json, statistics, time
from pathlib import Path
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

MODELS=(
    ("350m","LiquidAI/LFM2-350M-GGUF","LFM2-350M-Q4_K_M.gguf","31cd51db1365",None),
    ("700m","LiquidAI/LFM2-700M-GGUF","LFM2-700M-Q4_K_M.gguf","155d118","684e8406dc13321452b3f6aeca432776e2a6a7e1ad6c23f7887b8fe3efbe2efa"),
)
PROMPTS=("What's your name?","Explain what a GGUF model is in one sentence.","Write a friendly two-sentence greeting.")

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
    return h.hexdigest()

def trial(model,prompt):
    start=time.perf_counter(); first=None; pieces=[]; chunks=0
    for chunk in model.create_chat_completion(messages=[{"role":"user","content":prompt}],max_tokens=128,temperature=0.3,stream=True):
        choice=(chunk.get("choices") or [{}])[0]
        delta=(choice.get("delta") or {}).get("content")
        if delta:
            if first is None:first=(time.perf_counter()-start)*1000
            pieces.append(delta);chunks+=1
    return {"prompt":prompt,"firstDeltaMs":round(first,3) if first is not None else None,
            "totalMs":round((time.perf_counter()-start)*1000,3),"deltaCount":chunks,
            "responseChars":len("".join(pieces)),"response":"".join(pieces)[:500]}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,default=Path("lfm2-350m-vs-700m.json"))
    args=ap.parse_args()
    results={"schema":"swrlz-lfm2-gguf-benchmark-v1","settings":{"n_ctx":1024,"n_threads":4,"n_threads_batch":4,"n_batch":128,"n_gpu_layers":0,"use_mmap":True,"max_tokens":128,"temperature":0.3},"models":[]}
    for label,repo,filename,revision,expected_sha in MODELS:
        path=Path(hf_hub_download(repo_id=repo,filename=filename,revision=revision))
        digest=sha(path)
        if expected_sha and digest!=expected_sha:raise ValueError(f"{label} SHA mismatch: {digest}")
        start=time.perf_counter()
        model=Llama(model_path=str(path),n_ctx=1024,n_threads=4,n_threads_batch=4,n_batch=128,n_gpu_layers=0,use_mmap=True,verbose=False)
        load_ms=round((time.perf_counter()-start)*1000,3)
        # Warm the model before measuring the same three prompts.
        warmup=trial(model,"Hello.")
        trials=[trial(model,p) for p in PROMPTS]
        entry={"model":label,"repo":repo,"filename":filename,"revision":revision,"sha256":digest,"bytes":path.stat().st_size,"loadMs":load_ms,"warmup":warmup,"trials":trials,"medianTotalMs":round(statistics.median(t["totalMs"] for t in trials),3),"medianFirstDeltaMs":round(statistics.median(t["firstDeltaMs"] for t in trials if t["firstDeltaMs"] is not None),3)}
        results["models"].append(entry)
        print(json.dumps(entry,ensure_ascii=False),flush=True)
        del model;gc.collect()
    args.output.write_text(json.dumps(results,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(f"BENCHMARK_REPORT={args.output}",flush=True)
if __name__=="__main__":main()
