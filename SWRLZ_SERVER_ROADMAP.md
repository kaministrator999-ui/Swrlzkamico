# §wyrlz Server Roadmap & Version Ledger

**READ WITH:** `SWRLZ_HOTFIX_RULES.md`  
- **Current overall server baseline:** `2.3.228`
- **Current Chat component:** `1.5.65`
- **Current LALM Engine:** `2.1.75` (`v64`)
- **Current Web Frontend component:** `1.0.3`
- **Current LALM UI component:** `1.0.0`
- **Current Frozen Web Collector component:** `1.0.8`
- **Current Deployment Control component:** `1.0.6`

**Release policy:** every server development event gets an overall Server release/version entry plus independent component version changes where applicable, including unsuccessful attempts.

## Version model

§wyrlz uses two levels of versioning:

1. **Overall Server version** — chronological development/release event of the complete server architecture.
2. **Independent component versions** — Chat, Web Frontend, LALM/R39, Server/Infrastructure, Admin, Deployment Control, and other independently maintained surfaces.

Version authorities are read at event entry and re-read immediately before version assignment/commit. Concurrent advances must be reconciled from the newest authority rather than overwritten.

Before implementing each feature/fix/optimization/refactor, perform the Project Start **Pre-Feature Architecture Reconciliation** using `docs/engineering/SWRLZ_ARCHITECTURE_RECONCILIATION_PROTOCOL.md`: inspect the selected/affected architecture and related work, confirm the canonical owner/integration path, and avoid duplicate or competing implementations.

## Core architecture accomplished

- `runtime` is the durable live application source of truth for hot application changes.
- `main` is the stable loader/infrastructure and engineering-contract boundary.
- Runtime-owned Chat/page/LALM updates are supported without ordinary Vercel redeployment.
- GitHub runtime source is authoritative; ephemeral worker/browser state is disposable.
- Chat uses the Ice Dragon frontend-first shell and runtime-owned Chat geometry/theme behavior.
- Chat visible versions derive from the `VERSION.txt` routing authority and mapped `versions/*.txt` value authorities.
- LALM hot loading has explicit entry/lineage cameras for fetch, hydration, inherited-contract, and generation failures.
- Deployment approval follows actual deployment capability/action, not branch name.
- Repository documentation is deployment-inert under the verified configuration and does not require deployment approval.
- The programming-LALM curriculum now includes an explicit architecture-reconciliation execution protocol: outcome framing, architecture-radius discovery, authority mapping, reader/writer/lifecycle tracing, source-vs-live-vs-history evidence separation, overlap classification, integration-path selection, new-module tests, and post-change ownership verification.

## Component ownership

| Component | Source of truth | Versioning rule |
|---|---|---|
| Overall Server | `runtime/versions/server-runtime.txt` + this roadmap lineage | Advances on every governed server development event |
| Web Frontend | runtime frontend assets + `runtime/versions/web-frontend.txt` | Advances when frontend architecture changes |
| Chat | `runtime/web/chat*` + `runtime/versions/web-chat.txt` | Advances when Chat UI/protocol/behavior changes |
| LALM/R39 | `runtime_hot/r39_engine*` + `runtime/versions/lalm-engine.txt` | Advances when LALM/inference behavior changes |
| Server/Infrastructure | `main/api/*`, deployment/configuration | Advances with stable infrastructure releases |
| Deployment Control | deployment-control authority + governing configuration | Advances when deployment-control behavior changes |
| Page system | `runtime_pages/manifest.json` + runtime page assets | Advances when page routing/system behavior changes |

## Hot-update boundary

Normally no Vercel deployment/restart is required for runtime Chat HTML/JS/CSS, stream behavior, runtime page assets, supported hot LALM/R39 changes, version-authority changes, or documentation/contract commits.

Documentation-only repository commits are explicitly **deployment-inert** and **do not require deployment approval**. If deployment configuration ever causes docs-only changes to create deployments, that configuration is treated as the defect to correct rather than making documentation approval-gated.

Actual deployment-capable stable loader/infrastructure/configuration changes remain behind the Deployment Approval Gate.

## Release ledger

### Server 2.3.228 — Programming-LALM architecture reconciliation curriculum

**Status:** engineering curriculum / governance source complete.  
**Affected module versions:** none; LALM Engine remains `2.1.75` / `v64`, Chat remains `1.5.65`.  
**Deployment / restart:** NONE.

The mandatory pre-feature architecture rule introduced in Server 2.3.226 now has a concrete programming-LALM execution method instead of relying on the vague instruction to “check the architecture.” The new `docs/engineering/SWRLZ_ARCHITECTURE_RECONCILIATION_PROTOCOL.md` teaches the engineering LALM how to turn a user outcome into bounded architecture discovery before implementation.

The protocol introduces architecture-radius traversal from the requested outcome through direct owner, readers/writers/dependencies, cross-cutting authority, and historical/live evidence only as far as needed. It requires an authority map rather than a file list; traces both data flow and control/lifecycle flow; searches by responsibility/state/readers/writers rather than only feature names; distinguishes current engineering authority, actual production activation, and historical evidence; and provides explicit stop conditions when ownership or activation remains materially ambiguous.

Existing work is classified before implementation as exact existing capability, partial overlap, legitimate composition, compatibility adapter, fallback, historical/retired path, conflicting duplicate owner, or genuinely independent new responsibility. The preferred integration ladder is now explicit: **reuse → extend canonical owner → refactor/consolidate → migrate+retire → create a genuinely independent structure**. New modules must pass an independent responsibility/lifecycle/state-contract/versioning test instead of being created because another layer is convenient.

The protocol also teaches Mask/Human/Brain placement, architecture-conflict signals, pre-implementation Architecture Reconciliation Records, post-change single-authority checks, and three verification dimensions when relevant: behavioral acceptance, ownership acceptance, and live activation acceptance.

**Architecture reconciliation for this event:** inspected the Project Start pre-feature rule, Version/Module Evolution programming curriculum, current roadmap, `docs/engineering`, current architecture contracts, version authorities, and deployment workflow. No existing dedicated method taught an engineering LALM how to traverse and reconcile architecture. Older formal control-plane documents were found that describe historical `dev`/`/tmp` behavior, demonstrating that the LALM must distinguish historical documentation from newer current Project Start/Hotfix/Roadmap/runtime authority rather than treating every formal document as equally current. The integration therefore keeps Project Start as the mandatory gate, adds one canonical execution curriculum under `docs/engineering`, and links that method into the Version/Module Evolution curriculum instead of duplicating another policy system.

**Intentionally unchanged:** no R39/inference source, Chat runtime behavior, server API, persistence schema, loader, deployment configuration, or component version was changed by this curriculum event.

**Verification:** the protocol is now a required Project Start document; the Version/Module Evolution contract incorporates architecture discovery before module/version impact; current `VERSION.txt`, Server/LALM/Chat authorities were re-read at the version boundary; the deployment workflow still only auto-triggers from `.deploy/REQUEST.txt` on `main` or explicit workflow dispatch, so these documentation/curriculum commits are non-deploying.

**Lineage:** architecture protocol `0db88e04f0f5059a7e9244e80b2cf1f8b8f0c5cc`; Project Start integration `a8d2f6203036c11611cf434a09c429753e8ed52f`; Version/Module Evolution integration `d91b2750b6d0e1f956f810defa6c04826eb768d6`; Server authority `1dafa6163956137a66269855677c606c42b034fe`.

### Server 2.3.227 — R39 v64 complete cold-load namespace repair

**Status:** runtime source complete; live rendered verification pending.  
**LALM Engine:** `2.1.75` / `v64`.  
**Chat:** `1.5.65` unchanged.  
**Deployment / restart:** NONE.

Production hot-loader cameras proved v63 successfully reached the repaired planner bootstrap but failed during inherited v55 hydration with `NameError: name '_response_contract' is not defined`. Architecture reconciliation traced both `_plan_response_budget` and `_response_contract` to the canonical implementation module and confirmed v55 captures both names immediately after v54 hydration, while v54 publishes neither into the shared exec namespace.

v58d now installs lazy canonical bridges for both symbols **before** v57→v56→v55 hydration. v60d preserves the v59 acceptance/completion lineage over v58d, and v64 preserves the v61 context-focus layer over v60d. The active hot entrypoint now targets v64 and its loader camera reports both planner and response-contract readiness on successful hydration.

**Architecture reconciliation:** extended the existing hot-loader lineage/camera architecture; no alternate LALM loader, Chat-side cognition, or duplicate response-contract implementation was introduced. Canonical response planning/contract behavior remains owned by the inherited R39 implementation; the repair only exposes those existing callables at the timing required by later wrappers.

**Verification evidence before repair:** repeated production `/api/lalm/status` and `/api/chat` traces reached v63 → v60c → v58c, emitted `prehydrate-bridges-ready`, then consistently failed at `hydrate-v57-failed` with `_response_contract` undefined. This isolated the defect to inherited namespace hydration rather than Chat presentation or cache.

**Lineage:** v58d `086652e834b340aaba8e70b5f8ca2a8d4f4f33cf`; v60d `1e3f6ff76df766a59538c369ed6d056becd3f515`; v64 `545dfb82d87654923c6f19dff65c52c71810e351`; active entrypoint `721b21d1ef8d48206933412729cd846b1fb39380`; LALM authority `cec503c30a5a74ec5ee17a076ef223865dc5e7c3`; Server authority `f3f37ce35599c37f11c80752e8ee85983802bd81`.

### Server 2.3.226 — Mandatory pre-feature architecture reconciliation governance

**Status:** engineering-contract and roadmap source complete.  
**Affected module versions:** none.  
**Deployment / restart:** NONE.

Project Start requires architecture reconciliation before implementation so related/partial/retired implementations are inspected and canonical ownership is deliberately reused, extended, refactored, or retired rather than stacked.

### Server 2.3.211 — Chat live version authority + phone drawer lineage

Chat visible versions were routed through the live version authority. Later mobile work superseded the original full-phone drawer geometry; current rendered-device geometry is governed by the accepted bounded drawer/runtime viewport implementation.

### Server 2.3.210 — Chat single geometry authority correction

Account identity and early-shell layers stopped independently owning workspace/message/composer geometry; runtime viewport CSS became the post-boot geometry authority while Google identity behavior remained separate.

### Roadmap reconciliation note

Historical release entries omitted from this compact ledger remain in Git history and runtime release records. This ledger is reconciled to the current authoritative runtime files rather than fabricating omitted intermediate events.