# Server 2.3.121 — collector storage acceptance with explicit credential scope

Date: 2026-09-13
Checkpoint: FROZEN-WEB-COLLECTOR-001
Status: production storage acceptance PASS; signed-in browser/API action not verified.

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


## Production storage acceptance — PASS (2026-09-13T19:52:26Z)

[Verification run 34778963286](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/34778963286) completed successfully from main commit 2d7e7125e55b65b55057746641b79b6ad996176b. Runtime verification authority/docs commit: 3598deb92a00e08d469e5a712a95c30fff615054. The exact live Collector 1.0.8 source was pinned to SHA-256 95e9b808c9f35360804e047dc02ba13d8df2f7cb93e1a53b66879e33c4e0caa5.

The real collector state advanced from revision 1 to 2, and a new BlobStore session read back revision 2 with all saved content identical. Configuration and every collection-content field remained unchanged. Collector remained idle with 1 source, 0 documents, and 0 training acceptances. No crawl, Start, source edit, seal, training decision, or deletion was performed.

The run confirmed that the exported application credential is redacted. Therefore no API mutation was attempted: this is production-blob-exact-engine acceptance, with apiWriteVerified=false. It verifies the actual configure action and conditional persistence against the real private store; signed-in browser/API action acceptance is not claimed. The earlier HTTP 401 was caused by submitting the export placeholder, not evidence that the user's actual administrator credential is invalid.

The provider metadata ETag is strong; delivery returns a different weak ETag. This production evidence confirms the root cause of the user's 412 errors and accepts the Collector 1.0.8 metadata-token repair. Public readiness reports the exact repaired source, configured private storage, and deploymentRequiredForRuntimeChanges=false. GET /collector returned HTTP 200 with the expected page, Start new and Save safety configuration controls, and Cache-Control: no-store. The user can refresh /collector and retry the signed-in action.

No Vercel deployment/restart or credential configuration change was made for the repair/acceptance. Production remains on the independently deployed main 9a962f2165b291876c091ac8351fed80ae54da62 (stable Server 2.3.109); Server 2.3.121 records this runtime/verification event and does not imply a new stable binary deployment. Authority and source/verification files remain on their owning branches. This documentation commit closes the existing Server 2.3.121 verification event without changing code or module versions.

```json
{
  "apiWriteVerified": false,
  "applicationCredential": "redacted",
  "beforeRevision": 1,
  "collectionContentUnchanged": true,
  "collectionStatus": "idle",
  "collectorVersion": "1.0.8",
  "configurationUnchanged": true,
  "documents": 0,
  "engineSha256": "95e9b808c9f35360804e047dc02ba13d8df2f7cb93e1a53b66879e33c4e0caa5",
  "ok": true,
  "reloadedRevision": 2,
  "savedRevision": 2,
  "scope": "production-blob-exact-engine",
  "sources": 1,
  "statePersisted": true,
  "trainingAccepted": 0
}
```
