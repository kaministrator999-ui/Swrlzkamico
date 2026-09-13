# Server Runtime 2.3.117 — Runtime Delivery Optimization

Date: 2026-09-13

## Module versions

- Server Runtime: 2.3.117
- Stable deployable server: 2.3.109 on `main`
- Web Chat: 1.5.0
- Deployment Control: 1.0.4
- Runtime manifest: v33

## Goal

Reduce avoidable server/network latency without weakening the runtime-source-of-truth, shared transcript, RMCCA, or hot-update contracts.

## Stable infrastructure changes prepared on `main`

### `api/runtime_hot.py`

- Adds one authoritative 30-second auto-sync gate shared by request middleware and engine refresh callers.
- Concurrent auto-sync callers do not queue behind the same GitHub refresh; they continue using the last known result while one refresh is in progress.
- A failed refresh retries on a shorter 5-second cadence.
- Runtime source checks are fetched concurrently rather than sequentially.
- Manual `/api/hot/sync` remains forceable and explicit.
- Runtime status exposes throttled/in-progress refresh information.

Prepared commits:
- `de4ea382073d1fc53efd37d653d6449a46a70e95` — hot-sync gating + parallel fetch

### `api/live_source_guard.py`

- HTML and runtime manifest remain `no-store` and stay live.
- Manifest-injected CSS/JS now use `?v=<manifest revision>` URLs.
- Versioned runtime assets receive `Cache-Control: public, max-age=31536000, immutable`.
- Unversioned live assets retain no-store behavior.
- Worker source cache increases from 1 second to 2 seconds to collapse near-simultaneous duplicate source fetches while retaining fast runtime propagation.

Prepared commit:
- `ced282fa91dab857556a254db87fe2c8b5dfff26` — manifest-versioned immutable asset delivery

### `api/index.py`

- Stable server version prepared as 2.3.109.
- Adds `runtime-delivery-optimization` capability contract `hot-runtime-delivery-v1`.
- Existing Server 2.3.108 shared private transcript continuity remains unchanged.

Prepared commit:
- `5fac3a98d691af38c24907ae8adf0d6da64df2fd`

### Deployment verification

- Production verifier now expects Server 2.3.109 and validates the runtime delivery optimization contract.
- Readiness polling window is expanded and empty/non-JSON final status output is handled more clearly after the transient false-red seen during Server 2.3.108 deployment.

Prepared commit:
- `c281abb2d4e65cb6b064b74dd4288d128a8f1fa8`

## Runtime branch changes

- Manifest v33 is the cache revision authority for the new stable delivery behavior.
- Web Chat 1.5.0 records the versioned runtime-asset delivery boundary.
- Deployment Control 1.0.4 records the updated 2.3.109 production verifier.

## Expected performance effect

The optimization removes two avoidable multipliers:

1. ordinary Chat traffic can no longer trigger repeated full five-source GitHub refresh sweeps inside the 30-second refresh window;
2. unchanged runtime CSS/JS does not need to be re-downloaded through Vercel on every browser reload after Server 2.3.109 is activated.

When a refresh is due, the fixed hot-source allowlist is checked concurrently so network latency approaches the slowest source request rather than the sum of all source request latencies.

## Safety / compatibility

- No change to LALM weights or generation semantics.
- No change to `generation-transcript-v1`, `shared-private-blob-v1`, `resumable-v1`, or `rmcca-direct-v1`.
- No deployment was triggered as part of this development event.
- Production remains on the currently deployed stable server until the user explicitly approves a new production deployment.
- Manifest v33 is safe before the stable deployment because the currently deployed server does not yet apply the new versioned-asset cache contract.
