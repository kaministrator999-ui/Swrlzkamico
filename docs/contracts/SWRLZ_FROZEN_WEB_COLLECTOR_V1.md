# SWRLZ Frozen Web Snapshot Collector Contract V1

Status: accepted implementation contract for Server 2.3.79
Module: `frozen-web-collector`
Module version: `1.0.0`
API schema: `1`
State schema: `1`

## Purpose

The Frozen Web Snapshot Collector provides a browser-operated, bounded pipeline for gathering public web evidence into durable, searchable, immutable snapshots. It also prepares high-quality material for a separate operator-controlled training review process. Collection is never equivalent to training authorization.

## Authority and ownership

| Surface | Authority | Responsibility |
|---|---|---|
| Stable host | `main/api/collector_host.py` | Authentication, fixed runtime source selection, request-size boundary, module contract validation, source/version receipts, last-known-good in-worker fallback |
| Collector engine | `runtime/runtime_hot/web_snapshot_collector.py` | Source policy, crawl lifecycle, extraction, canonicalization, deduplication, budgets, safety checks, snapshot/search/training artifacts |
| Browser console | `runtime/web/collector.html` | Operator controls and evidence views |
| Page route | `runtime/runtime_pages/manifest.json` | `/collector` runtime ownership |
| Module identity | `runtime/versions/frozen-web-collector.txt` | Collector version and API/state compatibility identity |
| Durable data | private Vercel Blob | Mutable control checkpoint plus immutable evidence and review artifacts |

`runtime` is durable live source for compatible collector page and engine updates. `/tmp` may cache loaded code but never owns collector state or evidence.

## Stable/runtime compatibility boundary

The stable host loads only these fixed runtime authorities from the `runtime` branch:

- `runtime_hot/web_snapshot_collector.py`
- `versions/frozen-web-collector.txt`

The loaded module must declare the expected module ID and API schema and must expose `handle` and `inspect_module`. A changed source hash loads as a unique module. If a later refresh fails after a valid module has loaded, that worker may continue with its last-known-good module and exposes the failure in its source receipt.

Compatible page/engine changes do not require Vercel redeployment. A stable deployment is required when authentication, host routing, dependencies, source allowlisting, API schema, or another stable contract changes.

## Authentication and routes

`GET /api/collector/readiness` is the only unauthenticated collector route. It returns non-sensitive module, storage-readiness, source-branch, source-hash, and compatibility facts. It never returns credentials or the full private store identifier.

Every operational route is authenticated by the stable Admin-token boundary.

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/collector/status` | Bounded current control state, budgets, pressure, sources, frontier, evidence summaries, review queue, and source receipt |
| POST | `/api/collector/action` | Apply one lifecycle/configuration/source/review/storage action |
| GET | `/api/collector/search?q=...&snapshotId=...` | Lexical search over the active or a sealed snapshot index |
| GET | `/api/collector/document?snapshotId=...&sha256=...` | Retrieve one frozen document by content identity |
| GET | `/api/collector/snapshots` | List known snapshots/manifests |
| GET | `/api/collector/snapshot?id=...` | Retrieve one immutable manifest |
| GET | `/api/collector/host/refresh` | Request a runtime source refresh through the authenticated host |

The browser surface is `/collector`. Tokens are held only in browser `sessionStorage`, never `localStorage`.

## Lifecycle

Supported actions are:

- `configure`
- `add-source`
- `remove-source`
- `start`
- `pause`
- `continue`
- `step`
- `seal`
- `review`
- `storage-check`

`start` creates a new snapshot from enabled registered sources and processes the first bounded batch. `pause` checkpoints the current frontier. `continue` resumes the same durable snapshot. `step` processes a bounded batch. `seal` is allowed only after collection is paused or ready to seal and at least one document was accepted.

Sealing first writes a durable seal intent and fixed totals, then writes deterministic immutable index and manifest payloads. Retrying an interrupted seal is expected to reproduce the same content rather than create a competing snapshot.

## Source policies

Each source has a label, canonical URL, priority from 1 through 100, optional license/provenance note, enabled state, and crawl policy:

- `shallow` — depth is capped at 1;
- `balanced` — depth is capped at 2;
- `deep` — uses the configured global depth limit.

External-domain discovery is disabled by default. Preferred and blocked domain lists are explicit. The collector preserves an exploration allocation without allowing low-priority exploration to continue under high pressure.

## Default budgets

| Budget | Default |
|---|---:|
| Storage | 100 MiB |
| Run duration | 1,800 seconds |
| Request duration | 35 seconds |
| Pages per run | 600 |
| Accepted documents | 500 |
| Global depth | 2 |
| Links per page | 30 |
| Documents per domain | 100 |
| Bytes per domain | 20 MiB |
| Domains | 12 |
| Document bytes | 1,500,000 |
| Batch size | 1, maximum 5 |
| Minimum quality | 0.62 |
| Training-candidate quality | 0.76 |
| Minimum text characters | 320 |
| Chunk size / overlap | 700 / 80 words |
| Minimum domain delay | 1 second |
| Exploration allocation | 25 percent |

Pressure is reported at 70 percent, becomes restrictive at 85 percent, and automatically pauses at 95 percent. Immutable writes and sealing are preflighted against the 95-percent storage boundary.

## Network and content safety

- Only `http` and `https` URLs without embedded credentials are accepted.
- Resolution must produce public globally routable addresses; loopback, private, link-local, multicast, reserved, unspecified, and local-name destinations are rejected.
- Connections are pinned to validated addresses while preserving TLS hostname/SNI verification.
- Every redirect target is canonicalized and revalidated. Cross-domain redirects remain subject to the configured source/domain boundary, the destination's robots policy, politeness delay, and budgets.
- Robots compliance is mandatory, cached for a bounded interval, and fail-closed on errors. It cannot be disabled by configuration.
- Accepted MIME types are fixed to safe HTML/XHTML/plain-text types.
- Redirect count, robots bytes, response bytes, document bytes, request duration, and state collections are bounded.
- The collector identifies itself with a stable user agent and applies per-domain delay.

This contract does not authorize bypassing authentication, access controls, paywalls, robots directives, rate limits, or site terms.

## Evidence transformation

The pipeline is:

`seed → validate/robots/politeness → fetch → extract → canonicalize → deduplicate → quality/privacy → chunk → index → frozen snapshot`

Raw response HTML is not stored. Accepted documents contain extracted text, title, quality/privacy signals, chunk references, content hash, canonical/final URL, redirects, selected response headers, source identity, timestamps, depth, and runtime source/version receipts.

Content hashes deduplicate identical documents. Canonical URL history records revisions when a URL later produces different content.

## Frozen search

The collector builds a bounded lexical term-frequency index suitable for BM25-style ranking. Search returns evidence summaries and excerpts; document retrieval uses the snapshot ID and SHA-256 identity. Vector embeddings are not claimed by V1.

## Training separation

High-quality, low-privacy-risk documents may enter a pending training-candidate queue. They do not enter training automatically.

An operator must explicitly accept or reject each candidate. Acceptance requires `confirmRights=true` and records the review note, rights confirmation, snapshot ID, content identity, source URL, provenance, quality, text, and chunks under a training-specific namespace. Rejection records a separate immutable review decision.

Frozen documents and manifests do not change when a later training decision is made.

## Storage layout

```text
swrlz/collector/control/state.json
swrlz/collector/snapshots/<snapshot-id>/documents/<sha256>.json
swrlz/collector/snapshots/<snapshot-id>/chunks/<sha256>.json
swrlz/collector/snapshots/<snapshot-id>/revisions/<url-sha>.json
swrlz/collector/snapshots/<snapshot-id>/training_candidates/<candidate-id>.json
swrlz/collector/snapshots/<snapshot-id>/index.json
swrlz/collector/snapshots/<snapshot-id>/manifest.json
swrlz/collector/training/accepted/<candidate-id>.json
swrlz/collector/training/rejected/<candidate-id>.json
```

Mutable state uses optimistic ETag checks. Evidence, manifests, and review artifacts are write-once; an identical retry is tolerated, while different content at an immutable path is a conflict.

## Non-claims and exclusions

- V1 is not a general unrestricted internet crawler.
- V1 does not run a permanent background daemon; the browser advances bounded batches.
- V1 does not provide semantic/vector search.
- V1 does not automatically train or modify the LALM.
- Deployment does not add a source, initiate a crawl, seal a snapshot, or accept training material.
- Compatibility across a future API or state schema change requires a new stable-host review and, when necessary, a separately approved deployment.
