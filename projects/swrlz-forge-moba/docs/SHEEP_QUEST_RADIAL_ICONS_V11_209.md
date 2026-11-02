# §E v11.209 — Sheep Tag Quest quick-wheel graphical overhaul

## Scope
**Sheep Tag PLAY only.** Native v11.204 hold/tap controls, game authority and native quick house lattice are retained. No gameplay house rotation tools.

## Graphical radial changes
- **Illustrated icons:** Farm, Income Farm (gold), Fortified Farm, Mirror, Totem and Cancel/None. Original procedural canvas artwork (128×128 icon texture) is generated once per icon key per XR session, then reused on both center and perimeter elements.
- **Visible selection feedback:** translucent segmented angular wedges, brighter active sectors, 10% active icon enlargement, a central preview of the current selected item, distinct label positions and a restrained eight-point fixed glint ring. Haptics remain owned by v11.204 only when selection changes.
- **Native costs:** cost values from `stBuildingConfig`, with current player `stSession.resources` used to dim unavailable houses and show `NEED N GOLD`. No fake fixed price numbers. The final build validator still owns cost, footprint and permissions.
- **Abilities:** native rules detect disabled Mirror/Totem; Totem displays SELECT HOUSE when no relevant building selection is present. The native command validates ownership and cooldowns when cast; this graphic layer does not fabricate cooldown remaining times.
- **Budget:** two small cached wheel roots, no separate frame loop, no additional saved scene actors, only short-lived handful of sector/label GPU meshes while a wheel is visible. Icon textures and materials are disposed on XR end, shared Quest `se195Text` cache is released by its previous owner.

## Other requested scope
v11.208 map region art and fog-depth pass stays. Issue #320 continues to track physically validated Quest FPS, full multiple floating camera/inspector panels, persisted panel layouts, an extended contextual control legend and further level-model polish. That work is not presented as complete.

## QA
Run `node projects/swrlz-forge-moba/tests/test_v11_209_radial_icons.cjs` plus v11.208/v11.207 prior VR release regressions. Strict version/hashes from 241 ordered patches and original 68 assets must pass before merge/deploy.
