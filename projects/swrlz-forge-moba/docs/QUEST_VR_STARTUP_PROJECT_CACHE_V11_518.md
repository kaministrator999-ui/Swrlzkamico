# §WYRL§ Engine v11.518 — Quest startup and selected-project cache

Environment: normal Quest 2 VR Browser 2D editor vs **immersive WebXR** are separate. This change targets immersive WebXR entry plus project loading/restoration shared by the native engine. No unrelated game mode, tool rail, menu hierarchy, canonical starter or user-saved asset is replaced.

## 1 — Correct `se220RigAvailable is not defined` during VR entry

The original immersive rig extension v11.514 evaluated a function `se220RigAvailable` and several private bone/model variables from outside the **ModelAtelier** lexical closure, so opening *any* immersive workspace triggered a `ReferenceError`, even for a plain sphere.

v11.518 inserts a narrow facade inside the original ModelAtelier closure, retaining its authoritative rig, skeleton, root, selected joint, pose/undo and checkpoint functions. The existing compiled immersive rig runtime receives dynamic accessors for those private state variables. It no longer assumes the private identifiers are in WebXR's outer lexical scope. The existing scene, 3-stage WebXR menu, controller dispatch, rigging operations and cleanup remain in place.

Acceptance: open a simple sphere and a non-rigged cone in Quest immersive WebXR without a `se220RigAvailable` error. Re-open authored rigged cloth and the Sorting Hat and verify selection, bone pose, weight visualization, Undo and exit work. This source fix requires physical Quest owner acceptance.

## 2 — Selected My Projects item determines the next project

The native `My Projects` account picker and the startup project chooser now persist *user-triggered* local/account selection using the existing default-project preference (never a project document in localStorage). An automatic list refresh does not rewrite the choice. When signed-in project metadata arrives, the startup controller prefers an actively selected project rather than applying an unrelated fallback over it. Opening a model in VR or 2D continues to use the existing native loader. Other starter registry and user project records are preserved.

Acceptance: choose a saved Model Atelier project, reload the browser, reconnect, and confirm the same project opens, retaining name and working geometry. Repeat with an on-device and a cloud project. A user may still explicitly clear the default through the existing preference controls.

## 3 — Use version-verified local project cache

Signed-in account project opening now checks lightweight current cloud revision metadata first. It looks for a matching IndexedDB project record with the **same remote project ID + revision**. A valid saved copy loads through the existing local project loader, which maintains conflict/recovery semantics. A missing/stale/invalid snapshot, mismatched revision, or unavailable metadata falls back to the authoritative authenticated cloud load.

The first successful cloud download already persists a local mirror through v11.371's account link, so ordinary revisit/download costs drop substantially without losing server updates. The modeler's static JavaScript bundle still follows normal browser HTTP caching rules and is separate from account project data. No passwords, account tokens or project bytes are placed in localStorage.

Acceptance: first account project open downloads; second open at the same remote revision uses a local cache hit; a new remote revision triggers a fresh download; signing out prevents account cache reads. Test saving and editing after a cache hit as well as reloading and Undo, plus the user's Quest browser storage retention settings. Clearing browser/site data also clears IndexedDB and requires a new download.

## Verification limitations

Automated Node tests cover cache-hit, remote revision change, signed-out denial, missing snapshots and busy guards. Release CI checks compiled WebXR rig controls with Three.js r169 and preserved earlier VR rig and project regression suites. Physical Meta Quest acceptance is a separate step.

