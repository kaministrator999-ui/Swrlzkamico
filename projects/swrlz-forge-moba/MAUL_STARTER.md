# Frostveil Maul starter

Frostveil Maul is a separate native §E tower-defense project inspired by cooperative Wintermaul custom maps for Warcraft III: The Frozen Throne. Open **Projects → Frostveil Maul**, or use [the direct starter link](https://kamiloki-swrlz-forge-moba.static.hf.space/index.html?project=maul-frostveil), then press the editor's **Play** button.

Nine connected sectors form a three-by-three board. Enemies entering an upstream sector travel through successive defended sectors to a shared crystal exit. Each leak costs shared lives. Defeat all thirty waves with lives remaining to win; exhausting lives loses the match. Ground enemies follow open cells through player-built mazes. Flying rounds cross sectors without following tower mazes, and boss rounds demand concentrated damage.

One local controller manages nine builders and can switch the active sector. Optional auto-defenders build in the eight other sectors. This is a local playable starter; online player synchronization, competitive Maul Wars creep sending and Warcraft's original racial tower roster are future extensions.

## Playing and building

Choose a build tool, then place its preview on the ground grid. The visible footprint is the full area the tower or wall occupies. Green indicates an allowed placement and red explains a rejected one; touch previews sit above the finger. A new structure may not overlap another structure, occupy protected gates or seal the complete ground route. A rejected build charges no gold and leaves the world unchanged. Placement also preserves a route for enemies already in the maze.

The four original tower families are **Arrow**, **Cannon**, **Frost** and **Storm**. They provide direct fire, splash damage, slowing and air-capable lightning defense. Each tower has three upgrade tiers. Click a placed tower on desktop, or double-tap it on a phone, to see range and stats, choose a target priority, upgrade it or sell it for a partial refund. Single ground taps move the current builder. Maze walls provide a cheaper way to shape ground routes. Kill rewards fund additional defenses; wave completion funds preparation for the next attack.

Use **Defense sector** to switch builders, **Map overview** to inspect all sectors and **Start wave 1 / Start next wave** to launch an attack, and inspect wave type, remaining enemies, shared lives and gold in the Maul HUD. Native **Pause** freezes the match; **Stop** restores the authored editor scene. Runtime purchases, kills and enemy movement do not overwrite the saved starter.

## Authoring the map

The shipped source is `scenes/maul-frostveil.swyrl.json`. Terrain, sector gates, builders, route waypoints, shared exit and tower actors are native editor objects in populated layers. Use native transforms, the **Maul rules** panel, Undo/Redo and **Save Project / Load Project** to make a separate variant. Settings control the wave campaign and local assistance; actual game rules are stored with the project rather than browser-only preferences. Spawn and route changes must pass preflight before Play.

The starter uses original procedural frost, stone and crystal scenery and original tower models. It runs inside the existing editor and rendering engine, with a dedicated Maul runtime rather than an embedded external game.

## Recording a match

Before Play, open **Run recorder** and enable **Record Play run**. Recording is off by default and its device preference applies to every starter and imported project. Full capture observes each native update; 10 Hz and 2 Hz capture reduce state sampling while retaining timed events. Maul adds wave, gold, lives, towers, enemies, route choices and accepted/rejected commands to the shared world-object and camera record.

After Stop, export `.swyrl-run.json`, written `.swyrl-run.txt` spatial observations or the standalone `.swyrl-run.html` spectator schematic. The viewer can seek, orbit, follow an object or display the recorded player camera. Review/export stay unavailable during Play or Pause. Export before closing the tab to retain the run.

## Research and deliberate differences

| Source | Design evidence used |
|---|---|
| [Wintermaul X10 Final, Epic War](https://www.epicwar.com/maps/2824/) | The 2006 Frozen Throne listing describes nine-player cooperative play, nine spawns, thirty waves and seventy-two towers. This anchors the cooperative nine-sector campaign rather than competitive Maul Wars. |
| [Wintermaul: The Remake, CurseForge](https://www.curseforge.com/sc2/maps/wintermaul-the-remake) | Its author describes race builders, towers used to make mazes and leaked enemies reducing lives at a shared ship exit. |
| [Contemporary 2003 Warcraft III guide, GameFAQs](https://gamefaqs.gamespot.com/pc/256222-warcraft-iii-reign-of-chaos/faqs/23533) | Ordered waypoint travel, air rounds ignoring mazes, boss rounds at 10/20/30 and distinct tower families informed the wave and route design. |
| [Maul making discussion, Hive Workshop](https://www.hiveworkshop.com/threads/maul-making.21468/) | Historical blocking behavior can make creeps attack towers. Full blocking has not had one universal rule across Maul variants. |
| [Wintermaul Redux, Hive Workshop](https://www.hiveworkshop.com/threads/wintermaul-redux-1-08g.121401/) | Another variant discusses handling blocked paths by selling a tower. |

Frostveil keeps the recognizable linked sectors, shared exit, tower mazes, economic upgrades, air waves and thirty-round defense. It uses four original tower families and three tiers to keep the starter approachable. Rejecting a complete route closure is an explicit §E design choice for predictable editor testing and touch building; it is not a claim that every Warcraft Maul used that rule.

## Release and acceptance

The v10.6 candidate appends the 66th governed patch, `patches/v10_6_maul_tower_defense.py`, and adds this map as the 24th packaged asset. All 65 earlier patches, earlier runtime files, 23 predecessor assets and payload chunks remain byte-identical. Artifact: `swyrl_engine_v10_6.html`; marker: `V10_6_MAUL_TOWER_DEFENSE`.

Required acceptance includes thirteen desktop/phone native browser suites, the new sealed Maul CPU routing/wave suite, the existing thirteen Sheep Tag geometry scenarios and all six engine workflows. Publication authority is the dedicated final request, terminal successful deployment and exact hosted package audit; candidate documentation alone does not establish that the release is live.
