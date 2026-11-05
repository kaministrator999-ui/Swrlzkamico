# 2026-11-05 — §C Vision Build-Time Preload v3

**Scope:** existing §wyrlz Chat Space `kamiloki/Swyrlz`; documentation and HF Space YAML preload only. This follows local free CPU vision release v2.

## Problem / owner observation
User captured the mobile §C composer with a selected multi-view reference image and persistent `Analyzing image…` status. The screenshot proves a request was in progress, but it does not identify whether the latency was model download, cold RAM initialization, or CPU inference.

## Implementation
- Set `hf_space/README.md` frontmatter `preload_from_hub` to **only** the exact two pinned local vision assets: `ggml-org/SmolVLM-256M-Instruct-GGUF` files `SmolVLM-256M-Instruct-Q8_0.gguf` and `mmproj-SmolVLM-256M-Instruct-Q8_0.gguf` at commit `b9e4379657e1450d04d02eec8e345667265b0a00`. Hugging Face Space build preloading puts the assets in the default Hub cache, removing first-user-download dependency when that cache is retained.
- Added a focused Python test confirming the Space preloader references the same immutable model revision and artifact file names as `hf_space/chat_vision.py`.
- Deliberately left model initialization on demand to avoid competing RAM/CPU load from existing 700M, Qwen Coder 7B, stock 350M, and R39 backend warmup. The first request may still perform CPU model loading and actual image generation.
- No paid provider, no new tokens, no GPU or hardware upgrade, no new persistent storage, no changes to text chat model, frontend image/microphone controls, Google account security, or §E Forge.

## Evidence
- [PR #376](https://github.com/kaministrator999-ui/Swrlzkamico/pull/376) merged to source branch `fix/chat-embed-mobile-composer-v1-20261103` as `cd31be9a2003799e0ffbb1678e177f6eead61952`.
- [HF Candidate Offline Validation #42100708024](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42100708024): image endpoint, model preload contract, and composer regression PASS; unrelated existing `hf_space/test_forge_modeling_lessons_v2.py` assertions cause full workflow FAIL. These are not masked or attributed to the build-preload change.
- Approved deployment request `main:.deploy/HF_SPACE_REQUEST.txt` commit `f58b413970a72d90963aad3907fc23371459535f`.
- [Guarded HF deploy workflow #42100856769](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42100856769) SUCCESS: package validation, R39/700M acceptance, rollback snapshot, Space publication and release checkpoint completed.
- **New Space source revision:** `bebf80279efc837b001546e303ff75aa4c505c51`.
- **Rollback Space revision:** `b308fc6eb8031fbebd5a7c277f1413786ff03478`.
- Runtime authorities: Repository Work `1.0.263`, Server Runtime `2.3.454`. Web Chat `1.5.171`, canonical local UI `1.1.22`, and existing model weights unchanged.

## Acceptance boundary
**DEPLOYED_UNVERIFIED**: the guarded workflow confirms upload/revision, not successful real CPU vision inference or a measured reduction of `Analyzing image…` time. Owner should refresh §C, upload a small test image, and inspect the result. If the request is still slow, investigate Space runtime logs/CPU queue, cold model RAM initialization, image encoder and generation separately; do not silently use paid hosting or inference.
