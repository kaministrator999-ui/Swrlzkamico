# Forge in-place mesh shaping

Model Atelier's native Chat bridge accepts a single `mesh.reshape` proposal on a supported existing part. An explicit shape request can use this operation when the open editor advertises `swrlz-forge-mesh-shape-edit-v1` with eligible mesh IDs from its current snapshot. A request to remove a part and add a replacement follows the existing construction path.

The planner chooses a sphere, box, cone, cylinder, or loft. A loft carries a local path, matching radii, and segment count through existing shape validation. The operation targets one exact existing ID and carries only geometry. The preview names that part, displays the proposed shape at the existing transform, and shows the full frozen fields. The preview projection uses the editor's XYZ rotation convention and shows a cylinder as two connected rings.

The server requires the same account, conversation, host, project, and snapshot at approval. The fresh approval turn registers one batch on its active lease and atomically claims the stored proposal. The server rejects an expired, changed, or already used proposal. Verified image observations can inform planning. The current human approval phrase is the write trigger.

Completion requires a native receipt for the reviewed operation, target ID and shape. A receipt for an already matching shape reports zero changed operations. The release test exercises bounded shape-only routing, compatibility with older hosts, frozen data, the approval boundary, stale snapshots, replay, and native receipt checks. The served Atelier host and autonomous modeling quality require separate live verification.
