# §E v11.306 — Sheep Tag pursuit slowdown

**Owner reproduction:** With maximum houses and only the controlled sheep surviving, three wolves can attack stationary houses smoothly. Moving outside and causing pursuit produces a gradual whole-game slowdown; earlier, when **all sheep and all wolves** move, the owner also sees occasional stutter.

## Effective source, not obsolete base implementation

`runtime/sheep_lanes.js` overrides the original base `stBotWolf` and `stOrderTarget` logic. It probes up to **nine A* approach candidates** around a sheep. The old target cache required sheep movement less than 0.2 units and expired in 0.3 seconds. A running sheep exceeds that distance in very few frames, so three wolves can repeatedly probe routes while chasing, even with the same houses and same wolf actors already present.

The v11.256 sheep AI already distributes escape-route candidates across frames (`se256AIBudget.perFrame=2`) and is intentionally unchanged. The older v11.244 removal/nav invalidation optimization is also retained.

## Change

`patches/v11_306_sheep_pursuit_performance.py` adds one shared cached-approach function for the active `stLanesOrderTarget` path and the active `stLanesBotWolf` decision. A positive or negative approach result is reused for 0.40–0.56 seconds, conditional on target identity, current navigation revision, and sheep movement no more than two world units. Changes to building navigation invalidate the cache. No new controllers, timing loops, actors, physics, capture rules or XR camera calculations.

`runtime/sheep_pursuit_performance_v11_306.js` adds Nerd Stats pages 7/8 and 8/8. Measurements include A* calls and JavaScript CPU cost by **path radius**, cache hits/refreshes, update CPU time, and simulation/wall-clock progression. Wolf-radius queries can also be made by sheep evasive planning, so this is a **radius grouping, not caller attribution**. Callback gap is not GPU time; real-device measurements remain pending.

The base 50ms `stUpdate` simulation timestep cap was not changed: unbounded catch-up work could make a CPU-bound Quest frame worse. If simulation clock ratio drops during pursuit despite improved cache hits, a separately measured bounded-step change should follow.

## Test and release boundaries

A focused Node regression checks live-bundle cache reuse, substantial sheep movement and nav invalidation, short-lived negative caching, both callers using one cache, and preserved v11.256 budget. Sealed source is 337 ordered patches, 71 packaged assets, **8,397,357 bytes**, SHA-256 `a47415627055cda09f2152e9c6adc311347ed709971e6c0bea1be6bc7195910c`. JS syntax/source-integrity checks are performed by the dedicated v11.306 verifier. Successful deployment does not establish Quest FPS or visual comfort: the owner tests the two reproduction scenarios.
