# Server 2.1.16 / Chat 1.3.13

Date: 2026-09-07

Production route: `https://swrlzkamico-o3nu.vercel.app`

## Trigger receipt

A live `LOCAL_R39` request admitted successfully, reconstructed/verified R39, resolved the local Python reference route, and began a 55-token prefill. The trace reached only `Prefill 16/55` before the browser stream failed at roughly 153 seconds. Repeated compute heartbeats showed that the request remained inside active inference rather than failing routing or model loading.

## Change

- Increase bounded matvec dequantization target from 4 MiB to 16 MiB to amortize dequantization and BLAS-call overhead.
- Cache small decoded matrices/vectors per model instance.
- Compact only the stock local bridge response directive before tokenizer prefill; custom directives remain untouched.
- Preserve the canonical Python/NumPy reference engine, bounded-memory behavior, stream contract, and Truth Firewall.

## Non-claim

This revision reduces avoidable reference-executor overhead. It does not claim compiled-backend throughput and does not guarantee that arbitrary context/output lengths will complete inside Vercel execution limits.

## Validation targets

1. production reports Server `2.1.16` and Chat `1.3.13` after deployment;
2. hot engine revision reports `2.1.16-prefill-hotpath`;
3. the same short prompt produces fewer prefill tokens than the 55-token baseline when the stock bridge directive is used;
4. `Prefill 16/N` occurs materially earlier than the prior ~79-second mark;
5. first `DELTA`/TTFT is measured rather than inferred;
6. if still too slow, the next rung is a compiled/vectorized execution backend rather than additional heartbeat tuning.
