# §E v11.321 — Enemy sight and busy Quest frame behavior

**Owner feedback:** Solo sheep versus three wolves is substantially smoother after v11.306. However a crowded match—with other teammate sheep alive and many houses being constructed—slows badly during head movement. Wolves also appear to keep following after entering the owner's fog-of-war.

**Important distinction:** The player's fog-of-war does not represent the wolves' vision. Wolves have their own vision range and, in team-vision mode, may inherit other wolves' current sightings. The existing AI also pursues a **last-observed position** for a limited time, and can investigate approximate scent clues. This is not equivalent to retrieving hidden live sheep coordinates. Nevertheless, `stPerceivesDirect` previously tested only radius/concealment and ignored houses between the observer and target, allowing unwanted line-of-sight through buildings.

## Targeted gameplay changes

- In fog-enabled matches, enemy **wolf ↔ sheep** sight now checks intersections between the observer-to-target segment and the world footprints of constructed houses. Rotated houses use oriented-rectangle slab intersection; destroyed houses do not block sight. Elevated routes remain unchanged until their separate vertical line-of-sight geometry can be tested.
- A per-observer/target cache for the same simulation tick avoids repeating house visibility checks, and correctly refreshes after movement or navigation revisions.
- Existing `stOrderTarget` last-known-memory search and `s.archive.scentClues`, visibility sharing, player input, blocking/collision, save data, LAN authority and capture rules are unchanged.
- During **WebXR gameplay only**, with at least two living sheep and at least eight live houses, the existing v11.256 shared escape-search budget changes from **two candidates per update to one**; every candidate is still considered in sequence using the same scoring. Normal matches and browser sessions retain the two-candidate budget.
- The prior v11.306 A* CPU counter incorrectly classified queries using the old hard-coded wolf radius `0.68` even though the gameplay-configured wolf radius is `0.78`. The appended patch corrects the counter's classification against the configured wolf radius.

## Diagnostic evidence for the next Quest comparison

Nerd Stats pages **9/10** and **10/10** complement preexisting pages 5/10–8/10, measuring busy-world head-moving and still frame gaps, late callbacks and previous completed-frame draw-call counts, plus occluded sight checks and current escape-search budget. These are callback measurements, **not GPU execution time**. No new headset pose reads, XR reference-space changes, renderer or frame loop were introduced.

Regression test `tests/sheep_sight_xr_crowd_v11_321.cjs` uses the **assembled HTML** with a sandboxed source slice to verify house occlusion, clear sight around corners, hidden/visible transition, rotation, destroyed-house invalidation, fog-off mode, same-tick caching and crowded-vs-solo budget. Exact source integrity is **342 patches / 71 assets / 8,451,859 bytes / SHA-256 `47e8cc9f9f54fb1592715961ecd4faab13fc94f56e0f8208c250efc3306b2079`**. Checkpoint is a source/syntax regression, not measured on Quest 2.

## Owner test

Use the same map and builds in two separate trials: all sheep and wolves active while constructing many houses, holding head still vs turning it; and the last-sheep / three-wolf chase around houses. Observe Nerd Stats pages 5/10, 7/10, 8/10, 9/10 and 10/10. Report whether the visible wolf can still anticipate a sheep moving behind a house from an **unseen** new direction. Do not infer GPU cause from frame callback gaps alone.
