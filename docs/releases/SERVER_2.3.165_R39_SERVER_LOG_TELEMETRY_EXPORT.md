# Server 2.3.165 — R39 server-log deep telemetry export

## Scope
- Overall Server Runtime: 2.3.165
- LALM Engine: 2.1.49
- R39 hot revision: `2.1.49-hot-server-log-deep-telemetry-v38`
- Deployment: none
- Restart: none

## Evidence that triggered this event
Server 2.3.164 / R39 v37 generated observation-only inference telemetry as stream STATUS events, but production Vercel runtime-log searches did not expose those engine measurements. The telemetry existed inside the inference event stream but was not exported to server stdout, leaving external diagnostics unable to directly inspect prefill/decode performance.

## Change
R39 v38 wraps the proven v37 engine and exports bounded structured lines prefixed `SWRLZ_R39_TELEMETRY` to server stdout. Each record is correlated by `requestId` and includes the active engine version/revision.

Exported observations include:
- inference start/end;
- safe phase transitions;
- prefill start and wall time;
- decode start and prefill wall time;
- first-delta wait/total timing;
- engine PERF_METRICS parsed into TTFT, cached/uncached token counts, prefill seconds/tok-s, batch tokens/blocks, serial-prefill tokens, fallbacks, decode tokens/compute seconds/tok-s;
- terminal event/summary and total elapsed time.

## Privacy / authority boundary
This is observation-only. It does not alter prompting, inference, sampling, semantic acceptance, generated text, canonical state, or client behavior. Server-log telemetry deliberately excludes prompt text, history text, PREFILL_TOKEN text, response text, credentials, cookies, authorization material, and other content-bearing fields. Request identity is retained only for diagnostic correlation.

## Runtime lineage
- v37 source pinned at commit `337aa9838a867432073b4c814298b6bfb266072f`.
- v38 source creation commit: `5562e716e5d8ae70e57c71776ce101305ef329e4`.
- hot entrypoint update commit: `8f876586b8bd4f872803f520b5f9a73e0923cadd`.
- Server Runtime authority commit: `957e8de5a5d167bc3f26128270120fc839b8e704`.
- LALM Engine authority commit: `7c6617843786bc4aeb2538b0caed372f9c9528fe`.
- hot manifest update commit: `159c7adf55ebc029d51aeb5f75c4cb9f913c32a4`.

## Acceptance criteria
A fresh Chat generation must produce `SWRLZ_R39_TELEMETRY` records in production runtime logs for the same requestId as the canonical Chat turn. A completed inference should expose lifecycle timing and, when the underlying batch adapter emits PERF_METRICS, parsed prefill/decode performance fields. No prompt/response text may appear in these telemetry records.
