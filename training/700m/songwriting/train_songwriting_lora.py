#!/usr/bin/env python3
"""LoRA candidate trainer for independently reviewed ORIGINAL songwriting.

Loads full-precision LiquidAI/LFM2-700M; never trains directly on GGUF.
Does not publish, merge, quantize, or change a production model reference.
"""
import argparse
import hashlib
import json
from pathlib import Path

from corpus import load_reviewed_corpus, split_corpus, corpus_receipt


def prepare_example(tokenizer, record, max_length):
    user = [{"role": "user", "content": record["prompt"]}]
    full = user + [{"role": "assistant", "content": record["completion"]}]
    # Mask all system/user/prompt tokens; only the accepted target contributes
    # to the gradient. Respect the original LFM2 tokenizer's chat template.
    prefix = tokenizer.apply_chat_template(user, tokenize=True, add_generation_prompt=True)
    content = tokenizer.apply_chat_template(full, tokenize=True, add_generation_prompt=False)
    if content[:len(prefix)] != prefix:
        raise ValueError(f"{record.get('id', 'record')}: chat-template completion boundary not aligned")
    if len(content) > max_length:
        raise ValueError(f"{record.get('id', 'record')}: {len(content)} tokens exceed {max_length}; no silent truncation")
    labels = [-100] * len(prefix) + content[len(prefix):]
    if not any(token != -100 for token in labels):
        raise ValueError("empty assistant loss mask")
    return {"input_ids": content, "attention_mask": [1] * len(content), "labels": labels}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, help="Private independently reviewed JSONL")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--base-model", default="LiquidAI/LFM2-700M")
    parser.add_argument("--dry-run", action="store_true", help="Validate corpus without loading model or using GPU")
    parser.add_argument("--rank", type=int, default=16)
    parser.add_argument("--alpha", type=int, default=32)
    parser.add_argument("--epochs", type=float, default=2.0)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--max-length", type=int, default=4096)
    parser.add_argument("--seed", type=int, default=700)
    args = parser.parse_args()
    if args.rank < 1 or args.alpha < 1 or args.epochs <= 0 or args.lr <= 0 or args.max_length < 512:
        parser.error("invalid training hyperparameters")
    records = load_reviewed_corpus(args.dataset)
    train, holdout = split_corpus(records)
    receipt = corpus_receipt(records)
    print(json.dumps(receipt, indent=2))
    if args.dry_run:
        return
    if len(train) < 32 or len(holdout) < 8:
        raise ValueError("weight training requires >=32 independently approved train records AND >=8 separate holdouts")
    if args.base_model != "LiquidAI/LFM2-700M":
        raise ValueError("first candidate is pinned to LiquidAI/LFM2-700M full-precision weights")
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments, DataCollatorForSeq2Seq
    from peft import LoraConfig, get_peft_model
    if not torch.cuda.is_available():
        raise RuntimeError("No CUDA device available; candidate training was not started")
    tokenizer = AutoTokenizer.from_pretrained(args.base_model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    features = [prepare_example(tokenizer, row, args.max_length) for row in train]

    class LocalTrainingDataset(torch.utils.data.Dataset):
        def __len__(self):
            return len(features)
        def __getitem__(self, index):
            return features[index]

    bf16 = torch.cuda.is_bf16_supported()
    model = AutoModelForCausalLM.from_pretrained(
        args.base_model, torch_dtype=torch.bfloat16 if bf16 else torch.float16
    )
    model.config.use_cache = False
    model = get_peft_model(model, LoraConfig(
        r=args.rank, lora_alpha=args.alpha, lora_dropout=0.05,
        bias="none", task_type="CAUSAL_LM", target_modules="all-linear"
    ))
    config = TrainingArguments(
        output_dir=args.output_dir, num_train_epochs=args.epochs,
        learning_rate=args.lr, per_device_train_batch_size=1,
        gradient_accumulation_steps=8, seed=args.seed,
        bf16=bf16, fp16=not bf16, save_strategy="no",
        logging_steps=5, report_to="none", remove_unused_columns=False
    )
    trainer = Trainer(
        model=model, args=config, train_dataset=LocalTrainingDataset(),
        data_collator=DataCollatorForSeq2Seq(
            tokenizer=tokenizer, model=model, padding=True, label_pad_token_id=-100
        ), processing_class=tokenizer
    )
    trainer.train()
    destination = Path(args.output_dir)
    destination.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(destination)
    tokenizer.save_pretrained(destination)
    digest = hashlib.sha256(Path(args.dataset).read_bytes()).hexdigest()
    (destination / "swrlz-songwriting-training-receipt.json").write_text(
        json.dumps({"schema": "swrlz-songwriting-training-receipt-v1",
                    "baseModel": args.base_model, "trainingDatasetSha256": digest,
                    "trainExamples": len(train), "heldOutExamples": len(holdout),
                    "rank": args.rank, "alpha": args.alpha,
                    "epochs": args.epochs, "learningRate": args.lr,
                    "productionPromoted": False}, indent=2) + "\n",
        encoding="utf-8"
    )


if __name__ == "__main__":
    main()
