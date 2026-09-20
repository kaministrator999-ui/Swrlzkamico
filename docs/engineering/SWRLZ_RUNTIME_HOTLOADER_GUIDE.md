# §wyrlz Runtime Hotloader Integration Guide

**Role:** operational manual for adding, changing, verifying, and troubleshooting runtime-hot application surfaces without confusing repository work, runtime activation, and Server deployment.

**Entry point:** `SWRLZ_PROJECT_START.md` routes here whenever work adds or changes runtime-hot pages/assets/modules.

---

## 1. Mental model

```text
runtime branch = durable runtime application authority
main branch    = stable loader / infrastructure / engineering contracts

runtime commit
   ↓
runtime manifest / registered hot source
   ↓
stable loader reads runtime authority
   ↓
live application observes new runtime source
```

A runtime-hot update does not inherently deploy the stable Server. Repository Work still advances because governed repository work occurred. The changed component advances because its source changed. Server Runtime advances only when a Server release/deployment advances deployed Server lineage.

---

## 2. Two runtime-hot delivery mechanisms

### A. Manifest-routed live pages/assets — preferred for web pages

Stable owner: `api/live_source_guard.py`.

Runtime authority: `runtime_pages/manifest.json` plus runtime-owned source files.

The stable guard reads the manifest from GitHub repository-content authority, resolves a route, fetches its runtime source, and injects only the styles/scripts declared by that route. Manifest-routed runtime changes require no Server restart/deployment while the stable loader ABI already supports them.

Use this path for new runtime pages such as `/chat/§wyrlz`.

Route shape:

```json
"/chat/§wyrlz": {
  "source": "chat/§wyrlz/index.html",
  "styles": [],
  "scripts": []
}
```

The route source itself is the stage. Add styles/scripts to the route only when that scene actually needs them. Do not inherit another page's loader stack merely for convenience.

### B. Hydrated hot sources — bounded server-side/runtime modules

Stable owner: `api/runtime_hot.py`.

Its `SOURCES` registry maps a runtime-branch source path to a worker-local hydrated target. The loader resolves one immutable runtime branch head, fetches all registered sources from that same snapshot, compares hashes, atomically writes changed files, and invalidates/reloads owners where required.

Use this mechanism only when the stable runtime already expects a worker-local hydrated file/module. Do not register ordinary manifest-routed pages here just to call them “hot.”

---

## 2A. Route-to-source discovery convention

Runtime-hot naming is resolved from authority, not guessed from the default branch.

For a user-facing route or page reference:

```text
live/user route
   ↓
runtime:runtime_pages/manifest.json
   ↓
exact route entry
   ↓
source + styles + scripts
   ↓
runtime-owned files
```

Preserve route segments exactly, including Unicode characters and sigils. For example, `/chat/§wyrlz` resolves through the manifest to `runtime:chat/§wyrlz/index.html`; the implicit page filename is `index.html` because the manifest declares that source, not because callers should blindly append `index.html` to every route.

For hydrated runtime sources, use the stable hotloader registry/owner to resolve the runtime source path. Do not infer absence from a `main`-branch 404 when the component class is runtime-hot capable. A generic/default-branch code search is secondary discovery evidence because it may not index the `runtime` authority.

When the user supplies a live route or recognizable runtime-hot component name, prefer **route/component → manifest/registry → declared source** over filename guessing.

---

## 3. Adding a new manifest-routed page

1. Enter through `SWRLZ_PROJECT_START.md` and read the required contracts.
2. Capture Repository Work, Server Runtime, affected component, Runtime Manifest, and target-source SHAs.
3. Reconcile ownership before adding files.
4. Write Roadmap **UPDATE STARTED**.
5. Create the runtime-owned page/source.
6. Add the exact route to `runtime_pages/manifest.json`.
7. Add only the assets that page needs.
8. Re-read version authorities for concurrency.
9. Advance Repository Work, the changed component, and Runtime Manifest. Do **not** advance Server Runtime unless a Server release/deployment actually occurs.
10. Fetch back source + manifest + version authorities.
11. Verify the route through the runtime source path/live surface when available.
12. Write Roadmap **UPDATE FINISHED** with source/static/runtime/live truth explicitly separated.

---

## 4. Adding a hydrated runtime source

Before changing `api/runtime_hot.py`, determine whether the existing stable loader ABI can already hydrate the needed class of source. If stable loader code itself must change, that is stable/main work and may require a later Server deployment to activate.

For an already-supported hydrated source:

1. place durable source on `runtime`;
2. register source path, hydrated target, and bounded size in the canonical `SOURCES` owner if registration is already runtime-configurable; otherwise stable-loader modification is required;
3. define invalidation/reload behavior when code/state can remain resident;
4. keep one runtime-head snapshot per sync so files cannot mix revisions;
5. verify hashes and loader status;
6. advance the affected component and Repository Work;
7. advance Server Runtime only for an actual Server release/deployment event.

Never use `/tmp` as durable authority. Worker-local hydrated files are caches/materializations of repository authority.

---

## 5. Runtime Manifest contract

`runtime_pages/manifest.json` is the route/asset activation map.

A manifest revision advances whenever its route/source/style/script activation map changes. `versions/runtime-manifest.txt` owns the declared manifest version and must match the manifest's version.

For each route:

- `source` identifies the one canonical page source;
- `styles` are ordered page-owned stylesheet dependencies;
- `scripts` are ordered deferred page-owned script dependencies;
- omit unrelated legacy assets;
- never make two visual shells co-own one route.

The manifest is activation metadata, not a dumping ground for feature logic.

---

## 6. §wyrlz Chat theater rule

For `/chat/§wyrlz`:

- one authoritative stage/page source;
- scenery required for the first meaningful frame is present before curtain-open;
- starting props/actors are scoped to the opening scene;
- open-curtain actors may enter/leave/update without rebuilding the stage;
- major scene transitions are prepared and committed coherently;
- stagehands (transport, persistence, cameras, routing, inference, tools) remain backstage;
- first meaningful frame should closely match settled idle geometry;
- no obsolete fallback Chat may visually compete underneath it.

The page begins intentionally minimal and grows by scoped tiers. Do not copy the legacy `/chat` runtime-loader stack into it.

---

## 7. Verification levels

Always state which level actually passed:

- **source verified** — committed/fetched source is correct;
- **static verified** — manifest/contracts/version ownership reconcile;
- **runtime-hot verified** — stable loader resolved the new runtime revision;
- **live verified** — user-visible route behaved as intended;
- **Server deployed** — only when the canonical deployment workflow actually released stable Server code.

These states are not interchangeable.

---

## 8. Roll-forward discipline

Runtime-hot does not mean uncontrolled mutation.

Each scoped tier follows:

```text
Project Start
→ baseline
→ architecture reconciliation
→ Roadmap START
→ smallest coherent tier
→ re-read authorities
→ version affected axes
→ verify
→ Roadmap FINISH
→ next tier
```

If a tier fails, preserve the failure in roadmap lineage and correct it in a later tier. Do not hide a failed route/manifest revision by rewriting history.

---

## Bottom line

**Repository Work tracks the engineering journey. Component versions track the pieces. Runtime Manifest tracks runtime page/asset activation. Server Runtime tracks deployed Server releases. Runtime-hot lets the stage evolve without pretending every prop change rebuilt the theater.**
