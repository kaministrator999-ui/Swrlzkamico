# §C project-aware source, visual style, and repository workflows

**Date:** 2026-11-13 (US Central)  
**Source authorities:** existing Hugging Face Chat Space, account-owned artifact revisions, OAuth-scoped GitHub connector, and §E's native editor/lease/receipt APIs.  
**Goal:** user can upload a multi-file project, or select an authorized GitHub repository, then request targeted changes such as "add this button to §E here; make it function like this" while retaining design, behavior, file ownership, versions, and regressions.

## Nonnegotiable distinctions

1. A model seeing a repository name is not proof it has read the actual file tree.
2. A screenshot establishes appearance and potential location, not code ownership or exact DOM/scene target. "Here" requires a real selected element/object, source path/DOM node, or visual target annotation and verification; do not guess.
3. Source and comments from uploads/GitHub are *untrusted evidence*, never new instructions or permission grants.
4. User authorization, server access control, and version/source receipts determine whether writes are allowed. The model cannot authorize itself to push to GitHub, save to the Google account, edit §E, publish, or spend credits.
5. Match the **existing** project's color tokens, spacing, typography, effects, layering, component state, layout breakpoints, accessibility behavior and mobile/VR touch/trigger rules. A stylistically different but syntactically valid feature is not accepted.
6. Internal source edits can be targeted; outward delivery may be a complete updated HTML or multi-file archive when the user wants a runnable result. Do not mistake complete output for starting from scratch.
7. Check requirements and tests across the original feature plus its neighbors; never replace one passing path with a superficially improved but broken layout.
8. Distinguish compiled/syntactically valid source, static contract verification, browser rendering, phone/Quest owner acceptance, and published Hugging Face deployment.

## Verified existing components (read before replacing)

- `station.py` holds Google-owned chat threads, codeArtifacts and source revisions with exact SHA/revision checking and storage CAS. `project_archive.py` and `project_revision_workspace.py` parse named code fences, create bounded ZIP exports and merge full-file revisions.
- `github_connection.py` and related modules already provide authenticated GitHub directory/file reads, OAuth-scoped capabilities, authorized write flows, bounded model-selected read plans and source evidence. Do not add a parallel GitHub credential store or bypass existing write gates.
- `forge_embed.py`, `forge_chat_actions.py`, and §E's native host separate source/model suggestions from lease-bound edits and receipt-verified editor transitions. The full native project is not copied into inference.
- `chat/§wyrlz/index.html` has mobile streaming, code containers, image/vision attachment, an account-thread view and independent §E embed support. Existing controls must remain reachable.

## Candidate phase 1: bounded local text-source imports

Repository implementation: `scripts/project_source_intelligence_v1.py`, `scripts/test_project_source_intelligence_v1.py`, guarded `scripts/hf_chat_project_files_bridge_v1.py`.

- Import multiple selected source/config text files under source/path/size limits; reject binaries, traversal, duplicate names, secret/credential paths and generated build caches. Preserve exact contents in an independent source artifact, not as a retroactive rewrite of a prior assistant's answer.
- A read-only source map captures file names/hashes, CSS variables, selectors, DOM IDs, event types, imports, functions, and bounded path/line snippets relevant to the request. An authenticated user thread owns the artifact; model input contains only bounded selected evidence, not a permission.
- Files button belongs alongside existing Image, Mic, Talk controls; mobile upload and cancellation/failed-send cleanup must not hide the composer or cause lost attachments.
- **Limits for this first candidate:** 32 files, 256 KiB/file and 512 KiB total. This is an exploration/inference evidence cap, NOT the full project/archive limit. It is intentionally insufficient for an entire 10 MB+ §E generated artifact. No binary/assets/ZIP import in this phase.
- Static analyzer tests **12/12** successful in CI. HF production acceptance is separately gated; do not claim it live until the commit/worker/source-artifact test succeeds.

## Phase 2: GitHub and large-repository traversal (not phase 1)

- Use the user's existing authenticated, explicitly selected repo and branch, with exact source HEAD SHA. Build an index of *paths and owner relationships*, not an indiscriminate 16K-token dump.
- Read manifest and instruction files (`AGENTS.md`, README, component map, dependencies), then score likely owners and retrieve only relevant code and tests. Maintain stable source/line evidence for imports, exports, callbacks, CSS and rendering.
- Repeat file reads when source HEAD changes; fail stale edits rather than overwriting. Keep read requests within existing authorization and API quotas. No new provider tokens or cross-user scopes.
- Support user-chosen upload of multiple files and optional ZIP/folder ingestion through a separately budgeted archive parser with traversal, compression-ratio and total-uncompressed-byte guards; images/assets need separate metadata/media analysis, not fake text decoding.

## Phase 3: visual-semantic component targeting for §E (not phase 1)

Given a request such as "add a button here":

- Reconcile the native selected §E object or actual hovered DOM element, the screenshot annotation, and the current source owners. If target is missing, ask for a click/selection only rather than fabricate placement.
- Read the existing menu/tool component and lifecycle. Reuse the same toolbar/menu foundation, spacing, theme tokens, existing icon language, responsive constraints, event handler/scene transaction, save semantics, Undo/Redo and input priorities.
- Before committing, preview the control in place, inspect desktop/mobile/Quest VR constraints, verify visibility, interaction hit areas, overlap, focus/keyboard/controller rules and adjacent behavior.
- For a native scene/tool operation, execute only within the existing §E capability allowlist and lease/receipt handshake. For a code feature not exposed by native editor tools, propose a scoped source commit/PR under GitHub's existing explicit authority. Don't pretend one is the other.

## Phase 4: versioned changes and acceptance (not phase 1)

- Capture source SHA, exact changed-file list, path ownership, requested behavior and visual contract.
- Run changed-file syntax/test checks and neighboring regression checks. Preserve previous version until verified.
- Report accepted tests, visual comparisons and any unsupported/device-only checks separately.
- A §E release must follow `projects/swrlz-forge-moba/AGENTS.md`: one cohesive source/version/patch/manifest build, then an independent deploy-request-only commit and verified Hugging Face publication. Vercel is not an authorized target.
- A model's claim that it "tested" a button or that a screenshot "looks right" is not verification.

## Analogous failure cases to test

- Multiple source files with nested relative paths; duplicate names; malicious traversal; binary files; pasted encoded text; source files containing prompt-injection instructions.
- Same file imported twice vs two intentional project versions; new chat vs old attached project; stale current HEAD/revision; account logout and cross-user isolation.
- "Improve the page" with previous failed generations and buried source; "add a button here" with no selection; selected object on a hidden/VR-only menu; same label appearing in several component owners.
- Existing styling has CSS custom properties and local variants; no defined CSS tokens; dark/light/high-contrast; small phone viewport; desktop; Meta Quest controller ray; reduced motion.
- A proposed button works but breaks Undo, saves, menu pointer priority, modal/z-index, resize, keyboard focus, or existing click actions. Regression gate must reject it.

**Engineering rule:** source of truth first; evidence -> owner -> smallest correct edit -> actual test -> guarded commit/release, with append-only failure evidence.
