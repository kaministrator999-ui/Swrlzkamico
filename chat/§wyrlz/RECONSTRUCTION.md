# §wyrlz Clean-room Chat Reconstruction

**Version:** 1.0.1  
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

## Current component inventory

- **Foundation:** ACCEPTED as 1.0.1 — minimal document and viewport metadata only. The visible `§wyrlz` placeholder and page-title label were removed; the body is intentionally empty.
- **Ice Dragon canonical scenery:** NEXT.
- All other legacy Chat structure, composer, message surface, transport, settings, context meter, account/session UI, diagnostics, and optional tooling: NOT YET ADMITTED.
