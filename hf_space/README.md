---
title: Swyrlz R39 Candidate
emoji: 🐉
sdk: gradio
app_file: app.py
pinned: false
---

# §wyrlz R39 isolated candidate

This is a migration candidate, not a claim of production Chat parity. The real R39 engine and its accepted overlays are staged from the canonical repository. The model is reconstructed on startup from 54 SHA-verified source chunks pinned to the exact source commit. A full clean-room Chat transport, account persistence, and queue migration require separate acceptance.

## Local image understanding for §wyrlz Chat (no paid inference API)

Chat's primary LALM remains text-only. **Image** uses a CPU-based local
`ggml-org/SmolVLM-256M-Instruct-GGUF` model, Q8_0 text weights and
matching multimodal projector, at pinned upstream revision
`b9e4379657e1450d04d02eec8e345667265b0a00` (Apache-2.0).
The existing `llama-cpp-python==0.3.35` runtime provides
`MTMDChatHandler`. Both GGUF files download from the public Hugging Face
model repository into the Space's nonpersistent cache the first time image
analysis is requested. The total download is approximately 279 MB, with
no external inference API or API key and no per-image provider fee.
CPU Basic hosting is $0/hour; usage may be slow on two vCPUs and free
Spaces sleep when inactive. Do not upgrade hardware for this feature.

No `SWRLZ_VISION_API_URL`, `SWRLZ_VISION_MODEL`, or
`SWRLZ_VISION_API_KEY` configuration is necessary. The self-hosted path
does not use these legacy external provider settings even if present.
Images are **not** sent to a paid or external inference endpoint. The
public GGUF weights themselves are downloaded from Hugging Face.

Only verified Google-chat sessions may call the image endpoint. The
browser compresses a selected JPEG/PNG/WebP image and sends it when
the user explicitly presses Send. The server caps incoming images at
2 MB decoded, rejects oversize pixel dimensions, resizes to 768px
on its longest edge, and runs only one CPU vision request at a time.
Only a short visual description reaches the existing text LALM;
pixels remain ephemeral and are never saved to thread history.
The selected image briefly appears in the browser preview and is
not restored when reopening a thread.

First-use model download or CPU inference may take a while on a free
Space. The dedicated endpoint fails closed rather than sending the
original chat request when visual inference fails. Model quality and
latency require real-device acceptance; mocked tests are not evidence
of successful live inference.

**Mic** uses a browser-supported SpeechRecognition implementation (where available).
Recognized partial/final words fill the ordinary editable text box; the user
must still explicitly send the message. Browser permissions, language support,
speech service availability, and HTTPS context determine whether dictation works.
In unsupported browsers, use the system keyboard's microphone instead.

Offline checks: `node tests/test_chat_media_v1.mjs` and
`python tests/test_chat_vision_v1.py`.
