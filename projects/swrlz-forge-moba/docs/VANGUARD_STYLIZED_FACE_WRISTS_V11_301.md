# §E v11.301 — Hooded Vanguard: face, painted UVs, hand A-pose

## Evidence
Owner Android screenshot of v11.300 shows a poorly proportioned/blurry facial image, patches of high-contrast illustrated photographic source applied to armor/scarf/coat, and fully down-facing palms/fingers despite both forearms angling diagonally outwards. A successful source-image load was not a correctly authored, stylistically unified game texture.

## Focused changes
1. **Face mesh and front-only UV artwork:** build a continuous face mesh with gently broadened jaw and smaller sculpted nose, author matching blue-gray eyes, brows, cheek shade, nose and lips in one coherent skin UV atlas. Face art is restricted to front longitude, so the neck/side and back do not acquire a second face.
2. **Eleven native game-material paintings:** paint purpose-designed mapped albedo canvases for hair, hood, scarf, charcoal cloth, breastplate, pauldrons, teal coat, belt leather, gloves, boots and skin. Use gold trim, stitched seams, fabric folds and form-specific highlights at the correct UV coordinates rather than source-image collage rectangles. The original generated image remains available in the release history as a color/design reference; no false claim that its photographs are directly mapped.
3. **Cohesive chest armor:** change the rigid rectangular chest front to a tapered lower point and maintain native UV alignment.
4. **Neutral hand directions:** rotate both native five-finger hand geometries around their own cuff/wrist centers approximately 0.64 rad in opposite directions. The long axis of each hand follows the downward/outward line of its forearm, not world-down. Slightly scale finger length to avoid oversize hands; preserve geometry/UV correspondence and all fingers.

## Invariants and checks
Only newly created Starter Models Hooded Vanguard projects get this override, not existing local/account models or other starters. All **17 editable mesh part IDs** remain. Hands retain fingers; new geometry and UV indices validated. Tests exercise exact authored atlas assignment for *every* late-created material to catch blank texture cache regressions, reject photographic cutout copy operations, check left/right rotated finger tips, face UV art and geometry, and inspect app source syntax. Full build SHA/size measured and sealed before release. Final face likeness and artistic quality need real phone/Quest acceptance.

**Not included:** bird, weapon, facial skeleton/animation, full-body rig or general model-editor UI changes.
