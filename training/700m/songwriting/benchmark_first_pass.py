#!/usr/bin/env python3
"""Actual FIRST-PASS inference against untouched HF weights or a LoRA adapter.

Never supplies external lyric-craft policy, prior drafts, repair instructions,
a reference song, or a private history. Exactly one .generate() per test.
This benchmark is intentionally independent of the live Station/runtime.
"""
import argparse
import hashlib
import json
import re
import time
from pathlib import Path

PROMPT_SCHEMA = "swrlz-songwriting-benchmark-prompt-v1"
_SECTION = re.compile(r"(?i)^\s*(?:\[\s*)?(?:verse|chorus|hook|refrain|bridge|intro|outro|pre[- ]?chorus|cypher|performer|title)\b")
_CHORUS = re.compile(r"(?i)^\s*(?:\[\s*)?(?:chorus|hook|refrain)\b")


def load_prompts(path):
    rows = []
    ids = set()
    for num, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        count = row.get("expectedLines")
        if (row.get("schema") != PROMPT_SCHEMA or not isinstance(row.get("prompt"), str)
                or not row["prompt"].strip() or not isinstance(row.get("id"), str)
                or row["id"] in ids or (count is not None and (type(count) is not int or not 4 <= count <= 120))):
            raise ValueError(f"invalid prompt row {num}")
        ids.add(row["id"])
        rows.append(row)
    if not rows:
        raise ValueError("empty benchmark prompts")
    return rows


def inspect_form(text, row):
    """Necessary shape checks ONLY. These do not score cadence, rhyme or originality."""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    # Strip Markdown code fence markers without changing the captured raw output.
    lines = [l for l in lines if not l.startswith(chr(96) * 3)]
    lyric_lines = [l for l in lines if not _SECTION.match(l) and not l.startswith("#")]
    issues = []
    wanted = row.get("expectedLines")
    if wanted is not None and len(lyric_lines) != wanted:
        issues.append("line-count")
    if row.get("noChorus") and any(_CHORUS.match(line) for line in lines):
        issues.append("unexpected-chorus-section")
    if not lyric_lines:
        issues.append("empty")
    return {"observedLyricLines": len(lyric_lines), "formPass": not issues, "formIssues": issues,
            "semanticQualityReviewed": False}


def run(args):
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    tokenizer = AutoTokenizer.from_pretrained(args.base_model)
    model = AutoModelForCausalLM.from_pretrained(args.base_model, device_map="auto")
    if args.adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, args.adapter)
    model.eval()
    pad = tokenizer.pad_token_id or tokenizer.eos_token_id
    prompts = load_prompts(args.prompts)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as writer:
        for index, row in enumerate(prompts):
            torch.manual_seed(args.seed + index)
            encoded = tokenizer.apply_chat_template(
                [{"role": "user", "content": row["prompt"]}],
                add_generation_prompt=True, tokenize=True, return_tensors="pt"
            ).to(model.device)
            started = time.perf_counter()
            with torch.inference_mode():
                returned = model.generate(
                    encoded, max_new_tokens=args.max_new_tokens, do_sample=True,
                    temperature=args.temperature, min_p=args.min_p,
                    repetition_penalty=args.repetition_penalty, pad_token_id=pad
                )
            elapsed_ms = round(1000 * (time.perf_counter() - started), 2)
            completion_ids = returned[0, encoded.shape[-1]:]
            text = tokenizer.decode(completion_ids, skip_special_tokens=True)
            eos = tokenizer.eos_token_id
            eos_seen = eos is not None and eos in completion_ids.tolist()
            capped = len(completion_ids) >= args.max_new_tokens and not eos_seen
            result = {
                "schema": "swrlz-songwriting-first-pass-receipt-v1",
                "id": row["id"], "baseModel": args.base_model,
                "adapter": args.adapter or None, "prompt": row["prompt"],
                "promptSha256": hashlib.sha256(row["prompt"].encode()).hexdigest(),
                "seed": args.seed + index, "temperature": args.temperature,
                "minP": args.min_p, "repetitionPenalty": args.repetition_penalty,
                "maxNewTokens": args.max_new_tokens,
                "promptTokens": encoded.shape[-1], "completionTokens": len(completion_ids),
                "endedOnEos": eos_seen, "reachedTokenCap": capped,
                "durationMs": elapsed_ms, "rawText": text,
                "form": inspect_form(text, row),
                "generationAttempts": 1, "externalCraftPrefill": False,
                "retryOrContinuation": False
            }
            writer.write(json.dumps(result, ensure_ascii=False) + "\n")
            writer.flush()
            print(f"{row['id']}: {len(completion_ids)} tokens; form={result['form']['formPass']}; capped={capped}")
    print(f"Written {len(prompts)} one-pass receipts to {output}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-model", default="LiquidAI/LFM2-700M")
    parser.add_argument("--adapter", default=None, help="Locally verified LoRA adapter path; no publication")
    parser.add_argument("--prompts", default=str(Path(__file__).with_name("prompts.jsonl")))
    parser.add_argument("--output", required=True, help="Local private benchmark receipts; NEVER commit model responses automatically")
    parser.add_argument("--max-new-tokens", type=int, default=2048)
    parser.add_argument("--temperature", type=float, default=0.3)
    parser.add_argument("--min-p", type=float, default=0.15)
    parser.add_argument("--repetition-penalty", type=float, default=1.05)
    parser.add_argument("--seed", type=int, default=700)
    args = parser.parse_args()
    if not 384 <= args.max_new_tokens <= 4096 or not 0 < args.temperature <= 2 or not 0 <= args.min_p < 1:
        parser.error("invalid decoding/budget parameters")
    run(args)


if __name__ == "__main__":
    main()
