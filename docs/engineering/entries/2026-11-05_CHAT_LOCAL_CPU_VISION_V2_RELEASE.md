# 2026-11-05 — §C Free Self-Hosted Local CPU Vision Release

**Scope:** §wyrlz Chat Hugging Face Space `kamiloki/Swyrlz` only. This release supersedes the optional metered-provider requirement documented in the 2026-11-04 Chat media v1 release. No changes to §E Forge, chat/§wyrlz UI or microphone, Google login/session mechanics, existing model weights, or text LALM orchestration.

## Owner requirement

Provide image understanding without per-image paid inference, private paid-provider credentials, new Space creation, or paid hardware. Use existing HF CPU Basic resources ($0/hour compute tier) and preserve the existing text-only LALM chat and Image button.

## Implementation

- Replaced external OpenAI-compatible image-analysis provider with local `ggml-org/SmolVLM-256M-Instruct-GGUF` Q8_0 GGUF plus matching mmproj, pinned at revision `b9e4379657e1450d04d02eec8e345667265b0a00`.
- The already pinned `llama-cpp-python==0.3.35` provides `MTMDChatHandler`, CPU execution with two threads and no GPU layers; added Pillow as the only new runtime dependency.
- Fetch public model weights via `hf_hub_download` on first image request into Space-local cache (~279 MB total); no API key, hosted inference provider, per-image fee, or provider environment variables required.
- Google-account-gated `POST /api/lalm_station/vision`; accept JPEG/PNG/WebP ≤2 MB decoded, source dimensions ≤16M pixels, downscale to ≤768px, one concurrent CPU image task, response capped at 112 generated tokens / 6,000 characters. The upload pixels are not saved in persisted Chat conversations and are not relayed to a third-party vision API. Only returned visual text is given to existing text LALM.
- Source image and question are held in request process memory; original pixels do not survive the chat reload; independent username/chat sessions continue unaffected.

## Source / CI / deployment receipts

- [PR #375](https://github.com/kaministrator999-ui/Swrlzkamico/pull/375), merged to real canonical HF-source branch `fix/chat-embed-mobile-composer-v1-20261103` via squash commit `28c07377f36cd342a556ae320a18ac774df7ad6b`.
- HF Candidate Offline Validation [run #42083677552](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42083677552): focused Python local vision + JS composer/media checks PASS and backend compiles. Overall workflow FAILS on four old unrelated `hf_space/test_forge_modeling_lessons_v2.py` §E rig/lesson expectations; these files were unchanged. No spurious clean CI claim.
- Canonical guarded HF request commit `b2029b17353308a0611a9450830d6347ceae1a73` published exact tested source ref. [Deploy workflow #42084116670](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42084116670) SUCCESS: source staging, R39 and 700M acceptance, prior Space snapshot, upload and immutable release checkpoint all passed.
- **New HF Space revision:** `b308fc6eb8031fbebd5a7c277f1413786ff03478`.
- **Rollback Space revision:** `d8fb9d12a7c41303b26b189d367d907947097c00`.
- Runtime authority version updates: Repository Work `1.0.262`, Server Runtime `2.3.453`. Web Chat runtime `1.5.171` and canonical UI local `1.1.22` remain unchanged.

## Verification truth / next acceptance

**DEPLOYED_UNVERIFIED:** guarded upload and HF repository revision were observed, but not an authenticated live image inference. First image request must download public model weights (~279MB) to a nonpersistent cache; latency, available memory, image understanding quality and potential HF request timeout on free CPU are still unverified and may be limited. The user will test by opening §C on their Moto, signing in, tapping Image, choosing a small photo, and asking what it contains. If it fails, report the exact failure without silently switching to a paid provider or hardware upgrade. The model download is from the public Hugging Face Hub, not a paid inference provider.
