# §C vision model training: $0 only

**Hard constraint: no paid compute, no credits, no subscription upgrade, no automatic GPU job, no automatic production deployment.**

## What is actually possible

LoRA/QLoRA changes **learned adapter weights** for the original Qwen/Qwen3-VL-4B-Instruct model. Our currently deployed Q4_K_M GGUF is an **inference** artifact; train from the original Hugging Face safetensors model instead.

Preparing verified data and writing training/evaluation code is free. Actual training requires a compatible GPU. Free Google Colab may provide a T4 (availability and quotas vary), but a 4B vision-language training run may not fit its 16 GB VRAM. We cannot promise training completion at $0. Do not use Hugging Face Jobs: they are billed by the minute, even when a free CPU Space is available.

The initial manual script tries 4-bit QLoRA with frozen vision encoder and aligner. This can improve output behavior and learned association with image features, but it does not directly train the vision encoder. Visual localization errors may require a separate adapter strategy.

## Ground truth (keep private)

Do not train on old inaccurate analyzer reports. Each image needs an actual human-reviewed **gold answer** describing the visible pixels (not hidden geometry), object interactions, uncertain handedness, view-by-view differences, and surface vs shape.

Keep all images, gold annotations and model adapters **outside the GitHub repository**. Annotation JSONL fields:

- id: unique example identifier
- character_id: stable identity across all angles/crops of one character
- split: train or val or test
- image: relative file path beneath the private image root
- question: e.g. What do you see in this image?
- human_verified: must be true
- gold_answer: inspected factual answer, 40-6000 characters

Create at least three distinct training characters plus a validation and a held-out test character for a tiny pipeline pilot. A real accuracy improvement needs substantially more independently verified diverse subjects. Keep one character, including all variants/angles, in one split only; don't train on test characters.

## Prepare (no GPU required)

python training/vision/prepare_qwen3vl_sft.py --annotations /private/annotations.jsonl --image-root /private/images --output /private/prepared

This checks file magic, image size, annotation format, source verification flag, character leakage and exact-image hash leakage. It writes ms-swift-compatible image+conversation JSONL plus a preflight summary.

## Optional manual training on a VERIFIED free GPU

Training is never launched automatically. Only if a CUDA GPU is genuinely available free of charge, install compatible ms-swift and bitsandbytes packages in the free runtime, set:

SWRLZ_VISION_DATA=/private/prepared
SWRLZ_VISION_OUTPUT=/private/adapter
SWRLZ_FREE_GPU_APPROVED=yes

Then manually run:

bash training/vision/train_qwen3vl_qlora_free_gpu.sh

The GPU script has a gating variable, checks required files and CUDA, trains one epoch and saves adapters locally. It does not call paid Jobs, upload model weights or deploy to HF Spaces. Free T4 memory may still be insufficient. A training failure is not permission to pay.

## Hold-out evaluation

Before promoting any adapter compare **base vs adapted** output under the same source image/question/preprocessing/decoding settings. Score objectively reviewed: coverage, object identity, view consistency, proportions, hand-to-prop contact, visibility limits, unsupported topology claims, repetition, and stability across several fresh submissions. Compare on unseen characters, not only Little Crystal Mage.

Retain the original GGUF for rollback. Merge/export/re-quantize and deploy only after independently verified quality improvement and an explicit user decision.

## Official documentation

- ms-swift Qwen3-VL: https://github.com/modelscope/ms-swift/tree/main/examples/models/qwen3_vl
- ms-swift custom multimodal data: https://swift.readthedocs.io/en/latest/Customization/Custom-dataset.html
- Google Colab FAQ: https://research.google.com/colaboratory/faq.html
- Hugging Face Jobs billing: https://huggingface.co/docs/hub/jobs-pricing
