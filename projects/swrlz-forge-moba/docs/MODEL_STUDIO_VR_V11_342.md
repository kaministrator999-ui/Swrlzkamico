# §E v11.342 · Native Model Studio VR proxy picking

## Quest 2 observation
After v11.341, one controller aimed at the native simple skinned-hand model still reduced FPS; two aimed controllers slowed further. v11.341 had throttled per-controller hover to ~18 Hz but still used `Raycaster.intersectObjects(roots,true)` against skinned parts for each sample and sometimes a CPU-computed skinned mesh bounding box.

## Corrected path
- Idle hover: cached conservative Box3 intersection for each visible model part, including skinned models. **No model triangle tests and no per-vertex CPU skin bounds during idle hover.**
- Trigger and grip: unchanged exact geometry raycasting and native selection/transform validation, so clicking between fingers does not become an approximate box selection.
- Both hands: refreshed native projection only when the model revision changes; controller hover timers aligned so both benefit from one per-frame matrix update.
- UI targets: world transforms now refreshed when layout changes, not on every controller hover hit test.
- Inspector: `se340ModelXRInspect()` includes a read-only `picking` snapshot with counts and `lastHoverMs`/`maxHoverMs`.
- **Tradeoff:** the displayed hover reticle/box uses approximate coarse shape bounds; precise selection occurs on trigger/grip. Skinned animations outside conservative bounds can leave hover less exact, without changing click accuracy.

## Validation
Candidate [GitHub Actions run 42448714716](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/42448714716) succeeded on 353 ordered patches. Controlled Node test simulates both controller hovers and proves zero model mesh raycast calls; exact trigger still calls geometry raycasting and model matrices refresh once per XR frame. Source bundle is 9,122,053 bytes, SHA-256 `ab1f1309ac860c540583db730c4ff1866be5fc074f73ca220181a6cf5029a4ad`.

## Owner test
On Quest 2 in Model Studio: display the simple hand at normal scale, move one ray from clear space to inside the hand bounding region, then repeat with both rays. Observe FPS under stationary and moving pointers. Trigger an actual fingertip and a gap between fingers; selection must follow precise mesh rather than coarse hover. Check grip/release, recenter and orbit/pan. Model and Game XR remain separate.

No physical Quest measurements are claimed from automated software checks.
