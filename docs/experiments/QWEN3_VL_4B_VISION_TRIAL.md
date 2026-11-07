# Qwen3-VL-4B Image-Analysis Trial (isolated experiment)

Status: **source prepared, offline validation not yet executed; live inference NOT verified**.
Baseline: `fix/chat-vision-complete-crop-observations-20261106`.
This branch changes only the optional vision model and its targeted tests; it does not deploy to `kamiloki/Swyrlz`.

## Motivation

Compare a stronger vision-language model against the current SmolVLM-500M CPU image analyzer for *one user-uploaded image*: visible anatomy, spatial relations, occlusion, silhouette, materials versus geometry, and evidence-gated uncertainty. Original image pixels are still preserved in request memory and all derived views come from those source bytes. No external paid inference API is introduced.

## Configuration

Default: `SWRLZ_VISION_MODEL=smolvlm-500m` (unchanged).
Experimental: `SWRLZ_VISION_MODEL=qwen3-vl-4b` (opt in, separate test runtime only).

Pinned Qwen model:
- `Qwen/Qwen3-VL-4B-Instruct-GGUF`, revision `1cd86afb9a95c410a6038ab3b40d8b578c892266`
- `Qwen3VL-4B-Instruct-Q4_K_M.gguf` (~2.5 GB)
- `mmproj-Qwen3VL-4B-Instruct-Q8_0.gguf` (~454 MB)
- 768px first whole-image view, max 224 new tokens, Qwen3-VL-specific handler with at least 1024 image tokens and no thinking output.

**Blocking dependency:** the current production `llama-cpp-python==0.3.35` runtime does not expose the required `Qwen3VLChatHandler`. The experimental loader checks for a compatible handler *before downloading weights*. Do not flip this flag in the live Space or silently replace its production dependency. Validate a trusted Qwen3-VL-capable llama.cpp binding in an isolated environment first; then check the CPU and RAM footprint, initialization, genuine first image prefill, completion and cancellation.

## Trial acceptance

1. Run the existing CPU vision tests and the new `tests/test_chat_vision_qwen3_vl_experiment.py` in an isolated environment. These are **mocked and source-level** checks, not evidence of model accuracy.
2. On a runtime with verified Qwen3-VL GGUF support, run actual original-image samples for SmolVLM and Qwen, capturing model revision, input size, first-token latency, full latency, exact response and any failure/cancellation. A successful model constructor alone is not proof of image understanding.
3. Compare observations on the *same images*: subject identity, piece counts, left-right orientation, relative depth/occlusion, contour details, real mesh geometry vs shading/material texture, confidence calibration, source-region correctness, and whether irrelevant details were invented.
4. If Qwen cannot meet resource or latency constraints, retain SmolVLM as the live default and record the measured reason instead of deploying an unverified switch.
5. Live deployment requires the existing guarded HF release process and real-device acceptance, not merely source changes.

The existing chat route and image-data privacy boundary are preserved. No model weights, user images, or API tokens should be committed to Git.
