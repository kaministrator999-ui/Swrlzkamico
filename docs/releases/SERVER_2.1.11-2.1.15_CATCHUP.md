# SERVER 2.1.11–2.1.15 catch-up release notes

Date: 2026-09-07  
Chat lineage: 1.3.5 -> 1.3.12

## 2.1.11

- separated Chat status from R39 model inspection;
- `/api/chat/ops` became a cheap receipt path instead of an inference trigger;
- introduced Admin-authorized ephemeral Chat sessions while preserving direct Chat-token fallback.

## 2.1.12

- resolved `SWRLZ_ADMIN_TOKEN` per request instead of using an import-time snapshot;
- normalized only harmless outer whitespace / one matching quote pair;
- kept exact constant-time identity comparison;
- repaired Page Manager SET ADMIN failures seen after deployment.

## 2.1.13

- moved live page/Chat reads to GitHub `dev` per request;
- added short bounded in-instance cache plus bundled fallback;
- eliminated dependency on one Vercel instance's `/tmp` for normal live reads;
- proved Chat UI version changes on `dev` could appear live with the server version unchanged and without `/api/pages` sync.

## 2.1.14

- replaced instance-local in-memory Admin Chat sessions with stateless signed sessions;
- allowed any Vercel instance with the shared signing secret to verify the same issued session;
- Chat stopped auto-opening settings when authorization was absent and reported authorization state instead.

## 2.1.15

- changed normal Chat authorization to server-managed same-origin browser sessions;
- `/api/chat` page loads receive a bounded HttpOnly, Secure, SameSite=Strict cookie scoped to `/api/chat`;
- session signatures derive from the server-side Chat secret;
- the permanent `SWRLZ_WEB_CHAT_TOKEN` never enters browser JavaScript;
- direct Chat-token and explicit Admin-session paths remain compatibility fallbacks;
- Chat 1.3.12 removes the normal credential field, renames the dialog to Chat Settings, and no longer requires Admin bootstrap before send.

## Live page acceptance receipt

The intended no-redeploy flow is now:

`GitHub dev page/UI change -> browser refresh -> live source changes`

Stable server version remains unchanged for page-only updates. Backend/auth/middleware/inference changes still require deliberate `main` deployment.

## Truth boundary

These notes record source changes and observed version receipts from the live Chat UI. They do not claim R39 interactive inference readiness unless a generation/verification receipt establishes it separately.
