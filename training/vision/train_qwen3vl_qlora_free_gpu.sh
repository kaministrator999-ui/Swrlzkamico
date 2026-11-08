#!/usr/bin/env bash
# Manual-only: training never starts automatically; never invokes paid Jobs.
set -euo pipefail

if [ "$SWRLZ_FREE_GPU_APPROVED" != "yes" ]; then
  echo "Set SWRLZ_FREE_GPU_APPROVED=yes ONLY on a verified no-charge local/free GPU runtime." >&2
  exit 2
fi
if [ -z "$SWRLZ_VISION_DATA" ] || [ -z "$SWRLZ_VISION_OUTPUT" ]; then
  echo "Provide SWRLZ_VISION_DATA (private prepared data) and SWRLZ_VISION_OUTPUT (private output)." >&2
  exit 2
fi
test -s "$SWRLZ_VISION_DATA/train.jsonl" || { echo "Verified train.jsonl missing" >&2; exit 2; }
test -s "$SWRLZ_VISION_DATA/val.jsonl" || { echo "Held-out val.jsonl missing" >&2; exit 2; }
test -s "$SWRLZ_VISION_DATA/test.jsonl" || { echo "Untouched test.jsonl missing" >&2; exit 2; }
test -s "$SWRLZ_VISION_DATA/preflight-summary.json" || { echo "Dataset preflight summary missing" >&2; exit 2; }
command -v nvidia-smi >/dev/null || { echo "CUDA GPU required for this baseline" >&2; exit 2; }
command -v swift >/dev/null || { echo "Install compatible ms-swift and bitsandbytes dependencies on the GPU runtime" >&2; exit 2; }
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

# Baseline 4-bit QLoRA. Intended for a free GPU if available; not guaranteed
# to fit a 16 GB T4, especially with high-resolution multimodal inputs.
# Starting point is ORIGINAL safetensors model, not inference Q4_K_M GGUF.
# No pushes to Hub, no GH Actions, no automatic publication, no paid API.
export IMAGE_MAX_TOKEN_NUM=512

swift sft \
  --model Qwen/Qwen3-VL-4B-Instruct \
  --use_hf true \
  --dataset "$SWRLZ_VISION_DATA/train.jsonl" \
  --val_dataset "$SWRLZ_VISION_DATA/val.jsonl" \
  --tuner_type lora \
  --quant_method bnb \
  --quant_bits 4 \
  --bnb_4bit_compute_dtype float16 \
  --torch_dtype float16 \
  --lora_rank 8 \
  --lora_alpha 32 \
  --target_modules all-linear \
  --freeze_vit true \
  --freeze_aligner true \
  --gradient_checkpointing true \
  --per_device_train_batch_size 1 \
  --per_device_eval_batch_size 1 \
  --gradient_accumulation_steps 4 \
  --num_train_epochs 1 \
  --learning_rate 1e-4 \
  --max_length 2048 \
  --logging_steps 5 \
  --save_steps 50 \
  --eval_steps 50 \
  --save_total_limit 2 \
  --output_dir "$SWRLZ_VISION_OUTPUT"

echo "Adapter created locally. Do not deploy or merge weights before held-out testing."
