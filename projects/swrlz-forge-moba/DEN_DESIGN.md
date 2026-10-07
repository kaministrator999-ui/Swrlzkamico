# Embervault Atelier: design and authoring contract

Build a welcoming dragon sanctuary where a person can arrive, choose a project area, write, prototype, and return to a shared hearth. The cave should feel inhabited and substantial: stone shelter, brass ribs, restrained crystals, warm lamps, clear paths, and usable empty floors.

## Three perspectives, three physical tiers, three editor layers

| System | Purpose |
|---|---|
| Whole engine source | Reusable geometry, components, collision/support rules, serialization, and runtime controls. |
| Native editor | Assemble this project with prefabs, grouped transforms, signs, stations, and layers. |
| Play | Check the den at visitor height: walking, sightlines, navigation, station use, and return to editing. |
| Physical tiers | Lower workshop at **0**, upper study at **3.4**, guardian council at **4.6**. |
| Editor layers | **Architecture / Wayfinding**, **Atmosphere / Guardians**, **Project Spaces**. Membership controls editing visibility; it does not define floor height. |

Engine features must exist before authoring depends on them. Scene arrangements and workspace content remain project-owned; reusable tools remain in the engine lane.

## Whole-den map

Coordinates use **X across the room, Y up, Z toward the arrival gate**. Dimensions are design targets in editor units, treated approximately as meters. Heights below describe nominal walkable surfaces; verify the rendered mesh support height at every seam.

The main chamber occupies roughly **40 × 32**, from X −20 to +20 and Z −16 to +16. The stone vault rises to **Y 10.45**, with brass ribs and a central oculus. Preserve a roughly **3-wide central route** and at least **4.6 × 4.6 clear building space** in each project bay.

| Place | Center / route coordinates | Dimensions / height | Role |
|---|---|---|---|
| Welcome court | X 0, Z 13 | 9 × 5; Y 0 | Clear arrival, immediate view of hearth and both ramp entrances. |
| Quiet nook | X −5.7, Z 13 | Compact human-scale furnishing | Rest and orientation outside the through-route. |
| Guest seat | X +5.7, Z 12.5 | Compact seat | Optional conversation place. |
| AI hearth | X 0, Z 0.6 | Low pedestal; Y 0 | Shared project notes and the working external §wyrlz chat link. |
| World Forge | X −11.5, Z 7 | 8 × 8; Y 0 | World-building files, perimeter desk, empty central pad. |
| Prototype Court | X +11.5, Z 7 | 8 × 8; Y 0 | Experiments and scene planning; perimeter desk and empty pad. |
| Code Studio | X −11.5, Z −5.3 | 8 × 8; Y 3.4 | Quiet code/text editing on the upper gallery. |
| Archive Garden | X +11.5, Z −5.3 | 8 × 8; Y 3.4 | Notes, reference files, and restrained living-grove accents. |
| Study gallery bridge | X −16 to +16, Z −4.8 | Continuous cross-room deck; Y 3.4 | Connect both upper bays and the guardian approach. |
| Twin workshop ramps | X ±5.7, center Z 3.7 | Z +8.7 → −1.3; rise 3.4 over run 10 | Continuous ascent from workshop to study without jumping. |
| Guardian connector | X 0, center Z −8.6 | Z −6.6 → −10.6; rise 1.2 over run 4 | Short ascent from study to council. Native ramp scale: `[1.4, 1.2/3.4, 0.4]`. |
| Guardian council | X 0, Z −12.7 | Raised rear platform; Y 4.6 | Calm council/viewpoint; dragons face the room without crowding its entrance. |
| Dragon alcoves | Rear center and outer side refuges | Three moderate-scale dragons | Companions/guardians, with wings and tails clear of routes and work pads. |
| Vault and oculus | Whole chamber; oculus above center | Crown Y 10.45 | Enclosure and quiet overhead landmark, visible in Play. |

Keep decks, landings, and ramps flush: the bridge-to-connector transition must have continuous support, including any small landing needed to close a seam. Rails protect raised edges while leaving ramp mouths and entrances open.

## Asset inventory

| Asset family | Native source / purpose | Placement rule |
|---|---|---|
| Stone vault, brass ribs, oculus | `denVault`, `denVaultRib`, `denOculus` architecture prefabs | Reusable enclosed roof; reserve the central skylight. |
| Ramp, gallery deck, rails | Native level primitives and collision surfaces | Actual supported geometry; no decorative imitation of a walkable route. |
| Three dragons | Existing procedural dragon actors | Plant paws on their support surfaces; preserve approachable scale and clear silhouettes. |
| Crystals and marker bases | `crystal`, `pedestal` | Small accents at bay entrances and perimeter desks; avoid blocking view across a pad. |
| Lamps | Existing warm lantern assemblies | Light arrivals, ramp entrances, desks, and landings. |
| Perimeter desks | `denWorkbench` with `Workspace` | One usable station per project bay; screens stay near visitor eye height. |
| World signs | `workspaceSign`; `createSign` / `updateSign` | Readable two-line wayfinding at decision points; serialized text and dimensions. |
| Quiet nook and guest seat | `denNook`, `throne` at reduced scale | Domestic anchors at arrival, outside circulation. |
| AI hearth / pedestals | Existing low pedestal with `Workspace` kind `chat` | Project notes plus an explicit external chat portal. |
| Floor/pad assemblies and cave shell | Existing grouped stone pieces | Preserve generous floors and distinct rooms; layer membership supports inspection. |

## Editor-needed checklist

Code implementation and successful isolated checks are separate from integrated editor/Play acceptance.

- [x] Prefab library: native vault architecture, desks, crystals, signs, and reusable existing props.
- [x] Grouped transforms: move upper project bays as assemblies; preserve child positions and station identities.
- [x] Visibility, save, and undo: persisted manual visibility, layer membership, transactional layer changes, and runtime-shell composition.
- [x] World-sign editing: canvas-texture signs, inspector text editing, native actor serialization, and agent methods.
- [x] Workspace component: configurable title, kind, accent, optional link, label offset, and interaction radius.
- [x] File persistence: create/rename/edit/delete text files, station notes, device drafts, native project Save, workspace JSON import/export, and individual file downloads.
- [x] Modal interaction: nearby **E / Open**, released pointer lock, suspended world input, Close/Escape, and restoration of the prior pause state.
- [x] Readable desktop layout: full-width viewport, correctly sized collapsible docks, and clear Play chrome.
- [x] Walkable surfaces: native ramps/decks and downward support raycasts; actual WASD ascent, descent, landing seams, and the council connector passed.
- [x] Rail collisions: actual ramp side exits blocked; native transformed-rail and height-filter checks passed. Leave through the open ramp mouths.
- [x] Canonical boot: the native authored project opens on startup with 167 actors, six station records, signs, levels, and three editor layers.
- [x] Visual authoring acceptance: three physical tiers, empty build pads, signs, enclosed vault, and visitor-scale views are present; sign backs now have their own readable face.
- [x] Integrated Play acceptance: the native route, all six stations, document transfer, Save/Load, layer history, and pause/Stop restoration passed. See VERIFICATION.md.

## Workspace and movement contracts

Station configuration belongs to the actor's serialized `workspace` field and `Workspace` component. File contents and notes belong to `project.workspaces.stations[actorId]`. Duplicated actors receive distinct IDs; station data must not accidentally share a storage identity.

Canonical reload may hydrate newer device drafts; imported project/workspace files remain authoritative. Save includes station data even before every station is opened. Code is editable text and downloadable source; this release does not execute project code.

Use downward raycasts against approved walkable meshes plus terrain to find floor support. Ramp/deck geometry must survive Save/Load with the same transforms and support behavior. Walking should adhere to the surface rather than hovering through a raised floor. Rail collision and vertical support are separate responsibilities; a support ray alone does not block a fall through an edge.

The AI hearth opens the existing [§wyrlz chat](https://kamiloki-swyrlz.hf.space/) in a new tab. In-room LALM conversation, spatial audio, executable coding sessions, headset rendering, and VR controller input remain future capabilities.

## Author → Play → fix → verify

1. **Engine gate:** build the combined patches, check JavaScript syntax and scene roundtrips, then confirm all required assets/components exist in the editor.
2. **Native authoring:** assemble tiers, ramps, rails, lighting, signs, and stations; assign the three editor layers; save the authored project.
3. **Arrival test:** start Play at human eye height. Locate the hearth, workshops, and ramps without an overhead camera; inspect scale, shadows, and sign readability.
4. **Route test:** walk both ramps up and down; cross the study gallery; reach guardian council through its connector; check seams, rail blocking, and clearance below the vault.
5. **Workspace test:** open every bay and the hearth using E and Open; edit a file and notes; close/resume; download a file; export/import a workspace; verify the external chat link.
6. **Persistence test:** Stop, Save/Load, undo/redo a scene change, and reload canonical boot. Confirm geometry, labels, layer visibility, files, and notes survive; return to the editor's original actor state after Play.
7. **Iteration:** record the failure and trigger, fix the engine rule or authored placement that caused it, and repeat that route/workspace check. Do not count an attractive screenshot as movement or persistence evidence.

**Current status:** the three-tier native scene is authored. Actual WASD walking reaches both upper bays, the council, both lower bays, and the hearth, and passes underneath the gallery. All six stations open with E. Workspace persistence, native Save/Load, layer history, and pause/Stop restoration passed. Release integrity and live verification follow the governed deploy contract. Headset VR and an in-room LALM backend are future work.

## Design references

The domestic/guardian mood draws from [Smithsonian's *Dragons and Clouds*](https://asia.si.edu/interactives/symbols/serpent/dragons-and-clouds/index.html); distinct cave rooms draw from [UNESCO's Mogao Caves](https://whc.unesco.org/en/list/440/) and [Getty's full-scale cave-temple replicas](https://www.getty.edu/news/getty-presents-cave-temples-dunhuang-exhibition/). These are visual/spatial inspirations. Visitor-scale placement and restrained head movement follow [Meta's comfort guidance](https://developers.meta.com/vr/design/comfort/); headset comfort still requires headset testing.
