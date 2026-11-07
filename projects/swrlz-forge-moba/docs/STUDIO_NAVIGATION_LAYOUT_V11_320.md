# Organized studio interfaces and project navigation — v11.320

Lifecycle: IMPLEMENTATION_APPROVED; SOURCE_VERIFIED; BROWSER_VERIFIED. Publication/hosted confirmation and owner device acceptance are recorded separately below.

## Resulting behavior

Model Studio has a hierarchy, canvas, category rail and inspector in distinct columns. The rail sits immediately left of the inspector and remains at the viewport edge when it collapses. Compact mode puts the categories in a scrollable row above the inspector. Selection, component, group and quick-mesh controls live inside the inspector; the native left hierarchy toggle remains reachable when collapsed. Native and external inspector show/hide controls cooperate. A direct Projects action and the actual project name are visible in the header.

Project Library keeps its header and Starter Projects / My Projects tabs outside its scrolling content pane. Starter categories stick only within that pane, removing the overlapping fixed header offsets.

Game Engine has separate studio-tab, menu and quick-action rows. Existing advanced scene/build/VR controls are grouped under More tools. Levels, view settings and diagnostics have separate positions. The native tab installer, GUI subtab and live-preview controllers recognize the relocated Game rail, so repeated studio switching retains one rail.

Particle Studio has separate studio-tab, menu and action rows, including visible phone menus. Projects and Preview are first in its action rail. Native layout selectors live under Tools; dropdowns use bounded viewport positions so compact toolbars cannot clip them. Existing modifier, preview, library, timeline, keyboard and rendering handlers retain their original nodes/listeners.

Completed native loads select Modeling for model documents, a saved Particle/Material workspace hint where applicable, and Game Engine otherwise. New native exports store `editor.studioWorkspace`; ordinary games with VFX remain games. Valid emitter-library imports open Particle Studio. Canceled, failed, superseded and history-preserving loads do not redirect. Explicit native loads suppress the deferred first-game initialization that could otherwise replace the loaded document.

## Canonical source and integrity

The release integrates on canonical `38832d5cc76e6303a6b439b2de20fa3eebb5d58d`, preserving the owner's v11.309 native-ray work and every earlier registered patch. The new UI patch appends at position **341**. No provisional UI deployment replaced the concurrent Arcane releases.

Full ordered reconstruction and strict packaging verified **8,445,313 HTML bytes**, SHA-256 **`784249443e626d13740ada224b61f54358011c98678c6e6ee41f581660264347`**, **71 assets** and exactly **75 package files**. Index and Modeler HTML are identical; every asset matches its bytes/hash receipt. The manifest, runtime identity, deploy marker, verifier, workflow and current docs identify v11.320. The predecessor deployment request remains until the source publication and final separate request-only commit.

No source integrity check was waived. Historical release-history generation depends on the complete ordered manifest, so the final seal is measured from the original checksum-gated payload and all 341 patches.

## Verification

The current strict verifier passes assembled JavaScript parsing, native character tools, outward loft normals, real-Three 59-part scene/list/production GLB, preserved Vanguard anatomical/whole-mesh tests, project-routing VM and the owner's scoped Arcane grip/native-ray VM tests. The routing VM covers model/game/particle classification, games with VFX, invalid hints, canceled/failed/superseded loads, history restoration, asynchronous templates, VFX import and workspace-hint serialization.

The complete interaction suite passed at 1440×1000 and 390×844 before the final identity integration: no rail/inspector overlap, accessible hierarchy and inspector restore, project tabs while scrolling, My Projects, native game/particle load preservation, and two repeated studio round trips with one Game rail. Final native parts and mesh rows remained 59, with zero page errors. Particle Tools was checked by viewport bounds and an actual hit-test, rather than nominal visibility alone. A native four-emitter Astral Vortex also rendered correctly in an isolated test context.

The final interface/routing JavaScript and CSS are byte-equivalent to that tested implementation after normalizing only the release namespace. The final sealed v11.320 integration passed a fresh browser smoke check: repeated studio switches, hierarchy restore, native inspector restore, phone project tabs and the Particle menu hit-test all passed with 59 unchanged parts and zero page errors. Logs and screenshots remain in the private task workspace; private projects and account credentials never enter public source or the HF package.

```sh
python projects/swrlz-forge-moba/scripts/verify_v11_320_release.py --output dist/swrlz-forge-moba
python projects/swrlz-forge-moba/scripts/check_studio_ui_v11_320.py --html dist/swrlz-forge-moba/index.html --output /tmp/swrlz-ui320-check
```

The portable browser check requires Playwright and Chromium. It uses a fresh isolated profile, local sealed HTML at the canonical app origin, and verified-TLS guest Chat/CDN requests. An optional `--native-project` exercises a private fixture without packaging it. Browser checks do not establish physical phone/Quest appearance or XR calibration acceptance.

## Saved-mage cleanup and account flow

After the owner completed a fresh Google connection, both Little Crystal Mage records were downloaded and matched their expected hashes, revisions and part counts. Only the older **41-part revision-3** checkpoint was deleted, with an expected-revision guard. The protected catalog then contained one Little Crystal Mage: the unchanged complete **59-part revision 2**. No other account projects were removed.

In the account-connected interface preview, canonical My projects/Load started from Game Engine, restored that real account save, and automatically selected Model Studio. It displayed 59 mesh rows and every native part descriptor matched the cloud backup. The picker contained one saved mage record. The routing implementation is unchanged in the final integration. No new cloud save or model edit was needed for this verification.
