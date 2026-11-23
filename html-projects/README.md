# §C standalone HTML projects

Generated HTML project source belongs in `html-projects/<slug>/` on GitHub,
including a required `index.html`. These files are not served from the
authenticated chat application tree.

The existing Hugging Face Space `kamiloki/Swyrlz` stores published files in
`published-html-projects/<slug>/` and serves them at
`https://kamiloki-swyrlz.hf.space/api/html-projects/<slug>/index.html`.
Every HTML/SVG document receives a CSP sandbox that forces an opaque origin
(no `allow-same-origin`), blocks network fetches and forms, and keeps Chat
account cookies/API unavailable to project scripts.

## From §C Chat

1. Use the existing `@GitHub` reviewed CREATE_FILE / UPDATE_FILE workflow to
   commit the HTML, CSS and JavaScript in `html-projects/<slug>/`.
2. Open the GitHub connection panel and select **Publish HTML**.
3. Enter the slug and choose **Review committed project**. The server reads
   the precise `main` commit, validates all project files and displays the
   pinned manifest and an opaque-origin `index.html` preview. Relative assets
   in this preview may not load until the project is actually published.
4. Check the explicit approval box, then **Approve and deploy**. Approval is
   single-use and expires. No model-generated text authorizes this action.
5. §C dispatches `.github/workflows/hf-html-project-publish-v1.yml` with
   the pinned commit, slug and unique deployment receipt. The UI tracks GitHub
   Actions and opens the public page only after the workflow has verified
   exact uploaded bytes, a live HTML 200 response, the CSP sandbox and the
   served `index.html` digest.
6. If a Space rebuild resets the Chat server, deployment status is recovered
   from the immutable GitHub Actions run title and the browser tab's stored
   receipt. A failed run is not reported as deployment success.

## Security and scope

Only owner-authenticated, linked GitHub accounts can approve the deployment.
The workflow runs trusted code from the default branch and reads the reviewed
project in a separate checkout. It uses the repository's existing `HF_TOKEN`
secret and serializes access to the existing Chat Space; no new Space,
account, service, or secret is required. §E, Station, account records and the
existing Chat page are never part of a project file upload.

Publish rejects missing or excessive files, unsafe paths, symlinks, unapproved
extensions and stale files that would require deletion. Deleting previously
published files requires a separate explicit change.

The publish UI and owner action are released by
`.github/workflows/hf-chat-html-publish-integration-release.yml` using a
separate, guarded live Station patch. GitHub Actions logs and scoped backup
artifacts provide deployment evidence and a rollback path.
