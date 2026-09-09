# SWRLZ-WEB-KNOWLEDGE-001A Checkpoint Receipt

- Title: Offline-preserving Online Evidence foundation
- Status: implemented on review branch; merge/deployment not authorized
- Date: 2026-09-09
- Repository: `kaministrator999-ui/Swrlzkamico`
- Review branch: `feature/swrlz-web-knowledge-001a`
- Stable baseline: `main@b43bd9f63bf53dd1e6372de034613c92092a0716`
- Live-development baseline inspected: `dev@18e4233260a732a48d9760bc4752c76aaffa012c`
- GitHub implementation commit: `396f66cf56188c0c6339f2e1da26724143230210`
- Implementation tree: `cc074f2bd6a11995914d95fa51f93a90c1a170cd`
- Constitutional source read: `ahazus420-stack/Swrlzcore@35fe6f095cc87c7e8b46ce1c7ee41ed417ba52e9/docs/governance/SWRLZ_CONSTITUTION.md` (`sha 9dbc2b208617179cc0fad218533e505b6707bb27`)
- User authorization: `Approve`, given in response to the bounded `SWRLZ-WEB-KNOWLEDGE-001A` proposal

## Authorized scope

- create one review branch from the exact stable baseline;
- implement a provider-neutral Online Evidence request/source contract;
- add an SSRF-resistant bounded safe-fetch boundary;
- add an explicit Offline/Online Chat UI control;
- extend streaming with V3 source and lineage receipts;
- add mocked/fixture verification;
- synchronize architecture, data-policy, environment, and checkpoint documentation.

## Explicitly prohibited in this checkpoint

- merging or deploying;
- enabling a live provider or using/provisioning API keys;
- crawling, background ingestion, durable evidence storage, or user-data collection;
- training, fine-tuning, LoRA, model/checkpoint promotion, or weight changes;
- changing the default offline route or silently falling back between local/remote routes;
- triggering Vercel or GitHub workflows.

## Facts

- The stable baseline provides a V2 NDJSON Chat contract whose Truth Firewall appends only `DELTA.text` to assistant prose.
- The stable baseline has local R39 generation and an optional proof-bound V2 upstream route, but no search provider, crawler, evidence database, or training implementation.
- Production Chat presentation is currently fetched from mutable GitHub `dev`; backend Python comes from the deployed stable image. Backend and live UI therefore require ordered, separately reviewed promotion.
- The `main` and inspected `dev` baselines are materially divergent. This checkpoint does not merge or overwrite either lineage.
- This checkpoint contains no registered production provider. `SWRLZ_ONLINE_EVIDENCE_ENABLED=false` remains the documented default.

## Requirements preserved

- offline-first ordinary use;
- explicit local versus remote route identity;
- evidence/provenance separate from model prose;
- no silent fallback;
- bounded human approval and auditable lineage;
- compatibility evidence for a protocol change;
- training rights distinct from technical retrievability.

## Implementation result

- `api/online_evidence.py` defines provider registration, current-prompt-only query derivation/redaction, public-address-pinned HTTPS fetch, redirect revalidation, bounded text extraction, source records, bundle receipts, and prompt grounding.
- `api/chat.py` preserves V2 offline normalization and adds explicit V3 request validation/status metadata.
- `api/chat_extensions.py` composes Online Evidence with local R39, emits `SOURCE` records separately, reports `LOCAL_R39+REMOTE_WEB_EVIDENCE`, attaches terminal receipts, and fails without an offline fallback.
- `web/chat.html` adds separate execution-route and knowledge-mode controls, V3 validation, safe source-link rendering, and receipt export.
- `web/chat_enhancements.js` preserves protocol/mode in the existing browser stream ledger; candidate UI identity is `1.4.0-rc.1`.
- Contract and data-policy records define the future provider, persistence, licensing, consent, and training gates.

## Classification

### Facts

- Source and mocked tests can verify contract behavior without live network access.
- V2 offline output contains no `knowledgeMode`, derived query, source, or receipt fields.
- Online Evidence source text is request-memory-only in this implementation.

### Requirements

- A production provider must be explicitly selected, registered, configured, and approved.
- Backend V3 support must precede any live `dev` UI promotion to avoid UI/backend incompatibility.
- A future durable corpus must carry rights, provenance, privacy, transform, review, and deletion lineage.

### Assumptions

- The existing R39 prompt renderer continues to honor server-created `SYSTEM` history turns.
- A provider adapter can return candidate HTTPS URLs within a bounded timeout.
- The current browser source panel remains acceptable presentation pending product review.

### Recommendations

- Keep Online Evidence as request-time retrieval before considering weight updates.
- Begin any future durable corpus with SWRLZ-owned and clearly licensed material.
- Add durable addressable evidence/job state or disable automatic V3 replay before production provider activation.
- Benchmark source count/context length and R39 prompt-prefix behavior using a separate performance checkpoint.

## Verification evidence

Run from repository root:

```text
python -m unittest discover -s tests -v
python -m py_compile api/chat.py api/chat_extensions.py api/online_evidence.py api/chat_ui_guard.py
node --check web/chat_enhancements.js
node --check web/chat_stream_focus.js
node -e "parse the inline web/chat.html script with Function"
python scripts/verify_vercel_chat.py
```

Verified source results before the implementation commit:

- 12/12 fixture/unit tests passed;
- the integrated Chat source gate passed all six sections;
- Python compilation passed for the changed server modules;
- external and inline browser JavaScript parsed successfully;
- `git diff --check` passed.

The implementation commit and tree identities above bind these results to the reviewed source state. The following receipt-only commit records that binding and does not change runtime behavior.

No live provider request, R39 model load, Vercel deployment, production browser request, or workflow run is claimed.

## Rollback

- Do not merge the review branch, or revert its review commit if later integrated.
- Leave `SWRLZ_ONLINE_EVIDENCE_ENABLED` disabled.
- V2 Offline Chat remains the compatibility path and requires no knowledge configuration.

## Known limitations

- No live provider adapter is registered.
- No production/runtime validation has occurred.
- No durable evidence cache/job exists; V3 replay semantics require resolution before provider activation.
- Current live UI comes from `dev`, so this branch's bundled UI is not a claim about production presentation.
- Retrieved source truth and training rights remain contestable/unassessed.

## Next approval gate

A separate checkpoint must name and approve the exact provider, credentials/configuration boundary, quota/cost controls, provider terms, retention behavior, V3 replay strategy, deployment order, and production verification. Durable ingestion or training requires another independent data/training checkpoint.
