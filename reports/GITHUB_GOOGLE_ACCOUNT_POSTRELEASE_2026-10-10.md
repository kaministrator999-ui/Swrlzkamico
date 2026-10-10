# §wyrlz · Google-scoped GitHub connection · deployment and acceptance handoff

Date (UTC): 2026-10-10

## Source and deployment truth
- Canonical main Space: `kamiloki/Swyrlz` (`https://kamiloki-swyrlz.hf.space/`)
- Integration branch: `feature/github-account-project-start-v191-integration`
- Exact deployed source commit: `dde48db5a68047e4f6074470d2f456b118ad8ac6`
- New Space revision: `a6c5b81e0d42a4f27aef81f9a2f5356810f28ff5`
- Captured rollback Space revision: `f6024df55eaff30d40aa15f783034cfd9589cb60`
- Source PR: https://github.com/kaministrator999-ui/Swrlzkamico/pull/68 (draft review; no claim of PR merge)
- Guarded deployment request run: https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38015433626 — SUCCESS; original Space preserved before upload, deployed checkpoint marked `DEPLOYED_UNVERIFIED`.
- GitHub account/login isolation + Chat JS CI: https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38015279194 — SUCCESS.
- HF candidate offline validation: https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38015302980 — SUCCESS.
- Postrelease external public-route smoke from GitHub runner: https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38015682520 — SUCCESS. Remote Space SHA matched `a6c5b81...`; `GET /api/account/status` returned 200 with Google client authority; unauthenticated `GET /api/github/status` returned 401.

## User-visible acceptance still required
1. Owner signs into Google at `https://kamiloki-swyrlz.hf.space/`, opens side menu, sees GitHub Connect control, selects `Connect GitHub`.
2. Authorizes their OAuth app; is redirected to same Space; GitHub connected status shows verified account.
3. Selects their own public repository, saves selection, presses Read §tart, sends the prepared prompt, and inspects source-grounded startup handoff.
4. Signs out, returns through Google auth and verifies GitHub connection is retained by the same Google subject.
5. Confirms a different Google account cannot view another's GitHub connection or account-owned sessions. Revocation/disconnect should fail closed.
6. Check the GitHub OAuth app is configured for non-expiring access tokens for this first release (future implementation should add refresh token support).
7. Rotate the Upstash REST token that was visible in a private troubleshooting screenshot and replace the Hugging Face secret. The model was never given an instruction to echo/store it and the GitHub source contains no credential.

## Status
`SOURCE_VALIDATED` + `DEPLOYED` + `PUBLIC_ROUTE_LIVE_VERIFIED`.
`FULL_USER_OAUTH_ACCEPTANCE_PENDING` — neither account-token continuity nor private encrypted Redis write/read was tested by public-route smoke. Do not assert production parity or full ChatGPT GitHub Connector semantics.

The existing implementation performs bounded public repository reading and deterministic evidence-backed §tart handoff. It does not grant agent repo writes or automatically execute untrusted repository instructions. Do not bump final module versions or mark the Roadmap FINISHED until user acceptance has been observed.
