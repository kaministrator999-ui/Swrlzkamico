# Sheep Tag · Moonbell Meadow

This separate native editor starter recreates the classic Sheep Tag loop with original models and an original meadow map: sheep build farms and survive, wolves hunt and break their defenses, and captured sheep become wisps that teammates can rescue from the central pen. The animation starter remains a separate project.

## Rules and starter defaults

The default local practice match has six sheep and two wolves, with a controlled unit and bots filling the other roles. Sheep receive a 30-second building head start, then must keep at least one sheep alive until the 20-minute survival timer expires. Wolves win immediately when every sheep is captured at once. A captured sheep becomes a Dragon's Den-style wisp in the central pen. A live sheep reaching a friendly wisp rescues it; there is no automatic timed revival.

The **Sheep Tag** rules panel edits survival time, sheep head start, your Sheep/Wolf role and starting gold. The saved defaults are 20 minutes, 30 seconds, Sheep and 80 gold. Add or remove sheep/wolf spawn actors in the editor to change team sizes. Building prices, health, construction times and income are engine balancing defaults; the rules panel does not edit that catalogue. Sheep Tag maps vary: GosuSheep and Behh describe 20-minute survival, Cryo's Reforged map describes 15 minutes, and other editions use different counts or timers. The head-start duration is our practice choice.

## Map and editor

Open [Sheep Tag directly](https://kamiloki-swrlz-forge-moba.static.hf.space/index.html?project=sheep-tag-meadow) or select it in **Projects**. The map is saved in [`scenes/sheep-tag-meadow.swyrl.json`](scenes/sheep-tag-meadow.swyrl.json). It contains **66 native actors in four populated layers**: meadow/paths, spirit pen/merchants, woodland/ponds and sheep/wolf spawns. Six sheep and two wolves join one meadow, one central pen, four corner shops, two ponds, six boulders and 44 trees. Four approaches to the pen and open building quadrants leave space to create farm mazes during a match.

Use native selection, Inspector transforms, grouping and project layers to adjust the map. Use native **Save Project** to export it and **Load Project** to restore it. Map layout belongs to the scene export; reusable models, RTS controls, construction, collisions, bots, economy, capture/rescue and the match lifecycle belong to the engine. Round buildings and running units are temporary Play state. **Stop** returns to the editable map rather than saving a running match over the authored starter.

Press the editor's **Play** button to start the practice match, or use **Save & Play** in the rules panel. The raised RTS camera keeps sheep, farm grids and the central pen visible. Tap/click ground to move your unit; tap units or farms to select them. As a wolf, tap a sheep or farm to attack. **My unit** selects your controlled sheep, wisp or wolf. Select a friendly trapped wisp as a live sheep to order a rescue.

Choose a building button, then tap/click a clear site; your sheep walks to it and constructs the farm. Desktop shortcuts **Q**, **E** and **F** choose Farm, Income farm and Fortified farm. **Cancel** or **Escape** leaves placement mode. Select an owned farm for **Upgrade farm** or **Sell / clear farm**. Wolves can use **Wolf upgrade** near a corner merchant. The game panel shows gold, the timer, free/captured sheep and the current phase.

Pan with **WASD/arrows**, right-drag or Space + drag on desktop, and drag on a phone. Tap the minimap to explore; **Following** returns the camera to the selected unit. The **＋/−** controls and mouse wheel zoom. **Pause** freezes the match, **Restart** begins a clean match and **Stop** returns to editor authoring.

## Construction and rescue loop

Sheep build blockers to force wolves around a farm grid or make them spend time breaking through it. Sheep use a smaller collision radius than wolves, so farm spacing matters. Buildings snap to a 3-unit grid and have a 2.4-unit base footprint. Valid construction needs clear, buildable ground; ponds, obstacles, occupied footprints and the rescue area remain protected. Sheep can remove their own buildings when they need an escape route.

| Building | Shortcut | Cost | Construction | Health | Income |
| --- | --- | ---: | ---: | ---: | ---: |
| Farm | Q | Free | 1.4 s | 180 | — |
| Income farm | E | 60 gold | 3 s | 240 | 3 gold/s after completion |
| Fortified farm | F | 100 gold | 4 s | 650 | — |

Live sheep also receive 1 gold/s. Building upgrades and hunter upgrades spend gold; the UI shows the current price. Wolves earn bounty by breaking farms and capturing sheep. Selling an owned farm returns half its total building investment and opens its footprint. Each sheep can own up to 14 buildings, with 84 total in the meadow.

Capture removes the captured sheep's farms and changes its body to a wisp inside the pen. Live teammates must return through a rescue approach, reach the wisp and free it. Rescue returns the player to the sheep form so it can run and rebuild. Guarding and rescuing the pen is part of the game, not a respawn countdown.

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

## Acceptance and release

[`tests/sheep_tag_playwright.mjs`](tests/sheep_tag_playwright.mjs) is the ninth desktop/phone browser suite. It must verify actual native editor Play, movement, building placement and costs, income and upgrades, collision-aware farm blocking, wolf attacks, capture/wisp/rescue, both victory conditions, and clean Restart/Stop/Save/Load. The eight animation suites remain required.

The map was placed and baked through the native editor, then downloaded with native Save Project. Editor validation reported zero issues and zero warnings, and the export retained all 66 actors and four populated layers. The Sheep Tag suite also passed all 14 cases on desktop and all 14 on phone, including native Play, construction/economy, farm-gap pathing, wisp capture/rescue, wolf bounty/merchant upgrades, both win paths and map/scene lifecycle restoration. All six local static gates passed. Remote acceptance of all nine browser suites and six engine CI workflows, deployment and hosted v10.0 verification remain pending.

The current v10.0 source candidate uses `patches/v10_0_sheep_tag.py`, artifact `swyrl_engine_v10_0.html` and marker `V10_0_SHEEP_TAG_STARTER`, with 60 governed patches and 22 bundled assets. Source/deployment authority resolves from the sealed manifest, final `DEPLOY_REQUEST.json`, exact dedicated deployment and hosted source/asset audit.
