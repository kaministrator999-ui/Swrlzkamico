# Server 2.3.104 — Collector 1.0.8 conditional storage writes

Date: 2026-09-13
Checkpoint: FROZEN-WEB-COLLECTOR-001
Status: transport repair and deterministic verification complete; production acceptance pending.

## Evidence and authority

The user's Collector 1.0.7 screenshots show the same exact provider rejection for Start and Configure: HTTP 412, "Precondition failed: ETag mismatch." Revision remains 1 and the collector is idle. This narrows the failure to the conditional Blob PUT, not a missing token or form-validation problem.

Entry authority was Server 2.3.102 / Collector 1.0.7. Concurrent stream-contract work advanced Server to 2.3.103 before commit. This event reconciles from runtime 658f0e252d3774c6ad93dd7667428aaa13c33063 and advances only Server Runtime to 2.3.104 and Collector to 1.0.8. Other module authorities and intervening work are preserved.

## Repair

Mutable control-state reads now obtain the conditional-write ETag from Vercel Blob's metadata API, matching the official head() contract. The code reads metadata before and after a cache-bypassed body read and rejects inconsistent versions. It no longer uses the delivery response's ETag as the mutable object's write token.

A missing/weak metadata ETag fails closed. Existing-state saves also reject a missing or empty ETag instead of relying on revision checks followed by an unconditional overwrite. New-state creation remains create-only. Conditional writes, post-write equality checks, state revision continuity, immutable artifacts, and API/state schema 1 are retained. No state reset or data migration occurs.

Using different delivery and metadata ETags is the evidenced-code repair hypothesis; the screenshots establish the provider mismatch but do not expose either raw ETag. Production acceptance must confirm this resolves the live rejection.

## Verification

The complete deterministic collector suite passes. The transport regression recreates the exact provider rejection when the delivery ETag is used, then verifies successful settings save/reload and new-snapshot revision continuity using the metadata ETag. A stale writer still receives HTTP 412 with no unconditional retry; an object changing during a read is rejected; missing metadata cannot enable overwrite; first save remains create-only. Existing SSRF, lifecycle, checkpoint, search, sealing, and separated training coverage passes.

Engine SHA-256: 95e9b808c9f35360804e047dc02ba13d8df2f7cb93e1a53b66879e33c4e0caa5.
Verification script SHA-256: ea3d18ef3173fc320d9582c2fb1e7cd6db5d94ed2a1a3e5bcab581f10b3a6895.

## Production acceptance and deployment

A bounded GitHub verification job will use the existing project credentials privately, verify the expected live engine hash, perform one configure action with an empty patch (persist existing settings unchanged), and confirm the resulting state on a fresh API read. It must never start, pause, seal, accept training, or delete data. It must stop if collection is running. No credentials or state contents may be logged or published.

Git deployment is disabled. The production deployment workflow triggers only by explicit dispatch or main .deploy/REQUEST.txt changes. This runtime repair and the separate verification job do not deploy or restart the server. The pre-event READY production deployment is dpl_ECF9abdHUzUKbuDYvvqj97yUUnNv, created independently from main 1a766f071a354b6d757b903aa9b5c56e486c0da4.

Sources: [Vercel conditional writes](https://vercel.com/docs/vercel-blob#conditional-writes), [SDK get()/head()](https://vercel.com/docs/vercel-blob/using-blob-sdk), and [official head transport](https://github.com/vercel/storage/blob/main/packages/blob/src/head.ts).
