# v262 — General GitHub CREATE_FILE / binary upload release receipt

Date: 2026-10-15
Target application: `kamiloki/Swyrlz` — the existing §wyrlz AI Chat Hugging Face Space

## User goal
Expand beyond the previously verified new `.txt` test file action to support the ordinary range of filenames and file formats stored on GitHub. Preserve the existing Google-linked GitHub connection, owner consent controls, and GitHub work statistics.

## Implemented
- Source, configuration, JSON/CSV/XML, Markdown, extensionless files and dotfiles in nested directory paths, and binary file uploads (e.g. PNG, PDFs) through a **separately reviewed** `CREATE_FILE` workflow.
- Uses the **currently selected** public owner repository, either `kaministrator999-ui/Swrlzing-core` or `kaministrator999-ui/Swrlzkamico`, and its verified default branch. The server checks current signed-in Google identity, connected encrypted GitHub OAuth record, actual write scope, owner account and live push role.
- Strict non-overwrite GitHub Contents API PUT with no previous-file SHA; preflight GET before prepare and again before create; exact remote byte-by-byte and SHA-256 verification after writing. One-time five-minute preparation ticket that another account cannot consume.
- Chat recognizes general file-creation requests as a bounded *proposal*, opening path/text or local binary selection, then explicit **Prepare** and **Confirm** controls. Untrusted generated text is never itself commit authorization.
- Returns a generalized verified GitHub work dashboard with filename/commit links, byte size, text-line count where applicable, and provider-backed commit diff statistics where available.
- The original v259 direct harmless `.txt` test-file shortcut remains unchanged. Existing edit, delete, branch, issue, workflow dispatch and deploy abilities are not unlocked.

## Limits / excluded work
- **1,000,000-byte per-file bound** for this initial GitHub Contents API + JSON base64 + exact-read-back adapter. GitHub itself supports other sizes/methods; this tier is not Git LFS or a bulk repository uploader.
- The current permission model is the two explicitly supported **public owner repositories** only. Private/third-party repo writes, larger files and Git LFS require separately reviewed authorization and implementation.
- Special `.github/workflows/*` file paths may require GitHub's additional workflow OAuth grant, which is not silently requested by the application.
- Arbitrary model-authored source generation or automatic commits outside the harmless test shortcut are not claimed. Creation of other files remains per-file review/confirmation.

## GitHub source / validation
- [PR #188](https://github.com/kaministrator999-ui/Swrlzkamico/pull/188): **merged**.
- Deployed source commit: `2f6dea82951aab7c283a09b17aa0ab4bb2cd8062`.
- Offline candidate CI [Actions #38824418111](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38824418111): **SUCCESS**.
- Mobile integrity [Actions #38824419133](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38824419133): **SUCCESS**.
- Guarded Hugging Face deployment [Actions #38824542751](https://github.com/kaministrator999-ui/Swrlzkamico/actions/runs/38824542751): **SUCCESS**.
- Resulting Space revision: `c3e42c8a4b7384ec17375864ed70af707be89b5f`.
- Preserved rollback revision: `8a57553a14603cb0826e600c275e11b0c5afc7dc`.
- Deployment checkpoint: **DEPLOYED_UNVERIFIED**; signed-in mobile non-`.txt` creation has not yet been independently verified.
- Version registry: repository-work `1.0.201`, server-runtime `2.3.413`, web-chat `1.5.144`.

## Suggested live acceptance
With `Swrlzing-core` selected in Chat, request `Create a new JSON file named docs/v262-check.json in my GitHub repo`. Confirm that the app opens a review of the **selected repository and path**, enter innocuous JSON content `{"ok":true}`, press Prepare, check the SHA-256 and no-overwrite status, then Confirm. Finally verify the exact file, commit and dashboard metrics directly on GitHub. To verify binary upload, repeat with a small local PNG. This tests the new file types rather than retesting the prior .txt shortcut.
