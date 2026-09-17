# Server 2.3.255 — R39 v73 inherited n-gram NumPy namespace repair

## Status

**Source complete / static verified / published, live activation and authenticated coding acceptance pending.**

- Overall Server event: `2.3.255`
- LALM Engine: `2.1.85`
- Revision: `2.1.85-hot-ngram-numpy-namespace-repair-v73`
- Chat: `1.5.75` unchanged
- Deployment Control: `1.0.8` unchanged
- Deployment / restart: **NONE**

## Triggering evidence

Authenticated production request `web:mu5zycye:4201205958924473599` under v71 produced the same failure twice: the first candidate and the one bounded repair each emitted exactly two decode steps and nine characters, then terminated `FAILED / inference-failed`. The completion checker still reported `complete-code` and `requested-explanation`, the degeneration guard had not fired, and v70's fence-repair normalization activated correctly. Chat then preserved the final 18-character failed text exactly.

Repository inspection localized an exact threshold in the inherited v55 sampling owner. `_ngram_guarded_sample` delegates to the earlier sampler while generated-token history has fewer than two entries. As soon as history reaches two entries, it executes `np.argpartition(...)` and related NumPy operations. v55 did not import `numpy as np` into the exec-shared hot-module namespace.

That produces a deterministic boundary matching live evidence:

```text
first generated token  → history length 0 → delegate
second generated token → history length 1 → delegate
third decode attempt    → history length 2 → n-gram branch → bare `np`
```

The generic v17 exception boundary then converts the resulting runtime exception into `R39_HOT_INFERENCE_RUNTIME_FAILED`, explaining why both first and repair passes died at exactly the same two-token depth.

## Architecture reconciliation

This is **Brain/LALM inherited decode-policy ownership**. The correct repair is not in Chat, persistence, the v69 context compiler, the v70 requirement repair, or the server stream controller.

The v55 n-gram sampler remains the semantic owner of phrase-level repetition pressure. v73 repairs only its missing inherited namespace dependency at the current hot edge, preserving the historical immutable source and all later programming behavior.

## Repair

v73:

- hydrates immutable v72, preserving v72 diagnostics plus v71/v70/v69 behavior;
- imports NumPy at the current LALM edge;
- restores `np` **after the full inherited exec chain hydrates**, so the v55 sampler resolves the dependency from the shared namespace;
- fail-closes hydration if `_ngram_guarded_sample` is unavailable;
- adds a deterministic hydration self-test that calls the n-gram sampler with a two-token history, deliberately crossing the exact branch that previously failed before token three;
- exposes the repair/self-test through `inspect_engine` and emits bounded `v73-enter` evidence.

No Chat code, server persistence, deployment configuration, or user-facing response contract was changed.

## Verification

- immutable v73 source was re-fetched from its exact commit;
- Python syntax compilation passed;
- active `runtime_hot/r39_engine.py` now targets immutable v73;
- `runtime_hot/manifest.json` declares the v73 revision;
- LALM and Server version authorities were re-read before assignment and had not advanced concurrently;
- no Vercel deployment or restart was performed;
- Git automatic deployment guards remain fail-closed.

A fresh production worker has not yet emitted v73 hydration/user-turn evidence, so this release is not labeled live-fixed yet. The next normal authenticated coding turn is the live acceptance surface; it must cross decode step 2 and ultimately satisfy runnable-code + explanation requirements.

## Concurrency / versions

The version gate observed Server `2.3.254`, LALM `2.1.84`, and Chat `1.5.75`. Those affected authorities remained unchanged immediately before assignment, so this event owns Server `2.3.255` and LALM `2.1.85`; Chat stays unchanged.

## Lineage

- v73 source: `023ac7efdabbe8c317490bc23f410e3a370b5eaf`
- v73 hot entry: `90ac4c548506d25b1a6f61c0dd15098dccc88b31`
- v73 manifest: `6eeb60934e8b119e38c61b486da0739e5ded92ba`
- LALM authority: `fa2b37776f5f3a76fc8b3388ef3527e0ddc2b529`
- Server authority: `5263ae849029674c29bb66b4404ccd1b60044692`

## Acceptance target

A normal authenticated standalone coding request should hydrate v73, pass the two-token sampler threshold without an inference failure, continue decoding beyond step 2, and complete with valid runnable code plus the requested explanation. If another lower failure remains, v72's bounded failure-detail camera remains preserved in the lineage to classify it.
