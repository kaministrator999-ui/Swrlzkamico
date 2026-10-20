# §E v11.60 floating tool dock — governed release candidate

## 2026-10-20 production closeout — deployment and hosted acceptance

The v11.60 tool dock is **LIVE**, not solely a candidate. Production source commit `67f835019f850788cc4b4eddf9ca57729e1c11ac` and final deployment trigger `e8cad46238e735135012a4c87319f5fe692d4639` correspond to [successful deploy 39369014929](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39369014929). [Independent hosted audit 39369120445](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39369120445) verified source receipt, 43 assets and 2,933,954-byte live normalized HTML SHA-256 `fe11e3e748184db1797ef66bc327f7867a25f91d431823a4c8794f157117d97f`. [Desktop and Android-browser character-editor tests 39369120456](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39369120456) passed.

**Where users find the controls:** [live editor](https://kamiloki-swrlz-forge-moba.static.hf.space/) → Model Atelier → right-side rail **Meshes / Sculpt / Lasso / Face / Topology / More**. Tap a category; drag **⠿ Move tools**; tap **✕ Hide** and a category to reopen. Existing editing, Undo and original 283-part project persist. Owner physical-phone UX and artistic likeness review remain separately unverified. Older pre-release text below remains historical. No production code, manifest or deployment request is changed by this documentation receipt.


Owner request: replace the bottom-half mobile Model Atelier inspector with a persistent compact vertical tool rail plus a movable, collapsible, independently scrollable floating panel, preserving the 3D viewport.

Additive `patches/v11_60_floating_tool_dock.py` builds on sealed v11.59, reuses all native controls and event handlers, protects the original 283-part character and all 43 assets, and changes only the editor presentation and public version badges. v11.60 canonical release marker `V11_60_FLOATING_MODEL_ATELIER_DOCK`, 92 patches, 2933954 HTML bytes, SHA-256 `fe11e3e748184db1797ef66bc327f7867a25f91d431823a4c8794f157117d97f`.

Independently measured in CI [39356939978](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39356939978). Mobile and desktop Chromium dock interaction checks passed [39354801625](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39354801625) and [39356939978](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39356939978).

Merge and production deployment are independent gates. After production regression/tests and source merge, change `DEPLOY_REQUEST.json` only as the LAST main mutation. Require exact deploy terminal success, normalized hosted HTML + SOURCE/43 assets SHA audit and hosted desktop/mobile dock review; do not call live on source-only success.
