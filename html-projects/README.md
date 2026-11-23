# §C standalone HTML projects

This folder contains project source, **not** live §C application code.
Each project is isolated in `html-projects/<slug>/`, with a required `index.html`.
The existing Hugging Face Chat Space is the initial publication destination.\nThe project artifacts are kept outside the chat static mount under\n`published-html-projects/<slug>/` and served only through the CSP-sandboxed\n`/api/html-projects/<slug>/index.html` route. The response forces an opaque\norigin (no `allow-same-origin`) and disables network connections and forms.

## Publishing

1. In §C, use its existing owner-reviewed GitHub create/edit actions to commit project files.
2. Review source and validate the project; use an immutable GitHub commit SHA.
3. In §C, send `@GitHub publish HTML project <slug>` to inspect the committed files, source SHA, and exact publication destination. Confirm the same-thread approval in the review panel; the server rechecks the owner-linked GitHub repository and dispatches the Actions workflow, never the model or browser.
4. Send `@GitHub status HTML project <slug>` to check the Actions run and exact live byte/CSP verification. The public URL uses `/api/html-projects/<slug>/index.html`; GitHub byte readback alone is not successful runtime deployment.

No Space or secret setup is added. Publishing uses the existing repository
`HF_TOKEN` secret. The workflow touches only
`published-html-projects/<slug>/` in `kamiloki/Swyrlz`; it must not modify Station,
§E, the existing chat page, or any other project.

Existing previously published project files cannot be silently deleted. Use a
separate expressly approved cleanup flow when removal is needed.

**Security:** The trusted publishing workflow executes only source from its main-branch checkout; a separately checked-out immutable reviewed project revision supplies static assets. Publication requires the owner identity, a same-thread five-minute approval, and a GitHub Actions dispatch; it uses no browser-side GitHub or Hugging Face secret. Published HTML receives a Content-Security-Policy `sandbox allow-scripts` without `allow-same-origin`, blocking §C session access, forms, and network calls. File updates must be committed and reviewed in GitHub before each new publish request.

**Acceptance:** The `swrlz-html-smoke` project is a real three-file page published through this lane and checked with a mobile Chromium click, stylesheet, and sandbox isolation test. The user can use the same approval flow for subsequent projects.
