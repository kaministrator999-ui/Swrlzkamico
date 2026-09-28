# §wyrlz Clean-room Chat Reconstruction

**Version:** 1.0.55  
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
- **Composer / opening stage scenery:** SOURCE-INTEGRATED as 1.0.12 — preserves the compact 42px mobile / 44px desktop resting rail and native keyboard-safe anchoring, then auto-grows upward with wrapped input text. Growth is bounded to 50% of the current visible viewport; beyond that cap the textarea becomes vertically scrollable. The send control remains anchored at the lower-right of the expanding composer. This is the first minimal composer behavior rigging; no send/transport behavior is admitted. Composer shell now uses an explicit `bottom:0`; safe-area inset is applied as padding rather than as the positioning coordinate, preventing environment-variable resolution from moving the fixed shell away from the viewport edge. Correction: removed `max()`/`env()` from the shell padding declaration entirely; the shell now uses the last-known-good fixed 8px bottom padding while retaining `bottom:0`.
- **Side-menu control / opening stage scenery:** SOURCE-INTEGRATED as 1.0.11 — compact fixed top-left glass menu button with a hamburger glyph, safe-area-aware placement, and accessibility semantics. Button is scenery/control affordance only; drawer opening behavior and side-menu contents are not yet admitted. Top anchoring is explicitly 12px rather than using the safe-area environment variable as the positioning coordinate.
- **Ice Dragon remaining scenery/components:** NOT YET ADMITTED.
- All other legacy Chat structure, message surface, transport, settings, context meter, account/session UI, diagnostics, and optional tooling: NOT YET ADMITTED.

- **1.0.13 opening geometry:** composer shell is explicitly pinned to the viewport bottom; top-left side-menu shortcut remains a three-horizontal-line hamburger control. No drawer behavior added.

- **1.0.14 parser repair:** removed literal `\\n` tokens between menu-button CSS rules. Those tokens invalidated the selector/rule boundary and swallowed the following `.composer-shell` declaration, which is why the footer rendered in normal document flow at the top despite its source text saying `position:fixed; bottom:0`.

- **1.0.15 side menu:** hamburger now opens a left sliding drawer with a full-viewport blue dimming shade. The bottom drawer box displays the complete canonical runtime VERSION.txt registry values read from their owning `runtime:versions/*.txt` authorities at this integration checkpoint. Shade tap closes the drawer; no legacy Chat surface is reintroduced.

- **1.0.16 version panel:** reduced the drawer Versions box maximum height from 42vh to 26vh while preserving independent vertical scrolling and hiding horizontal overflow.

- **1.0.17 drawer account + versions:** Versions is now a header-toggled collapsible panel that retains bounded scrolling when expanded. Immediately above it, the drawer uses the existing server account contract (`/api/account/status`, `/api/account/me`, `/api/account/google`, `/api/account/logout`) and Google Identity Services; it does not create a second account authority. Existing signed HttpOnly session state is checked on load, sign-in credentials are server-verified, and sign-out uses the canonical account route.

- **1.0.18 legacy-account routing correction:** the clean-room drawer account UI now routes status, session restore, Google credential verification, and logout through the existing `/live/api/account/*` server surface used by the legacy/server-backed Chat architecture. The clean-room static Vercel deployment does not own Python account functions, so direct `/api/account/*` calls on that isolated project were the wrong boundary. No duplicate auth authority was introduced.

- **1.0.19 account transport trace:** ancestry/source inspection confirmed legacy Google verification is canonically `/api/account/*`; `/live/api/account/*` was an incorrect inferred prefix and produced non-JSON responses. Clean-room account requests now target the canonical account paths at the legacy server origin and wrap every request with an account camera capturing path/status/content-type/body preview/duration or network error. The camera also attempts relay to `/api/chat/client-debug`; console trace remains available when the isolated static deployment has no debug ingestion route.


## Research-tier continuation

The component inventory above is historical through the early clean-room reconstruction. Later research-driven Chat evolution continues the same canonical owner and does not replace that lineage.

- **1.0.48 — Tier A visual foundation:** tokenized Glitch Dragon/Ice Dragon visual system, compact top edge, drawer/message/composer refinement, reduced-motion baseline, and bounded UI cameras. No transport/account/LALM ownership changed.
- **1.0.49 — Tier B settings shell:** General, AI/Model, Appearance, Motion, Accessibility, and Privacy surfaces. Existing account profile authority is reused for explicit user-triggered settings persistence; previews remain local until Save.
- **1.0.50 — Tier C profile + lore source integration:** adds You and §wyrlz profile surfaces plus Lore & Memory inspect/create/edit/delete UI. The stable account authority gains `companion_profile` and account-owned `LoreRecord` storage with USER-authored manual writes, source/provenance, scope, active/editable state, optimistic versioning, and payload-redacted Redis diagnostics. Proposal Inbox is presentation-only until Tier D installs the durable proposal/approval protocol. Shared rapport remains Tier E.

Tier C requires a later explicitly approved stable-server deployment before its new `/api/account/lore` routes can be accepted as live. Source integration alone is not runtime acceptance.


- **1.0.51 — Tier D approval protocol:** account-owned AI proposal records + append-only audit history, bounded profile/companion/lore operations, user Edit/Approve/Decline/Revert, per-category ASK/AUTO_LOW_RISK/SESSION_ONLY/NEVER policy, Redis compare-and-set proposal claims, reversible before/after snapshots, and payload-redacted diagnostics. Browser clients cannot forge assistant-authored proposals. A trusted server submission helper exists, but the current R39 stream does not yet emit a structured proposal event; natural-language output is not scraped into durable proposals.


- **1.0.52 — Tier D.1 structured proposal bridge:** the durable Workstation subscriber now consumes only exact trusted `ACCOUNT_PROPOSAL` events using `swrlz-account-proposal-signal-v1`. Signals require bounded `signalId`, category/target/operation/payload/rationale fields, and receive authoritative thread/request identity from the Workstation job. A stable proposal ID derived from `requestId + signalId` suppresses at-least-once duplicates before target lookup. Proposal payload/rationale never enter the ordinary chat stream; only sanitized decision/id/state/category/operation/risk/version receipts may flow as STATUS metadata. Chat invalidates/refetches Proposal Inbox state from those receipts. Browser clients still cannot create assistant-authored proposals, natural-language output is never scraped, and the current R39 generator does not autonomously decide when to emit the structured signal.


- **1.0.53 — Tier E shared rapport:** introduces a separate account-owned Rapport domain for shared vocabulary, callbacks, and interaction conventions. Rapport records carry kind, cue, meaning, optional preferred response, source/provenance, GLOBAL/THREAD/PROJECT scope, active state, generation, optimistic version, and authorship. A versioned RapportControl owns pause state and lineage-preserving reset generations: reset advances the current generation instead of deleting history. Current Chat can inspect reset history, edit only the active generation, pause/resume, and reset. THREAD scope is ownership-validated; new PROJECT scope is blocked until a project authority exists. AI-originated rapport changes use the existing Tier D proposal gate under SHARED_RAPPORT with bounded RAPPORT_CREATE/UPDATE/DELETE operations; auto-low-risk is suppressed while rapport is paused. Tier E does not inject rapport into R39 inference.


- **1.0.54 — Tier F companion animation state machine:** binds companion presentation to existing Chat/Station truth rather than a parallel runtime authority. States are idle, listen, accepted, thinking, acting, responding, approval, and error. Prompt focus/input may produce listen only when no active generation exists; send start/ack produces accepted; active pre-output generation maps conservatively to thinking unless an explicit action/tool/work phase exists; visible generated text produces responding; proposal wait/approval phases produce approval; terminal/client failures produce error. Unknown active phases default to thinking/responding based on whether response text exists. State is exposed through `data-companion-state` plus an accessible text chip, so meaning never depends on motion alone. CSS-only restrained animations decorate the top dragon mark and assistant avatar; no canvas/WebGL/particle engine/animation-frame loop/network decoration was added. Reduced/Off/system-reduced-motion modes disable looping icon/dot animations and retain static state color/border cues.


- **1.0.55 — Tier G work surface, agent cards, and evidence:** completes the research blueprint with a compact right-side Work surface that stays backstage from the main conversation. Tool/action cards are rendered only from explicit structured Station phase/category metadata; assistant prose is never scanned or interpreted as tool activity. Proposal receipts and real pending Tier-D records render as approval cards that navigate to the existing Proposal Inbox rather than creating a second approval authority. The artifacts section consumes only explicit structured artifact metadata and otherwise states that no structured artifacts were emitted. Assistant messages gain expandable Evidence / provenance details from allowlisted committed-message lineage (requestId, projection authority, source authority, turn contract, commit phase, terminal type) plus any already-structured source/evidence arrays if present. External links are limited to validated HTTP(S) URLs. The side surface adds no background polling, canvas/WebGL, animation loop, or decorative network call; mobile becomes full-screen and reduced-motion/high-contrast/reduced-transparency remain supported.
