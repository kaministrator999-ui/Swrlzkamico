# Qwen3-VL-4B Image Analysis — Qwen-only production route

## Current implementation and evidence

Qwen3-VL-4B is the **only image-analysis model** in this source branch.
The earlier SmolVLM model selector, runtime branch and model-weight
build preload were removed. The older `SWRLZ_VISION_MODEL` Space variable
has no effect on the chosen model. This does **not** remove or replace
separate text-only §wyrlz LALM models.

Pinned model: `Qwen/Qwen3-VL-4B-Instruct-GGUF`
revision `1cd86afb9a95c410a6038ab3b40d8b578c892266`;
model file `Qwen3VL-4B-Instruct-Q4_K_M.gguf`,
projector `mmproj-Qwen3VL-4B-Instruct-Q8_0.gguf`.

Qwen runs in an isolated local `llama-server` with official
`ggml-org/llama.cpp` commit
`fd27b2034905f8dadd8bd6d2cc44595f4929d391`.
No external inference endpoint handles private uploaded image pixels.
The original image stays in transient server request memory and is
resized/cropped there. The Space startup worker prewarms the model once
per server process. Subsequent image analysis jobs reuse that model
instance unless the runtime or child process restarts.

## Whole-image + crops, then coherent synthesis

For qualifying wide character sheets, the SAME Qwen3-VL model runs:

1. Whole-image overview at up to 768px, with 224 output tokens.
2. Four overlapping crops of original full-resolution figure regions,
   each labeled with its actual source region.
3. A final 768px whole-image pass with the overview caption and
   accumulated unverified crop observations, up to 256 tokens.

The final synthesis receives actual image pixels rather than only text.
It leads the answer when it supplies concrete visible detail; four verbose
crop captions do not automatically outrank it by keyword count.
Raw crop descriptions remain inspectable for provenance, and vague
synthesis does not overwrite stronger evidence. Simple uploads with no
qualifying regions still run one fast whole-image pass. All observations
remain fallible model-generated text, not human-verified ground truth.

## Verification boundaries

The user has reported a successful near-instant description of a
character turnaround after Qwen3 was deployed. This is user-observed
response behavior, not a benchmark or a verified visual accuracy score.

Targeted offline/contract tests cover the one-model selector, image
preparation, real pixel crops, integration-pass input pixels and
response selection. They are not a substitute for real-device quality
and actual full-model inference measurements. The separate preexisting
§E lesson-source test mismatch should not be described as a Qwen
inference failure.

Historical trial plans to keep SmolVLM as fallback have been superseded.
Release through the snapshot/rollback-protected manual HF workflow;
verify Space runtime and user-visible image output after publication.
