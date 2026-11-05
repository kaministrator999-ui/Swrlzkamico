# 2026-11-04 — §C Image Upload / Vision and Speech-to-Text Release

**Scope:** §wyrlz Chat/Hugging Face Space `kamiloki/Swyrlz` only. No §E engine deployment.

## User-visible changes
- **Image** opens a JPEG/PNG/WebP picker, preserves a local thumbnail until send, compresses the image and calls a separate authenticated vision API for a bounded visual description. This description is submitted through the existing LALM Station text-only queue alongside the user's question. Original image bytes are not saved in account chat history; local previews do not survive reloading an old conversation.
- **Mic** toggles browser SpeechRecognition and writes interim/final speech into the editable composer; the user explicitly chooses when to send. Unsupported browsers should use the native keyboard microphone.
- Existing authenticated conversation persistence, model IDs/weights, stream/stop controls and §E host bridge remain unchanged.

## Inference configuration / privacy
The image endpoint is **disabled unless** the Hugging Face Space is configured with server-only `SWRLZ_VISION_API_URL`, `SWRLZ_VISION_MODEL`, and `SWRLZ_VISION_API_KEY`. The configured URL must be HTTPS and offer OpenAI-compatible chat completions with image input. The selected image and question are sent to that external provider only on explicit Send. Google Chat identity is required; image size is restricted to 2 MB decoded on the server. The external provider's retention rules are separate. **Do not claim working image inference until credentials and live response are verified.** No credentials were added or exposed in this repository update.

## GitHub / validation / deploy receipts
- Release-source branch: `fix/chat-embed-mobile-composer-v1-20261103`; source base `d7e4bfb854f6be63cfdf9a66cb663bec99fcc687`.
- [PR #374](https://github.com/kaministrator999-ui/Swrlzkamico/pull/374) merged as `adcab6555d7e6f9ba284ca072d073682ccd30f41`.
- Chat surface file local version: `1.1.22`.
- Offline checks `tests/test_chat_vision_v1.py` and `tests/test_chat_media_v1.mjs` passed in HF candidate CI run `41962013212`. Exact-source native embedded-composer CI run `41962369900` passed. Existing Chat Android/desktop widget, stream, scroll, and file flow workflows passed. Independent legacy modeling-lesson expectation assertions and older lyric-reader exact-string assertion remain red; unrelated to this patch and not masked.
- Canonical guarded [Chat-only deployment workflow #41962451298](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/41962451298) **SUCCESS**. Existing Space target `kamiloki/Swyrlz` published exact source with revision `d8fb9d12a7c41303b26b189d367d907947097c00`. Prior Space revision `6f8b3ff8191fe4d4d57678955fb1ffd9eb9afc61` retained as rollback; immutable checkpoint artifact captured. This proves upload, **not** active provider inference, browser speech support or user-device behavior.
- Version authorities updated on `runtime`: Repository Work `1.0.261`, Web Chat `1.5.171`, Server Runtime `2.3.452`; model/§E versions unchanged.

**Verification state:** `DEPLOYED_UNVERIFIED`; awaiting real Google Chat account/browser image service configuration and device testing.
