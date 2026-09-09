# SWRLZ Online Evidence Contract V1

- Contract ID: `swrlz_online_evidence_v1`
- Checkpoint: `SWRLZ-WEB-KNOWLEDGE-001A`
- Status: review candidate; not deployed
- Governing Constitution: `ahazus420-stack/Swrlzcore@35fe6f095cc87c7e8b46ce1c7ee41ed417ba52e9/docs/governance/SWRLZ_CONSTITUTION.md`
- Stream extension: `swrlz_llm_stream_v3`

## Purpose

Define a provider-neutral boundary that lets the Vercel Chat explicitly compose local R39 inference with request-scoped remote web evidence while preserving offline-first behavior, route truth, provenance, the Truth Firewall, and human authority.

Online Evidence is retrieval-augmented inference. It does not train, fine-tune, update, or otherwise modify LALM/R39 weights.

## Capability and availability

Capability, configuration, availability, and permission remain distinct:

- the source contains an Online Evidence capability;
- live network retrieval is disabled unless `SWRLZ_ONLINE_EVIDENCE_ENABLED` is explicitly enabled;
- a provider name alone is insufficient—the corresponding adapter must be registered in-process;
- this checkpoint registers no production provider and uses no API key;
- the default and ordinary path remains `OFFLINE`.

`AUTO` is not implemented. A user or caller must choose `ONLINE` explicitly. If Online Evidence cannot run, the request fails with a classified reason; it does not silently fall back to offline generation.

## Request contract

Offline requests remain protocol V2 and preserve their existing normalized payload:

```json
{
  "protocolVersion": 2,
  "prompt": "..."
}
```

An Online Evidence request is explicit:

```json
{
  "protocolVersion": 3,
  "knowledgeMode": "ONLINE",
  "prompt": "..."
}
```

The server derives the search query from the current prompt only. It does not send conversation history to the search provider. The query is whitespace-normalized, bounded to 384 characters, and redacts common email addresses, phone numbers, bearer/JWT values, API keys, passwords, and high-entropy secret-like tokens.

Client-supplied derived-query text, hashes, sources, and receipts are not accepted as authority.

## Provider adapter boundary

An adapter implements the `SearchProvider` interface:

```text
provider_id: bounded stable identifier
search(query, limit) -> ordered SearchHit(url, title, provider_ref)
```

The adapter must enforce its own provider timeout, authentication, quota, terms, and error classification. It returns candidate URLs, not trusted facts. Provider output remains untrusted until the safe-fetch boundary independently validates and retrieves a source.

## Safe-fetch boundary

For every initial URL and redirect target, the fetcher:

- accepts HTTPS only on port 443;
- rejects embedded or query-parameter credentials, control characters, local hostnames, and oversized URLs, and strips fragments before retrieval;
- resolves DNS before connecting and rejects the entire answer set if any used address is non-public, including loopback, private, link-local, multicast, reserved, or unspecified addresses;
- pins the TLS connection to a validated public IP while verifying the certificate for the original hostname;
- limits redirects, timeout, response bytes, and document characters;
- requests identity encoding and accepts only `text/html`, `text/plain`, or `application/xhtml+xml`;
- strips executable/non-content elements such as scripts, styles, forms, SVG, canvas, templates, and noscript blocks;
- never executes retrieved content.

An unsafe or failed source is skipped with a classified code and a URL hash. If no source passes, the Online Evidence request fails.

## Evidence source record

Every source is assigned by the server after fetch:

| Field | Meaning |
|---|---|
| `sourceId` | Stable request evidence identifier derived from canonical URL and content hash |
| `providerId` | Adapter identity |
| `providerRef` | Bounded provider result reference, if supplied |
| `url` | Canonical validated HTTPS URL |
| `title` | Bounded fetched/provider title |
| `mediaType` | Accepted text media type |
| `byteCount` | Retrieved body size |
| `contentSha256` | SHA-256 of retrieved bytes |
| `retrievedAt` | UTC retrieval timestamp |
| `rightsStatus` | `UNASSESSED` in this checkpoint |
| `trainingEligible` | Always `false` in this checkpoint |
| `usePolicy` | `REQUEST_SCOPED_INFERENCE_ONLY` |

The server emits these records as V3 `SOURCE` events. Source data is operational evidence and is never appended to assistant prose by the browser.

## R39 grounding boundary

After evidence passes safe fetch, the server appends one server-created `SYSTEM` history turn immediately before the current user turn. This preserves the existing response-directive prefix and prior conversation order.

The grounding block labels source text as untrusted reference data, instructs the model to ignore instructions found inside sources, includes source IDs/URLs, and asks the model to cite source IDs. Content is bounded to 8,000 characters across at most five sources. Chat-control token markers are neutralized before prompt composition.

The resulting execution route is reported as `LOCAL_R39+REMOTE_WEB_EVIDENCE`. It must not be reported as wholly local.

## Lineage receipt

The terminal event may include `knowledgeReceipt` with:

- contract and provider identity;
- SHA-256 of the redacted bounded query;
- redaction count;
- collection time;
- source count and IDs;
- deterministic evidence-bundle SHA-256;
- skipped-source count;
- `REQUEST_SCOPED_EPHEMERAL` retention;
- `trainingEligible: false` and `rightsStatus: UNASSESSED`.

The receipt supports audit and replay comparison. It is not a claim that the underlying page is true, complete, current, legally reusable, or suitable for training.

## Explicit failure classes

Representative classes include:

- `ONLINE_EVIDENCE_DISABLED`;
- `ONLINE_EVIDENCE_PROVIDER_NOT_CONFIGURED`;
- `ONLINE_EVIDENCE_PROVIDER_UNREGISTERED`;
- `ONLINE_SEARCH_FAILED`;
- `ONLINE_EVIDENCE_EMPTY`;
- `EVIDENCE_URL_*`, `EVIDENCE_DNS_*`, `EVIDENCE_ADDRESS_REJECTED`;
- `EVIDENCE_FETCH_FAILED`, `EVIDENCE_HTTP_REJECTED`, `EVIDENCE_MEDIA_TYPE_REJECTED`;
- `ONLINE_EVIDENCE_UPSTREAM_UNSUPPORTED`.

Failures remain operational events/categories. They are not assistant text.

## Persistence and privacy

This source implementation does not create a server-side evidence database, cache, crawler, or training corpus. Source text exists only in request memory. Browser-local conversation exports may preserve source metadata and bundle receipts, but not the fetched source body added to the model prompt.

Enabling durable collection, analytics, user-content capture, or training requires a separate checkpoint with retention, consent, deletion, rights, security, and dataset-lineage approval.

## Compatibility and rollback

- V2 offline requests and event types remain unchanged.
- V3 is required only for explicit Online Evidence.
- An upstream V2 Chat route is not silently used for V3.
- Rollback is disabling `SWRLZ_ONLINE_EVIDENCE_ENABLED` or reverting this review branch; offline V2 remains available.
