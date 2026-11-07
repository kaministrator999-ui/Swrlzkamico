---
title: Swyrlz R39 Candidate
emoji: 🐉
sdk: gradio
app_file: app.py
pinned: false
preload_from_hub:
  - "ggml-org/SmolVLM-500M-Instruct-GGUF SmolVLM-500M-Instruct-Q8_0.gguf,mmproj-SmolVLM-500M-Instruct-Q8_0.gguf 72e986006ef53e37cdd3f6d4241c90b0f01df376"
  - "Qwen/Qwen3-VL-4B-Instruct-GGUF Qwen3VL-4B-Instruct-Q4_K_M.gguf,mmproj-Qwen3VL-4B-Instruct-Q8_0.gguf 1cd86afb9a95c410a6038ab3b40d8b578c892266"
---

# §wyrlz R39 isolated candidate

### Qwen3-VL-4B CPU image analysis trial (deployment still requires guarded release)

This source branch selects Qwen3-VL-4B-Instruct Q4_K_M plus its Q8 vision
projector, pinned to the immutable official model revision above. Source
image bytes stay inside the authenticated Space request. A pinned official
llama.cpp executable runs Qwen on loopback only so the established Python
llama-cpp text/model routes remain unchanged. SmolVLM-500M is still available
via `SWRLZ_VISION_MODEL=smolvlm-500m`; this trial defaults to Qwen3-VL-4B.

The server executable is compiled on the Space the first time Qwen warms up,
using the exact llama.cpp commit in `qwen3vl_local_server.py`. This demands
build tools and can extend cold startup. We do not claim the model or deploy
works until the existing guarded release plus live image-request receipts
confirm it. The current free CPU configuration may impose considerable delay.

This trial preserves the chat image source privacy boundary and existing
per-pass observations. It does not enable an external inference API, publish
images to third parties, or rewrite older release records.

### Chat v1.1.28 — original-image transport, native server crops

The browser now transfers the **actual user-selected JPEG, PNG or WebP
file bytes**, via FileReader/readAsDataURL, without canvas downscaling,
JPEG recompression, or pixel reconstruction. The same 8 MiB attachment
limit applies. Authenticated server accepts at most 8 MiB decoded image
bytes (12 MB JSON/base64 request cap), still rejects images above
16 megapixels, and verifies the actual incoming source width/height/bytes
with Pillow before inference. The browser shows server-measured dimensions
on the image job card; L3 saves them alongside the level outputs.

CPU inference stays bounded and local. L1 (384px) and conditional L2
(640px) still see the full sheet after the **server** resizes directly
from original pixels. In L3 comparison mode, pass 3 can now analyze a
*centered half-size crop of the actual original pixels* when the image's
longest edge is at least 1536px. It is labeled as a geometric center
crop, **not** an AI-chosen subject region or an established recognition
success. For smaller originals, L3 uses the full image at up to 768px.
Each pass is measured, comparison text remains true raw vision output,
and no source image pixels are written into persistent chat history.
The original image may take longer to upload than a reduced JPEG.
No upgraded CPU hardware, new inference model, paid provider, or
additional mandatory inference pass is introduced.

### Chat v1.1.27 — empirical 1–3 level vision study

An image attachment now offers three bounded, user-controlled analysis modes:
**L1 Fast** (384px / 88 tokens, no automatic retry), **L2 Adaptive**
(default: fast pass, then conditional 640px / 144-token retry on generic
captions), and **L3 Compare all (slow)**. L3 intentionally runs L1 and L2
even when L1 seems specific, then adds a 768px / 192-token pass using the
existing transient browser image. No additional model/provider is used.

The authenticated image-job status contains actual completed level records
(level number, input-side cap, decoder-token limit, seconds, first-chunk
seconds, the exact generated description and a *keyword count*). The progress
card can expand each raw level output. **L3 results also appear as a full
comparison in the saved chat message and its JSON export**, so the user can
inspect the captions after the transient card disappears. The chosen level
is *only* a descriptor-count heuristic, never a certified visual truth score.
Only an actual image-versus-answer check by the user can establish which
level is accurate. Failed or cancelled passes are not fabricated. CPU work
remains sequential and bounded; L3 is opt-in because it may be substantially
slower than the 10-second baseline. Stored chat image pixels are still
excluded, and the source upload is not persisted.

### Chat v1.1.26 — adaptive detail recovery for character sheets

An exported Little Crystal Mage example verified that local 384px SmolVLM
descriptions remained generic after direct-text handoff. The 384px/88-token
first pass remains the default. The browser now retains **up to 768px** in
its transient JPEG upload rather than discarding small details before the
server. The server *still downsamples to 384px for the fast first pass*.
Only when a character/reference sheet's initial description lacks at least
two observable distinguishing descriptors, or a caption is entirely
content-free (such as "image with various objects"), does the same CPU model try
a **single** 640px/144-token detail pass; it reports honest DETAIL_RETRY,
DETAIL_PREFILL, and DETAIL_DECODING stages. It keeps the refined output only
if it adds concrete descriptors rather than longer generic prose. A failed
optional retry preserves the original factual observation. Cancellation,
account ownership, bounded queue and ephemeral pixels remain unchanged.
Other images and already-specific sheets incur no second inference.

The second pass is deliberately slower when triggered, and the small
SmolVLM model may still miss details. Resolution and heuristics do not prove
accuracy; device timings and the exported analyzer text remain acceptance
evidence. No hard-coded mage traits are inserted into inference output.

### Chat v1.1.25 — direct observation fidelity

The fast local vision path stays pinned at 384px, 88 tokens, one CPU worker,
and build-preloaded Q8_0 weights. Visual requests now prompt for *distinctive,
observable specifics* (named objects, colors, attire, arrangements and legible
labels) instead of generic categories. For basic "what do you see in this image"
questions, Station receives the analyzer's exact factual description through
the existing Chat model dispatcher with a VISION_DESCRIPTION_DIRECT status
event; §C does **not** paraphrase it through the separate text model.
The reply identifies its origin as local vision analysis, not a direct
inspection by the text-only §C model. For open-ended design, reasoning, or
follow-up questions, normal Chat reasoning remains enabled with stronger
instructions to preserve every supported detail. This prevents a second
model from inventing filler or discarding detail, but **does not prove the
vision model's own observations are correct or detailed**. The saved
vision-analysis handoff in Download Chat JSON remains unmodified.
No image, authorization, paid-provider, or provenance changes.

## Local image understanding for §wyrlz Chat (no paid inference API)

Chat's primary LALM remains text-only. **Image** uses a CPU-based local
`ggml-org/SmolVLM-256M-Instruct-GGUF` model, Q8_0 text weights and
matching multimodal projector, at pinned upstream revision
`b9e4379657e1450d04d02eec8e345667265b0a00` (Apache-2.0).
The existing `llama-cpp-python==0.3.35` runtime provides
`MTMDChatHandler`. Both GGUF files download from the public Hugging Face
model repository into the Space's standard cache **at build time** via
Space YAML `preload_from_hub`. This avoids the first-upload model download.
The total pretrained weight download is approximately 279 MB, with
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
8 MiB decoded, rejects images above 16 megapixels, resizes to 384px for L1
on its longest edge, and runs only one CPU vision request at a time.
Only a short visual description reaches the existing text LALM;
pixels remain ephemeral and are never saved to thread history.
The selected image briefly appears in the browser preview and is
not restored when reopening a thread.

Vision output is intentionally factual and limited: identify the image type,
readable titles/labels, multiple viewpoints of the same design, and supported
shapes, colors, and accessories. The downstream text LALM receives an explicit
grounding reminder that the vision description is fallible and must not be
turned into speculative transformation stories, emotions, or symbolism.
For reduced CPU text decoding, the local vision request now uses a concise
factual prompt and **88 maximum output tokens** (previously 112). It may
describe fewer fine details; no improvement in actual throughput is assumed
without real runtime measurement. The browser now sends the original file without canvas conversion.
The server derives capped 384px/640px views and a conditional 768px
source-pixel focus crop. Upload can be larger than in previous versions. The original local image preview remains
untouched; the image bytes are never added to the persisted conversation.
Preloaded GGUF files now resolve from the local Hub cache first, avoiding
first-image network metadata checks; missing weights may still download from
the public model hub. Startup warms vision after the primary 700M route but
before optional text routes, sharing the CPU lock with image jobs to avoid
duplicate initialization. Real speed improvements require a timed live image
request; the lower pixel budget may omit small text detail.

**Image upload progress:** POST /api/lalm_station/vision validates the image
and immediately returns a short-lived, account-owned job ID (HTTP 202).
GET /api/lalm_station/vision/status?jobId=... provides factual phases:
QUEUED, PREPROCESSING, LOADING_MODEL, ANALYZING, COMPLETE, FAILED or CANCELLED.
Only the authenticated Google account that started the job can poll it.
One image is analyzed at a time; one additional image may wait in a
bounded local queue. A third distinct simultaneous image gets
VISION_QUEUE_FULL (429). An identical request while a job is retained
reuses the same job ID, so a retry can resume instead of launching
another costly inference. Progress contains no fabricated percentage.
Jobs and visual descriptions are process-memory-only, bounded by a short
TTL; the original image bytes are not added to saved conversation history.
The image card offers **Cancel analysis**: it requests owner-authenticated
POST /api/lalm_station/vision/cancel, then stops polling. The local CPU model
now streams generated text and checks cancellation between chunks. A queued
job can be cancelled before it acquires the model lock. An active native image
encoder/prefill cannot necessarily be preempted until it returns control to
Python, so cancellation is cooperative, not an instant CPU kill.
The last progress poll is tracked per job: an active job with no watcher for
90 seconds is marked for cooperative cancellation on the next request/status
check, preventing abandoned work from indefinitely occupying the free CPU
when other requests arrive. Jobs with active status polling are not evicted.

The first real output chunk now marks the transition from native image/prompt
prefill to CPU text decoding in the authenticated progress view, with measured
time-to-first-chunk rather than a fabricated progress percentage. The local
llama.cpp backend uses larger logical prefill batches (512, physical 256)
on the same two CPU threads. This is a latency-focused candidate, **not**
proof of faster end-to-end runtime until live device timing is observed.
Smaller input resolution and output budget may lose fine print/detail.

The browser image card displays a live MM:SS elapsed counter and the elapsed
time in its current stage, anchored to server monotonic job timings when
available. A running image job does **not** expire from client-side polling
after six minutes. Status fetch/network interruptions trigger automatic
reconnection to the same job. If the free Space restarts and the in-memory
job disappears (404), the browser can resubmit the still-attached image
(up to two Space restart recoveries). A full CPU queue is also retried
automatically rather than requiring repeated Send taps. These mechanisms
improve observability and resilience, not the underlying local CPU's
image-processing throughput. Cancel analysis is the user's explicit exit and a best-effort CPU cancellation request.
A pending image appears in the chat viewport with its preview and five
short steps, clearly marked as **not yet sent to Chat** until the vision
description succeeds and Station accepts the normal text conversation.
Once the vision endpoint **accepts** a job, a new image send from draft mode
immediately creates and activates a durable named conversation via the
existing authenticated chat-state UPSERT_THREAD + SET_CURRENT_THREAD operations,
before image inference completes. The new thread appears in the chat sidebar
with its pending activity card and the composer clears; an image sent from an
existing chat stays in that existing conversation. The thread itself exists,
but the pending image and question are **not yet saved as a user message**;
the authoritative Station send occurs after vision completion. If vision or
chat acknowledgement fails, the thread remains visible with a truthful
temporary failure card, and the draft/image are restored for retry when the
composer is otherwise empty. Pending
attachment image object URLs stay alive until Station accepts the generated
text chat message; the existing UI preview is preserved. A failure before
job acceptance never discards the composer draft. No image is saved in
account chat just because its vision job was accepted.

**Download Chat JSON** in the side menu includes a structured
`visionAnalysis` field on image-associated user turns with
`questionSentToChatModel` and `descriptionSentToChatModel`, parsed exactly
from the pre-existing saved message's vision markers. The original `text`
remains unchanged; prior saved image turns are included automatically. This
is a transparency/extraction field, **not** independent proof the browser's
image description was generated by the authenticated vision endpoint
(`isVerifiedVisionModelReceipt: false`). Pixels are never added to the
download, nor duplicated in account storage.

Build-time model caching avoids a first-request download when the Space
retains its standard preloaded Hub cache. Initial RAM initialization and
CPU image inference can still be slow on the free two-core Space; these
are separate from file download. Do not eagerly load duplicate models into
RAM or upgrade to paid hardware. The dedicated endpoint fails closed rather than sending the
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
