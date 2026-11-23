# §C standalone HTML projects

This folder contains project source, **not** live §C application code.
Each project is isolated in `html-projects/<slug>/`, with a required `index.html`.
The existing Hugging Face Chat Space is the initial publication destination.\nThe project artifacts are kept outside the chat static mount under\n`published-html-projects/<slug>/` and served only through the CSP-sandboxed\n`/api/html-projects/<slug>/index.html` route. The response forces an opaque\norigin (no `allow-same-origin`) and disables network connections and forms.

## Publishing

1. In §C, use its existing owner-reviewed GitHub create/edit actions to commit project files.
2. Review source and validate the project; use an immutable GitHub commit SHA.
3. Explicitly dispatch `.github/workflows/hf-html-project-publish-v1.yml` with the full
   commit SHA, project slug, and **approved=yes**.
4. Verify the Actions receipt and public HTML URL. Do not equate Git blob readback
   with functioning browser delivery.

No Space or secret setup is added. Publishing uses the existing repository
`HF_TOKEN` secret. The workflow touches only
`published-html-projects/<slug>/` in `kamiloki/Swyrlz`; it must not modify Station,
§E, the existing chat page, or any other project.

Existing previously published project files cannot be silently deleted. Use a
separate expressly approved cleanup flow when removal is needed.

**Current limitation:** §C's conversational create/edit approval is separate from
GitHub Actions dispatch. A server-side owner-approved workflow trigger and a
corresponding in-chat deployment status/receipt UI still need integration.
