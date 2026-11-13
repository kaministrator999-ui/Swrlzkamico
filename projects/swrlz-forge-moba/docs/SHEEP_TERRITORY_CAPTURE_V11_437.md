# §E v11.437 — Sheep Tag AI home territory and capture hitches

Date: 2026-11-12. Builds on the independently sealed v11.436 satchel/cube release. Native Quest acceptance pending.

## Source findings
- The effective standard and Quest AI base planners both used the first 12 existing sheep-owned houses as candidate locations, even those built by the controlled player. A shared ownership-blind list could draw the flock to the player's new construction.
- Capture already employed the v11.136 batch-navigation invalidation and at-most-two visual disposals per subsequent simulation tick. That existing protection was retained, rather than duplicated.
- Captured-wisp creation still invokes the native wisp factory synchronously. This release prepares at most four hidden, unattached wisp models gradually during solo Quest play, and uses the pool on captures when available. An early/rapid capture can fall back to native creation.

## Scoped changes
The fallback AI planner and v11.411 Quest planner both use independent deterministic candidate locations around the sheep's authored home. Candidate and construction plots avoid the controlled sheep's house cluster and other already assigned bases. The original Quest one-candidate-per-game-tick planning and v11.419 path-search quota remain in force. Solo behaviors change; LAN network authority, simulation mode, controlled sheep placement, rescue and wolf logic remain native.

The spirit pool is session-owned and disposed on Stop. Capture CPU timings and pool hits/misses are exposed by `SWYRL_ENGINE_SHEEP_TERRITORY_CAPTURE_437.diagnose()` (does not measure GPU/Quest compositor stalls). No extra render loop or polling interval is introduced.

## Verification
A GitHub Actions source-seal preview verified the 414-patch build against JavaScript syntax and standalone functional tests: [source-seal run 43365462216](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/43365462216). The identical current authored patch source and runtime produced 9,947,658 bytes, SHA-256 `b1bfaf78a0c16c87ed96f826e574e857c904a85746f6707dccf1505d148be309`.

Physical Quest acceptance remains needed: watch whether teammates establish independent areas, whether building next to the player still causes convergence, capture-frame pauses and final-capture win transition. This release does not guarantee zero headset hitches.
