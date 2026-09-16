# Server 2.3.186 — Chat Activity Single Ownership + Online Default

- Server Runtime: 2.3.186
- Web Chat: 1.5.45
- Runtime manifest: 110
- Deployment: none
- Restart: none

## Activity log
Replaces the observer-driven Activity expansion synchronizer with render-time state application and one delegated user-toggle writer. This removes the MutationObserver/render feedback loop that could cause repeated DOM churn, lag, and Activity controls visibly jumping between intermediate layouts. Streaming state remains the initial default only until the user explicitly chooses an expansion state; the saved user choice then owns subsequent renders.

## Online research
Online research is enabled by default when Chat initializes. The user can still turn the Online control off for the current page/session. The Mask continues to relay only the explicit control state; research interpretation remains Brain-owned and retrieval execution remains server-owned.

## Verification
Repository/runtime authorities were re-read at the commit boundary. Live browser acceptance remains to be verified with a fresh Chat load and Activity toggle/stream test.
