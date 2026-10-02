#!/usr/bin/env python3
"""Train a governed LoRA adapter for the 700M student from validated JSONL only."""
import argparse, json
from pathlib import Path

def load_validated(path):
    rows=[]
    for n,line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(),1):
        if not line.strip(): continue
        row=json.loads(line)
        ev=row.get("evaluator") or {}
        if row.get("schema")!="swrlz-700m-training-example-v1" or ev.get("result")!="PASS":
            raise ValueError(f"line {n}: example is not independently validated")
        if not row.get("originalRequest") or not row.get("correctedTarget"):
            raise ValueError(f"line {n}: missing request/target")
        rows.append({"text":f"<|user|>\n{row['originalRequest']}\n<|assistant|>\n{row['correctedTarget']}"})
    if not rows: raise ValueError("validated corpus is empty")
    return rows

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--base-model",required=True)
    ap.add_argument("--dataset",required=True)
    ap.add_argument("--output-dir",required=True)
    ap.add_argument("--rank",type=int,default=16)
    ap.add_argument("--alpha",type=int,default=32)
    ap.add_argument("--epochs",type=float,default=2.0)
    ap.add_argument("--lr",type=float,default=2e-4)
    args=ap.parse_args()
    from datasets import Dataset
    from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
    from peft import LoraConfig
    from trl import SFTTrainer
    rows=load_validated(args.dataset)
    ds=Dataset.from_list(rows)
    tok=AutoTokenizer.from_pretrained(args.base_model,trust_remote_code=True)
    model=AutoModelForCausalLM.from_pretrained(args.base_model,trust_remote_code=True)
    cfg=LoraConfig(r=args.rank,lora_alpha=args.alpha,lora_dropout=0.05,bias="none",task_type="CAUSAL_LM",target_modules="all-linear")
    ta=TrainingArguments(output_dir=args.output_dir,num_train_epochs=args.epochs,learning_rate=args.lr,per_device_train_batch_size=1,gradient_accumulation_steps=8,logging_steps=5,save_strategy="epoch",report_to=[])
    trainer=SFTTrainer(model=model,train_dataset=ds,peft_config=cfg,args=ta,processing_class=tok,dataset_text_field="text")
    trainer.train()
    trainer.model.save_pretrained(args.output_dir)
    tok.save_pretrained(args.output_dir)
    Path(args.output_dir,"swrlz-training-receipt.json").write_text(json.dumps({"baseModel":args.base_model,"examples":len(rows),"rank":args.rank,"alpha":args.alpha,"epochs":args.epochs,"learningRate":args.lr},indent=2),encoding="utf-8")

if __name__=="__main__": main()
