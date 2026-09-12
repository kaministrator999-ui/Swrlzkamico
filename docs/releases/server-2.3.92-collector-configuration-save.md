# Server 2.3.92 — Collector configuration save repair

Date: 2026-09-12
Checkpoint: `FROZEN-WEB-COLLECTOR-001`
Collector: `1.0.5` → `1.0.6`
Server Runtime: `2.3.91` → `2.3.92`
Deployment Control: `1.0.3` unchanged
Deployment / restart: **NONE**

## Observed defect

After secure administrator sign-in, the live browser successfully read existing durable state and the private storage access test returned `storage check completed.`. The response-size configuration was hydrated as `1.430511474609375` MiB, exactly 1,500,000 bytes. Its HTML field required steps of `0.032` MiB starting at `0.032`. The browser reported `valid:false` and `stepMismatch:true`, preventing the existing settings from being submitted.

## Targeted repair

Only the response-limit input in `web/collector.html` changes. It accepts arbitrary decimal MiB values and its minimum/maximum exactly match the engine's 32,000–10,000,000 byte limits after unit conversion. The existing byte rounding and server validation remain authoritative. No collector engine, API/state schema, saved configuration, source registry, or training behavior changes.

## Lineage and verification

- Runtime baseline: `778bf62887a65e03d0b87da56748c797f2af911e`.
- Main workflow/evidence checkpoint: `f9dd1b8e80bd6e56cb4fdb2d4817c712dde6bbfc`.
- Router and affected version authorities were re-read immediately before version assignment.
- Static check confirms the HTML's scripts are byte-for-byte unchanged and converted field bounds match the engine.
- Current collector engine suite and missing-ETag new-snapshot revision regression passed during the preceding 2.3.91 verification.
- Live acceptance pending immediately after this source publication: reload the runtime-owned page, confirm native input validity, save the current settings, reload, and verify durable revision advancement with unchanged settings.
- Keep the collector idle; this repair does not authorize a crawl, source registration, sealing, or training acceptance.
- Rollback requires a new versioned runtime correction and must preserve the durable state and source registry.
