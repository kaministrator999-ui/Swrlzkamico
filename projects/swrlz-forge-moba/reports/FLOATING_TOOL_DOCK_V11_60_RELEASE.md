# §E v11.60 floating tool dock — governed release candidate

Owner request: replace the bottom-half mobile Model Atelier inspector with a persistent compact vertical tool rail plus a movable, collapsible, independently scrollable floating panel, preserving the 3D viewport.

Additive `patches/v11_60_floating_tool_dock.py` builds on sealed v11.59, reuses all native controls and event handlers, protects the original 283-part character and all 43 assets, and changes only the editor presentation and public version badges. v11.60 canonical release marker `V11_60_FLOATING_MODEL_ATELIER_DOCK`, 92 patches, 2933489 HTML bytes, SHA-256 `20ba9446b3d778a852efbc458ed610e4c46938c2af83de46557dfaaf67e8ab98`.

Independently measured in CI [39356939978](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39356939978). Mobile and desktop Chromium dock interaction checks passed [39354801625](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39354801625) and [39356939978](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39356939978).

Merge and production deployment are independent gates. After production regression/tests and source merge, change `DEPLOY_REQUEST.json` only as the LAST main mutation. Require exact deploy terminal success, normalized hosted HTML + SOURCE/43 assets SHA audit and hosted desktop/mobile dock review; do not call live on source-only success.
