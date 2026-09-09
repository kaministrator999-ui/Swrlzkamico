# SWRLZ LLM Stream V3

- Contract ID: `swrlz_llm_stream_v3`
- Checkpoint: `SWRLZ-WEB-KNOWLEDGE-001A`
- Status: review candidate; not deployed
- Extends: `swrlz_llm_stream_v2`
- Evidence contract: `SWRLZ_ONLINE_EVIDENCE_V1.md`

## Compatibility rule

V3 is an opt-in extension for Online Evidence. It does not replace V2. Offline Chat continues to request and receive `swrlz_llm_stream_v2` with schema V1/V2 compatibility.

Every V3 event has:

```json
{
  "protocolVersion": 3,
  "schemaVersion": 3,
  "contractId": "swrlz_llm_stream_v3"
}
```

V3 preserves the V2 sequence, identity, terminal-flag, and Truth Firewall rules. Sequence values are strictly increasing and terminal types remain `COMPLETED`, `CANCELLED`, and `FAILED`.

## Event types

V3 supports:

- `STARTED`
- `STATUS`
- `ROUTE`
- `SOURCE`
- `DELTA`
- `RESET`
- `COMPLETED`
- `CANCELLED`
- `FAILED`

Only `DELTA.text` is assistant response text. `SOURCE`, receipts, status, route identity, reasons, categories, and failures remain separate evidence.

## SOURCE event

`SOURCE` is non-terminal and carries one server-validated `source` object defined by `swrlz_online_evidence_v1`. Its top-level `text` remains empty. A browser may render the validated HTTPS URL as a separate source link, but it must not merge title, URL, metadata, or retrieval diagnostics into the assistant message body.

## Route identity

Online Evidence with local R39 reports:

```json
{
  "identity": {
    "route": "LOCAL_R39+REMOTE_WEB_EVIDENCE"
  }
}
```

This identity is used on all V3 events, including events projected from the local engine.

## Terminal receipt

Once an evidence bundle exists, `COMPLETED`, `CANCELLED`, or `FAILED` may carry `knowledgeReceipt`. The browser validates the receipt contract ID, bundle hash format, and `trainingEligible: false` before retaining it as message metadata.

A failure before evidence collection may have no receipt. Its classified reason still proves that no silent offline fallback occurred.

## Browser reconnection boundary

V3 retains the request ID and event sequence rules. Because this checkpoint adds no durable server-side evidence/job store, a transport retry may repeat retrieval for the same request ID on another Vercel instance. Production provider enablement must either add addressable request persistence or disable automatic V3 replay before rollout. This limitation does not affect default V2 offline behavior.
