# Server 2.3.68 — Frozen Web Snapshot Collector

Date: 2026-09-12
Lifecycle: IMPLEMENTATION_VERIFIED / DOCUMENTATION_SYNCED
Production status at source publication: deployment approved and pending

## Versions

- Server Runtime: `2.3.68`
- Frozen Web Collector: `1.0.0`
- Deployment Control: `1.0.2`
- Web Chat: `1.4.61` unchanged
- LALM Engine: `2.1.26` unchanged

## Result

This release adds an authenticated browser-operated pipeline for creating bounded, durable, searchable frozen web snapshots. The operator registers sources, controls collection budgets and lifecycle, reviews evidence, seals immutable manifests, and separately decides whether qualified material may enter a reviewed training corpus.

The stable deployment hosts authentication and a fixed module contract. The interface and compatible collector engine remain owned by the `runtime` branch, so later compatible updates can be loaded live without another Vercel deployment.

## Safety and authority

- Private Vercel Blob owns durable state and immutable artifacts; `/tmp` is not authoritative.
- Robots compliance is mandatory and fail-closed.
- Only public HTTP/S destinations on safe ports are permitted; DNS results and every redirect are revalidated.
- TLS hostname verification is preserved while the connection is pinned to a validated address.
- Content types, bytes, redirects, domains, pages, documents, runtime, storage, and crawl rate are bounded.
- Raw HTML is discarded after extraction.
- Frozen search evidence is distinct from reviewed training data.
- Training acceptance requires explicit rights/provenance confirmation.

## Verification

`STATIC VERIFICATION PASS`

- `scripts/verify_web_snapshot_collector.py`
- `scripts/verify_collector_console.mjs`
- stable-host verification on the reconciled `main` candidate
- deployment workflow YAML parsing

`BUILD NOT RUN` and `RUNTIME NOT TESTED` refer only to the production deployment at the time this source record was authored. Deployment and live-browser evidence are recorded after the approved workflow completes.

## Lineage

- Runtime baseline: `26009037b55c158a0606e84bf69202b165e59057`
- Main baseline: `4a070f5d5cc8aba67ef0575d8567b2f0f9813f7a`
- Rebased runtime checkpoint: `5b7744acc78a1a8508e5a954a4f5b2161db7a8d8`
- Rebased stable checkpoint: `636321dcd9f204eae08f5e9cfc567ab1b2ac5c1d`

No crawl, snapshot sealing, or training acceptance was performed as part of deployment.
