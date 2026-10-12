# §wyrlz GitHub Project Workbench — v213

## Purpose and authority

Make §wyrlz useful for genuine GitHub-based project engineering: understand a repository, inspect code/evidence, compare branches, review PRs, triage CI and issue history, prepare a small source correction, and open a draft review PR. These tools reuse the existing verified Google-account-owned encrypted GitHub connection and explicitly selected repository. They are not a freeform shell, git CLI, browser automation runner, model-generated API client or unrestricted code-edit agent.

**Source provenance:** Each operation reads the real GitHub REST response using verified account authorization and selected repository. Issue bodies, source files, comments and workflow YAML are untrusted data and do not grant new permissions, override the user, create arbitrary tools or require model obedience. Model reasoning is exposed as high-level, factual tool progress—not hidden chain-of-thought.

## Read-only engineering commands

| Command | Grounded action |
| --- | --- |
| `@GitHub project guide` | Explain the actual project development lifecycle, review discipline, CI/truth levels and allowed commands |
| `@GitHub overview` | Verify selected repository metadata and its default branch |
| `@GitHub project brief` | Read bounded excerpts of `§wyrlz_§tart.md`, README, CONTRIBUTING, PR template and AGENTS if available, with blob provenance |
| `@GitHub dependencies` | Inspect bounded Python/Node/Rust/Gradle/Docker manifest excerpts, not guess language/build tooling |
| `@GitHub triage` | Snapshot open issues, draft/open PRs and recent Actions runs without fabricating priorities |
| `@GitHub tree` or `@GitHub tree src` | Recursively list a bounded Git tree at the verified default HEAD, explicitly report truncation |
| `@GitHub code search gather` | Ask GitHub's own code-search API for a literal term within the selected repository, report paths not unverified snippets |
| `@GitHub file history src/module.py` | Return provider commit messages and source SHAs affecting one named file |
| `@GitHub compare main...feature/work` | Compare named refs via the official three-dot compare API; report merge base/changed paths |
| `@GitHub pr review 123` | Inspect PR head/base, file changes and actual check-run status/conclusion |
| `@GitHub issue inspect 123` | Inspect one verified issue, bounded description/labels/recent comments |
| `@GitHub checks <40-char-SHA>` | Read check-run state for one exact commit; no fabricated CI pass |
| `@GitHub project readiness` | Read HEAD and check-run/Actions evidence, explicitly **not** a release approval certificate |
| `@GitHub branch policy` | Inspect GitHub default-branch protections when this account can read them; 403 is **unknown**, not unprotected |
| `@GitHub releases` | List bounded GitHub Releases/tag metadata; a Release is not proof of deployed healthy runtime |

The selected existing §wyrlz model may propose up to three allowlisted read operations from a conversational request. It may include a parameterized read such as `pr review 123`, `issue inspect 123`, `checks SHA`, `code search TERM`, `file history PATH`, or `compare BASE...HEAD` only when the user's actual message names the relevant identifier and intent. All model proposals are untrusted: server-side tool validation and a fresh repository permission check remain authoritative. Invalid model plans fall back to labeled, bounded read checks.

**Pagination:** This release shows partial first pages and labels them; it does not claim exhaustiveness for all files, PR checks, search matches or history. GitHub search may be incomplete, unindexed, disabled or unavailable with a given OAuth grant. A failed request is not proof no matching code exists. The read-only summary returns no access tokens and never executes retrieved repository text.

## Controlled change workflow

Exact two-stage command syntax:

`@GitHub edit file src/example.py on feature/fix-example replace OLD_LITERAL :: NEW_LITERAL`

- User must type the exact path, **existing** feature/fix/chore branch and two bounded nonempty, single-line literal fragments (up to 180 characters each). The old fragment must occur exactly once.
- Reject default/runtime branches, root/nested `.env` files, `.github/`, `.deploy/`, versions, sensitive credential/key/token paths, binary/nonallowlisted file extensions and invalid path traversal. Limit read to 90 KB of UTF-8 file content; nothing changes if unverifiable.
- Verify effective repository branch-write authority. Record branch HEAD SHA and source Git blob SHA, present a before/after review and issue a **one-use, 10-minute Google-owner-and-repository-bound** `@GitHub confirm CODE`. No write at proposal time.
- At confirmation, independently recheck account, selected repo, OAuth scope/repo role, feature branch HEAD, file blob and exact old literal. Only then issue a SHA-CAS GitHub Contents PUT for precisely that file on that branch.
- Report a confirmed response only when GitHub supplies the expected path and a valid commit SHA. No automatic PR, merge, deploy or known-good claim. User should inspect the diff and tests.

Draft PR review syntax:

`@GitHub pr draft feature/fix-example into main`

- Only existing feature/fix/chore head, verified real default base, bounded compare with no protected file paths and a short, fully verified file list.
- Preview exact changed paths, branch SHA and target. A separate one-time confirmation rechecks repo authority, branch SHA and diff file set, then requests a **draft** PR—never an automatic merge.
- Opening a PR can itself activate the repository's PR workflows. Inspect potential CI/release implications before confirmation. All production deploy/release operations remain under the independent guarded Space release procedure.

## Practical development loop §wyrlz should teach

1. Identify project, account, purpose, branch, source-of-truth documents, original user constraints, and what “done” means.
2. Look up repository structure, relevant exact source, dependencies and recent commits—do not hallucinate files.
3. Diagnose by comparing specific refs, examining PR files/checks, issues, failed job steps, and exact GitHub evidence.
4. Plan a minimal patch and its tests; explain what is supported and what needs owner approval.
5. Prefer a feature branch, and preview **only** the actually supported literal edit or existing safe workflow template.
6. Require explicit user approval before any branch/file/PR/dispatch changes, and separately approve any new OAuth scopes with GitHub.
7. Run or inspect appropriate checks via the supported Actions workbench. “Queued”, “in progress”, “accepted”, “CI-success”, “published” and “owner-accepted” are different states.
8. Review source SHA, CI and release notes against the live release owner. Preserve rollback. Do not claim a newly deployed version is known-good without real-user acceptance.
9. Record progress and decisions in the existing Roadmap. Keep unfinished work scoped to clear next actions and avoid duplicating concurrent updates.

## Intentionally NOT supported

Unrestricted model-generated patches, arbitrary GitHub shell/terminal or network commands, arbitrary URL access, auto merges, production branch direct writes, deploy or secret management, repo deletion, PR autoapproval, arbitrary Workflow YAML changes, broad autonomous branch loops, hidden paid API usage, claiming a model understands uninspected code, and GitHub access escalation without user consent.

Additional valuable future tiers: safe multiline patch/diff parsing with static checks, trusted sandbox execution, GitHub issues/PR conversations with explicit review feedback, check-run annotations/artifact summaries with secret-safe redaction, granular repository permission probing for PR creation, durable bounded execution journals and resumable plans, webhook/event ingestion with source verification, multi-repo search with owner scope and budgets, release deployment environment approvals, branch-protection/rulesets visibility, dependency/advisory audits, and automated test selection. These must be separate scoped designs and must not be advertised as implemented v213 capabilities.

## Source validation and owner acceptance

Test `hf_space/test_github_project_v213.py` alongside v210/v211/v212 tool and v211.3 assistant identity regressions, Chat JS parser, mobile UI and HF offline validation. After exact source/CI, publishing and atomic runtime versions are separate guarded steps. Actual signed-in GitHub connection, repository read, edit/PR proposals and live test outcomes remain owner acceptance—never inferred from synthetic mocks. Preserve native Chat save lineage and user-specific profiles.
