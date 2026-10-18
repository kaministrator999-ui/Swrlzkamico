# §wyrlz Rich Widget Atelier v284 — isolated candidate

Stage: SOURCE CANDIDATE / STATIC VERIFIED, NOT INTEGRATED OR LIVE-ACCEPTED.
Base: commit 736120579cc250a82319b157cfd661b61e6a06b1 (v283 accepted source).
Owner: clean-room Chat at /chat/§wyrlz; this is NOT Forge §E 3D modeling.

## Scoped implementation
Extend the existing swrlz-widget-v1 and one canonical renderWidgetStack slot, not a second framework.

- hf_space/chat/§wyrlz/assets/rich-widgets-v284.js: typed, bounded comparison, math-graph, model-3d renderer.
- hf_space/chat/§wyrlz/assets/rich-widgets-v284.css: mobile/accessibility styling.
- hf_space/chat/§wyrlz/assets/widget-atelier-v284.html: opt-in synthetic-data visual preview only.
- chat/§wyrlz/index.html: dispatch through preexisting structured widget card.
- hf_space/station.py: one script and stylesheet, served from preexisting StaticFiles asset route.
- tests/test_rich_widgets_v284.cjs and .github/workflows/rich-widgets-v284.yml: isolated acceptance only.

## Data contracts and safety
Existing envelope: {contract:swrlz-widget-v1,kind,version:1,title,provider,data}; no new persistent state.
Comparison: 2–4 items, up to 6 metrics; only explicit higherIsBetter ranks a metric. Numeric bars compare within each metric, not across mixed units. Numbers are not evidence of factual measurements.
Math: 1–5 explicit typed polynomials (degree <=3) or sine curves; finite axes/coefficients; safe equation text and local canvas plotting. Pan by pointer/keyboard, zoom/reset buttons. No eval, raw arbitrary math expression execution or external CDN.
3D: bounded cube, sphere, torus or pyramid wireframe meshes projected locally to Canvas 2D. Pointer and keyboard rotation; zoom/reset. This is not WebGL, mesh import, physics, rigging or Forge.
Text rendering uses textContent, never assistant-content HTML. Invalid widgets fail closed. An assistant prose reply is never itself executable widget metadata.

## Existing ownership and cameras
Only Station emits and persists structured WIDGET metadata; Chat presents. Keep weather, time, search, GitHub and other widget implementations unchanged. Use existing Station WIDGET events, request traces and widgetKinds summaries as cameras; no raw proprietary geometry or arbitrary private data logging. Camera OFF/ON must not alter functional rendering.

## Verification
- CI 39145092917 FAILED on a real guard defect: a degenerate user-specified graph domain silently defaulted rather than failing.
- Correction e068710782f1c246f203ae350e5c05d7d368d1f4 rejects invalid explicit axes.
- CI 39145156950 SUCCESS on JS syntax, six Node behavior/contract tests and Python Station compile.
- Browser touch/keyboard acceptance, deployed asset integrity, phone acceptance, automated data producer, account behavior, model generation quality and production activation NOT YET VERIFIED.

## Next governed integration
Re-fetch newest canonical source and Roadmap. Preserve concurrent branches. Review exact diff, run browser/device verification and combined CI, then integrate with one writer. Register module versions and Roadmap lifecycle at the real governed commit. If release-worthy, use only the canonical guarded main Hugging Face request, observe terminal deployment and verify live acceptance; never infer known-good from unit tests.

No Server Runtime/Web Chat version bump, merge or production deployment is claimed by this standalone candidate.