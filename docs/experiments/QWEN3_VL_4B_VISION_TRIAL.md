# Qwen3-VL-4B Image-Analysis Trial (isolated experiment)

Status: **source and CI trial prepared; live inference and deployment NOT verified**.
Baseline: `fix/chat-vision-complete-crop-observations-20261106`.
This branch adds an isolated Qwen local backend, pinned weights/build dependencies and regression checks; it has NOT deployed to `kamiloki/Swyrlz`.

## Motivation

Compare a stronger vision-language model against the current SmolVLM-500M CPU image analyzer for *one user-uploaded image*: visible anatomy, spatial relations, occlusion, silhouette, materials versus geometry, and evidence-gated uncertainty. Original image pixels are still preserved in request memory and all derived views come from those source bytes. No external paid inference API is introduced.

## Configuration

Default: `SWRLZ_VISION_MODEL=smolvlm-500m` (unchanged).
Experimental: `SWRLZ_VISION_MODEL=qwen3-vl-4b` (opt in, separate test runtime only).

Pinned Qwen model:
- `Qwen/Qwen3-VL-4B-Instruct-GGUF`, revision `1cd86afb9a95c410a6038ab3b40d8b578c892266`
- `Qwen3VL-4B-Instruct-Q4_K_M.gguf` (~2.5 GB)
- `mmproj-Qwen3VL-4B-Instruct-Q8_0.gguf` (~454 MB)
- 768px first whole-image view, max 224 new tokens; model and projector are loaded by a separate official llama.cpp loopback server.

**Runtime separation:** Production still pins `llama-cpp-python==0.3.35`, which lacks a Qwen3-VL-specific handler. Instead of replacing the shared wheel, this trial builds official `ggml-org/llama.cpp` from commit `fd27b2034905f8dadd8bd6d2cc44595f4929d391`, starts `llama-server` bound to `127.0.0.1`, and adapts its OpenAI-compatible SSE results to the existing chat analyzer. Cold compilation/model startup and CPU performance are **not yet runtime-verified**; they must be inspected before claiming the trial is ready.

## Trial acceptance

1. Run the existing CPU vision tests and the new `tests/test_chat_vision_qwen3_vl_experiment.py` in an isolated environment. These are **mocked and source-level** checks, not evidence of model accuracy.
2. On a runtime with verified Qwen3-VL GGUF support, run actual original-image samples for SmolVLM and Qwen, capturing model revision, input size, first-token latency, full latency, exact response and any failure/cancellation. A successful model constructor alone is not proof of image understanding.
3. Compare observations on the *same images*: subject identity, piece counts, left-right orientation, relative depth/occlusion, contour details, real mesh geometry vs shading/material texture, confidence calibration, source-region correctness, and whether irrelevant details were invented.
4. If Qwen cannot meet resource or latency constraints, retain SmolVLM as the live default and record the measured reason instead of deploying an unverified switch.
5. Live deployment requires the existing guarded HF release process and real-device acceptance, not merely source changes.

The existing chat route and image-data privacy boundary are preserved. No model weights, user images, or API tokens should be committed to Git.
