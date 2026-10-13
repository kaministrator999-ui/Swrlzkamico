# Frostveil Wintermaul Wars starter

Open **Projects → Wintermaul Wars · Frostveil Divide**, or use [the direct starter link](https://kamiloki-swrlz-forge-moba.static.hf.space/index.html?project=maul-wars-frostveil), then press the native editor's **Play** button. The original cooperative [Frostveil Maul](MAUL_STARTER.md) campaign remains available separately.

The Wars map has two mirrored, broad snowy team halves, with three builder positions on each side. Dark raised ice islands, a central divider and open outer turns shape the connected defense route. Ground creeps follow ordered beacons through the defending team's maze before reaching its ship; every successful leak removes a shared team life. A team loses when its lives reach zero. Flying creeps bypass the tower maze and need air-capable defenses.

This starter is a local match against three AI opponents. Switch between all three friendly builders to manage their separate gold and income. Optional friendly auto-defenders assist slots 1 and 2 with their own wallets. Selecting a different builder changes the construction sector, available wallet and owned tower actions. The six colored builder positions describe a 3v3 map arrangement; they do not imply six connected human players.

## Sending and defending

Buying creeps sends them into the opposing team's route. Each accepted send spends the sender's gold and permanently increases that player's recurring income. Income pays every **25 seconds**. Balance early defense against sending: a stronger economy permits larger attacks, while insufficient towers let enemy sends reach your ship. The AI also sends creeps and builds defenses, so the opposing half develops during the match.

Build **Arrow**, **Cannon**, **Frost** and **Storm** towers or inexpensive maze walls. These original tower families retain three upgrade tiers, direct fire, splash damage, slowing and air-capable lightning. Ground creeps route around towers through the remaining open cells. The placement grid shows the complete structure footprint; green permits construction and red explains a rejected placement. On a phone, the preview sits above the finger and releasing commits the displayed footprint.

Placement rejects overlapping or protected cells, enemy-owned defense territory and a complete ground-route closure before spending gold. It also preserves routes for ground creeps already moving through the maze. A rejected command leaves the wallet and map unchanged. This anti-block policy is an explicit §E rule: historical Wintermaul Wars versions vary in how blocked creeps behave.

Click a placed tower on desktop, or double-tap its visible surface on a phone, to inspect its range and stats. Use the tower controls to upgrade, sell for a partial refund or choose a targeting priority. Only the currently selected builder's towers can be changed. Single ground taps move that builder. The overview shows both teams; builder framing focuses the selected defense area.

The HUD shows the selected player's gold/income, the income countdown, both teams' lives and send choices. Native **Pause** freezes the entire match. **Stop** returns to the authored editor map, including its original builder positions and towers. Purchases, creep movement, kills and AI construction during Play do not overwrite the saved starter.

## Authoring the map

The native source is `scenes/maul-wars-frostveil.swyrl.json`. Its 49 × 51-cell board is authored in seven populated editor layers: **Wars Snowfields**, **Raised Ice and Borders**, **Routes and Ships**, **Builders**, **Sender Islands**, **Winter Scenery** and **Authored Towers**. The two spawns, five ordered beacons per team, two ship exits and six builder slots retain explicit team/route metadata with their native actors.

Use ordinary native transforms and **Wars rules** while stopped to make a variant. Undo/Redo records the authored changes; **Save Project / Load Project** carries the scene and its project-owned rules. Preflight checks team entrances, ordered route stages, ships, builder slots, finite transforms and the remaining ground routes before Play. Decorations sit on raised or protected ground so construction lanes remain readable and the camera can frame the battlefield.

The terrain, structures, ships, builder colors and units use original native engine content. The research guides the map silhouette and gameplay; the package includes no copied Warcraft artwork or map binary. The classic Maul source and every previously published scene, asset and runtime module remain unchanged.

## Recording a match

Before Play, open **Run recorder** and enable **Record Play run**. Recording remains off by default, and the device preference works across all starters and imported projects. Full capture records each native update; 10 Hz and 2 Hz reduce state sampling while retaining timed commands and events.

Wars records player gold/income, team lives, send outcomes, towers, creep health and route progress, attack traces, builder orders and terminal results alongside the world-object catalog and actual camera. After Stop, export `.swyrl-run.json`, written `.swyrl-run.txt` spatial observations or the self-contained `.swyrl-run.html` spectator schematic. The viewer can seek, orbit, follow an object or use the recorded player camera. Export before closing the tab to retain the run.

## Research and differences

| Source | Evidence used |
|---|---|
| [WMW: The Next Generation 2.0, developer page](https://www.hiveworkshop.com/threads/wmw-the-next-generation-2-0.119036/) | Upper red/blue/teal and lower purple/yellow/orange teams; three players per team; ground sends from a Shrine and flyers from an Air Nest; sending raises income paid every 25 seconds; ordered lightning waypoints and a ship exit with shared team lives. Its route fix also supports keeping waypoint objectives monotonic. |
| [WMW Evolution v1.03, developer page](https://www.hiveworkshop.com/threads/wmw-evolution-v1-03.277090/) | The author's whole-map screenshot shows two horizontal snowy defense bands, raised central cliff islands, open outer turns, three builder stations per side and a central separator. These features inform the mirrored Frostveil map. |
| [Dragon Ball Z Wintermaul Wars, official developer repository](https://github.com/arhstevens/DBZWMW) | Describes the long-running Tower Wars pattern: teams of up to three build tower mazes against creeps sent by the opposing team. It traces this variant to a 2005 branch and separates Frozen Throne releases from later Reforged releases. |
| [Wintermaul Wars X14.2, Epic War listing](https://www.epicwar.com/maps/223952/) | Confirms the official series supports 1v1, 2v2 and 3v3 formats; this starter chooses the recognizable 3v3 arrangement. |

Income timing, tower rosters, initial resources, heroes, blocked-path behavior and optional air modes differ across Wintermaul Wars versions. Frostveil selects one clear local ruleset and original tower roster. Its grid coordinates are an authored adaptation of the recognizable mirrored layout, rather than an exact recreation of any proprietary map. Online synchronization, race-specific Warcraft tower catalogs and extra historical modes are future extensions.

## Release acceptance

The v10.7 candidate appends the 67th governed patch, `patches/v10_7_wintermaul_wars.py`, and adds this native map as the 25th packaged asset. Artifact: `swyrl_engine_v10_7.html`; marker: `V10_7_WINTERMAUL_WARS`.

Required acceptance includes fourteen desktop/phone native browser suites, sealed Wars economy/route CPU cases, all seventeen classic Maul CPU scenarios, all thirteen Sheep Tag geometry scenarios and all six engine verification workflows. The dedicated final deployment and exact hosted HTML, `SOURCE.json` and all-asset audit establish publication authority. Candidate documentation alone does not establish that the revised starter is live.
