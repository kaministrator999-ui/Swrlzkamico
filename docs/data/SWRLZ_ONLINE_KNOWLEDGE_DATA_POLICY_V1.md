# SWRLZ Online Knowledge and Training Data Policy V1

- Checkpoint: `SWRLZ-WEB-KNOWLEDGE-001A`
- Status: proposed policy foundation; no corpus collection or training authorized
- Applies to: Vercel Chat, Online Evidence, LALM/R39 knowledge improvement

## Two different knowledge paths

SWRLZ must preserve the distinction between:

1. **Online Evidence / retrieval-augmented inference** — fetches current sources for one explicit user request, grounds the answer, emits citations/receipts, and does not change model weights.
2. **Training or fine-tuning data** — a durable, reviewed, licensed, versioned dataset used by a separately approved model-training process.

Material retrieved for the first path does not automatically qualify for the second. In this checkpoint every online source is `rightsStatus: UNASSESSED` and `trainingEligible: false`.

## Recommended source priority for a future corpus

Start with sources whose authority and reuse rights can be established:

1. SWRLZ-owned specifications, contracts, runbooks, release notes, support answers, and reviewed examples.
2. User-contributed material only through explicit opt-in consent, purpose limitation, redaction, deletion controls, and account/tenant separation.
3. Public-domain or clearly permissively licensed technical/reference material whose license permits the intended training use.
4. Partner or commercial datasets covered by a written agreement that permits storage, transformation, and model training.

Do not treat arbitrary search results, scraped pages, private repositories, browser-local conversations, secrets, or unlabeled model-generated text as training-ready.

## Required future ingestion stages

A later, separately approved ingestion system should preserve this sequence:

1. **Source registry** — canonical URL/repository, owner/publisher, acquisition method, provider, timestamps, license/terms snapshot, allowed uses, and raw SHA-256.
2. **Quarantine** — immutable raw object plus malware/content-type checks; not yet available to training.
3. **Extraction** — normalized text/code with extractor identity/version and parent-object hash.
4. **Safety/privacy review** — secret, credential, PII, regulated-data, and prompt-injection classification.
5. **Quality review** — authority, correctness, freshness, duplication, language, domain coverage, and contradiction checks.
6. **Rights decision** — explicit `ALLOW_TRAINING`, `ALLOW_RETRIEVAL_ONLY`, `REJECT`, or `NEEDS_REVIEW`, with reviewer and evidence.
7. **Dataset release** — immutable manifest, source/transform lineage, content hashes, train/validation/test split rules, deduplication receipt, and rollback/deletion map.
8. **Training gate** — separate approval for model/checkpoint identity, method, compute, evaluation, safety tests, and promotion.

No stage may silently upgrade an unknown rights state into permission.

## Suggested quality fields

Each durable candidate record should eventually include:

- `sourceId`, `parentSha256`, and normalized `contentSha256`;
- `publisher`, `canonicalUrl`, `retrievedAt`, and `freshnessClass`;
- `licenseId`, `termsEvidence`, `rightsDecision`, `allowedUses`, and reviewer;
- language/domain/topic labels and authoritative-source score;
- duplicate/near-duplicate group;
- PII/secret/safety classifications and remediation receipt;
- extractor/normalizer versions;
- human-review state and dispute/correction history;
- dataset release ID and split assignment.

## Quality gates before training

At minimum, a dataset release should fail closed if:

- origin or content hash is missing;
- rights are unknown or incompatible;
- secrets/PII policy has not been evaluated;
- train/evaluation leakage checks are absent;
- duplicate and synthetic-content proportions are unmeasured;
- a deletion/correction cannot be traced to every derived record;
- model evaluation lacks offline behavior, Truth Firewall, factuality, citation, regression, and safety checks.

## User interaction data

Chat content currently stays browser-local except for bounded history sent for the active request. It is not silently collected for training. A future feedback program must use an explicit opt-in control, show what is submitted, exclude secrets by default, support revocation/deletion, and record the consent/policy version with each sample.

## Current checkpoint boundary

Authorized now:

- request-scoped evidence contracts;
- query redaction;
- safe-fetch controls;
- source and bundle receipts;
- fixture tests;
- UI mode/source presentation.

Not authorized now:

- live provider/API-key use;
- crawling or background ingestion;
- durable source/content storage;
- use of conversations or retrieved pages as training data;
- fine-tuning, pretraining, LoRA, checkpoint promotion, or weight changes;
- deployment or production enablement.
