# Server 2.3.121 — collector storage acceptance with explicit credential scope

Date: 2026-09-13
Checkpoint: FROZEN-WEB-COLLECTOR-001
Status: local verification passed; production storage receipt pending.

## Authority and previous failure

Baseline runtime commit 9769991aa364e631e08ced6252f4ed49d8177bda: Server 2.3.120, Deployment Control 1.0.5, Collector 1.0.8. VERSION.txt and each affected authority were re-read at the commit boundary. This event advances Server to 2.3.121 and Deployment Control to 1.0.6. Collector remains 1.0.8 because its production source is unchanged. Independent Chat and server work is preserved.

The preceding [verification run](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/34778401085) confirmed different storage metadata and delivery ETags (strong versus weak), then failed at authenticated status with HTTP 401 before any write. Vercel CLI supports a [SENSITIVE] marker for non-readable secrets; the prior script mistakenly treated every nonempty export as a usable credential. Whether that marker explains this deployment's rejection is explicitly reported by the next run, not assumed.

## Bounded verification

The job never submits the redaction marker as an application credential. It uses the public production readiness receipt to pin Collector 1.0.8 and SHA-256 95e9b808c9f35360804e047dc02ba13d8df2f7cb93e1a53b66879e33c4e0caa5. If the exported application credential is available and accepted, the existing one-empty-configure API verification runs. Only an unavailable/redacted credential or HTTP 401 on status before a write selects the independently authorized storage check; no failed mutation is replayed.

The storage check uses the existing BLOB_READ_WRITE_TOKEN, downloads the exact hash-verified engine from runtime commit a7d2cc0d99ba399c288ba8f82e8eb7582b746231, reads the real private collector state and passes that state and its strong metadata ETag through the engine's original configure action with an empty patch. A new BlobStore session must read identical saved content at exactly the next revision. Every state field except revision, update time, and the configure audit event must remain identical. Running collection and active sealing are refused. No start, crawl, reset, source change, training review, seal, or deletion is performed.

A storage-only result is labeled production-blob-exact-engine with apiWriteVerified=false. It proves actual production storage writes through the exact live code, not an authenticated browser/API action. Credential values and private state contents are never printed, uploaded, persisted in Git, or exposed to the model. The exported environment and captured CLI log remain private to the existing protected production runner and are removed on exit.

## Verification and delivery boundary

Local fixtures pass: the exact configure action advances one revision while preserving content; a running collector produces no write; a [SENSITIVE] value is never sent; Node syntax, YAML parsing, and bash syntax pass. The full collector transport/lifecycle suite already passed for unchanged Collector 1.0.8.

Only .collector/VERIFY_REQUEST.json triggers this bounded check. The production deployment workflow, .deploy/REQUEST.txt, stable loader/authentication, and vercel.json remain unchanged. No deployment, restart, secret creation, or environment modification is requested. Append the actual run result here before declaring storage acceptance.
