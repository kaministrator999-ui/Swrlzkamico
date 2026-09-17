# Server 2.3.237 — Deployment Gate Repair

## Status

- **Server:** `2.3.237`
- **Deployment Control:** `1.0.8`
- **LALM:** `2.1.78` / `2.1.78-hot-programming-mode-context-v66-camera-lineage` unchanged by this event
- **Chat:** `1.5.66` unchanged
- **Repair state:** source/config complete; Git auto-deployment gate verified by post-repair canary commits

## Problem

A documentation-only `main` commit unexpectedly created production Vercel deployment `dpl_FPM6etnF9ZMHVeVmhx7AnLMSCwCe` from Git commit `88eed351f6e768d3da544a5cd0c69aeb8f17545e`.

This violated the intended production boundary: ordinary source/documentation commits should not deploy the stable application. Production deployment should occur only through an explicitly approved deployment path.

Inspection of the exact unexpectedly deployed commit proved that `vercel.json` already contained:

```json
"git": {
  "deploymentEnabled": false
}
```

Therefore the observed defect could not be repaired by merely re-adding that declaration.

## Architecture reconciliation

The deployment architecture had two effective production writers:

1. the intended approved GitHub Actions → Vercel CLI path;
2. an unintended native Git integration path capable of deploying `main`.

The correct repair was to preserve one canonical deployment owner and disable the competing automatic writer.

## Repair

### Dual fail-closed Git guard

`vercel.json` now contains both:

```json
"git": {
  "deploymentEnabled": false
},
"github": {
  "enabled": false
}
```

The modern Git-disable declaration remains canonical. The GitHub-specific compatibility guard is retained because observed production behavior showed the modern declaration alone was insufficient for the project's existing integration state.

### Source-bound manual production verification

`.github/workflows/manual-vercel-production.yml` remains the canonical production deployment path and still requires explicit authorization.

Its acceptance step now:

1. records the exact SHA of the approved checkout;
2. parses canonical stable-server `VERSION` from `api/index.py` using Python AST;
3. deploys the approved source through the Vercel CLI;
4. requires `/api/server/status.version` to equal that source-owned stable version;
5. requires `/api/server/status.deploymentCommit` to equal the exact approved source SHA;
6. requires production environment identity;
7. preserves the existing continuity, manifest-authority, RMCCA, hot-runtime, and collector acceptance checks.

This replaces the stale duplicated literal `2.3.110`. At repair time the canonical stable server source and live production status both report `2.3.111`.

The stable server version is intentionally distinct from the overall runtime-hot Server lineage in `versions/server-runtime.txt`.

## Verification

### Automatic deployment canaries

After the dual guard was committed:

- commit `492b23f56bb4533c448da47adf7f15b6f622b09d` changed `vercel.json`;
- commit `9fdab0ea4ab72747b471cabd942702d5f1959cb1` changed the manual deployment workflow;
- later documentation/governance commits completed the contract/roadmap closure.

Vercel deployment history remained anchored at the pre-repair deployment `dpl_FPM6etnF9ZMHVeVmhx7AnLMSCwCe`; no newer native-Git production deployment appeared during the repair canaries.

### Manual path architecture

No manual production deployment was required merely to prove that automatic Git deployment had been disabled. The manual path was statically reconciled to source-owned identity and remains subject to explicit deployment approval when actually invoked.

## v66 activation evidence discovered during diagnosis

Production runtime logs also supplied the previously missing loader-level proof for Phase 1 programming mode:

- hot-entry target `v66`;
- immutable source commit `3b2379eecd3f68d2aec20ae9839f156b9d79e175` fetched successfully;
- hydration completed with `hotServerVersion=2.1.77` and revision `2.1.77-hot-programming-mode-context-v66`;
- planner, response contract, conversation state, programming profile, programming context, and camera contracts were callable.

Concurrent runtime work subsequently advanced the LALM authority to `2.1.78` with v66 camera-lineage changes. Server 2.3.237 preserves that lineage and does not claim full repository/tool-loop acceptance from loader hydration alone.

## Version/concurrency handling

While this repair was underway, concurrent work advanced Server authority through `2.3.236` and LALM authority to `2.1.78`.

The repair re-read current authorities before assignment, preserved those changes, advanced only Deployment Control from `1.0.7` to `1.0.8`, and then assigned overall Server `2.3.237`.

## Lineage

- dual Vercel Git guard: `492b23f56bb4533c448da47adf7f15b6f622b09d`
- source-bound manual deployment verification: `9fdab0ea4ab72747b471cabd942702d5f1959cb1`
- Deployment Control `1.0.8`: `717d4ed563c48fec551ae66a0059b4507eff5c64`
- Server `2.3.237`: `7dfe75b6f5c5c94bbcec8aceed894bf366aeb118`
- Hotfix contract update: `62dfae9abd0f9af152b64d224cf14d6b5a520a2e`
- roadmap update: `7e03eb5507c7af0a0a04400326937a42285a9199`

## Bottom line

Production deployment now has one intended authority: an explicitly approved manual deployment path. Native Git deployment is guarded fail-closed with both the modern Vercel Git declaration and the GitHub compatibility declaration, and deployment acceptance is bound to the exact approved source rather than a stale duplicated version literal.
