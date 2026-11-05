---
title: Swyrlz R39 Candidate
emoji: 🐉
sdk: gradio
app_file: app.py
pinned: false
---

# §wyrlz R39 isolated candidate

This is a migration candidate, not a claim of production Chat parity. The real R39 engine and its accepted overlays are staged from the canonical repository. The model is reconstructed on startup from 54 SHA-verified source chunks pinned to the exact source commit. A full clean-room Chat transport, account persistence, and queue migration require separate acceptance.

## Optional image understanding for §wyrlz Chat

Chat's primary LALM is text-only. The **Image** attachment control can analyze a
JPEG, PNG, or WebP using a separately configured, vision-capable OpenAI-compatible
Chat Completions provider. Set these **server-side Space secrets** (never expose them
in JavaScript or check a real key into GitHub):

- `SWRLZ_VISION_API_URL`: full HTTPS Chat Completions endpoint URL.
- `SWRLZ_VISION_MODEL`: a vision-capable model ID that the endpoint serves.
- `SWRLZ_VISION_API_KEY`: bearer key with access to that endpoint.

The button fails closed with a clear unavailable message if the provider is not
configured. Only verified Google-chat sessions can use this server endpoint.
The browser scales/compresses a user-selected image and sends it only when Send
is clicked. The endpoint imposes a 2 MB decoded image cap, never puts the source
pixels in account snapshots or the LALM queue, and returns a short description
that the text LALM can reason over. The selected image is briefly previewed in
the browser; original pixels are **not restored** when reopening a thread.
The external vision provider *does receive the image*, and its privacy/retention
policy is independent of §wyrlz Chat.

**Mic** uses a browser-supported SpeechRecognition implementation (where available).
Recognized partial/final words fill the ordinary editable text box; the user
must still explicitly send the message. Browser permissions, language support,
speech service availability, and HTTPS context determine whether dictation works.
In unsupported browsers, use the system keyboard's microphone instead.

Offline checks: `node tests/test_chat_media_v1.mjs` and
`python tests/test_chat_vision_v1.py`.
