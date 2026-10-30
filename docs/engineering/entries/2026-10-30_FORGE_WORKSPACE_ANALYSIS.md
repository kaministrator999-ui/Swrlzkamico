# §E v11.178 read-only current workspace analysis — engineering checkpoint

Stage: SEALED_SOURCE_CI_PASS / Chat deploy requested / ENGINE_DEPLOY_PENDING at documentation close.

Goal: Chat must analyze the active, real §E editor project and current scene/workspace, not assume it can see a rendered scene or inspect code by default. User has physically confirmed successful account/profile/photo and active Sheep Tag picker in the prior release.

- Exact engine source `a05bbe7a1b38121d98eb1044d54373d6da99d2d5` plus synchronized documentation.
- New append-only patch 210 `patches/v11_178_workspace_analysis.py`; local scene/Model Atelier and active level metadata is read through the existing native `context()` function, with 48-record snapshot cap and 32KB overall limit.
- Diagnostic hints: per-type counts, duplicate names, shared positions. These are *review hints*; no collision physics or rendering assertions. No scene/object modification.
- Explicit Analyze workspace button sends `host.analyze` to Chat's authenticated, origin-bound message channel. The Chat side submits the fixed read-only analysis request on the normal conversation path. Existing drafts are preserved.
- Chat source `869ffbb65cb803bb548e0c36061f9ca4c7ff8e9a`; full Chat CI `41128929702` SUCCESS. Its native read dispatcher and `brain_forge.inspection_text` return bounded facts only.
- Engine candidate `b621b19993c6d9c35f2b1e019f89df2a7d603dba`; exact v11.178 seal CI `41129255647` SUCCESS; 210 patches, 68 assets, 7,034,587 bytes, SHA `925c1761e8bc89e22a1ba807320d4ff74f8ed53a6410c4f6e29ed16477773386`. Real browser/Quest user acceptance not established.
- Separate Chat HF and engine HF publication receipts should be appended only after guarded workflows complete. Do not accidentally trigger extra gameplay suites or auto-update game data.

