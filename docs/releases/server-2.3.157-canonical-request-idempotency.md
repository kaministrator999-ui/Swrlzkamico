# Server 2.3.157 — Canonical request idempotency

Production verification of 2.3.156 showed that request-scope exactly-once handling fixed redirect/nested-middleware duplication, but a later resumable HTTP request with the same logical request ID still rewrote the same canonical user message and advanced account state from revision 92 to 93.

2.3.157 makes canonical request/message identity immutable and idempotent. An exact replay of the same request ID, role, message ID, text, state and required server metadata is acknowledged at the existing revision without another durable write. Conflicting reuse of a request or message identity is rejected instead of silently overwriting canonical state.

Web Chat remains 1.5.27. No runtime client asset changed. Production deployment of the stable Python correction remains pending a separate explicit/manual deployment action.

Lineage:
- Stable implementation: d83c77796631196d109abad0cb53fc412b91433f
- Server Runtime 2.3.157 authority: 74ac7616411eb397a8de7ab15a4bd81fd337f8e7