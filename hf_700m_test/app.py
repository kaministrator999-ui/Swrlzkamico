"""Standalone §wyrlz 700M native GGUF trial. No R39 or production Space dependency."""
import json, threading, time
import gradio as gr
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

REPO="LiquidAI/LFM2-700M-GGUF"
FILE="LFM2-700M-Q4_K_M.gguf"
_lock=threading.RLock()
_model=None

def load():
    global _model
    with _lock:
        if _model is None:
            path=hf_hub_download(repo_id=REPO,filename=FILE)
            _model=Llama(model_path=path,n_ctx=1024,n_threads=4,n_threads_batch=4,n_batch=128,n_gpu_layers=0,use_mmap=True,verbose=False)
        return _model

def reply(message,history):
    start=time.perf_counter()
    model=load()
    load_ms=(time.perf_counter()-start)*1000
    messages=[]
    for item in (history or [])[-16:]:
        if isinstance(item,dict) and item.get("role") in ("user","assistant") and isinstance(item.get("content"),str):
            messages.append({"role":item["role"],"content":item["content"]})
    messages.append({"role":"user","content":message})
    first=None;out=""
    with _lock:
        for chunk in model.create_chat_completion(messages=messages,max_tokens=128,temperature=0.3,stream=True):
            delta=(chunk.get("choices") or [{}])[0].get("delta",{}).get("content")
            if delta:
                if first is None:first=(time.perf_counter()-start)*1000
                out+=delta
                yield out
    print(json.dumps({"model":"lfm2-700m-q4_k_m","loadLatencyMs":round(load_ms,3),"firstDeltaLatencyMs":round(first,3) if first else None,"totalLatencyMs":round((time.perf_counter()-start)*1000,3),"responseChars":len(out)}),flush=True)

def probe(prompt):
    start=time.perf_counter();model=load();loaded=time.perf_counter()
    first=None;out="";deltas=0
    with _lock:
        for chunk in model.create_chat_completion(messages=[{"role":"user","content":prompt}],max_tokens=128,temperature=0.3,stream=True):
            delta=(chunk.get("choices") or [{}])[0].get("delta",{}).get("content")
            if delta:
                if first is None:first=(time.perf_counter()-start)*1000
                out+=delta;deltas+=1
    return json.dumps({"phase":"COMPLETE","model":"lfm2-700m-q4_k_m","loadLatencyMs":round((loaded-start)*1000,3),"timeToFirstDeltaSeconds":round(first/1000,3) if first else None,"elapsedSeconds":round(time.perf_counter()-start,3),"deltaCount":deltas,"responseChars":len(out),"response":out},indent=2)

with gr.Blocks(title="§wyrlz 700M GGUF Test Bench") as demo:
    gr.Markdown("# 🐉 §wyrlz 700M GGUF Test Bench\nNative llama.cpp test of untouched LFM2-700M Q4_K_M. Separate from production and R39.")
    gr.ChatInterface(fn=reply,type="messages")
    with gr.Accordion("Latency probe",open=True):
        p=gr.Textbox(value="What's your name?",label="Probe prompt")
        b=gr.Button("Run latency probe")
        result=gr.Code(label="Probe metrics",language="json")
        b.click(probe,p,result)
if __name__=="__main__":
    demo.launch()
