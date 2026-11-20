# §WYRL§ Engine v11.529 — project account-save correction and browser My Projects redesign

Owner-reported observations, Nov 19, 2026: Phone browser shows §Chat account connected, but clicking Save to Account says account sync failed. Browser My Projects repeats Save to Account, Save Project, Refresh, Clone and related controls across top, middle and bottom rows. Two device project cards have a crowded grid of primary and destructive actions.

## Root cause and change

The v11.488 Model Studio account-save wrapper changes `saveCloud()` so, whenever Model Studio is active, it redirects to `SWYRL_ENGINE_ASSET_LIBRARY.save('modeler',true)`. That is a **model-asset** save operation with a different identity and revision, not the complete **project** save expected by §Chat and My Projects.

The v11.528 button path called `saveCloud()===true` and would report a failure or unconfirmed account sync even with a connected account. Its prior error text could also report a stale account status instead of the actual save result.

v11.529 separates these operations instead of replacing the asset library:

- **Save project to account**: `se529SaveNativeProjectToAccount()` validates the Chat account, preserves existing project naming and independent starter cloning, saves a native local recovery snapshot, then calls **`se371PreviousSaveCloud()`**, the original complete-project path. That facade does remote revision preflight, native scene serialization, and authenticated `cloud.save` with `durable: true` enforcement. It does not call the v11.488 model-asset dispatcher.
- The account success message requires matching project identity, a confirmed remote project ID and an advancing integer revision. Missing confirmation remains an error, with real status details. Local-only saves never display an account success.
- Both §Chat panel and My Projects invoke this same function; the immersive VR account-save facade also points to it. No account secret leaves the existing §Chat host bridge.
- **Standalone Model/Particle asset Save to Account** remains untouched. A model asset and a full project are distinct things; saved identity and in-place revision checks must remain distinct.

## Browser My Projects layout

Retain the existing native project hub and all real on-device and account project cards. Reorganize in place:

- One coherent header showing the active project and account status.
- One action bar: **Save to Account**, **Save on Device**, **Refresh**. The account button is visibly unavailable while disconnected.
- **More project tools** contains the original less-used controls, including Clone, Revision History, local project selector, project import/export and model updates. Existing DOM nodes and click handlers are moved rather than recreated.
- Device and account galleries are distinct labeled sections with counts.
- Each project card retains Open and Preview as its two prominent actions. Delete, Export and Update are behind **More actions**, preserving confirmation handlers and default-project settings.
- Responsive layout, consistent text sizes, accessible labels and focus states, and no repeated primary save buttons.
- §Chat status has sufficient room to show an actual account-save error rather than truncating it.

The change is strictly in **browser My Projects + shared native account project save**. The immersive WebXR Projects dialog and controller menus, the source model, textures, UVs, animations, rigging, physical XR controls and persistent edit journal are not replaced.

## Verification and user acceptance

Compiled tests verify the new Save Project path without invoking asset save, a simulated successful durable revision, simulated cloud failure, account-disconnected behavior, module existence, hierarchy, preserved card action handlers, and inherited VR/Model Studio suites. The full source build must match `source-manifest.json` by SHA-256 and pass inline JavaScript syntax validation.

An actual signed-in §Chat save/load round trip requires owner testing: save **Smooth Witch Hat Copy**, then check the **Saved to Account** cards and revision, reload it and verify model geometry/UV and project history are still intact. If the server refuses a write, capture the displayed error before attempting any destructive reset or overwrite.

Do not interpret source or simulated tests alone as a successful authenticated cloud transfer.
