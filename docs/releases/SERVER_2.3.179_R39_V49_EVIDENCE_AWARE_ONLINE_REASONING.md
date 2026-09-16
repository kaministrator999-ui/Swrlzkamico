# Server 2.3.179 — R39 v49 Evidence-Aware Online Reasoning

**LALM:** 2.1.60 / v49  
**Deployment:** NONE for this runtime event  
**Restart:** NONE

R39 now accepts a bounded `swrlz_online_evidence_v1` bundle supplied by an authorized server capability. Retrieved titles, URLs, snippets, and source metadata are explicitly treated as untrusted external evidence with zero instruction authority. The Brain is instructed to map evidence back to the user's actual goal and constraints, distinguish discovery from verification, evaluate authority/recency/directness/corroboration/conflict, and expose source basis when retrieved evidence materially supports an answer.

This event does not itself create the stable network retrieval capability. That implementation is staged separately on `server-online-research-v1` because it crosses the stable server/API boundary and requires an approved production deployment before it can become live.

Camera instrumentation adds an `online-evidence` event with bounded evidence count and trust/authority metadata. Operational progress remains visible status, never hidden chain-of-thought.
