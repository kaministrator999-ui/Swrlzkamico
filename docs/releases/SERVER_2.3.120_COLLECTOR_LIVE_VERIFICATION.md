# Server 2.3.120 — bounded live collector verification

Date: 2026-09-13
Checkpoint: FROZEN-WEB-COLLECTOR-001
Status: verification workflow prepared; live result pending.

## Authority and purpose

Runtime baseline 84918d106df0291633d782c8ca703d66499c082b: Server 2.3.119, Deployment Control 1.0.4, Collector 1.0.8. Authorities and VERSION.txt were re-read at the commit boundary. This event advances Server to 2.3.120 and Deployment Control to 1.0.5; Collector remains 1.0.8. Intervening Chat and server work is preserved.

Collector 1.0.8 was published by commit a7d2cc0d99ba399c288ba8f82e8eb7582b746231 (Server 2.3.104). It uses Vercel's metadata ETag to bind mutable state to a consistent cache-bypassed read, retains conditional writes, and rejects missing versions. The user's preceding screenshots confirmed HTTP 412 ETag mismatch for Start and Configure on 1.0.7. The complete deterministic collector suite and transport regression pass. The real production save remains the acceptance gate.

Production readiness at 2026-09-13T19:36:26Z confirmed Collector 1.0.8 and engine SHA-256 95e9b808c9f35360804e047dc02ba13d8df2f7cb93e1a53b66879e33c4e0caa5, with private storage configured and runtime changes requiring no deployment.

## Verification operation

The new main workflow uses the existing VERCEL_TOKEN and the already connected production project's environment privately in an ephemeral GitHub runner. Project/team IDs and API origin are fixed. No credential values, private state contents, or downloaded environment files are published; environment and CLI capture files are removed on exit. It uses the same production environment protection as the existing deployment workflow.

The script reports only storage-version comparison flags and an acceptance receipt. It verifies the expected live collector source, reads authenticated state, refuses a running collector or active seal, sends exactly one configure action with an empty patch, then reads state again. An empty patch persists the current server configuration without replaying values from a previous read. Success requires a higher durable revision, identical configuration and source registry, and unchanged snapshot/lifecycle/training/counters on reload. Redirects are rejected and failed writes are not retried. No start, pause, collection, sealing, training acceptance, or deletion is performed.

## Trigger and deployment boundary

The verification workflow runs only by workflow_dispatch or a main change to .collector/VERIFY_REQUEST.json. This commit deliberately requests the bounded verification. It contains no deploy, build, restart, environment modification, or secret-creation command. Current vercel.json disables Git deployment, and the separate production deployment workflow watches only .deploy/REQUEST.txt or explicit dispatch. That file and workflow remain unchanged.

The script syntax and safety fixtures pass: fixed origin, no redirects, exactly one empty configure patch, and no write if collection is running. YAML parsing, bash syntax, and verification/deployment trigger separation pass. The expected collector engine remains pinned in the request file so another source event cannot silently receive this event's acceptance.

## Continuation

Read the verification run and append its actual status, provider-version comparison, durable revision receipts, and any remaining errors. A successful readiness response alone must never be described as successful storage writes.


## Server 2.3.120 / Collector 1.0.8 live verification — 2026-09-13

Runtime event commit: 92b4865b0466c77bfdefc595911ef2932c018b12. Collector repair commit: a7d2cc0d99ba399c288ba8f82e8eb7582b746231. Deployment Control advances to 1.0.5; Collector code remains 1.0.8.

The user's 1.0.7 screenshots confirmed HTTP 412 ETag mismatch on both Start and Configure. The 1.0.8 repair now uses the Blob metadata ETag, brackets the uncached state read, and rejects missing/changing versions rather than writing without a condition. Complete deterministic verification passes. Production readiness at 2026-09-13T19:36:26Z reports the exact 1.0.8 engine hash and private storage configuration.

This event runs a bounded, separate GitHub verification job using the existing project's production credentials privately. It saves the current configuration with an empty patch and verifies a fresh read, without starting/interfering with collection or training. Environment/credential files remain only in the ephemeral runner and are deleted; logs contain no state contents or credentials. The browser sign-in limitation is no longer the planned acceptance path.

The new .collector/VERIFY_REQUEST.json trigger runs verification only. Current Git deployment is disabled; .deploy/REQUEST.txt and the existing deployment workflow are unchanged. No redeploy/restart is requested. See docs/releases/SERVER_2.3.120_COLLECTOR_LIVE_VERIFICATION.md for the exact operation and pending acceptance receipt.


## 2026-09-13 live result — verification incomplete

[Run 34778401085](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/34778401085) failed before any configuration write. Both metadata and private delivery reads returned HTTP 200. The metadata ETag was strong, the delivery ETag was weak, and they differed. This confirms the provider-version mismatch behind the user's HTTP 412 reports. Readiness matched Collector 1.0.8 and its exact published engine hash. The following authenticated status request returned HTTP 401; no configure action was attempted. This result must not be called storage-write acceptance. Server 2.3.121 adds explicit handling for non-readable credential exports and a separately scoped exact-engine/private-Blob verification using the existing storage credential.
