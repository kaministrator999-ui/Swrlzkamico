# Frostveil Maul starter

**Shipped vs. planned gameplay:** See [Wintermaul Design Architecture — verified v11.1 minion-wave status](reports/WINTERMAUL_DESIGN_ARCHITECTURE.md#verified-v111-minion-wave-status-2026-10-14) for the exact feature matrix, including which special creeps, collision systems and game modes are **not implemented**. Do not interpret future design requirements as completed code.

## Current v11.1 candidate · Physical builders, tower mazes, protected entrances

The current **Frostveil Maul** starter (not historical imported maps) now uses **walk-to-build**: tower placement queues the chosen sector builder to path to a clear adjacent cell; the tower only exists after the builder arrives, when the game rechecks the route, footprint and available gold. Pausing freezes the walk. Moving a builder deliberately cancels their pending construction; changing sectors does not. Building in an entrance pad, gate, or exit is forbidden, and the spawn pads are visibly outlined. Standalone maze walls are hidden from the current build menu; the four combat tower families still physically obstruct ground routes and form staggered, jagged mazes. Historical saved walls are not deleted, and old Maul imports preserve legacy rules.

This is the **first playable delivery** against the larger Wintermaul specification, not a claim that every discussed feature exists. Remaining distinct design/engineering work includes physical crowding/no overlap, completely blocked-path creep aggression against towers, stealth/detection, speed and immunity variations, teleport, hydra/infernal splits, healing creeps, themed balanced builders, Mirror Survival (identical automatic waves for both teams; no player-sent waves), endless scaling/rewards and the dedicated in-editor Maul creator. Keep both player territory independence and team-shared survival. Extend in separate validated slices rather than silently enabling unimplemented mechanics. Older 30-wave rules, animated story projects, Sheep Tag and recorder formats are preserved.

Release candidate: **71 governed patches**, **27 assets**; new patch `patches/v11_1_maul_walk_builder.py`. CI, browser/device acceptance, and exact live release audit must pass before production publication.


## Current v11.0 candidate · Compressed recordings and clear Maul spectator

Frostveil Maul Play-run review now renders recorded snowfields, water, cliffs, tower families, maze walls, builders, creeps and the exit as distinct visual layers, with camera framing adjusted to the actual Maul map dimensions. The original Sheep Tag recorder presentation and recording schema remain intact. A new **Export compressed (.json.gz)** control uses lossless browser-native gzip; the recorder also imports these gzip files with format validation and a bounded 256 MiB decompressed limit. Existing raw JSON, text, HTML spectator, camera, timelines, events and saved projects continue to work.

The add-only release brings the engine to **70 governed patches** and keeps **27 packaged assets**. All 69 predecessor patches and their runtime files are unchanged. Candidate code requires package, browser, CPU and exact hosted release verification; these notes are not publication evidence.


Frostveil Maul is a separate native §E tower-defense project inspired by cooperative Wintermaul custom maps for Warcraft III: The Frozen Throne. Open **Projects → Frostveil Maul**, or use [the direct starter link](https://kamiloki-swrlz-forge-moba.static.hf.space/index.html?project=maul-frostveil), then press the editor's **Play** button.

The classic layout has three long upper building bays, a broad crossbar and a lower defense funnel leading to one shared ship. Raised cliff edges separate the snowy maze floors; colored builder positions, spawn arches, route beacons and shore water make the lanes readable. Each round releases three scattered groups at each entrance, with 2.5 seconds between releases. Members of each group arrive together on distinct clear cells in the entrance area. Occupied entrances defer a whole group until it can fit safely. Nine connected defender sectors share these spaces. Enemies entering an upstream sector travel through successive defended sectors to the ship. Each leak costs shared lives. Defeat all thirty waves with lives remaining to win; exhausting lives loses the match. Ground enemies follow open cells through player-built mazes. Flying rounds cross sectors without following tower mazes, and boss rounds demand concentrated damage.

One local controller manages nine builders and can switch the active sector. Optional auto-defenders build in the eight other sectors. This is a local playable cooperative starter. Online player synchronization and Warcraft's original racial tower roster are outside this release.

## Playing and building

Every defender begins with empty building space; Player 1 has no sample towers or walls. Choose a build tool, then place its preview on the ground grid. The visible footprint is the full area the tower or wall occupies. Green indicates an allowed placement and red explains a rejected one. On phones the whole footprint sits 140 CSS pixels above the finger; drag to adjust it, then release to build at the displayed grid position. Cancelling the gesture creates no structure. A new structure may not overlap another structure, occupy reserved entrance areas or protected gates or seal the complete ground route. A rejected build charges no gold and leaves the world unchanged. Placement also preserves a route for enemies already in the maze.

The four original tower families are **Arrow**, **Cannon**, **Frost** and **Storm**. They provide direct fire, splash damage, slowing and air-capable lightning defense. Each tower has three upgrade tiers. Click a placed tower on desktop, or double-tap it on a phone, to see range and stats, choose a target priority, upgrade it or sell it for a partial refund. Single ground taps move the current builder. Maze walls provide a cheaper way to shape ground routes. Kill rewards fund additional defenses; wave completion funds preparation for the next attack.

Use **Defense sector** to switch builders, **Map overview** to inspect all sectors and **Start wave 1 / Start next wave** to launch an attack, and inspect wave type, remaining enemies, shared lives and gold in the Maul HUD. Native **Pause** freezes the match; **Stop** restores the authored editor scene. Runtime purchases, kills and enemy movement do not overwrite the saved starter.

## Authoring the map

The default shipped source is `scenes/maul-frostveil-groups.swyrl.json`, marked `project.maulLayout: "classic-v2"` and `project.maulSpawnStyle: "grouped-v1"`. Both the original v10.6 `scenes/maul-frostveil.swyrl.json` and v10.7 `scenes/maul-frostveil-classic.swyrl.json` remain bundled unchanged for native import and retain their earlier spawn behavior. The 78 baked native actors include snowfield, water, cliffs, nine sector gates, nine builders, nine spawns, six editable lower-funnel route turns, and the ship exit in six populated layers. Use native transforms, the **Maul rules** panel, Undo/Redo and **Save Project / Load Project** to make a separate variant. Settings control the wave campaign and local assistance; actual game rules are stored with the project rather than browser-only preferences. Spawn and route changes must pass preflight before Play. Keep lower-lane turns on the 2-unit grid at ground height (Y = 0); Play rejects misplaced turns and preserves the authored project.

The starter uses original procedural frost, stone and crystal scenery and original tower models. It runs inside the existing editor and rendering engine, with a dedicated Maul runtime rather than an embedded external game.

## Recording a match

Before Play, open **Run recorder** and enable **Record Play run**. Recording is off by default and its device preference applies to every starter and imported project. Full capture observes each native update; 10 Hz and 2 Hz capture reduce state sampling while retaining timed events. Maul adds wave/group arrivals, gold, lives, towers, enemies, route choices and accepted/rejected commands to the shared world-object and camera record.

After Stop, export `.swyrl-run.json`, written `.swyrl-run.txt` spatial observations or the standalone `.swyrl-run.html` spectator schematic. The viewer can seek, orbit, follow an object or display the recorded player camera. Classic Maul records the camera lens offset so this view matches the editor framing on phones. Review/export stay unavailable during Play or Pause. Export before closing the tab to retain the run.

## Research and deliberate differences

| Source | Design evidence used |
|---|---|
| [Wintermaul DV4, Epic War](https://www.epicwar.com/maps/1/) | The classic snowy Maul terrain and minimap anchor three upper bays, broad connecting defense space and the lower common exit funnel. |
| [Warcraft Maul, Epic War](https://www.epicwar.com/maps/66/) | A second cooperative Maul example informs open maze-building spaces and a shared downstream defense. |
| [Wintermaul X10 Final, Epic War](https://www.epicwar.com/maps/2824/) | The 2006 Frozen Throne listing describes nine-player cooperative play, nine spawns, thirty waves and seventy-two towers. This anchors the cooperative nine-sector campaign. |
| [Wintermaul: The Remake, CurseForge](https://www.curseforge.com/sc2/maps/wintermaul-the-remake) | Its author describes race builders, towers used to make mazes and leaked enemies reducing lives at a shared ship exit. |
| [Contemporary 2003 Warcraft III guide, GameFAQs](https://gamefaqs.gamespot.com/pc/256222-warcraft-iii-reign-of-chaos/faqs/23533) | Ordered waypoint travel, air rounds ignoring mazes, boss rounds at 10/20/30 and distinct tower families informed the wave and route design. |
| [Maul making discussion, Hive Workshop](https://www.hiveworkshop.com/threads/maul-making.21468/) | Historical blocking behavior can make creeps attack towers. Full blocking has not had one universal rule across Maul variants. |
| [Wintermaul Redux, Hive Workshop](https://www.hiveworkshop.com/threads/wintermaul-redux-1-08g.121401/) | Another variant discusses handling blocked paths by selling a tower. |

Frostveil now follows the recognizable classic Maul terrain silhouette, linked defenders, shared ship exit, tower mazes, economic upgrades, air waves and thirty-round defense. The map uses original procedural geometry rather than copied Warcraft assets. It uses four original tower families and three tiers to keep the starter approachable. Rejecting a complete route closure is an explicit §E design choice for predictable editor testing and touch building; it is not a claim that every Warcraft Maul used that rule.

## Release and acceptance

The v10.8 candidate appends the 68th governed patch, `patches/v10_8_maul_batch_placement.py`, and adds the empty grouped-spawn native map as the 26th packaged asset. All 67 published patches, previous runtime files, 25 predecessor assets and payload chunks remain byte-identical. Artifact: `swyrl_engine_v10_8.html`; marker: `V10_8_MAUL_BATCH_PLACEMENT`.

Required acceptance includes fifteen desktop/phone browser suites, all grouped-spawn CPU cases, all twelve classic-layout CPU cases, all seventeen preserved Maul CPU cases, all thirteen Sheep Tag geometry cases and all six engine workflows. The two preserved Maul browser suites import their unchanged scenes, while the grouped suite checks the default map. Publication authority is the dedicated final request, terminal successful deployment and exact hosted package audit; candidate documentation alone does not establish that the release is live.
