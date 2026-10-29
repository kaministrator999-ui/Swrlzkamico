# Starforge Observatory

Starforge is a separate celestial workspace starter. Floating stone islands,
quiet stars, brass instruments, living gardens, and readable destinations make
a place to think and build. The den stays the grounded shared sanctuary;
Starforge provides open sky and independent project islands.

## Map and visitor experience

Arrive on the low welcome terrace, look through the garden, and choose Code or
Prototype Island. Bridges connect the lower islands. Two protected ascents
reach the archive and companion islands. The central final rise reaches the
Observatory, where the armillary and sky journal provide a quiet viewpoint.

| Zone | Finished height | Purpose |
|---|---:|---|
| Arrival | 2.4 | Welcome terrace and return point. |
| Constellation Garden | 2.4 | Shared rest, notes, and orientation. |
| Code Island | 2.4 | Focused code, perimeter desk, clear 5 × 5 build pad. |
| Prototype Island | 2.4 | Experiments, independent files, clear 5 × 5 pad. |
| Archive Garden | 5.8 | Reference files and decisions in a living upper garden. |
| Companion Chamber | 5.8 | Stationary wisp, conversation notebook, external §wyrlz chat. |
| Observatory | 7.0 | Brass armillary, sky journal, and view over the campus. |

The islands fit within the existing world bounds. Rails protect edges, while
bridge and ramp mouths remain open. An elevated island top is its authored
local Y=0: support follows the visible mesh after scaling and grouping.

## Editor capability checklist

- [x] Native floating-island prefab with a supported top and stone underhang.
- [x] Static constellation sky and reusable brass astrolabe.
- [x] Dedicated noncombat visitor and neutral companion-wisp prefabs.
- [x] Project-owned environment settings: background, fog, exposure, terrain
  visibility, and scenery visibility; Save/Load restores the same environment.
- [x] Existing decks, ramps, transformed rails, groups, layers, signs, and
  Workspace components are reused.
- [x] Native scene assembly, station documents, and authored teleport zones.
- [x] Walk lower bridges, ascend and descend both ramps, reach the Observatory,
  and open each station from visitor height.
- [x] Test zone destinations, pause restoration, and native Save/Load.

The three editor layers are **Islands & Wayfinding**, **Sky & Living Gardens**,
and **Project Stations**. They organize editing visibility; physical heights
belong to the actual island, bridge, and ramp geometry.

## Teleport and workspace contracts

Each project owns its own zone list. Named destinations have a safe landing
point, facing direction, purpose, and accent. Teleporting leaves the visitor
on a supported surface inside the rails and clears movement before resuming.
Arrival is the saved return and fall-recovery point. A hidden, blocked, or
unsupported destination rejects travel; the pad must remain clear in the map.
The project opts into recovery below height 1 through its saved Arrival zone.
Paused sessions, open menus/workspaces, and a flying wisp do not trigger it.

Station files and notes remain scoped to this project's canonical identity.
The Code and Prototype islands are independent work areas; Archive keeps
references and decisions. The companion's explicit chat link opens the
existing LALM in a new tab. Headset rendering, VR controllers, spatial voice,
in-room inference, and executable coding sessions remain future capabilities.

## Authoring evidence

The scene is assembled through the editor's native prefab, transform, grouping,
layer, sign, Workspace, project-settings, and zone APIs. Documents are entered
through the native Workspace panel. The final scene is downloaded with the
native **Save Project** control, then reloaded and tested in **Play**.

The final native scene contains 123 actors, three editing layers, six project
stations, and seven destinations. A continuous Play visit passed 23 movement
legs: the lower bridges, east ascent, upper crosswalk, Observatory rise and
descent, and west descent. All six stations opened with **E** at visitor height.
All seven destinations passed both landing checks and native **T** menu journeys.
Stop restored the authored visitor; cancelling the menu preserved a paused visit.

Authoring exposed two concrete clearance problems. The lower islands and bridges
were moved south so they no longer cut through the ascending ramps. The low
ends of the ramp rails were shortened where they entered lateral walking routes.
The signs and tested route now tell visitors to finish reaching a landing before
turning; the Observatory descent reaches its low landing before joining the
crosswalk. The exposed stairs retain their side rails.

Native background input, Save, and Load preserved the chosen colour together
with hidden terrain/scenery, fog, exposure, zones, station files, and recovery
metadata. An unsupported visitor start outside the islands returned to Arrival
through the same validated destination logic; the authored start was restored
before the final native save. Movement measurements skipped GPU drawing only
in the scratch test fixture; native input, simulation, support, and collisions
ran throughout. Arrival and menu screenshots used normal rendering.

## Design references

- [Unreal Engine VR Template](https://dev.epicgames.com/documentation/en-us/unreal-engine/vr-template-in-unreal-engine)
  treats teleport locomotion as travel to allowed navigable areas, with excluded
  volumes. Starforge follows that principle with authored destinations checked
  against visible support and actual clearance before moving the visitor.
- [W3C XR Accessibility User Requirements](https://www.w3.org/TR/xaur/)
  discusses orientation, navigation, a safe harbour, motion preferences, and
  avoiding sickness triggers. The saved Arrival terrace, readable signs, static
  stars, optional destination travel, and reduced-motion-aware fade reflect
  those considerations.

These are design references for the desktop workspace and future VR work.
They do not imply implemented headset support or full accessibility compliance.

## v8.4 arrival and wayfinding pass

The Garden route guide now sits beside the eastern planting at [3.6, 4.45, 5.5],
facing the Arrival approach. Its panel was reduced from 5 × 0.82 to 2.6 × 0.68
and shortened to lower-island directions plus a reminder to follow the ramps
to their landings. The normal first-person view now keeps the central
Observatory, armillary, and both ascents visible. The existing upper guide
covers the next decision point without another panel.

This pass changed one sign through the native Transform and Sign APIs, then
used native Save Project and Load. The scene remains at 123 actors, three
layers, six stations, and seven zones. Rails, pads, all other actor fields,
station files, destination coordinates, and environment/recovery settings
were preserved. Eight affected walking legs passed from Arrival through the
Garden and both lower island bridges; the Garden, Code, and Prototype stations
opened with E. All seven destinations passed native T-menu travel, pause
cancellation preserved the paused visit, and Stop restored the authored visitor.
A background input change survived native Save/Load; restoring the project
restored its original background and metadata. An unsupported test start
returned to Arrival, and the authored start was restored before the final save.
Project validation reported zero issues and zero warnings, with no browser
page errors. Normal rendered arrival screenshots show the sightline change;
movement measurements used the existing scratch-only drawing gate.
