# Sheep Tag · Moonbell Meadow

The v10.1 starter follows the player's **SE_Sheep_Tag_Complete_Design_Archive.docx**, prepared 11 October 2026. Sheep survive through movement, precise house placement and wisp rescues; wolves chase, break houses and guard the central pen. The [archive decision ledger](SHEEP_TAG_ARCHIVE.md) records fixed intent, provisional experiments and ideas left open for playtesting. This is a local player-and-bots starter; it does not claim network multiplayer.

## Open and play

Choose **Sheep Tag · Moonbell Meadow** in **Projects**, or [open the archive starter](https://kamiloki-swrlz-forge-moba.static.hf.space/index.html?project=sheep-tag-meadow). Press **Sheep Tag** to choose your Sheep/Wolf role, the **Classic** or **Archive** preset, round time, head start and tuning; then use native **Play**. The new authored scene contains **92 baked actors in six populated layers**, with eight sheep, three wolves, a central wisp pen, four merchants, twelve thorns, nine ground-paint tiles and two no-build zones. Team sizes and starts remain editable scene actors.

The default **Archive** map enables thorn sensing, stealth totems, raised routes and Illusive Split. Special events remain off until selected. **Classic** keeps the house-maze, demolition, capture and rescue loop while disabling all four magic experiments and events. Either preset has a provisional 20-minute round and 30-second sheep head start. Sheep win with at least one survivor when the timer expires; wolves win when every real sheep is captured at once. A tagged sheep becomes the engine's Dragon's Den-style wisp at the pen. A live ally must reach it and maintain the configured rescue contact; there is no automatic timed revival.

Tap/click ground to move. Select your sheep, wisp, wolf, friendly house or a visible target; **My unit** returns to your controlled unit. A wolf can tap a visible sheep or house to attack. Sheep select a building and tap a valid site; they travel to it, pay and construct it. **Q**, **E** and **F** select House, Income house and Fortified house. **Cancel** or **Escape** leaves placement. Select an owned house to **Upgrade house** or **Sell / clear**; wolves buy **Wolf upgrade** near a merchant using earned bounty.

Pan with **WASD/arrows**, right-drag or Space + drag on desktop, or drag on a phone. Tap the minimap to explore, use **Following** to return to your selected unit, and **＋/−** or the mouse wheel to zoom. **Pause** freezes the match; **Restart** starts cleanly; **Stop** restores the authored map and editor view.

## House maze craft and chase

Fine placement snaps to **0.15 ground units**, with a coarse 3-unit option. The preview draws the exact footprint, rotation and rejected overlap. Houses have a 2.4-unit base footprint; the provisional sheep and wolf collision radii are 0.27 and 0.68. A narrow opening can admit a sheep while blocking a wolf. Two houses can also close a sheep's exit completely: the engine allows deliberately bad spacing and does not automatically open a route or move the player out of the trap. True overlaps, occupied physical units, the protected pen and no-build zones reject placement without charging.

| Building | Shortcut | Candidate cost | Construction | Candidate health | Income |
| --- | --- | ---: | ---: | ---: | ---: |
| House | Q | Free | 1.4 s | 180 | — |
| Income house | E | 60 gold | 3 s | 240 | 3 gold/s after completion |
| Fortified house | F | 100 gold | 4 s | 650 | — |
| Castle wall | — | 45 gold | 3 s | 360 | — |
| Ramp | — | 55 gold | 3 s | 300 | — |

Live sheep receive 1 gold/s. Upgrades spend gold; selling returns half the paid investment. Candidate ownership limit is 28 houses per sheep. Wolves earn bounty by demolition and tags; the rules expose chase speed, strike damage, interval and building health. The default wolf speed/damage are **7.2 units/s and 85 per strike**, versus sheep speed **5.4 units/s**; these are test values, not a permanent balance commitment.

Sheep bots choose formations and escape lanes rather than scattering houses without purpose. Wolves pursue observed targets, breach a blocking house and reroute. Both use species-aware paths, terrain and building collision. Fog can use shared team vision, individual vision or be off. Hidden enemy locations do not appear in player selection, hunt commands or minimap; AI uses observed movement and last-known clues rather than an unconditional location feed.

Capture removes the victim's houses. A wisp remains in the pen and cannot build. Live allies return through a viable rescue route; the default contact hold is 0.6 seconds and post-rescue protection 3 seconds. Enemy guarding and route timing remain part of the rescue game.

## Archive experiments

Enable and tune each experiment independently in **Sheep Tag → Rules & tuning**. Every listed number is provisional, except the player's **more than eight houses** condition, implemented as nine or more qualifying allied houses.

| Experiment | Candidate behavior and controls |
| --- | --- |
| Thorn sensing | Bush contact has a 0.35 prick chance, temporary 15-second scent and a 6-second retry cooldown. Wolves receive approximate pulses, not a continuous exact position. Duration, chance and pulse timing are editable. |
| Stealth-shifting totem | Nine allied houses within the candidate 8-unit settlement radius qualify. Select an owned house and **Convert to totem**: it replaces that house. Nearby allies fade while inside its 5.5-unit effect, then gradually return on leaving. Choose once per sheep per match or a configurable repeat cooldown; neither is declared final design. |
| Castle walls and ramps | Build and rotate connected ramp/deck pieces, then use **Move: upper route** to travel up a reachable ramp. **Descend ramp** returns via a connected descent. Deck height defaults to 3.3; wolves can use connected ramps when configured and can destroy structures. A deck click never teleports a sheep upward. Tag and rescue respect vertical separation. |
| Illusive Split | Survival and rescue progression unlock a mirrored escape at candidate level 2. **Illusive Split** sends a convincing temporary sheep copy on a different vector. Contact dissolves the copy; the real flock totals, income and rescue rules exclude decoys. Candidate cooldown/lifetime are 30/5 seconds. |
| Warned events | Separately opt in and select the provisional **Hunt pressure**, **Deep fog** and **Supply windfall** pool. Both roles see an advance warning and duration. Candidate interval/warning/duration are 150/8/15 seconds. A positive seed repeats random choices for tests; zero chooses a new match seed. |

The event pool is an implementation experiment rather than adoption of every illustrative event in the archive. Pond cleansing, advanced illusion tiers, automatic structural collapse, every proposed event/reward and a future multi-game hub remain undecided future scope.

## Map Creator and native editor

Open **Map Creator** while stopped. Paint grass, earth and road tiles; place a forest brush, trees, rocks, ponds, thorns, sheep/wolf starts, the wisp pen, merchants and walkable no-build zones. Add authored houses, walls and ramps when testing a route. Rotate pieces, choose brush width and placement snap, or switch to **Pan / select** for native Move/Rotate/Scale. **Compare sheep / wolf routes** previews traversal without starting a match or moving authored actors.

**Map rules & experiments** edits vision, flags and allowed player structures; **Rules & tuning** opens the full settings. **Playtest map** invokes the native Play button, and Stop returns to the editable map. Native Undo/Redo retains creator changes. **Save map file** exports the curated `swyrl-sheep-tag-map-v1` schema; **Load map file** validates the allowed actors/rules and required sheep, wolf and pen. No arbitrary scripts are imported. **Save project / Load project** preserve the complete native `.swyrl.json` editor scene. Preview marks and runtime buildings, decoys, magic effects and fog are excluded from saved maps.

The new native map is [`scenes/sheep-tag-moonbell-archive.swyrl.json`](scenes/sheep-tag-moonbell-archive.swyrl.json). The released [`scenes/sheep-tag-meadow.swyrl.json`](scenes/sheep-tag-meadow.swyrl.json) remains byte-identical with its 66 actors, four layers, six sheep and two wolves. Its old file retains original saved rules; current engine rules fill new fields with Classic defaults when absent. The animation and Dragon Den starters remain separate projects.

## Research sources

Research completed 2026-10-11. No third-party map, textures, artwork or game code are bundled.

| Source | Design evidence |
| --- | --- |
| [Cryo's Sheep Tag Reforged map description](https://wc3maps.com/map/89197) | Sheep survival versus hunter capture, central wisp pen, contact rescue, farm destruction bounty and corner shops; 15-minute variant. |
| [Sheep Tag Ultimate 3.5 description](https://wc3maps.com/map/5941) | Friendly-wisp rescue using right-click; timer differences between editions. |
| [GosuSheep v7.1z](https://wc3maps.com/map/41482) | Four hunters, 20-minute survival and a 128×132 map listing; these are that variant's settings. |
| [Behh Edition 8.3](https://www.gamefront.com/games/warcraft-iii/file/sheep-tag-behh-edition) | Twenty-minute survival and cash-farm income every four seconds. |
| [Sheep Tag 2 sheep guide](https://sheeptag2.com/guides/sheep/) | Successor's farm-grid escapes, tight sheep passages and removing owned farms. |
| [Sheep Tag 2 farm reference](https://sheeptag2.com/guides/farms/) | Successor's basic blockers, stronger farms, savings structures and support farm roles; exact prices are not universal WC3 rules. |
| [Sheep Tag 2 resources](https://sheeptag2.com/guides/resources-and-stats/) | Successor's alive-player income and economy/upgrades. |
| [Sheep Tag 2 spirits](https://sheeptag2.com/guides/spirits/) | Capture penalty and farm removal before rescue/rebuilding. |
| [Terrain gallery](https://sheeptag2.com/terrains/) and [gameplay screenshots](https://sheeptag2.com/) | Central fenced pen, open grassy playfields, peripheral terrain, color-owned farm grids, small sheep and larger wolves. |
| [Sheep Tag Relapse author's comparison](https://github.com/W3Madhatters/Sheep-Tag-Relapse) | Distinguishes classic prison/rescue from roaming spirits and automatic revival; this starter follows the central-pen loop. |

## Acceptance and release authority

[`tests/sheep_archive_playwright.mjs`](tests/sheep_archive_playwright.mjs) is the tenth desktop/phone browser suite, alongside the original Sheep Tag suite and all eight animation suites. Acceptance must exercise actual native Play and canvas inputs for fine gaps/self-traps, attack/demolition, fog and observed-only AI, wisp rescue, thorn sensing, nine-house totem conversion, connected vertical traversal and failure, split progression/contact, warned event opt-in, creator brush/paths/import/export and clean native Undo/Redo/Save/Load/Pause/Restart/Stop. All six required engine CI workflows remain required.

v10.1 uses `patches/v10_1_sheep_tag_archive.py`, artifact `swyrl_engine_v10_1.html`, marker `V10_1_SHEEP_TAG_ARCHIVE`, 61 governed patches and 23 assets. These documents do not claim unrecorded v10.1 acceptance or deployment success. The final sealed manifest and `SOURCE.json` provide exact integrity. Production completion requires the final deliberate `DEPLOY_REQUEST.json`, terminal success of its exact dedicated deployment and hosted matching of normalized engine bytes, the current marker, the source receipt and all 23 assets.

The v10.0 starter is verified historical production: [PR #106](https://github.com/kaministrator999-ui/Swrlzkamico/pull/106), merged source `a06c89ed9e6cd65737de111efc11cac268519449`, final trigger `87b6a4be9319be30ac22b99212d773a289d2b199`, [deployment 38174454216](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38174454216) and [hosted audit 38174501776](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38174501776). It sealed 60 patches, 1,290,101 bytes, SHA-256 `abcab023bbec0b5cacc72d7b845096060feb56418ab12b9eacee62bf9b7bf8c4` and 22 assets. All nine desktop/phone suites and fourteen live gameplay checks per layout passed. Those receipts certify v10.0, not the new archive candidate.
