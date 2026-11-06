# Chat character mesh tools v2 checkpoint

Status: local implementation candidate; publication and real-model visual
acceptance remain owned by the coordinated §C/§E integration checkpoint.

Canonical Chat baseline: `28c07377f36cd342a556ae320a18ac774df7ad6b`, the
current main request source when this recovery began. This keeps the existing
free self-hosted CPU vision addition. Engine integration targets the successor
to main v11.280; the engine package, native append-only patch and release seal
are maintained independently. No deployment request is changed here.

Current integration baseline is `9487a4f0d587da07aed77ecfe5474f7dd8aeeb61`
(original-source vision v14). The earlier bases above are historical. Its newer
vision/cancellation/accepted-thread work was preserved when these character-tool
commits were replayed. The Engine build identity is assigned at its own final
promotion gate; no provisional version reserves a slot on concurrent main.

The user requests the embedded Chat to construct a recognizable crystal mage
from the supplied purple-hooded character reference, drive the visible native
editor, and describe actual work while it happens. The implementation adds
general mesh descriptions rather than a fixed mage model or server preset.

`forge_mesh_tools_v2.py` is the common Chat capability/geometry contract. Only
the exact current host declaration enables64 operations, loft and lathe meshes,
and Model Atelier framing. Existing hosts remain limited to16 primitive actions.
Loft has2–40 finite xyz points in[-100,100], corresponding radii[.00025,5],
and optional8–64 integer segments. Lathe has2–24 radius/y pairs, radius[0,5],
y[-100,100], at least one positive radius, optional arcStart[-2π,2π],
arcLength[.05,2π], and8–64 integer segments. Both reject consecutive points
at distance<=.000001 and fields belonging to another geometry. Geometry is
creation data; mesh.set retains its previous attribute-only contract.

The existing pinned Qwen7B planner and32k context remain in place. The native
planner reserves up to12k output tokens within the existing fitter, uses a
grammar derived from the actual leased workspace/capabilities, and receives
instructions for purposeful character decomposition, curved garments/hair,
local coordinates and face openings. One repair is allowed after a complete
decoded plan fails concrete typed validation. Truncated/invalid JSON and revoked
or stale capabilities do not trigger this repair. Neither failed plan executes.

All curved/frame/over16 plans require a v2 preview and the original exact frozen
server-held approval. Review includes every operation and full geometry values;
v1 remains available for legacy primitive plans. The encrypted owner/session/
host/project/snapshot binding and atomic one-use claim are unchanged.

The batch application deadline is fixed at registration+25s. Take returns the
floor of remaining milliseconds, at most25000 and at least1000, while delayed
or expired delivery fails closed. Native host enforcement uses a conservative
local request-start budget and existing heartbeat renewal. The server still
waits30s for actual receipts, so a late host cannot start a forgotten edit.

Trusted private-port progress is correlated to current batch, generation and
thread. It can display per-action work but cannot complete the answer. Stop
revokes immediately. Server terminal events retire the transient display.

Focused verification is recorded by the new backend mesh-tools regression and
the existing native planner/embed suites, plus broker and real Chromium
controlled-transport tests. These controlled tests establish protocol and UI
behavior; the real §C mage run and visual result remain separate integration
evidence. Full test counts and final source hashes belong in the release handoff
after the coordinated engine/Chat verification completes.

Local verification on2026-11-05 passed81 backend cases: mesh-tools19, native
planner30, encrypted embed25 and studio commands7. Broker and popup recovery
Node regressions passed. Actual controlled Chromium covered the canonical Chat
at desktop, mobile and Android desktop-site sizes, and the new40-step curved
preview/progress scenario at desktop and mobile sizes. The new scenario checks
literal markup names, complete geometry review, malformed-preview refusal,
stale-generation rejection, frozen approval, immediate Stop revocation and
retirement only after server terminal evidence. Existing CPU vision and media
contracts passed. Canonical source preparation and its exact-byte check passed.
ASGI TestClient runs used the environment's network-enabled sandbox because its
restricted socket implementation stalled the local test event loop; test
storage and account transport remained controlled fixtures without real Google
or Redis access.

The final followup also grounds inspection requests containing a no-edit
constraint in the authenticated native summary instead of generic inference.
Batch registration retries at most three confirmed failed atomic comparisons,
revalidating owner, session, generation, snapshot and one-use proposal on each
attempt. Heartbeat-only ciphertext/expiry refresh can therefore succeed; changed
scenes, cancellation, consumed approvals and unknown storage outcomes never
bypass the original guards. The planner and encrypted embed suites now contain
34 and 29 passing cases respectively, including the observed read-only wording
and the heartbeat race. Live model construction remains pending deployment.
