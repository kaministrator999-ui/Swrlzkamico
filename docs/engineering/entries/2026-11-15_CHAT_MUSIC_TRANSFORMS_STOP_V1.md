# §C music transformation quality + immediate request cancellation

Date: 2026-11-15 US Central. Canonical runtime: existing `kamiloki/Swyrlz` Hugging Face Space.

## User-observed issues

- A reference-driven song remix copied a non-chorus verse under a different performer label, repeated weak padding and included assistant preface/outro prose rather than only a finished song.
- Follow-up screenshot showed an active `THINKING` request and a failed lyrics verification response while the user's criticism text was still in the composer. Do not label that unsent composer text an actual misrouted user request without an account receipt.
- Stop button did not promptly terminate a running generation. The currently deployed Station cancel endpoint only set a request flag; a buffered model call might not yield another engine event for a long time. The client also waited for click/ack to display a result.

## Live-source evidence and owning seams

- Live source inspected read-only through `hf-chat-music-quality-inspect.yml`: `music_structure.py`, `lfm2_700m_engine.py`, `online_tools.py`, `station.py`, `qwen35_single_runtime.py`, and served `chat/§wyrlz/index.html`.
- Existing song-reference projection, source words exclusion, original-music form gate, code and token-budget gates remain authoritative.
- Existing `/api/lalm_station/cancel` requires the owner/session request ID. It sets `cancelRequested`, but the native CPU loopback SSE socket had no request-scoped interrupt.
- The client Stop handler uses an armed pointer click and keeps processing until the terminal server receipt.

## Changes in the scoped release candidate

1. Reusable `music_transform_quality.py` classifies remix, parody, lyric remaster, adaptation, rewriting, cover and mashup requests. Provides bounded creative directives and deterministic QA for identical or near-identical non-chorus verses, padding, empty lyric work and unsolicited assistant preface/outro. Chorus repeats and explicit AAB structures retain intended exemptions.
2. The existing `music_structure.py` route recognizes more reference pointers such as `from it` without sacrificing source verification. Existing original-music similarity/borrow guards are preserved and run alongside the new quality checks for reference transformations.
3. The `online_tools.py` route treats a genuine critique of the model's previous remix as conversation, not a fresh lookup, unless the user affirmatively requests another lyric search. This is scoped to current-turn intent; it does not fabricate a successfully sent user message.
4. The existing generation engine buffers the transformed song and performs one bounded repair on observable quality failures rather than streaming a duplicated song and retracting it later.
5. A request-scoped `stop_transport.py` binds Station's authenticated request to the actual loopback HTTP connection. Stop marks its own cancellation event and shuts down only that connection's socket, interrupting header/prefill waiting or SSE token reads without killing the resident model or other requests. Station still owns the durable `CANCELLED` receipt. No global kill, GPU upgrade or changed model parameters.
6. The mobile Stop button submits on the actual finger-down, immediately displays `STOPPING` while awaiting the authenticated server response, and preserves keyboard-click accessibility. No unverified local terminal success is claimed.

## Release / verification protocol

- Exact current Space revision and source-file SHA-256 preflight, per-file code patch anchors, Python AST checks, Node inline JS syntax verification, deterministic tests and previous-byte snapshot.
- Governed deployment uses `main:.deploy/HF_SPACE_REQUEST.txt` → `main:.github/workflows/hf-space-request.yml` → `main:.github/workflows/manual-hf-space.yml`, scope `music-transform-quality-v1`. No broad upload from an old `feature/hf-space-manual-deploy` branch.
- A single immutable-parent CAS commit patches existing source files and adds two helpers. Byte-for-byte readback verifies all. An unchanged revision is required before mutation; on post-commit readback mismatch and unchanged head, exact prior files and helper deletion are attempted.
- Tests are deterministic and structural, not evidence of subjective lyrical merit. Need live model behavior and physical Android Stop acceptance before claiming those experiences are confirmed. Native socket shutdown is best-effort when the underlying native server has not yet observed a disconnect; UI reports `STOPPING` until server terminal cancellation.
- Do not infer source research, lyrics verification, real audio remastering or named artist performance from a model claim alone.

## Release and real guest Stop receipts

- PR [#435](https://github.com/kaministrator999-ui/Swrlzkamico/pull/435) merged exact tested GitHub source `0db83901e549801c0c31563b9b08233a167654a2`.
- Canonical authorized request commit: `beccd1cdaeabc7c4df3639734375386d4bfbbd0c`, `CHANGE_SCOPE=music-transform-quality-v1`.
- Guarded production release [Actions #43802960845](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43802960845) **success**, exact Space revision changed from `1928c95561d57d02e21edbab076988cb98a15b4d` to `e49039b3af00d726742c84077ce3da3b10a0b425`. Eight changed files were byte-for-byte read back and previous versions preserved as a workflow artifact. The unrelated whole-Space package job and previous output-limit-only job were skipped.
- Independent real anonymous Stop acceptance [Actions #43803357453](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43803357453) **success** on a synthetic guest generation. The exact new revision was confirmed `RUNNING`; HTTP send returned 202; `GENERATING` phase observed; Stop acknowledgement took 91 ms with `nativeInterruptRequested=true`; authoritative Station `CANCELLED` terminal state was observed 1252 ms after Stop.
- This is a server-side live stop test only. A real Android pointer/touch test remains separate acceptance evidence, and cancellation latency may vary with queue state, prefill and network conditions.
