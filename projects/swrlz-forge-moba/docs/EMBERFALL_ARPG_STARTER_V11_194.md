# Emberfall · Shattered Vale — §E original hack-and-slash starter

## Creative direction and source research

An original dark-fantasy action RPG built with the native §E game-authoring scene and its existing Play mode. Mechanic-level references only; never copy protected characters, item names, art, maps, sounds, story, trademarks or unique UI assets.

| Reference | Design principle | Starter application |
| --- | --- | --- |
| Diablo II: Resurrected | Distinct active abilities, readable archetypes, loot that improves builds | Slash, arcane bolt and nova; equipment attack/armour rarity; elite Warden |
| Path of Exile | Player build customization and modular skills/passives | Upgradeable active abilities on level-up; a foundation for future modular skill components |
| Torchlight | Friendly accessibility, dungeon loop, companion and randomized items | Clear top-down controls, bright readable loot and an assisting lantern companion |

Primary public references: https://diablo2.blizzard.com/en-us/ ; https://www.pathofexile.com/passive-skill-tree ; https://www.torchlightgame.com/about/ .

## Native starter

Project card **Emberfall · Shattered Vale** under the existing §E Projects gallery; deep link `?project=emberfall-arpg`. Each new click generates a fresh editable project. No changes to the user's saved startup default, independently saved projects, or Dragon Den.

- Authored world: Wayfarer player, 11 enemies, one Cinder Warden boss, blightwood trees, cliffs, crystalline hazards, fallen shrine and a return-camp portal. Native actors remain editable/movable and save through §E's ordinary project JSON. Enemy / boss / player roles use the existing serialized actor role field.
- In Play: 2.5D high third-person camera; tap/click ground to move; target-click to approach and attack; WASD/arrows optional. Slash (Space), Bolt (Q), Nova (E), Healing Potion (R), plus mobile touch abilities and camera wheel zoom.
- Enemies chase, strike, take damage and disappear on defeat; a helper lantern floats near the hero and occasionally damages monsters.
- XP, gold and randomized common/magic/rare drops; proximity auto-pickup and straightforward automatic improvement to attack/armour. Skill upgrade points on level-up and a finite set of potions. Boss defeat marks the starter objective complete.
- State boundaries: enemies, effects, drops, player HP/XP/inventory and equipment are **play-session-only**; original authored map remains unchanged on Stop. This is intentionally not a persistent RPG character-save system.
- Quest browser rendering: normal responsive §E game editor and mobile HUD. Full VR ARPG hand controls, multiplayer, robust navmesh/pathfinding, class selection, procedurally generated dungeons, vendor economy, advanced inventory/equipment and damage-type balance are **future milestones**, not implemented here.

## Performance and acceptance

One existing Three renderer and animation loop; scene geometry uses native editor primitives and temporary low-poly VFX only. No external downloads or extra WASM. Keep <=12 native enemy actors. Test original project launch/exit, editor Save/Reload, zoom/movement/targeting, all abilities and cooldowns, potion limits, kill XP/loot, boss finish, Stop restore, Quest Browser frame stability, mobile input clearance, and regression to Sheep Tag, Maul, Dragon Den, Chat and Modeler.

## Future pieces (in priority order)

1. Physical browser/mobile acceptance and map-design polish (terrain blockers, terrain-aware click targets, damage flashes, audio).
2. Modular active skill components, class archetypes and meaningful upgrade branches.
3. Persistent character profile separate from authored scene project and explicit Save/Load, inventory and equipment slots.
4. Deterministic procedural rooms/dungeons, collision/navmesh, town portal, bosses and treasure rooms.
5. VR strategic ARPG perspective and Quest controller bindings, co-op networking through existing authoritative patterns.

## Release governance

Append-only `patches/v11_194_emberfall_arpg_starter.py`, runtime and styles, strict `source-manifest.json` version/integrity, verifier, and dedicated `DEPLOY_REQUEST.json` final commit only after validation. Preserve all 68 existing hosted assets. Hardware acceptance must be separately recorded; no optimistic claims.
