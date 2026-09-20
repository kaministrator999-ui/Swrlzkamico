# §wyrlz Clean-room Chat Reconstruction

**Version:** 1.0.11  
**Canonical source:** `main:chat/§wyrlz/`  
**Legacy reference:** `main:web/chat.html`

## Construction rule

The clean-room Chat is rebuilt from the minimal §wyrlz page by admitting legacy capabilities one component at a time. The legacy page is evidence/reference, not an opening shell and not a bulk dependency.

For every component migration:

1. Identify the component's single responsibility and exact legacy source.
2. Identify required dependencies and reject unrelated coupling.
3. Decide whether it belongs to static opening structure, functional hydration, or optional/deferred behavior.
4. Integrate only that component into `chat/§wyrlz/`.
5. Verify first paint, DOM/layout mutation, errors, and intended behavior with cameras/logs.
6. Record acceptance/correction before beginning the next component.

## First-paint law

The browser must not construct a generic legacy Chat and then transform it into Ice Dragon. When Ice Dragon is integrated, its stable opening scenery is owned by the initial clean-room source. JavaScript may hydrate behavior after parse, but must not replace the opening visual identity.

## Runtime boundary

Runtime-hot is not part of this reconstruction phase. The clean-room Chat is a server-deployed product surface: permanent page structure and accepted components are integrated into stable source, and the server deployment carries the accepted Chat generation only when the reconstruction reaches an explicitly approved load checkpoint. The audience must not assemble or hot-load this Chat from runtime repositories.

## Version lineage

Clean-room Chat starts at **1.0.1**. It is independent from the legacy Web Chat 1.5.x lineage. Each accepted component-level change advances this clean-room lineage according to the project version-evolution contract.


## Camera-first admission law

Observability is part of every component, not a later debugging add-on. A component is **not admitted** into the clean-room Chat unless its head-to-toe execution/render path is observable through structured cameras that §wyrlz can retrieve from the server-side diagnostic surface after deployment.

For every rendered or behavior-bearing component, cameras must cover, as applicable:

`source/version identity → component admission/start → dependency readiness → DOM creation/attachment → style/theme application → render/visibility state → geometry/layout changes → animation/frame transitions → event binding → user interaction → state mutation → network/server handoff → response/state application → terminal/settled state → error/fallback/removal`.

Every camera event must use a stable component ID, clean-room Chat version, correlation/request/session identity where applicable, monotonic/high-resolution timing where available, event name, bounded state/geometry metadata, and source/revision identity. Credentials, tokens, cookies, and authentication secrets are never logged.

Rendered components additionally require mutation/layout/frame observation sufficient to identify **what rendered, when it rendered, what changed its geometry/visibility, and which writer caused the change**. Cameras must be installed with the component rather than retrofitted after a defect.

Client/browser cameras must have a bounded server diagnostic ingestion/storage path that can be queried during development. Console-only telemetry does not satisfy this contract. If §wyrlz cannot retrieve the evidence, the component is not camera-complete.

The component acceptance cadence is therefore:

`integrate component + cameras → deploy approved checkpoint → pull correlated logs → inspect head-to-toe path → accept/correct → document → next component`.


## Current component inventory

- **Foundation:** ACCEPTED as 1.0.1 — minimal document and viewport metadata only. The visible `§wyrlz` placeholder and page-title label were removed; the body is intentionally empty.
- **Ice Dragon wallpaper / first-paint scenery:** ACCEPTED as 1.0.2 — canonical Ice Dragon image is initial-document scenery with no JavaScript/runtime/late injector. Repeated fresh-deployment audience tests showed immediate clean first paint.
- **Composer / opening stage scenery:** SOURCE-INTEGRATED as 1.0.11 — preserves the compact 42px mobile / 44px desktop resting rail and native keyboard-safe anchoring, then auto-grows upward with wrapped input text. Growth is bounded to 50% of the current visible viewport; beyond that cap the textarea becomes vertically scrollable. The send control remains anchored at the lower-right of the expanding composer. This is the first minimal composer behavior rigging; no send/transport behavior is admitted. Composer shell now uses an explicit `bottom:0`; safe-area inset is applied as padding rather than as the positioning coordinate, preventing environment-variable resolution from moving the fixed shell away from the viewport edge.
- **Side-menu control / opening stage scenery:** SOURCE-INTEGRATED as 1.0.11 — compact fixed top-left glass menu button with a hamburger glyph, safe-area-aware placement, and accessibility semantics. Button is scenery/control affordance only; drawer opening behavior and side-menu contents are not yet admitted. Top anchoring is explicitly 12px rather than using the safe-area environment variable as the positioning coordinate.
- **Ice Dragon remaining scenery/components:** NOT YET ADMITTED.
- All other legacy Chat structure, message surface, transport, settings, context meter, account/session UI, diagnostics, and optional tooling: NOT YET ADMITTED.
