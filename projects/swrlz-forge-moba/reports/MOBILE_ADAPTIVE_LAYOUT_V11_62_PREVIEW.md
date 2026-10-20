# §E v11.62 mobile adaptive layout — tested preview

**Status:** development PR #279, not deployed to the live §E. The current hosted production engine remains v11.61.

## Where to find and use

Open §E → **Model Atelier** on a phone.

- The right-hand tool rail now has **☷ Tools**, which opens a single contextual bottom drawer. The old inspector remains mounted and functional as the native source of truth but is hidden on mobile.
- Tap **Meshes, Sculpt, Lasso, Face, Topology, References, Motion, or Appearance** on the tool rail to open the corresponding contextual operation group.
- Select a related operation from the **horizontal scrollable strip** at the top of the drawer. Its original native properties and actions appear underneath, in a readable single-column layout.
- Use **▁ Collapse**, **◧ Half**, and **⛶ Expand** in the drawer header to control how much screen space the tools occupy.
- The original source data/geometry, Undo, and model save/export handlers are unchanged. Desktop retains the existing floating inspector / split contextual panels.
- Phone landscape gets its own smaller drawer height limits; touch inputs have a minimum target height of 44px where the adaptive surface applies.

## Verified evidence

[Four viewport browser test PASS](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/39469609173): 360×740, 412×915, 700×400 landscape, 1280×850 desktop. The test rebuilds exact sealed v11.61, verifies the original SHA256/bytes, applies additive patch, checks 283 unchanged parts, verifies phone single-drawer behavior, native source inspector preservation, open/close, group selection, drawer height states, and no page errors.

## Deliberate limits and next release gates

- **Do not claim v11.62 is live** until source-manifest/version update, full release regression suite, sole final DEPLOY_REQUEST mutation, Hugging Face deployment, and hosted asset/browser audit have succeeded.
- This patch targets **Model Atelier only**. Anime/Story Studio and game-builder HUDs are separately styled components and not silently modified.
- Physical device usability, software-keyboard viewport adjustment and persisted one-hand layout preference need expanded acceptance; simulated Chromium tests are not a physical Android UX signoff.
- Source patch: `patches/v11_62_mobile_tool_layout_preview.py`; test: `tests/model_atelier_mobile_layout_browser_v11_62.mjs`; CI: `.github/workflows/preview-atelier-mobile-v11-62.yml`.
