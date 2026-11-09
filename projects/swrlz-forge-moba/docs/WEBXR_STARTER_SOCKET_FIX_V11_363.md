# §E v11.363 — WebXR project starters: real-browser named-socket repair

## Root cause
The v11.361 release contains two converted hand mesh starters and two Quest 2 Touch controller mesh starters. The native-loader test was too permissive: its canonical model fixture did not include the `assemblies` field contributed by earlier patches. The actual v11.361 mobile browser click demonstrated the error `Invalid named socket`. Engine v11.294 already documented precisely the same failure with Hooded Vanguard: replacing the original Prism Jester model parts while retaining `assemblies.sockets[].partId` references to now-missing original parts causes native `loadProject` validation to reject the new model.

## Targeted repair
The v11.363 append-only patch clears only `project.modelAtelier.assemblies` in new WebXR reference hand/controller scenes before loading, and adds the same guard at the shared four-project starter loader. The Quest 2 controllers keep their 7-section `meshGroups`, real triangle topology, UV paint and named components. The Hand projects keep their 25 documented reference joint landmarks. No unrelated project data is modified. No new modeling overlays/panels.

## Checks
Native four-project loader checks use deliberate stale canonical `assemblies` data and verify cleanup before `loadProject`. A separate real mobile Chromium test clicks the four cards in Projects → Starter Models after dismissing native release notes, and verifies the visible modeling canvas, part list, active workspace and correct mesh count. Physical Quest 2 performance and fit are owner-tested after live deployment.
